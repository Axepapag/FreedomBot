import os
import json
from datetime import datetime
from typing import Optional

LOG_DIR = "logs"
TEXT_LOG_FILE = os.path.join(LOG_DIR, "events.log")
JSON_LOG_FILE = os.path.join(LOG_DIR, "events.jsonl")

def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)

def log_event(message: str, level: str = "INFO", session: Optional[str] = None):
    _ensure_log_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = f"[{timestamp}] [{level}]"

    if session:
        prefix += f" [Session:{session}]"

    # Write plain text log
    with open(TEXT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{prefix} {message}\n")

    # Write structured JSON log
    json_entry = {
        "timestamp": timestamp,
        "level": level,
        "session": session,
        "message": message
    }

    with open(JSON_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(json_entry) + "\n")

def log_patch_applied(patch: str, target: str, status: str = "APPLIED", session: Optional[str] = None):
    msg = f"Patch {status} to {target}"
    log_event(msg, level="PATCH", session=session)

def log_memory_action(action: str, summary: str = "", session: Optional[str] = None):
    msg = f"Memory {action} - {summary}"
    log_event(msg, level="MEMORY", session=session)

def log_security_warning(issue: str, session: Optional[str] = None):
    log_event(issue, level="SECURITY", session=session)

def log_error(error: str, session: Optional[str] = None):
    log_event(error, level="ERROR", session=session)
