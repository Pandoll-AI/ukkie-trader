from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict

class MarketRegime(str, Enum):
    NORMAL = "NORMAL"
    VOLATILE = "VOLATILE"
    ILLIQUID = "ILLIQUID"
    EVENT = "EVENT"

class Timeframe(str, Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"

class StrategyType(str, Enum):
    MOMENTUM = "MOMENTUM"
    MEAN_REVERSION = "MEAN_REVERSION"
    BREAKOUT = "BREAKOUT"
    TREND_FOLLOWING = "TREND_FOLLOWING"

class SignalType(str, Enum):
    EMA_CROSSOVER = "EMA_CROSSOVER"
    RSI_OVERSOLD = "RSI_OVERSOLD"
    BOLLINGER_BREAKOUT = "BOLLINGER_BREAKOUT"
    CUSTOM = "CUSTOM"

class ExecutionPolicy(str, Enum):
    MARKET_IMMEDIATE = "MARKET_IMMEDIATE"
    LIMIT_PASSIVE = "LIMIT_PASSIVE"
    LIMIT_TO_MARKET = "LIMIT_TO_MARKET"
    TWAP = "TWAP"
    VWAP = "VWAP"
    ADAPTIVE = "ADAPTIVE"

# --- Components ---

class SignalLogic(BaseModel):
    type: SignalType
    fast_period: Optional[int] = None
    slow_period: Optional[int] = None
    entry_condition: str
    exit_condition: str
    params: Dict[str, Any] = Field(default_factory=dict)

class PositionSizing(BaseModel):
    method: str  # FIXED_FRACTION, KELLY, VOLATILITY_TARGET
    fraction: Optional[float] = None
    target_vol: Optional[float] = None
    max_position_pct: float = 0.1

class RiskParams(BaseModel):
    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None
    trailing_stop_pct: Optional[float] = None
    max_holding_hours: Optional[int] = None

class ExecutionParams(BaseModel):
    policy: ExecutionPolicy = ExecutionPolicy.LIMIT_TO_MARKET
    limit_timeout_sec: int = 30
    max_slippage_bps: int = 50

# --- Core Entities ---

class StrategyProposal(BaseModel):
    """
    Initial strategy idea from the Proposer agent.
    """
    model_config = ConfigDict(extra="allow")

    proposal_id: str = Field(..., description="PROP-YYYYMMDD-XXX")
    name: str
    asset: str
    exchange: str
    timeframe: Timeframe = Field(default=Timeframe.H1)
    
    raw_idea: Dict[str, Any]
    status: str = "PENDING"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FrozenDefinition(BaseModel):
    """
    Immutable inner definition used for hashing.
    """
    strategy_type: StrategyType
    asset: str
    exchange: str
    timeframe: Timeframe
    signal_logic: SignalLogic
    position_sizing: PositionSizing
    risk_params: RiskParams
    execution_params: ExecutionParams

class FrozenStrategy(BaseModel):
    """
    The fully frozen strategy with identity hash.
    """
    strategy_id: str = Field(..., description="STRAT-{hash[:8]}")
    proposal_id: str
    definition_hash: str
    frozen_definition: FrozenDefinition
    frozen_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "ACTIVE"

    model_config = ConfigDict(frozen=True)

class DecisionOutcome(str, Enum):
    APPROVE = "APPROVE"
    HOLD = "HOLD"
    REJECT = "REJECT"

class DeploymentStage(str, Enum):
    SHADOW = "SHADOW"
    PAPER = "PAPER"
    LIVE = "LIVE"
    PROD = "PROD"

# --- Trading Models ---

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class PositionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

# --- Metrics & Results ---

class SummaryMetrics(BaseModel):
    total_return: float
    cagr: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int

class BacktestResult(BaseModel):
    backtest_id: str
    strategy_id: str
    summary_metrics: SummaryMetrics
    regime_breakdown: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DataQAResult(BaseModel):
    qa_id: str
    strategy_id: str
    qa_status: str # PASSED, FAILED, WARNING
    data_summary: Dict[str, Any]
    integrity_checks: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class HardGateResult(BaseModel):
    metric: str
    value: float
    threshold: float
    passed: bool

class Decision(BaseModel):
    decision_id: str
    strategy_id: str
    hard_gate_results: List[HardGateResult]
    hard_gate_passed: bool
    decision: DecisionOutcome
    decided_at: datetime = Field(default_factory=datetime.utcnow)

class Order(BaseModel):
    order_id: str
    strategy_id: str
    asset: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Position(BaseModel):
    position_id: str
    strategy_id: str
    asset: str
    side: str # LONG, SHORT
    entry_price: float
    quantity: float
    status: PositionStatus = PositionStatus.OPEN
    opened_at: datetime = Field(default_factory=datetime.utcnow)
