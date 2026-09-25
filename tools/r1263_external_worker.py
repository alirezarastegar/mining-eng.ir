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
_session_token=""
_session_expires_at=0.0

def _mint_oidc():
    base=os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]; sep="&" if "?" in base else "?"
    req=urllib.request.Request(base+sep+"audience="+urllib.parse.quote(AUDIENCE,safe=""),headers={"Authorization":"Bearer "+os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]})
    with urllib.request.urlopen(req,timeout=20) as r:return json.loads(r.read().decode())["value"]

def _post(payload,headers):
    raw=json.dumps(payload,separators=(",",":")).encode()
    req=urllib.request.Request(BROKER,data=raw,headers={"Content-Type":"application/json",**headers},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=45) as r:return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body=e.read().decode(errors="replace")
        raise RuntimeError(f"broker_http_{e.code}:{body[:500]}")

def start_session(force=False):
    global _session_token,_session_expires_at
    if MODE=="seed": return
    if not force and _session_token and time.time()<_session_expires_at-120: return
    out=_post({"action":"session_start","run_key":RUN_KEY,"worker_id":WORKER_ID},{"Authorization":"Bearer "+_mint_oidc()})
    if not out.get("ok") or not out.get("session_token"):
        raise RuntimeError("session_start_failed:"+json.dumps(out,sort_keys=True)[:800])
    _session_token=str(out["session_token"])
    _session_expires_at=time.time()+5.25*3600

def call(action,**kwargs):
    payload={"action":action,"run_key":RUN_KEY,"worker_id":WORKER_ID,**kwargs}
    if action=="seed":
        out=_post(payload,{"Authorization":"Bearer "+_mint_oidc()})
    else:
        start_session()
        try: out=_post(payload,{"x-mra-worker-session":_session_token})
        except RuntimeError as exc:
            if "broker_http_401:" not in str(exc): raise
            start_session(force=True)
            out=_post(payload,{"x-mra-worker-session":_session_token})
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
