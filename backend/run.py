import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

# CRITICAL: Set policy BEFORE importing anything that works with asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Starting Server with WindowsProactorEventLoopPolicy...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
