"""Mira production worker: Render chat -> Tavus adapter package."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parent
CONFIG_PATH=ROOT/"production_config.json"
DEFAULT_OUTPUT=Path("/workspace/influencer_media/output")
FALLBACK_OUTPUT=Path("/mnt/data/apex_workspace/influencer_media/output")
def load_config()->dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
def output_dir()->Path:
    target=DEFAULT_OUTPUT if DEFAULT_OUTPUT.parent.exists() else FALLBACK_OUTPUT
    target.mkdir(parents=True,exist_ok=True)
    return target
def render_chat(user_message:str,session_id:str)->dict:
    cfg=load_config()
    endpoint=cfg["primary_endpoint_wrapper"].rstrip("/")+cfg.get("chat_path","/stream/chat")
    request={"user_message":user_message,"session_id":session_id}
    with httpx.Client(timeout=30.0,follow_redirects=True) as client:
        response=client.post(endpoint,json=request)
        response.raise_for_status()
        chat=response.json()
    return {"provider":cfg["provider"],"replica_id":cfg["replica_id"],"persona_id":cfg.get("persona_id"),"session_id":session_id,"transport":chat.get("transport","webrtc"),"event":chat.get("event","avatar.speak"),"text":chat.get("text",""),"render_endpoint":endpoint}
def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("message",nargs="?",default="I almost kept this place to myself.")
    p.add_argument("--session-id",default="mira-production")
    a=p.parse_args()
    payload=render_chat(a.message,a.session_id)
    out=output_dir()/"latest_tavus_adapter_payload.json"
    out.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(payload,indent=2,ensure_ascii=False))
    print(f"Adapter payload saved: {out}")
if __name__=="__main__":
    main()
