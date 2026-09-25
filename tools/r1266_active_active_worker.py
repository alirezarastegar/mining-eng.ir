#!/usr/bin/env python3
"""R12.6.6 GitHub-hosted Python process fleet for active-active soak.
The runner's geographic placement is not claimed. Every broker request is pinned to the
requested Supabase Edge region and the broker rejects SB_REGION mismatches.
"""
import json, os, random, sys, time, urllib.error, urllib.parse, urllib.request
AUD="mra-r1266-active-active-fleet"
BASE="https://tinsqtvdnzzslgohtiyg.supabase.co/functions/v1/mra-r1266-fleet-broker"
RUN_KEY=f"gh-{os.environ['GITHUB_RUN_ID']}-{os.environ.get('GITHUB_RUN_ATTEMPT','1')}"
MODE=os.environ.get("MODE","worker"); WORKER_ID=os.environ.get("WORKER_ID","verify"); REGION=os.environ.get("WORKER_REGION","eu-central-1"); TASKS=int(os.environ.get("SOAK_TASKS","240")); SESSION=""
def get_oidc():
    base=os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]; sep="&" if "?" in base else "?"; url=base+sep+"audience="+urllib.parse.quote(AUD,safe="")
    req=urllib.request.Request(url,headers={"Authorization":"Bearer "+os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]})
    with urllib.request.urlopen(req,timeout=20) as r:return json.loads(r.read().decode())["value"]
def call(action,oidc=False,**kw):
    url=BASE+"?forceFunctionRegion="+urllib.parse.quote(REGION,safe="")
    payload={"action":action,"run_key":RUN_KEY,"worker_id":WORKER_ID,"region":REGION,**kw}; headers={"Content-Type":"application/json"}
    if oidc: headers["Authorization"]="Bearer "+get_oidc()
    elif SESSION: headers["x-mra-worker-session"]=SESSION
    req=urllib.request.Request(url,data=json.dumps(payload,separators=(",",":")).encode(),headers=headers,method="POST")
    try:
        with urllib.request.urlopen(req,timeout=30) as r: out=json.loads(r.read().decode())
    except urllib.error.HTTPError as e: raise RuntimeError(f"broker_http_{e.code}:{e.read().decode(errors='replace')[:600]}")
    if not out.get("ok"): raise RuntimeError("broker_error:"+json.dumps(out,sort_keys=True)[:900])
    if out.get("observed_edge_region") and out["observed_edge_region"]!=REGION: raise RuntimeError("edge_region_mismatch")
    return out
def start_session():
    global SESSION
    out=call("session_start",oidc=True); SESSION=str(out["session_token"]); return out
def setup():
    out=call("seed",oidc=True,tasks=TASKS); print(json.dumps({"mode":"setup","run_key":RUN_KEY,"result":out},sort_keys=True))
def worker():
    start_session(); handled=0; deadline=time.time()+300
    while time.time()<deadline:
        call("heartbeat")
        out=call("claim"); task=out.get("task")
        if not task:
            st=call("stats").get("stats") or {}
            if int(st.get("queued",0))+int(st.get("running",0))==0: break
            time.sleep(.25); continue
        time.sleep(random.uniform(.18,.38))
        if not call("complete",task_id=task["task_id"]).get("accepted"): raise RuntimeError("task_complete_rejected")
        handled+=1
    call("worker_state",state="drain"); time.sleep(.15); call("worker_state",state="stop")
    print(json.dumps({"mode":"worker","worker":WORKER_ID,"region":REGION,"handled":handled,"python_host_placement_verified":False},sort_keys=True))
def chaos():
    start_session(); time.sleep(5); call("fault",open=True); time.sleep(8); call("fault",open=False); call("worker_state",state="stop"); print(json.dumps({"mode":"chaos","run_key":RUN_KEY},sort_keys=True))
def verify():
    start_session(); end=time.time()+75; stats={}
    while time.time()<end:
        stats=call("stats").get("stats") or {}
        if int(stats.get("queued",0))+int(stats.get("running",0))==0 and int(stats.get("stopped_workers",0))>=4: break
        time.sleep(1)
    out=call("finalize").get("result") or {}; print(json.dumps({"mode":"verify","result":out},sort_keys=True))
    if out.get("software_gates")!="pass": sys.exit(2)
if __name__=="__main__":
    {"setup":setup,"worker":worker,"chaos":chaos,"verify":verify}[MODE]()
