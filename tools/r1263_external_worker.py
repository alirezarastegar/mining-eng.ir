#!/usr/bin/env python3
import json, os, random, sys, time, urllib.error, urllib.parse, urllib.request

BROKER=os.environ.get("MRA_R1263_BROKER_URL","https://tinsqtvdnzzslgohtiyg.supabase.co/functions/v1/mra-r1263-worker-broker")
AUDIENCE="mra-r1263-external-worker"
RUN_KEY=f"gh-{os.environ['GITHUB_RUN_ID']}-{os.environ.get('GITHUB_RUN_ATTEMPT','1')}"
MODE=os.environ.get("MODE","worker")
WORKER_ID=os.environ.get("WORKER_ID","verify")
DURATION=int(os.environ.get("BURNIN_SECONDS","17400"))
JOBS=int(os.environ.get("BURNIN_JOBS","450"))
JOB_INTERVAL=max(30,int(os.environ.get("JOB_INTERVAL_SECONDS","696")))
IDLE_INTERVAL=max(10,int(os.environ.get("IDLE_INTERVAL_SECONDS","30")))
TARGET_SECONDS=int(os.environ.get("TARGET_SECONDS","86400"))
OIDC_MAX_AGE_SECONDS=240
_oidc_token=""
_oidc_minted_at=0.0

def _mint_oidc():
    base=os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]; sep="&" if "?" in base else "?"
    req=urllib.request.Request(base+sep+"audience="+urllib.parse.quote(AUDIENCE,safe=""),headers={"Authorization":"Bearer "+os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]})
    with urllib.request.urlopen(req,timeout=20) as r:return json.loads(r.read().decode())["value"]

def get_oidc(force=False):
    global _oidc_token,_oidc_minted_at
    now=time.monotonic()
    if force or not _oidc_token or now-_oidc_minted_at>=OIDC_MAX_AGE_SECONDS:
        _oidc_token=_mint_oidc();_oidc_minted_at=now
    return _oidc_token

def call(action,**kwargs):
    raw=json.dumps({"action":action,"run_key":RUN_KEY,"worker_id":WORKER_ID,**kwargs},separators=(",",":")).encode()
    for auth_attempt in range(2):
        req=urllib.request.Request(BROKER,data=raw,headers={"Authorization":"Bearer "+get_oidc(force=auth_attempt>0),"Content-Type":"application/json"},method="POST")
        try:
            with urllib.request.urlopen(req,timeout=45) as r:out=json.loads(r.read().decode())
            break
        except urllib.error.HTTPError as e:
            body=e.read().decode(errors="replace")
            if e.code==401 and auth_attempt==0:continue
            raise RuntimeError(f"broker_http_{e.code}:{body[:500]}")
    else:raise RuntimeError("broker_auth_retry_exhausted")
    if not out.get("ok"):raise RuntimeError("broker_error:"+json.dumps(out,sort_keys=True)[:800])
    return out

def suffix(job):
    try:return int(str(job["idempotency_key"]).rsplit(":",1)[1])
    except Exception:return -1

def seed():
    out=call("seed",jobs=JOBS)
    print(json.dumps({"mode":"seed","run_key":RUN_KEY,"result":out.get("data")},sort_keys=True))

def worker():
    deadline=time.time()+DURATION;handled=0;provider_calls=0;idle_claims=0
    while time.time()<deadline:
        out=call("claim");job=out.get("job")
        if not job:
            idle_claims+=1;time.sleep(IDLE_INTERVAL);continue
        handled+=1;idx=suffix(job);jid=str(job["job_id"]);token=str(job["lease_token"])
        if idx>0 and idx%100 in (7,8,9,10):
            p=call("provider_probe",job_id=jid,lease_token=token)
            if not p.get("ok"):
                time.sleep(min(JOB_INTERVAL,60));continue
            provider_calls+=1
        hb=call("heartbeat",job_id=jid,lease_token=token)
        if not hb.get("accepted"):
            time.sleep(min(JOB_INTERVAL,60));continue
        time.sleep(random.uniform(0.04,0.14))
        fin=call("finalize",job_id=jid,lease_token=token,terminal_status="succeeded",reason="wall_clock_burnin")
        if not fin.get("accepted"):
            call("event",event_kind="wallclock_stale_finalize",job_id=jid,lease_token=token,details={"wave_worker":WORKER_ID})
        remaining=deadline-time.time()
        if remaining>0:time.sleep(min(JOB_INTERVAL,remaining))
    call("event",event_kind="wallclock_worker_done",details={"handled":handled,"provider_calls":provider_calls,"idle_claims":idle_claims,"duration_seconds":DURATION})
    print(json.dumps({"mode":"worker","worker":WORKER_ID,"handled":handled,"provider_calls":provider_calls,"idle_claims":idle_claims,"duration_seconds":DURATION},sort_keys=True))

def verify():
    end=time.time()+180;stats={}
    while time.time()<end:
        stats=call("stats").get("stats") or {}
        active=int(stats.get("queued",0))+int(stats.get("retry",0))+int(stats.get("running",0))
        if active==0:break
        time.sleep(5)
    elapsed=int(stats.get("elapsed_seconds",0))
    checks={
      "wall_clock_24h":elapsed>=TARGET_SECONDS,
      "target_declared":int(stats.get("target_duration_seconds",0))>=TARGET_SECONDS,
      "total_jobs":int(stats.get("total_jobs",0))==JOBS,
      "queue_drained":int(stats.get("queued",0))+int(stats.get("retry",0))+int(stats.get("running",0))==0,
      "terminal_count":int(stats.get("succeeded",0))+int(stats.get("blocked",0))+int(stats.get("failed",0))==JOBS,
      "four_external_workers":int(stats.get("worker_count",0))>=4,
      "provider_calls_spread":int(stats.get("provider_ok_events",0))>=16,
      "provider_errors_zero":int(stats.get("provider_error_events",0))==0,
      "lease_uniqueness":int(stats.get("unique_lease_hashes",0))>=JOBS,
      "no_wallclock_stale_finalize":int(stats.get("wallclock_stale_finalize_events",0))==0,
    }
    passed=all(checks.values());status="passed" if passed else "failed";real_calls=int(stats.get("provider_ok_events",0))
    cleanup=call("cleanup").get("data")
    call("complete",status=status,observed_duration_seconds=elapsed,real_provider_calls=real_calls,metrics={"profile":"24h-wall-clock","stats":stats,"checks":checks,"cleanup":cleanup},notes="R12.6.3 real wall-clock external GitHub-hosted Python fleet burn-in; PASS requires elapsed_seconds >= 86400.")
    print(json.dumps({"mode":"verify","run_key":RUN_KEY,"status":status,"elapsed_seconds":elapsed,"checks":checks,"stats":stats,"cleanup":cleanup},sort_keys=True))
    if not passed:sys.exit(2)

if __name__=="__main__":
    if MODE=="seed":seed()
    elif MODE=="worker":worker()
    elif MODE=="verify":verify()
    else:raise SystemExit("unknown MODE")
