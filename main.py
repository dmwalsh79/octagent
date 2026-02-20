import asyncio
import os
import glob
import yaml
from core.orchestrator import OrchestratorBrain

async def main():
    print("🐙 Booting OctAgent Boardroom...")
    
    # Dynamically load all personas from the YAML directory
    # This implements the "Swappable Personas" architecture natively.
    persona_files = glob.glob("personas/*.yaml")
    if not persona_files:
        print("ERROR: No YAML files found in the 'personas/' directory.")
        return

    arm_configs = {}
    for file_path in persona_files:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
            # Use the defined name or fallback to the filename
            name = config.get('name', os.path.basename(file_path).split('.')[0])
            arm_configs[name] = config

    print(f"✅ Loaded {len(arm_configs)} Arms into the Consensus Engine.")
    
    # Initialize the Orchestrator (from your v0.3 code)
    brain = OrchestratorBrain(arm_configs)
    
    # Interactive CLI Loop
    while True:
        try:
            print("\n" + "="*50)
            user_task = input("Enter a task for the boardroom (or 'exit' to quit):\n> ")
            if user_task.lower() in ['exit', 'quit']:
                break
                
            # Execute the fan-out boardroom vote
            await brain.process_high_stakes_action(user_task)
            
        except KeyboardInterrupt:
            print("\nShutting down OctAgent...")
            break

if __name__ == "__main__":
    # Ensure standard asyncio event loop behavior across OS platforms
    asyncio.run(main())