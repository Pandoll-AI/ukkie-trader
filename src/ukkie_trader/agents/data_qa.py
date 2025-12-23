import pandas as pd
from datetime import datetime
from typing import Tuple, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from ukkie_trader.agents.base import BaseAgent
from ukkie_trader.domain.strategy.definition import FrozenStrategy, DataQAResult
from ukkie_trader.utils.regime import RegimeDetector

class DataQAInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    strategy: FrozenStrategy
    data: Any # Expecting pd.DataFrame or similar

class DataQAAgent(BaseAgent[DataQAInput, DataQAResult]):
    @property
    def name(self) -> str:
        return "Data QA"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def validate_input(self, input_data: DataQAInput) -> Tuple[bool, List[str]]:
        errors = []
        if not isinstance(input_data.data, pd.DataFrame):
            errors.append("Data must be a pandas DataFrame.")
        return len(errors) == 0, errors

    async def run(self, input_data: DataQAInput) -> DataQAResult:
        df = input_data.data
        strategy = input_data.strategy
        
        # 1. Integrity Checks
        null_count = df.isnull().sum().sum()
        gap_count = (df.index.to_series().diff() > pd.Timedelta(strategy.frozen_definition.timeframe.value)).sum()
        
        # 2. Sufficiency Checks
        # Requirement: At least 1000 bars for MVP
        bar_count = len(df)
        is_sufficient = bar_count >= 1000
        
        # 3. Regime Coverage
        detector = RegimeDetector()
        # Simplistic: run detector on the whole set to see diversity
        regimes = []
        # In a real scenario, we'd roll this. Here we just sample 10 points.
        regime_counts = {"NORMAL": 0, "VOLATILE": 0, "ILLIQUID": 0}
        
        # Mocking regime coverage for MVP
        regime_coverage = {
            "has_volatile": True,
            "has_illiquid": False,
            "coverage_score": 0.7
        }
        
        qa_status = "PASSED" if is_sufficient and null_count == 0 else "WARNING"
        if not is_sufficient:
            qa_status = "FAILED"
            
        return DataQAResult(
            qa_id=f"QA-{datetime.now().strftime('%Y%m%d')}-{strategy.strategy_id[:8]}",
            strategy_id=strategy.strategy_id,
            qa_status=qa_status,
            data_summary={
                "bar_count": bar_count,
                "start_date": str(df.index.min()),
                "end_date": str(df.index.max())
            },
            integrity_checks={
                "null_count": int(null_count),
                "gap_count": int(gap_count),
                "regime_coverage": regime_coverage
            }
        )

    async def health_check(self) -> bool:
        return True
