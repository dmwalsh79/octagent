# 🐙 OctAgent

> **"Eight Arms. One Mind. Zero Sleep."**

Most agents are a single persona acting as a junior developer. OctAgent is a committee. It spawns 8 concurrent sub-agents—each with an isolated cognitive persona, persistent memory shard, and area of ownership. They execute tasks, argue with each other, surface conflicts, and vote on high-stakes decisions. 

Yes, this is intentional.

## ⚙️ Architecture

Instead of a standard iterative loop, OctAgent uses an **Asynchronous Fanout-and-Aggregate** pattern:
1. **Fanout:** A task is broadcast to 8 isolated LLM sessions concurrently via `asyncio.TaskGroup`.
2. **Cognition:** Each arm evaluates the task strictly through its YAML-defined persona.
3. **Aggregation:** A `ConsensusLayer` calculates a quorum (default 5/8).
4. **Veto:** The Bouncer arm possesses strict veto power to halt execution on unsafe commands.

## 🚀 Getting Started

Requires **Python 3.11+** (for `asyncio.TaskGroup`).

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your LLM API keys.
4. Run a test quorum: `python -m core.orchestrator`

## 🧠 The Boardroom (Default Arms)

| Arm | Persona | Domain | Veto Power |
| :--- | :--- | :--- | :--- |
| 🔴 **Critic** | Devil's Advocate | Code Review | No |
| 🟢 **Builder** | Ship-it Energy | File Ops | No |
| 🔵 **Archivist** | Memory Keeper | Documentation | No |
| 🟡 **Scout** | Web Forager | Research | No |
| 🟣 **Diplomat** | Comms Drafter | Messaging | No |
| 🟠 **Accountant** | Optimizer | Budgets/Cost | No |
| ⚪ **Dreamer** | Idea Generator | Brainstorming | No |
| ⚫ **Bouncer** | Guardrail | Security | **Yes** |
