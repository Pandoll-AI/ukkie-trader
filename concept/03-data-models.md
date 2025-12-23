# Ukkie-Trader 개발 계획서 Part 3: 데이터 모델

---

## 4. 데이터 모델

### 4.1 핵심 엔티티 관계도

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ENTITY RELATIONSHIP DIAGRAM                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐         ┌─────────────────┐         ┌─────────────┐       │
│  │  Proposal   │────────→│ FrozenStrategy  │────────→│  Backtest   │       │
│  │             │   1:1   │                 │   1:N   │             │       │
│  └─────────────┘         └────────┬────────┘         └──────┬──────┘       │
│                                   │                         │              │
│                                   │ 1:N                     │ 1:1          │
│                                   ▼                         ▼              │
│                          ┌─────────────────┐       ┌─────────────────┐     │
│                          │    DataQA       │       │   CostSlippage  │     │
│                          └─────────────────┘       └────────┬────────┘     │
│                                                             │ 1:1          │
│                                                             ▼              │
│                                                    ┌─────────────────┐     │
│                                                    │  ExecutionSim   │     │
│                                                    └────────┬────────┘     │
│                                                             │ 1:1          │
│                                                             ▼              │
│  ┌─────────────┐                                   ┌─────────────────┐     │
│  │  Portfolio  │←──────────────────────────────────│   RiskStress    │     │
│  │             │   N:M                             └────────┬────────┘     │
│  └──────┬──────┘                                            │ 1:1          │
│         │                                                   ▼              │
│         │ 1:N                                      ┌─────────────────┐     │
│         ▼                                          │  OverfitAudit   │     │
│  ┌─────────────┐                                   └────────┬────────┘     │
│  │  Position   │                                            │ 1:1          │
│  │             │                                            ▼              │
│  └──────┬──────┘                                   ┌─────────────────┐     │
│         │ 1:N                                      │ PortfolioCapacity│    │
│         ▼                                          └────────┬────────┘     │
│  ┌─────────────┐                                            │ 1:1          │
│  │   Order     │                                            ▼              │
│  │             │                                   ┌─────────────────┐     │
│  └─────────────┘                                   │   Decision      │     │
│                                                    │ (Orchestrator)  │     │
│                                                    └─────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 SQLite 스키마

```sql
-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- 전략 제안
CREATE TABLE proposals (
    proposal_id TEXT PRIMARY KEY,              -- PROP-YYYYMMDD-XXX
    source TEXT NOT NULL,                      -- USER, SCAN, LITERATURE
    raw_idea JSON NOT NULL,                    -- 원본 아이디어
    constraints JSON,                          -- 제약 조건
    status TEXT NOT NULL DEFAULT 'PENDING',    -- PENDING, PROPOSED, REJECTED
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 동결된 전략 정의
CREATE TABLE frozen_strategies (
    strategy_id TEXT PRIMARY KEY,              -- STRAT-{hash[:8]}
    proposal_id TEXT NOT NULL REFERENCES proposals(proposal_id),
    definition_hash TEXT NOT NULL UNIQUE,      -- SHA256 전체
    frozen_definition JSON NOT NULL,           -- 불변 정의
    frozen_at TIMESTAMP NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',     -- ACTIVE, DEPRECATED, ARCHIVED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 데이터 품질 검사 결과
CREATE TABLE data_qa_results (
    qa_id TEXT PRIMARY KEY,
    strategy_id TEXT NOT NULL REFERENCES frozen_strategies(strategy_id),
    qa_status TEXT NOT NULL,                   -- PASSED, FAILED, WARNING
    data_summary JSON NOT NULL,
    integrity_checks JSON NOT NULL,
    bias_checks JSON NOT NULL,
    sufficiency_checks JSON NOT NULL,
    warnings JSON,
    data_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 백테스트 결과
CREATE TABLE backtests (
    backtest_id TEXT PRIMARY KEY,              -- BT-YYYYMMDD-XXX
    strategy_id TEXT NOT NULL REFERENCES frozen_strategies(strategy_id),
    config JSON NOT NULL,                      -- 백테스트 설정
    summary_metrics JSON NOT NULL,             -- 핵심 지표
    regime_breakdown JSON NOT NULL,            -- 레짐별 성과
    monthly_returns JSON,
    trade_log_path TEXT,
    equity_curve_path TEXT,
    status TEXT NOT NULL DEFAULT 'COMPLETED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 비용/슬리피지 분석
CREATE TABLE cost_slippage_results (
    cost_slip_id TEXT PRIMARY KEY,
    backtest_id TEXT NOT NULL REFERENCES backtests(backtest_id),
    cost_summary JSON NOT NULL,
    adjusted_metrics JSON NOT NULL,
    regime_cost_breakdown JSON NOT NULL,
    sensitivity_analysis JSON,
    adjusted_trade_log_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 실행 시뮬레이션
CREATE TABLE execution_sims (
    exec_sim_id TEXT PRIMARY KEY,
    backtest_id TEXT NOT NULL REFERENCES backtests(backtest_id),
    policies_tested JSON NOT NULL,
    recommended_policy TEXT,
    recommendation_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 리스크/스트레스 테스트
CREATE TABLE risk_stress_results (
    risk_stress_id TEXT PRIMARY KEY,
    strategy_id TEXT NOT NULL REFERENCES frozen_strategies(strategy_id),
    var_analysis JSON NOT NULL,
    stress_results JSON NOT NULL,
    tail_risk_metrics JSON NOT NULL,
    risk_rating TEXT NOT NULL,                 -- LOW, MODERATE, HIGH, EXTREME
    risk_notes JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 과최적화 감사
CREATE TABLE overfit_audits (
    overfit_audit_id TEXT PRIMARY KEY,
    strategy_id TEXT NOT NULL REFERENCES frozen_strategies(strategy_id),
    walk_forward_results JSON NOT NULL,
    deflated_sharpe JSON NOT NULL,
    randomization_test JSON NOT NULL,
    overfit_score REAL NOT NULL,
    overfit_rating TEXT NOT NULL,              -- LOW, MEDIUM, HIGH
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 포트폴리오 용량 분석
CREATE TABLE portfolio_capacity_results (
    portfolio_cap_id TEXT PRIMARY KEY,
    strategy_id TEXT NOT NULL REFERENCES frozen_strategies(strategy_id),
    capacity_analysis JSON NOT NULL,
    portfolio_fit JSON NOT NULL,
    stress_portfolio_metrics JSON NOT NULL,
    allocation_recommendation JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 최종 결정
CREATE TABLE decisions (
    decision_id TEXT PRIMARY KEY,
    strategy_id TEXT NOT NULL REFERENCES frozen_strategies(strategy_id),
    hard_gate_results JSON NOT NULL,
    hard_gate_passed BOOLEAN NOT NULL,
    failed_gates JSON,
    soft_scores JSON,
    final_score REAL,
    decision TEXT NOT NULL,                    -- APPROVE, HOLD, REJECT
    decision_reason TEXT,
    recommendations JSON,
    human_override_required BOOLEAN DEFAULT FALSE,
    deployment_stage TEXT,                     -- SHADOW, PAPER, LIVE, PROD
    decided_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TRADING TABLES
-- ============================================================================

-- 포트폴리오
CREATE TABLE portfolios (
    portfolio_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    initial_capital REAL NOT NULL,
    current_capital REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',     -- ACTIVE, PAUSED, CLOSED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 포트폴리오-전략 매핑
CREATE TABLE portfolio_strategies (
    portfolio_id TEXT NOT NULL REFERENCES portfolios(portfolio_id),
    strategy_id TEXT NOT NULL REFERENCES frozen_strategies(strategy_id),
    allocation_pct REAL NOT NULL,              -- 배분 비율
    max_position_pct REAL NOT NULL,            -- 최대 포지션
    status TEXT NOT NULL DEFAULT 'ACTIVE',     -- ACTIVE, PAUSED
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (portfolio_id, strategy_id)
);

-- 포지션
CREATE TABLE positions (
    position_id TEXT PRIMARY KEY,
    portfolio_id TEXT NOT NULL REFERENCES portfolios(portfolio_id),
    strategy_id TEXT NOT NULL REFERENCES frozen_strategies(strategy_id),
    asset TEXT NOT NULL,
    side TEXT NOT NULL,                        -- LONG, SHORT
    entry_price REAL NOT NULL,
    current_price REAL,
    quantity REAL NOT NULL,
    unrealized_pnl REAL,
    realized_pnl REAL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'OPEN',       -- OPEN, CLOSED
    opened_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 주문
CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    position_id TEXT REFERENCES positions(position_id),
    strategy_id TEXT NOT NULL REFERENCES frozen_strategies(strategy_id),
    exchange TEXT NOT NULL,
    asset TEXT NOT NULL,
    side TEXT NOT NULL,                        -- BUY, SELL
    order_type TEXT NOT NULL,                  -- MARKET, LIMIT, STOP
    quantity REAL NOT NULL,
    price REAL,                                -- LIMIT/STOP 가격
    filled_quantity REAL DEFAULT 0,
    avg_fill_price REAL,
    status TEXT NOT NULL DEFAULT 'PENDING',    -- PENDING, OPEN, FILLED, CANCELLED, REJECTED
    execution_policy TEXT,                     -- MARKET_IMMEDIATE, LIMIT_TO_MARKET, etc.
    slippage_bps REAL,
    fees_paid REAL,
    submitted_at TIMESTAMP,
    filled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 거래 로그 (체결 내역)
CREATE TABLE trade_logs (
    trade_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL REFERENCES orders(order_id),
    execution_price REAL NOT NULL,
    execution_quantity REAL NOT NULL,
    execution_time TIMESTAMP NOT NULL,
    fee REAL NOT NULL,
    fee_currency TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MONITORING TABLES
-- ============================================================================

-- 시스템 상태
CREATE TABLE system_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component TEXT NOT NULL,                   -- ORCHESTRATOR, DATA_FEED, etc.
    status TEXT NOT NULL,                      -- HEALTHY, DEGRADED, DOWN
    last_heartbeat TIMESTAMP NOT NULL,
    details JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 알림
CREATE TABLE alerts (
    alert_id TEXT PRIMARY KEY,
    alert_type TEXT NOT NULL,                  -- RISK, SYSTEM, TRADE
    severity TEXT NOT NULL,                    -- INFO, WARNING, CRITICAL
    message TEXT NOT NULL,
    strategy_id TEXT REFERENCES frozen_strategies(strategy_id),
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by TEXT,
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 감사 로그
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,                      -- CREATE, UPDATE, DELETE, EXECUTE
    entity_type TEXT NOT NULL,                 -- STRATEGY, ORDER, POSITION, etc.
    entity_id TEXT NOT NULL,
    user_id TEXT,
    old_value JSON,
    new_value JSON,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_proposals_status ON proposals(status);
CREATE INDEX idx_frozen_strategies_status ON frozen_strategies(status);
CREATE INDEX idx_backtests_strategy ON backtests(strategy_id);
CREATE INDEX idx_decisions_strategy ON decisions(strategy_id);
CREATE INDEX idx_decisions_decision ON decisions(decision);
CREATE INDEX idx_positions_status ON positions(status);
CREATE INDEX idx_positions_portfolio ON positions(portfolio_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_strategy ON orders(strategy_id);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_acknowledged ON alerts(acknowledged);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
```

### 4.3 Pydantic 모델

```python
# src/ukkie_trader/domain/models.py

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ============================================================================
# ENUMS
# ============================================================================

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


class Timeframe(str, Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class PositionSide(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class PositionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Regime(str, Enum):
    NORMAL = "NORMAL"
    VOLATILE = "VOLATILE"
    ILLIQUID = "ILLIQUID"
    EVENT = "EVENT"


class DecisionOutcome(str, Enum):
    APPROVE = "APPROVE"
    HOLD = "HOLD"
    REJECT = "REJECT"


class DeploymentStage(str, Enum):
    SHADOW = "SHADOW"
    PAPER = "PAPER"
    LIVE = "LIVE"
    PROD = "PROD"


class ExecutionPolicy(str, Enum):
    MARKET_IMMEDIATE = "MARKET_IMMEDIATE"
    LIMIT_PASSIVE = "LIMIT_PASSIVE"
    LIMIT_TO_MARKET = "LIMIT_TO_MARKET"
    TWAP = "TWAP"
    VWAP = "VWAP"
    ADAPTIVE = "ADAPTIVE"


# ============================================================================
# STRATEGY MODELS
# ============================================================================

class SignalLogic(BaseModel):
    type: SignalType
    fast_period: Optional[int] = None
    slow_period: Optional[int] = None
    entry_condition: str
    exit_condition: str
    params: dict = Field(default_factory=dict)


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
    order_type: ExecutionPolicy = ExecutionPolicy.LIMIT_TO_MARKET
    limit_timeout_sec: int = 30
    max_slippage_bps: int = 50


class FrozenDefinition(BaseModel):
    """불변 전략 정의 - 해시 생성 대상"""
    strategy_type: StrategyType
    asset: str
    exchange: str
    timeframe: Timeframe
    signal_logic: SignalLogic
    position_sizing: PositionSizing
    risk_params: RiskParams
    execution_params: ExecutionParams


class FrozenStrategy(BaseModel):
    """동결된 전략"""
    strategy_id: str
    proposal_id: str
    definition_hash: str
    frozen_definition: FrozenDefinition
    frozen_at: datetime
    status: str = "ACTIVE"


# ============================================================================
# BACKTEST MODELS
# ============================================================================

class BacktestConfig(BaseModel):
    initial_capital: float = 10000
    fee_rate: float = 0.0
    slippage_rate: float = 0.0
    margin_enabled: bool = False


class SummaryMetrics(BaseModel):
    total_return: float
    cagr: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    max_drawdown_duration_days: int
    win_rate: float
    profit_factor: float
    avg_trade_return: float
    total_trades: int
    avg_holding_hours: float


class RegimeBreakdown(BaseModel):
    trade_count: int
    total_return: float
    sharpe_ratio: float
    win_rate: float


class BacktestResult(BaseModel):
    backtest_id: str
    strategy_id: str
    status: str
    summary_metrics: SummaryMetrics
    regime_breakdown: dict[str, RegimeBreakdown]
    monthly_returns: dict[str, float]
    trade_log_path: Optional[str] = None
    equity_curve_path: Optional[str] = None


# ============================================================================
# TRADING MODELS
# ============================================================================

class Order(BaseModel):
    order_id: str
    position_id: Optional[str] = None
    strategy_id: str
    exchange: str
    asset: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None
    filled_quantity: Decimal = Decimal(0)
    avg_fill_price: Optional[Decimal] = None
    status: OrderStatus = OrderStatus.PENDING
    execution_policy: Optional[ExecutionPolicy] = None
    slippage_bps: Optional[float] = None
    fees_paid: Optional[Decimal] = None
    submitted_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Position(BaseModel):
    position_id: str
    portfolio_id: str
    strategy_id: str
    asset: str
    side: PositionSide
    entry_price: Decimal
    current_price: Optional[Decimal] = None
    quantity: Decimal
    unrealized_pnl: Optional[Decimal] = None
    realized_pnl: Decimal = Decimal(0)
    status: PositionStatus = PositionStatus.OPEN
    opened_at: datetime
    closed_at: Optional[datetime] = None


# ============================================================================
# DECISION MODELS
# ============================================================================

class HardGateResult(BaseModel):
    value: float
    threshold: float
    passed: bool


class SoftScore(BaseModel):
    criterion: str
    weight: float
    raw_score: float
    normalized_score: float
    weighted_score: float


class Decision(BaseModel):
    decision_id: str
    strategy_id: str
    hard_gate_results: dict[str, HardGateResult]
    hard_gate_passed: bool
    failed_gates: list[str] = Field(default_factory=list)
    soft_scores: Optional[list[SoftScore]] = None
    final_score: Optional[float] = None
    decision: DecisionOutcome
    decision_reason: str
    recommendations: list[str] = Field(default_factory=list)
    human_override_required: bool = False
    deployment_stage: Optional[DeploymentStage] = None
    decided_at: datetime
```

### 4.4 상태 전이 다이어그램

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  STRATEGY LIFECYCLE STATE MACHINE                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────┐                                                                │
│  │ DRAFT   │                                                                │
│  │(Proposal)│                                                               │
│  └────┬────┘                                                                │
│       │ propose()                                                           │
│       ▼                                                                     │
│  ┌─────────┐     reject()     ┌──────────┐                                 │
│  │PROPOSED │────────────────→ │ REJECTED │                                 │
│  └────┬────┘                  └──────────┘                                 │
│       │ freeze()                                                            │
│       ▼                                                                     │
│  ┌─────────┐                                                                │
│  │ FROZEN  │                                                                │
│  └────┬────┘                                                                │
│       │ validate()                                                          │
│       ▼                                                                     │
│  ┌─────────────┐                                                            │
│  │ VALIDATING  │ ◄─────────────────────────────────────────┐               │
│  │             │                                            │               │
│  │ ┌─────────┐ │                                            │               │
│  │ │ DataQA  │ │                                            │               │
│  │ └────┬────┘ │                                            │               │
│  │      ▼      │                                            │               │
│  │ ┌─────────┐ │     fail                                   │               │
│  │ │Backtest │─┼──────────────────────────────────┐        │               │
│  │ └────┬────┘ │                                  ▼        │               │
│  │      ▼      │                            ┌──────────┐   │               │
│  │ ┌─────────┐ │                            │ FAILED   │   │               │
│  │ │CostSlip │ │                            │(w/reason)│   │               │
│  │ └────┬────┘ │                            └────┬─────┘   │               │
│  │      ▼      │                                 │         │               │
│  │ ┌─────────┐ │                            revise()       │               │
│  │ │ ExecSim │ │                                 │         │               │
│  │ └────┬────┘ │                                 └─────────┘               │
│  │      ▼      │                                                           │
│  │ ┌─────────┐ │                                                           │
│  │ │RiskStrs │ │                                                           │
│  │ └────┬────┘ │                                                           │
│  │      ▼      │                                                           │
│  │ ┌─────────┐ │                                                           │
│  │ │OvfitAud│ │                                                           │
│  │ └────┬────┘ │                                                           │
│  │      ▼      │                                                           │
│  │ ┌─────────┐ │                                                           │
│  │ │PortCap │ │                                                           │
│  │ └────┬────┘ │                                                           │
│  └──────┼──────┘                                                           │
│         │ orchestrate()                                                     │
│         ▼                                                                   │
│  ┌───────────────────────────────────────────────────────────────┐         │
│  │                      ORCHESTRATOR DECISION                     │         │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │         │
│  │  │   APPROVE    │  │    HOLD      │  │       REJECT         │ │         │
│  │  │              │  │              │  │                      │ │         │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────────────────┘ │         │
│  └─────────┼─────────────────┼──────────────────────────────────┘         │
│            │                 │                                             │
│    deploy()│           human_review()                                      │
│            ▼                 ▼                                             │
│      ┌──────────┐      ┌──────────────┐                                    │
│      │  SHADOW  │      │PENDING_REVIEW│                                    │
│      └────┬─────┘      └──────────────┘                                    │
│           │                                                                 │
│    promote()                                                                │
│           ▼                                                                 │
│      ┌──────────┐                                                           │
│      │  PAPER   │                                                           │
│      └────┬─────┘                                                           │
│           │                                                                 │
│    promote() + approval                                                     │
│           ▼                                                                 │
│      ┌──────────┐                                                           │
│      │   LIVE   │ ←──────────────────────────┐                             │
│      └────┬─────┘                            │                             │
│           │                              resume()                           │
│           │ promote() + regulatory          │                              │
│           ▼                                  │                              │
│      ┌──────────┐      pause()         ┌──────────┐                        │
│      │   PROD   │─────────────────────→│  PAUSED  │                        │
│      └────┬─────┘                      └──────────┘                        │
│           │                                                                 │
│    kill() or deprecate()                                                    │
│           ▼                                                                 │
│      ┌──────────┐                                                           │
│      │ ARCHIVED │                                                           │
│      └──────────┘                                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 다음 파일: 04-algorithms.md

핵심 알고리즘 상세 (백테스트 엔진, 비용 모델, UCB1)
