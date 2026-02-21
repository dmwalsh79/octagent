import math
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ArmDecision:
    arm_name: str
    vote: bool
    reasoning: str
    cost: float
    is_veto: bool = False

class ConsensusLayer:
    def __init__(self, threshold_fraction: float = 0.625):
        self.threshold_fraction = threshold_fraction

    def resolve(self, decisions: List[ArmDecision]) -> Dict[str, Any]:
        total_cost = sum(d.cost for d in decisions)
        
        # 1. Check for Vetoes (Hard Block)
        vetoes = [d for d in decisions if d.is_veto]
        if vetoes:
            return {
                "status": "VETOED",
                "reason": f"Veto exercised by {vetoes[0].arm_name}: {vetoes[0].reasoning}",
                "cost": total_cost,
                "conflicts": [f"{v.arm_name} vetoed: {v.reasoning}" for v in vetoes]
            }

        # 2. Calculate Quorum
        yes_votes = [d for d in decisions if d.vote]
        count = len(decisions)
        
        if count == 0:
             return {"status": "FAILED", "reason": "No arms participated.", "cost": total_cost, "conflicts": []}

        required = math.ceil(count * self.threshold_fraction)

        # 3. Determine Outcome
        if len(yes_votes) >= required:
            return {
                "status": "APPROVED",
                "reason": f"Supermajority reached ({len(yes_votes)}/{count}). Threshold: {required}.",
                "cost": total_cost,
                "conflicts": []
            }
        
        conflicts = [f"{d.arm_name}: {d.reasoning}" for d in decisions if not d.vote]
        return {
            "status": "REJECTED",
            "reason": f"Consensus failed ({len(yes_votes)}/{count}). Required: {required}.",
            "cost": total_cost,
            "conflicts": conflicts
        }