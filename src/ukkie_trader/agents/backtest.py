import pandas as pd
from datetime import datetime
from typing import List, Tuple
from ukkie_trader import __version__
from ukkie_trader.agents.base import BaseAgent
from ukkie_trader.domain.strategy.definition import FrozenStrategy, BacktestResult, SummaryMetrics
from ukkie_trader.engine.backtest.engine import BacktestEngine

class BacktestInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    strategy: FrozenStrategy
    data: pd.DataFrame
    initial_capital: float = 10000.0

class BacktestAgent(BaseAgent[BacktestInput, BacktestResult]):
    @property
    def name(self) -> str:
        return "Backtest"

    @property
    def version(self) -> str:
        return __version__

    async def validate_input(self, input_data: BacktestInput) -> Tuple[bool, List[str]]:
        errors = []
        if input_data.data.empty:
            errors.append("Market data is empty.")
        return len(errors) == 0, errors

    async def run(self, input_data: BacktestInput) -> BacktestResult:
        engine = BacktestEngine(input_data.strategy, input_data.initial_capital)
        results = engine.run(input_data.data)
        
        metrics = SummaryMetrics(
            total_return=results["total_return"],
            cagr=0.0, # To be implemented
            sharpe_ratio=0.0, # To be implemented
            max_drawdown=results["max_drawdown"],
            win_rate=0.0, # To be implemented
            profit_factor=0.0, # To be implemented
            total_trades=results["total_trades"]
        )
        
        return BacktestResult(
            backtest_id=f"BT-{datetime.now().strftime('%Y%m%d')}-{input_data.strategy.strategy_id[:8]}",
            strategy_id=input_data.strategy.strategy_id,
            summary_metrics=metrics,
            regime_breakdown={} # To be implemented with RegimeDetector
        )

    async def health_check(self) -> bool:
        return True
