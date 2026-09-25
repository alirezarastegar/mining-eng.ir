#!/usr/bin/env python3
import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BROKER = "https://tinsqtvdnzzslgohtiyg.supabase.co/functions/v1/mra-r1263-worker-broker"
AUDIENCE = "mra-r1263-external-worker"
RUN_KEY = f"gh-{os.environ['GITHUB_RUN_ID']}-{os.environ.get('GITHUB_RUN_ATTEMPT','1')}"
MODE = os.environ.get("MODE", "worker")
WORKER_ID = os.environ.get("WORKER_ID", "verify")
DURATION = int(os.environ.get("BURNIN_SECONDS", "90"))
JOBS = int(os.environ.get("BURNIN_JOBS", "48"))

def get_oidc():
    base = os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]
    sep = "&" if "?" in base else "?"
    url = base + sep + "audience=" + urllib.parse.quote(AUDIENCE, safe="")
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())["value"]

OIDC = get_oidc()

def call(action, **kwargs):
    payload = {"action": action, "run_key": RUN_KEY, "worker_id": WORKER_ID, **kwargs}
    raw = json.dumps(payload, separators=(",", ":")).encode()
    req = urllib.request.Request(
        BROKER,
        data=raw,
        headers={"Authorization": "Bearer " + OIDC, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            out = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"broker_http_{e.code}:{body[:500]}")
    if not out.get("ok"):
        raise RuntimeError("broker_error:" + json.dumps(out, sort_keys=True)[:800])
    return out

def suffix(job):
    try:
        return int(str(job["idempotency_key"]).rsplit(":", 1)[1])
    except Exception:
        return -1

def seed():
    out = call("seed", jobs=JOBS)
    print(json.dumps({"mode": "seed", "run_key": RUN_KEY, "result": out.get("data")}, sort_keys=True))

def worker():
    deadline = time.time() + DURATION
    handled = 0
    provider_calls = 0
    while time.time() < deadline:
        out = call("claim")
        job = out.get("job")
        if not job:
            time.sleep(0.35)
            continue
        handled += 1
        idx = suffix(job)
        attempt = int(job.get("attempt") or 0)
        jid = str(job["job_id"])
        token = str(job["lease_token"])

        if idx == 6 and attempt == 1:
            call("event", event_kind="crash_claim", job_id=jid, lease_token=token,
                 details={"simulation": "worker_process_loss", "lease_seconds": 8})
            print(json.dumps({"worker": WORKER_ID, "simulated_crash_after_claim": jid}))
            return

        if idx == 5 and attempt == 1:
            call("event", event_kind="inject_network", job_id=jid, lease_token=token,
                 details={"simulation": "connection_blackout", "sleep_seconds": 11})
            time.sleep(11)
            stale = call("finalize", job_id=jid, lease_token=token,
                         terminal_status="succeeded", reason="stale_worker_should_be_rejected")
            if stale.get("accepted"):
                raise RuntimeError("stale_finalize_was_accepted")
            continue

        if idx == 3 and attempt == 1:
            call("defer", job_id=jid, lease_token=token, reason="inject_429", delay_seconds=1)
            continue

        if idx == 4 and attempt == 1:
            call("defer", job_id=jid, lease_token=token, reason="inject_503", delay_seconds=1)
            continue

        if idx in (1, 2):
            b = call("budget", job_id=jid, lease_token=token, estimated_cost_usd=0.6, daily_limit_usd=1.0)
            if not b.get("allowed"):
                fin = call("finalize", job_id=jid, lease_token=token,
                           terminal_status="blocked", reason="expected_budget_exhaustion")
                if not fin.get("accepted"):
                    raise RuntimeError("budget_block_finalize_rejected")
                continue

        if idx in (11, 12):
            call("rate", job_id=jid, lease_token=token, scope="fleet")

        if idx in (7, 8, 9, 10):
            p = call("provider_probe", job_id=jid, lease_token=token)
            if not p.get("ok"):
                call("defer", job_id=jid, lease_token=token, reason="provider_probe_retry", delay_seconds=1)
                continue
            provider_calls += 1

        hb = call("heartbeat", job_id=jid, lease_token=token)
        if not hb.get("accepted"):
            continue

        time.sleep(random.uniform(0.04, 0.14))
        fin = call("finalize", job_id=jid, lease_token=token,
                   terminal_status="succeeded", reason="")
        if not fin.get("accepted"):
            call("event", event_kind="stale_finalize_observed", job_id=jid, lease_token=token,
                 details={"after_heartbeat": True})

    call("event", event_kind="worker_done",
         details={"handled": handled, "provider_calls": provider_calls, "duration_seconds": DURATION})
    print(json.dumps({"mode": "worker", "worker": WORKER_ID, "handled": handled,
                      "provider_calls": provider_calls, "duration_seconds": DURATION}, sort_keys=True))

def verify():
    # Deterministic shared-rate-limit pair, isolated from fleet timing.
    call("rate", scope="verify")
    call("rate", scope="verify")

    end = time.time() + 35
    stats = {}
    while time.time() < end:
        stats = call("stats").get("stats") or {}
        active = int(stats.get("queued", 0)) + int(stats.get("retry", 0)) + int(stats.get("running", 0))
        if active == 0:
            break
        time.sleep(1)

    checks = {
        "total_jobs": int(stats.get("total_jobs", 0)) == JOBS,
        "queue_drained": int(stats.get("queued", 0)) + int(stats.get("retry", 0)) + int(stats.get("running", 0)) == 0,
        "terminal_count": int(stats.get("succeeded", 0)) + int(stats.get("blocked", 0)) + int(stats.get("failed", 0)) == JOBS,
        "four_external_workers": int(stats.get("worker_count", 0)) >= 4,
        "provider_calls": int(stats.get("provider_ok_events", 0)) >= 4 and int(stats.get("provider_error_events", 0)) == 0,
        "429_retry": int(stats.get("inject_429_events", 0)) >= 1,
        "503_retry": int(stats.get("inject_503_events", 0)) >= 1,
        "network_fault": int(stats.get("inject_network_events", 0)) >= 1,
        "stale_write_fenced": int(stats.get("stale_write_rejected_events", 0)) >= 1,
        "worker_loss_recovered": int(stats.get("crash_claim_events", 0)) >= 1 and int(stats.get("attempt_gt_1", 0)) >= 4,
        "budget_exhaustion": int(stats.get("budget_allowed_events", 0)) >= 1 and int(stats.get("budget_denied_events", 0)) >= 1,
        "rate_limit": int(stats.get("rate_allowed_events", 0)) >= 1 and int(stats.get("rate_denied_events", 0)) >= 1,
        "lease_uniqueness": int(stats.get("unique_lease_hashes", 0)) >= JOBS,
    }
    passed = all(checks.values())
    status = "passed" if passed else "failed"
    real_calls = int(stats.get("provider_ok_events", 0))
    notes = "R12.6.3 accelerated external GitHub-hosted Python fleet burn-in. This is not a 24-hour wall-clock certification."
    call("complete", status=status, observed_duration_seconds=DURATION,
         real_provider_calls=real_calls, metrics={"stats": stats, "checks": checks}, notes=notes)
    cleanup = call("cleanup").get("data")
    print(json.dumps({"mode": "verify", "run_key": RUN_KEY, "status": status,
                      "checks": checks, "stats": stats, "cleanup": cleanup}, sort_keys=True))
    if not passed:
        sys.exit(2)

if __name__ == "__main__":
    if MODE == "seed":
        seed()
    elif MODE == "worker":
        worker()
    elif MODE == "verify":
        verify()
    else:
        raise SystemExit("unknown MODE")
