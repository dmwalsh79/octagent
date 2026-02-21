import asyncio
import os
import glob
import yaml
from pathlib import Path
from dotenv import load_dotenv
import litellm
from core.orchestrator import OrchestratorBrain
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

# Load environment variables (API keys) from .env
load_dotenv("api.env")

app = FastAPI(title="OctAgent Boardroom")
brain = None
BASE_DIR = Path(__file__).resolve().parent
PERSONAS_DIR = BASE_DIR / "personas"
TEMPLATES_DIR = BASE_DIR / "templates"

class TaskRequest(BaseModel):
    task: str

@app.on_event("startup")
async def startup_event():
    global brain
    print("🐙 Booting OctAgent Boardroom...")
    
    # Ensure personas directory exists
    PERSONAS_DIR.mkdir(parents=True, exist_ok=True)
    persona_files = glob.glob(str(PERSONAS_DIR / "*.yaml"))
    
    if not persona_files:
        print("⚠️  No personas found. Generating default 'Genesis' persona...")
        with open(PERSONAS_DIR / "genesis.yaml", "w") as f:
            yaml.dump({
                "name": "Genesis",
                "persona": "You are the first agent. You are helpful and concise.",
                "owns": "Bootstrapping",
                "can_veto": False,
                "model": "gpt-4o-mini"
            }, f)
        persona_files = glob.glob(str(PERSONAS_DIR / "*.yaml"))

    arm_configs = {}
    for file_path in persona_files:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
            # Use the defined name or fallback to the filename
            name = config.get('name', os.path.basename(file_path).split('.')[0])
            arm_configs[name] = config

    print(f"✅ Loaded {len(arm_configs)} Arms into the Consensus Engine.")
    brain = OrchestratorBrain(arm_configs)

@app.get("/")
async def read_index():
    landing_page = TEMPLATES_DIR / "login.html"
    if not landing_page.exists():
        return "ERROR: templates/login.html not found."
    return FileResponse(landing_page)

@app.post("/api/process")
async def process_task(request: TaskRequest):
    if not brain:
        return {"status": "ERROR", "reason": "Brain not initialized"}
    
    # Execute the fan-out boardroom vote and return the result JSON
    result = await brain.process_high_stakes_action(request.task)
    return result

if __name__ == "__main__":
    # Run the web server
    uvicorn.run(app, host="0.0.0.0", port=8000)
