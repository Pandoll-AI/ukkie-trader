from datetime import datetime
from typing import Tuple, List, Dict, Any
from ukkie_trader.agents.base import BaseAgent
from ukkie_trader.domain.strategy.definition import (
    StrategyProposal, FrozenStrategy, FrozenDefinition, 
    SignalLogic, PositionSizing, RiskParams, ExecutionParams,
    StrategyType, SignalType, ExecutionPolicy
)
from ukkie_trader.domain.strategy.hash import compute_definition_hash

class FreezerAgent(BaseAgent[StrategyProposal, FrozenStrategy]):
    @property
    def name(self) -> str:
        return "Definition Freezer"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def validate_input(self, input_data: StrategyProposal) -> Tuple[bool, List[str]]:
        # Basic validation that required logic is present in raw_idea or elsewhere
        return True, []

    async def run(self, input_data: StrategyProposal) -> FrozenStrategy:
        # 1. Construct the inner FrozenDefinition
        # In a real scenario, this would extract/infer from raw_idea
        # For the MVP foundation, we assume some mapping logic
        
        raw = input_data.raw_idea
        
        definition = FrozenDefinition(
            strategy_type=raw.get("strategy_type", StrategyType.TREND_FOLLOWING),
            asset=input_data.asset,
            exchange=input_data.exchange,
            timeframe=input_data.timeframe,
            signal_logic=SignalLogic(
                type=raw.get("signal_type", SignalType.EMA_CROSSOVER),
                entry_condition=raw.get("entry_condition", "price > ema"),
                exit_condition=raw.get("exit_condition", "price < ema"),
                params=raw.get("signal_params", {"period": 20})
            ),
            position_sizing=PositionSizing(
                method=raw.get("sizing_method", "FIXED_FRACTION"),
                fraction=raw.get("sizing_fraction", 0.02)
            ),
            risk_params=RiskParams(
                stop_loss_pct=raw.get("stop_loss_pct", 2.0),
                take_profit_pct=raw.get("take_profit_pct", 5.0)
            ),
            execution_params=ExecutionParams(
                policy=raw.get("execution_policy", ExecutionPolicy.LIMIT_TO_MARKET)
            )
        )
        
        # 2. Compute Hash
        # Convert to dict for hashing
        def_dict = definition.model_dump()
        strat_hash = compute_definition_hash(def_dict)
        
        # 3. Create FrozenStrategy
        frozen = FrozenStrategy(
            strategy_id=f"STRAT-{strat_hash[:8]}",
            proposal_id=input_data.proposal_id,
            definition_hash=strat_hash,
            frozen_definition=definition,
            frozen_at=datetime.utcnow(),
            status="ACTIVE"
        )
        
        return frozen

    async def health_check(self) -> bool:
        return True
