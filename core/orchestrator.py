import asyncio
from typing import Any, Dict, List

from core.consensus import ArmDecision, ConsensusLayer


class OrchestratorBrain:
    """Coordinates persona arm decisions and resolves final consensus."""

    def __init__(self, arm_configs: Dict[str, Dict[str, Any]]):
        self.arm_configs = arm_configs
        self.consensus = ConsensusLayer()

    async def _evaluate_arm(self, arm_name: str, config: Dict[str, Any], task: str) -> ArmDecision:
        lowered = task.lower()
        risky_keywords = ["delete", "drop", "rm -rf", "shutdown", "destroy", "format"]
        unsafe = any(keyword in lowered for keyword in risky_keywords)

        if arm_name.lower() == "bouncer" and unsafe:
            return ArmDecision(
                arm_name=arm_name,
                vote=False,
                reasoning="Potentially destructive intent detected; veto engaged.",
                is_veto=True,
                cost=0.0,
            )

        cautious_keywords = ["production", "database", "migration", "security"]
        caution = any(keyword in lowered for keyword in cautious_keywords)

        if arm_name.lower() == "critic" and caution:
            return ArmDecision(
                arm_name=arm_name,
                vote=False,
                reasoning="Risk is high; request a safer rollout plan before approval.",
                cost=0.0,
            )

        role = config.get("role", "general")
        return ArmDecision(
            arm_name=arm_name,
            vote=True,
            reasoning=f"{arm_name} ({role}) supports this action with standard safeguards.",
            cost=0.0,
        )

    async def process_high_stakes_action(self, task: str) -> Dict[str, Any]:
        jobs: List[asyncio.Task[ArmDecision]] = [
            asyncio.create_task(self._evaluate_arm(name, config, task))
            for name, config in self.arm_configs.items()
        ]
        decisions = await asyncio.gather(*jobs)
        result = self.consensus.resolve(decisions)
        return {
            "task": task,
            "decisions": [
                {
                    "arm_name": decision.arm_name,
                    "vote": decision.vote,
                    "reasoning": decision.reasoning,
                    "is_veto": decision.is_veto,
                    "cost": decision.cost,
                }
                for decision in decisions
            ],
            "result": result,
        }
