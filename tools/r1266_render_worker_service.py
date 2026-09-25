#!/usr/bin/env python3
"""R12.6.6 Render-hosted physical Python worker.
No Supabase service-role key is stored on the host. Bootstrap uses a one-time
enrollment token, then a short-lived broker session token.
"""
from __future__ import annotations
import json, os, threading, time, urllib.error, urllib.parse, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

RELEASE="R12.6.6"
BASE="https://tinsqtvdnzzslgohtiyg.supabase.co/functions/v1/mra-r1266-fleet-broker"
WORKER_ID=os.environ.get("WORKER_ID","r1266-render-unknown")
REGION=os.environ.get("LOGICAL_REGION","eu-central-1")
PROVIDER_REGION=os.environ.get("PROVIDER_REGION","")
RUN_KEY=os.environ.get("RUN_KEY","")
PURPOSE=os.environ.get("PURPOSE","soak")
ENROLL=os.environ.get("R1266_ENROLL_TOKEN","")
HOST_REF=os.environ.get("HOST_REF") or os.environ.get("RENDER_SERVICE_ID") or WORKER_ID
PORT=int(os.environ.get("PORT","10000"))

state={"release":RELEASE,"worker_id":WORKER_ID,"logical_region":REGION,
       "provider_region":PROVIDER_REGION,"run_key":RUN_KEY,"ready":False,
       "session":False,"handled":0,"last_error":"","stopped":False}
SESSION=""

def request(action:str, *, enroll=False, **extra):
    global SESSION
    url=BASE+"?forceFunctionRegion="+urllib.parse.quote(REGION,safe="")
    body={"action":action,"run_key":RUN_KEY,"worker_id":WORKER_ID,"region":REGION,**extra}
    headers={"Content-Type":"application/json"}
    if enroll:
        headers["x-r1266-enroll-token"]=ENROLL
    else:
        headers["x-mra-worker-session"]=SESSION
    req=urllib.request.Request(url,data=json.dumps(body,separators=(",",":")).encode(),headers=headers,method="POST")
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            out=json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"broker_http_{e.code}:{e.read().decode(errors='replace')[:500]}")
    if not out.get("ok"):
        raise RuntimeError("broker_error:"+json.dumps(out,sort_keys=True)[:700])
    if out.get("observed_edge_region") and out["observed_edge_region"]!=REGION:
        raise RuntimeError("edge_region_mismatch")
    return out

def worker_loop():
    global SESSION
    if not (ENROLL and RUN_KEY and PROVIDER_REGION and REGION in ("eu-central-1","eu-west-1")):
        state["last_error"]="waiting_for_enrollment_env"
        return
    try:
        out=request("external_session_start",enroll=True,provider="render",provider_region=PROVIDER_REGION,
                    host_ref=HOST_REF,purpose=PURPOSE)
        SESSION=str(out["session_token"])
        state["session"]=True
        state["ready"]=True
        idle=0
        while True:
            hb=request("heartbeat")
            cmd=((hb.get("data") or {}).get("command") or "active")
            if cmd in ("drain","stop"):
                request("worker_state",state="stop" if cmd=="stop" else "drain")
                state["stopped"]=True
                return
            got=request("claim")
            task=got.get("task")
            if not task:
                idle+=1
                if idle>=20:
                    request("worker_state",state="drain")
                    time.sleep(.2)
                    request("worker_state",state="stop")
                    state["stopped"]=True
                    return
                time.sleep(.5)
                continue
            idle=0
            time.sleep(.2)
            if not request("complete",task_id=task["task_id"]).get("accepted"):
                raise RuntimeError("task_complete_rejected")
            state["handled"]+=1
    except Exception as e:
        state["last_error"]=str(e)[:500]
        state["ready"]=False

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        code=200 if self.path in ("/","/health","/healthz") else 404
        payload=dict(state)
        payload["healthy"]=code==200 and not bool(state["last_error"] and state["last_error"]!="waiting_for_enrollment_env")
        raw=json.dumps(payload,sort_keys=True).encode()
        self.send_response(code);self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(raw)));self.end_headers();self.wfile.write(raw)
    def log_message(self,*_): pass

if __name__=="__main__":
    threading.Thread(target=worker_loop,daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0",PORT),Handler).serve_forever()
