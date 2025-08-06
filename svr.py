import os
import subprocess
import time
import sys
from threading import Thread

API_HOST = "0.0.0.0"
API_PORT = "8080"
WEBUI_PORT = 3000
WEBUI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_ui")
LOG_PATH = os.path.join("logs", "server.log")

os.makedirs("logs", exist_ok=True)

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")

def run_api_server():
    while True:
        log("Launching Dexter API server...")
        try:
            proc = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "api:app", "--host", API_HOST, "--port", str(API_PORT)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            for line in proc.stdout:
                log(line.strip())
            proc.wait()
        except Exception as e:
            log(f"API server crashed with error: {e}")
        log("API server exited. Restarting in 3 seconds...")
        time.sleep(3)

def run_web_server():
    if not os.path.exists(WEBUI_DIR):
        log(f"ERROR: Web UI directory not found: {WEBUI_DIR}")
        return
    log(f"Launching Web UI at http://localhost:{WEBUI_PORT}")
    try:
        subprocess.run([sys.executable, "-m", "http.server", str(WEBUI_PORT)], cwd=WEBUI_DIR)
    except Exception as e:
        log(f"Web server crashed: {e}")

if __name__ == "__main__":
    log("=== Dexter Server Startup ===")
    api_thread = Thread(target=run_api_server, daemon=True)
    web_thread = Thread(target=run_web_server, daemon=True)
    api_thread.start()
    web_thread.start()

    log(f"API   → http://localhost:{API_PORT}")
    log(f"WebUI → http://localhost:{WEBUI_PORT}")
    log("Press Ctrl+C to stop both servers.")

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        log("Shutting down servers...")
        sys.exit(0)
