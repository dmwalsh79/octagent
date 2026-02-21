import asyncio
from dataclasses import dataclass
from typing import Any, Dict

from core.consensus import ArmDecision, ConsensusLayer


@dataclass
class PersonaArm:
    name: str
    config: Dict[str, Any]

    async def evaluate(self, task: str) -> ArmDecision:
        """Return a deterministic vote for a task based on lightweight guardrails."""
        await asyncio.sleep(0)

        lower_task = task.lower()
        unsafe_markers = (
            "rm -rf",
            "drop table",
            "delete production",
            "exfiltrate",
            "steal",
            "malware",
        )

        is_bouncer = self.name.lower() == "bouncer"
        is_unsafe = any(marker in lower_task for marker in unsafe_markers)

        if is_bouncer and is_unsafe:
            return ArmDecision(
                arm_name=self.name,
                vote=False,
                reasoning="Unsafe action pattern detected; veto applied.",
                is_veto=True,
                cost=0.0,
            )

        reasoning = self.config.get("persona", "Approved by persona policy.")
        return ArmDecision(
            arm_name=self.name,
            vote=True,
            reasoning=f"Approved: {reasoning}",
            is_veto=False,
            cost=0.0,
        )


class OrchestratorBrain:
    def __init__(self, arm_configs: Dict[str, Dict[str, Any]]):
        self.arms = [PersonaArm(name=name, config=config) for name, config in arm_configs.items()]
        self.consensus = ConsensusLayer()

    async def process_high_stakes_action(self, task: str) -> Dict[str, Any]:
        decisions = await asyncio.gather(*(arm.evaluate(task) for arm in self.arms))
        result = self.consensus.resolve(decisions)
        result["votes"] = [
            {
                "arm": d.arm_name,
                "vote": d.vote,
                "reasoning": d.reasoning,
                "is_veto": d.is_veto,
                "cost": d.cost,
            }
            for d in decisions
        ]

        print("\n🧠 Boardroom result:")
        print(f"Status: {result['status']}")
        print(f"Reason: {result['reason']}")
        if result["conflicts"]:
            print("Conflicts:")
            for conflict in result["conflicts"]:
                print(f" - {conflict}")
        print(f"Cost: ${result['cost']:.4f}")

        return result


async def _demo() -> None:
    sample_arms = {
        "Builder": {"persona": "Ship value quickly."},
        "Critic": {"persona": "Review for correctness."},
        "Bouncer": {"persona": "Enforce safety boundaries."},
    }
    brain = OrchestratorBrain(sample_arms)
    await brain.process_high_stakes_action("Draft a safe release plan")


if __name__ == "__main__":
    asyncio.run(_demo())
