from datetime import datetime
from typing import Tuple, List, Dict, Any
from pydantic import BaseModel
from ukkie_trader.agents.base import BaseAgent
from ukkie_trader.domain.strategy.definition import (
    FrozenStrategy, Decision, DecisionOutcome, HardGateResult, BacktestResult
)

class OrchestratorInput(BaseModel):
    strategy: FrozenStrategy
    backtest_result: BacktestResult
    # Other results would go here in full version

class OrchestratorAgent(BaseAgent[OrchestratorInput, Decision]):
    @property
    def name(self) -> str:
        return "Orchestrator"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def validate_input(self, input_data: OrchestratorInput) -> Tuple[bool, List[str]]:
        return True, []

    async def run(self, input_data: OrchestratorInput) -> Decision:
        strategy = input_data.strategy
        metrics = input_data.backtest_result.summary_metrics
        
        # Hard Gates from concept/03-data-models.md and strategy definition
        gates = []
        
        # 1. Sharpe Ratio (Mocked as 0 for now)
        gates.append(HardGateResult(
            metric="Sharpe Ratio",
            value=metrics.sharpe_ratio,
            threshold=1.5,
            passed=metrics.sharpe_ratio >= 1.5
        ))
        
        # 2. Max Drawdown
        gates.append(HardGateResult(
            metric="Max Drawdown",
            value=metrics.max_drawdown,
            threshold=-15.0,
            passed=metrics.max_drawdown >= -15.0 # Max DD is usually negative in our calc
        ))
        
        # 3. Win Rate (Mocked)
        gates.append(HardGateResult(
            metric="Win Rate",
            value=metrics.win_rate,
            threshold=45.0,
            passed=metrics.win_rate >= 45.0
        ))
        
        hard_gate_passed = all(g.passed for g in gates)
        
        decision_outcome = DecisionOutcome.APPROVE if hard_gate_passed else DecisionOutcome.REJECT
        
        return Decision(
            decision_id=f"DEC-{datetime.now().strftime('%Y%m%d')}-{strategy.strategy_id[:8]}",
            strategy_id=strategy.strategy_id,
            hard_gate_results=gates,
            hard_gate_passed=hard_gate_passed,
            decision=decision_outcome,
            decided_at=datetime.utcnow()
        )

    async def health_check(self) -> bool:
        return True
