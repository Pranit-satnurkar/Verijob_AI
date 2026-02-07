from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="VeriJob AI Backend")

# Fix for Windows asyncio loop issues with Playwright
import sys
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    Ensure browsers are installed for Playwright on startup.
    This fixes the 'Executable doesn't exist' error on Render.
    """
    import os
    import subprocess
    print("🚀 Checking Playwright Browsers...")
    try:
        # Check if we can run verify installation or just install
        # This command is safe to run multiple times (it verifies)
        subprocess.run(["playwright", "install", "chromium"], check=True)
        print("✅ Playwright Browsers Installed.")
    except Exception as e:
        print(f"⚠️ Failed to auto-install browsers: {e}")

from typing import Optional

class VerifyRequest(BaseModel):
    url: str
    content: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "VeriJob AI Verification Engine is Running!"}

from verifier import verify_job_listing


from tools import search_hiring_signals

@app.get("/feed")
def get_feed():
    """
    Returns a list of 'Green Flags' (Hiring Signals).
    """
    try:
        signals = search_hiring_signals()
        return signals
    except Exception as e:
        print(f"Feed error: {e}")
        return []

@app.post("/verify")
async def verify_job(request: VerifyRequest):
    try:
        result = await verify_job_listing(request.url, request.content)
        return result
    except Exception as e:
        import traceback
        return {
            "status": "Error",
            "score": 0,
            "details": f"Internal Error: {str(e)}",
            "traceback": traceback.format_exc()
        }

