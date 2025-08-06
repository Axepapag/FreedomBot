import os
import sys
import threading
import time
import traceback
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dexter_brain import DexterBrain

API_KEY = os.environ.get("DEXTER_API_KEY", "gliksbot")
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def check_api_key(request: Request):
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key.")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dexter Core ---
dexter = DexterBrain()

# --- Models ---
class ChatRequest(BaseModel):
    user_input: str

class SkillEdit(BaseModel):
    name: str
    code: str

class SkillRollback(BaseModel):
    name: str

# --- Endpoints ---

@app.post("/chat")
async def chat(chat_in: ChatInput, request: Request):
    check_api_key(request)
    print(f"[Chat] USER INPUT: {chat_in.user_input}")
    result = dexter.handle_input(chat_in.user_input)
    print(f"[Chat] DEXTER OUTPUT: {result}")
    return result

@app.get("/memory")
async def get_memory(request: Request):
    check_api_key(request)
    try:
        return {"memory": dexter.memory.mem}
    except Exception as e:
        return {"error": f"Memory error: {str(e)}", "trace": traceback.format_exc()}

@app.get("/logs")
async def get_logs(request: Request):
    check_api_key(request)
    try:
        with open(os.path.join(PROJECT_DIR, "data", "log.txt"), "r", encoding="utf-8") as f:
            return {"logs": f.read()}
    except Exception as e:
        return {"error": f"Logs error: {str(e)}", "trace": traceback.format_exc()}

@app.get("/sandbox/log")
async def get_sandbox_log(request: Request):
    check_api_key(request)
    try:
        sandbox_log_path = os.path.join(PROJECT_DIR, "sandbox", "sandbox.log")
        if not os.path.exists(sandbox_log_path):
            return {"log": ""}
        with open(sandbox_log_path, "r", encoding="utf-8") as f:
            return {"log": f.read()}
    except Exception as e:
        return {"log": f"Error: {e}", "trace": traceback.format_exc()}

@app.get("/skills")
async def get_skills(request: Request):
    check_api_key(request)
    try:
        skills = dexter.list_skills()
        return {"skills": skills}
    except Exception as e:
        return {"error": f"Skills error: {str(e)}", "trace": traceback.format_exc()}

@app.post("/skills/promote")
async def promote_skill(req: SkillEdit, request: Request):
    check_api_key(request)
    try:
        name = req.name
        code = req.code
        skills_dir = os.path.join(PROJECT_DIR, "skills")
        if not os.path.exists(skills_dir):
            os.makedirs(skills_dir)
        skill_path = os.path.join(skills_dir, f"{name}.py")
        # Backup old
        if os.path.exists(skill_path):
            os.rename(skill_path, skill_path + ".bak")
        with open(skill_path, "w", encoding="utf-8") as f:
            f.write(code)

        # Auto-restart server after patch
        def restart_server():
            time.sleep(1)
            print("Restarting server after skill patch...")
            os._exit(99)
        threading.Thread(target=restart_server, daemon=True).start()

        return {"success": True, "msg": f"Skill {name} promoted. Restarting server..."}
    except Exception as e:
        return {"error": f"Promote skill error: {str(e)}", "trace": traceback.format_exc()}

@app.post("/skills/rollback")
async def rollback_skill(req: SkillRollback, request: Request):
    check_api_key(request)
    try:
        name = req.name
        skills_dir = os.path.join(PROJECT_DIR, "skills")
        skill_path = os.path.join(skills_dir, f"{name}.py")
        backup_path = skill_path + ".bak"
        if not os.path.exists(backup_path):
            return {"success": False, "error": "No backup found to rollback."}
        os.replace(backup_path, skill_path)
        return {"success": True, "msg": f"Skill {name} rolled back."}
    except Exception as e:
        return {"error": f"Rollback skill error: {str(e)}", "trace": traceback.format_exc()}

@app.get("/health")
async def health(request: Request):
    check_api_key(request)
    return {"status": "ok"}

@app.get("/knowledge")
async def get_knowledge(request: Request):
    check_api_key(request)
    try:
        return {"knowledge": dexter.knowledge.graph}
    except Exception as e:
        return {"error": f"Knowledge error: {str(e)}", "trace": traceback.format_exc()}

@app.get("/")
def home():
    return {"status": "Dexter API running!", "endpoints": [
        "/chat", "/memory", "/logs", "/sandbox/log", "/skills", "/skills/promote", "/skills/rollback", "/health", "/knowledge"
    ]}