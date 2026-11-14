"""
Single command runner for Tone Checker (VibeCheck):
Launches:
  1. Backend (FastAPI / Uvicorn) on http://localhost:8000
  2. Frontend (React / Vite) on http://localhost:5173
Handles graceful shutdown on Ctrl+C.
"""

import os
import sys
import time
import subprocess
import signal

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

def run_app():
    print("=" * 60)
    print("  Tone Checker (VibeCheck) — Full-Stack Runner")
    print("=" * 60)
    print("Starting Backend on http://localhost:8000 ...")
    
    # Start Backend
    backend_env = os.environ.copy()
    backend_env["PYTHONPATH"] = ROOT_DIR
    backend_cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000"
    ]
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=ROOT_DIR,
        env=backend_env
    )

    # Wait a moment for backend startup
    time.sleep(2)

    print("Starting Frontend on http://localhost:5173 ...")
    # Start Frontend (npm run dev)
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=FRONTEND_DIR
    )

    print("-" * 60)
    print("  Both services are running!")
    print("  - Backend API: http://localhost:8000 (Docs at /docs)")
    print("  - Frontend UI: http://localhost:5173")
    print("  Press Ctrl+C to terminate both services.")
    print("-" * 60)

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("Backend exited unexpectedly!")
                break
            if frontend_proc.poll() is not None:
                print("Frontend exited unexpectedly!")
                break
    except KeyboardInterrupt:
        print("\nReceived stop signal. Shutting down services...")
    finally:
        for proc in [backend_proc, frontend_proc]:
            try:
                if proc.poll() is None:
                    if sys.platform == "win32":
                        subprocess.call(["taskkill", "/F", "/T", "/PID", str(proc.pid)])
                    else:
                        proc.terminate()
            except Exception:
                pass
        print("Tone Checker successfully stopped.")

if __name__ == "__main__":
    run_app()

