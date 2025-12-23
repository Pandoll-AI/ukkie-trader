from datetime import datetime
from typing import Tuple, List, Dict, Any
import numpy as np
from pydantic import BaseModel
from ukkie_trader.agents.base import BaseAgent
from ukkie_trader.domain.strategy.definition import FrozenStrategy, BacktestResult
from ukkie_trader.utils.overfit import OverfitAuditor

class OverfitAuditInput(BaseModel):
    strategy: FrozenStrategy
    backtest_result: BacktestResult
    returns: List[float] # List of daily/bar returns
    num_trials_conducted: int = 10

class OverfitAuditAgent(BaseAgent[OverfitAuditInput, Dict[str, Any]]):
    @property
    def name(self) -> str:
        return "Overfit Audit"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def validate_input(self, input_data: OverfitAuditInput) -> Tuple[bool, List[str]]:
        if not input_data.returns:
            return False, ["Returns data is required for overfit audit."]
        return True, []

    async def run(self, input_data: OverfitAuditInput) -> Dict[str, Any]:
        auditor = OverfitAuditor()
        
        # 1. Calculate DSR
        returns_arr = np.array(input_data.returns)
        dsr = auditor.calculate_dsr(returns_arr, num_trials=input_data.num_trials_conducted)
        
        # 2. Rating Logic
        rating = "LOW"
        if dsr < 1.0: rating = "MEDIUM"
        if dsr < 0.5: rating = "HIGH"
        
        return {
            "overfit_audit_id": f"OFA-{datetime.now().strftime('%Y%m%d')}-{input_data.strategy.strategy_id[:8]}",
            "deflated_sharpe": dsr,
            "overfit_rating": rating,
            "walk_forward_results": {
                "is_return": 10.0, # Placeholder
                "os_return": 8.0,  # Placeholder
                "decay_ratio": 0.8
            }
        }

    async def health_check(self) -> bool:
        return True
