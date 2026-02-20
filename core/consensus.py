import math
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class ArmDecision:
    arm_name: str
    vote: bool
    reasoning: str
    is_veto: bool = False
    cost: float = 0.0

class ConsensusLayer:
    def __init__(self, threshold_fraction: float = 0.625):
        """
        Sets the percentage of active arms required to pass a vote.
        Default is 62.5% (which equals 5 out of 8 arms).
        """
        self.threshold_fraction = threshold_fraction

    def resolve(self, decisions: List[ArmDecision]) -> Dict[str, Any]:
        """Calculates dynamic majority vote and strictly enforces veto overrides."""
        total_arms = len(decisions)
        
        # Edge case: No arms loaded
        if total_arms == 0:
            return {"status": "SYSTEM_ERROR", "reason": "Zero arms active.", "conflicts": [], "cost": 0.0}
            
        # Dynamic Quorum Mathematics: Q = max(1, ceil(N * p))
        quorum_threshold = max(1, math.ceil(total_arms * self.threshold_fraction))
        
        approvals = sum(1 for d in decisions if d.vote)
        total_cost = sum(d.cost for d in decisions)
        
        # 1. Evaluate Vetoes first (Strict Priority)
        vetoes = [d for d in decisions if d.is_veto]
        if vetoes:
            return {
                "status": "REJECTED_BY_VETO",
                "reason": f"Veto triggered by {vetoes[0].arm_name}: {vetoes[0].reasoning}",
                "conflicts": [d.reasoning for d in decisions if not d.vote],
                "cost": total_cost
            }

        # 2. Evaluate Quorum 
        if approvals >= quorum_threshold:
            return {
                "status": "APPROVED",
                "reason": f"Quorum met ({approvals}/{total_arms}). Required: {quorum_threshold}.",
                "conflicts": [d.reasoning for d in decisions if not d.vote],
                "cost": total_cost
            }
            
        # 3. Default Failure
        return {
            "status": "REJECTED_BY_QUORUM",
            "reason": f"Quorum failed. {approvals}/{total_arms} approved. Required: {quorum_threshold}.",
            "conflicts": [d.reasoning for d in decisions],
            "cost": total_cost
        }