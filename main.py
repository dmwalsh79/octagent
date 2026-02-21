import asyncio
import glob
import os
from pathlib import Path

import yaml
from aiohttp import web

from core.orchestrator import OrchestratorBrain


def load_arm_configs() -> dict:
    persona_files = glob.glob("personas/*.yaml")
    if not persona_files:
        raise RuntimeError("No YAML files found in the 'personas/' directory.")

    arm_configs = {}
    for file_path in persona_files:
        with open(file_path, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle) or {}
            name = config.get("name", os.path.basename(file_path).split(".")[0])
            arm_configs[name] = config

    return arm_configs


async def index(request: web.Request) -> web.Response:
    html_path = Path(__file__).parent / "web" / "index.html"
    return web.FileResponse(html_path)


async def process_prompt(request: web.Request) -> web.Response:
    brain: OrchestratorBrain = request.app["brain"]

    payload = await request.json()
    task = (payload.get("prompt") or "").strip()
    if not task:
        return web.json_response({"error": "Prompt is required."}, status=400)

    result = await brain.process_high_stakes_action(task)
    return web.json_response(result)


async def build_app() -> web.Application:
    app = web.Application()
    app["brain"] = OrchestratorBrain(load_arm_configs())
    app.router.add_get("/", index)
    app.router.add_post("/api/prompt", process_prompt)
    return app


if __name__ == "__main__":
    print("🐙 Booting OctAgent Boardroom Web UI at http://localhost:8080")
    web.run_app(asyncio.run(build_app()), host="0.0.0.0", port=8080)
