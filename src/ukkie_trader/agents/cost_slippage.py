from datetime import datetime
from typing import Tuple, List, Dict, Any
from pydantic import BaseModel
from ukkie_trader.agents.base import BaseAgent
from ukkie_trader.domain.strategy.definition import FrozenStrategy, BacktestResult
from ukkie_trader.utils.cost import CostModel

class CostSlippageInput(BaseModel):
    strategy: FrozenStrategy
    backtest_result: BacktestResult
    adv_usd: float = 1_000_000.0 # Placeholder for asset liquidity

class CostSlippageAgent(BaseAgent[CostSlippageInput, Dict[str, Any]]):
    @property
    def name(self) -> str:
        return "Cost/Slippage"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def validate_input(self, input_data: CostSlippageInput) -> Tuple[bool, List[str]]:
        return True, []

    async def run(self, input_data: CostSlippageInput) -> Dict[str, Any]:
        cost_model = CostModel()
        
        # In a real scenario, we would loop through all trades in backtest_result.
        # Here we apply a summary-level estimation for the MVP.
        metrics = input_data.backtest_result.summary_metrics
        avg_trade_size = 1000.0 # Placeholder
        
        # Calculate for Normal regime as baseline
        cost_info = cost_model.estimate_cost(
            trade_size_usd=avg_trade_size,
            regime="NORMAL", # Simplified for MVP
            adv_usd=input_data.adv_usd
        )
        
        total_estimated_cost_usd = cost_info["total_cost_usd"] * metrics.total_trades
        
        return {
            "cost_slip_id": f"CS-{datetime.now().strftime('%Y%m%d')}-{input_data.strategy.strategy_id[:8]}",
            "cost_summary": {
                "avg_trade_cost_usd": cost_info["total_cost_usd"],
                "total_impact_usd": total_estimated_cost_usd,
                "slippage_bps": cost_info["slippage_bps"]
            },
            "adjusted_metrics": {
                "net_return": metrics.total_return - (total_estimated_cost_usd / 100.0) # Simplified
            }
        }

    async def health_check(self) -> bool:
        return True
