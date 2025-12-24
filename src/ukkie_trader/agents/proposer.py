from datetime import datetime
from typing import Tuple, List, Dict, Any
from ukkie_trader import __version__
from ukkie_trader.agents.base import BaseAgent
from ukkie_trader.domain.strategy.definition import StrategyProposal, Timeframe
from pydantic import BaseModel

class ProposerInput(BaseModel):
    name: str
    asset: str
    exchange: str
    timeframe: Timeframe = Timeframe.H1
    raw_idea: Dict[str, Any]

class ProposerAgent(BaseAgent[ProposerInput, StrategyProposal]):
    @property
    def name(self) -> str:
        return "Proposer"

    @property
    def version(self) -> str:
        return __version__

    async def validate_input(self, input_data: ProposerInput) -> Tuple[bool, List[str]]:
        errors = []
        if not input_data.name:
            errors.append("Strategy name is required.")
        if not input_data.asset:
            errors.append("Asset (e.g., BTC/USDT) is required.")
        return len(errors) == 0, errors

    async def run(self, input_data: ProposerInput) -> StrategyProposal:
        # Generate a proposal ID
        proposal_id = f"PROP-{datetime.now().strftime('%Y%m%d')}-{input_data.name[:3].upper()}"
        
        proposal = StrategyProposal(
            proposal_id=proposal_id,
            name=input_data.name,
            asset=input_data.asset,
            exchange=input_data.exchange,
            timeframe=input_data.timeframe,
            raw_idea=input_data.raw_idea,
            status="PENDING",
            created_at=datetime.utcnow()
        )
        return proposal

    async def health_check(self) -> bool:
        return True
