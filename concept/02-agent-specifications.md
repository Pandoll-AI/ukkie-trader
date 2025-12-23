# Ukkie-Trader 개발 계획서 Part 2: 에이전트 상세 명세

---

## 3. 에이전트 명세

### 3.0 에이전트 공통 인터페이스

```python
# 모든 에이전트가 구현해야 하는 추상 기본 클래스

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from pydantic import BaseModel

InputT = TypeVar('InputT', bound=BaseModel)
OutputT = TypeVar('OutputT', bound=BaseModel)

class BaseAgent(ABC, Generic[InputT, OutputT]):
    """
    모든 Ukkie-Trader 에이전트의 기본 클래스
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """에이전트 고유 이름"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """에이전트 버전"""
        pass
    
    @abstractmethod
    async def validate_input(self, input: InputT) -> tuple[bool, list[str]]:
        """입력 검증, (통과여부, 오류메시지들) 반환"""
        pass
    
    @abstractmethod
    async def run(self, input: InputT) -> OutputT:
        """에이전트 실행"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """에이전트 상태 확인"""
        pass
```

---

### 3.1 Research Agent: Proposer

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AGENT: PROPOSER                                                             │
│  Role: 전략 아이디어 제안 및 초기 구조화                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PURPOSE                                                                    │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • 사용자 또는 자동 스캔에서 전략 아이디어 수집                              │
│  • 아이디어를 구조화된 StrategyProposal로 변환                               │
│  • 기본 실현가능성 체크 (데이터 가용성, 자산 지원 여부)                       │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ INPUT SCHEMA                                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ {                                                                           │
│   "proposal_id": "PROP-20251223-001",                                       │
│   "source": "USER" | "SCAN" | "LITERATURE",                                 │
│   "raw_idea": {                                                             │
│     "description": "BTC 20/50 EMA 크로스오버 모멘텀 전략",                   │
│     "asset_hints": ["BTC/USDT"],                                            │
│     "timeframe_hint": "1h",                                                 │
│     "reference_links": ["https://..."]                                      │
│   },                                                                        │
│   "constraints": {                                                          │
│     "max_position_pct": 0.1,                                                │
│     "allowed_exchanges": ["binance", "okx"],                                │
│     "excluded_hours_utc": [0, 1, 2, 3]                                      │
│   }                                                                         │
│ }                                                                           │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ OUTPUT SCHEMA                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ {                                                                           │
│   "proposal_id": "PROP-20251223-001",                                       │
│   "status": "PROPOSED" | "REJECTED",                                        │
│   "rejection_reason": null | "NO_DATA" | "UNSUPPORTED_ASSET",               │
│                                                                             │
│   "structured_proposal": {                                                  │
│     "strategy_type": "MOMENTUM",                                            │
│     "asset": "BTC/USDT",                                                    │
│     "exchange": "binance",                                                  │
│     "timeframe": "1h",                                                      │
│                                                                             │
│     "signal_logic": {                                                       │
│       "type": "EMA_CROSSOVER",                                              │
│       "fast_period": 20,                                                    │
│       "slow_period": 50,                                                    │
│       "entry_condition": "fast > slow AND fast_prev <= slow_prev",          │
│       "exit_condition": "fast < slow AND fast_prev >= slow_prev"            │
│     },                                                                      │
│                                                                             │
│     "position_sizing": {                                                    │
│       "method": "FIXED_FRACTION",                                           │
│       "fraction": 0.1                                                       │
│     },                                                                      │
│                                                                             │
│     "risk_params": {                                                        │
│       "stop_loss_pct": null,     // Freezer가 정의                          │
│       "take_profit_pct": null,   // Freezer가 정의                          │
│       "max_holding_hours": null  // Freezer가 정의                          │
│     }                                                                       │
│   },                                                                        │
│                                                                             │
│   "data_availability": {                                                    │
│     "earliest_date": "2020-01-01",                                          │
│     "latest_date": "2025-12-22",                                            │
│     "gaps_detected": false                                                  │
│   },                                                                        │
│                                                                             │
│   "next_agent": "DEFINITION_FREEZER"                                        │
│ }                                                                           │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ FAILURE CONDITIONS                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ┌─────────────────────────┬─────────────────────────────────────────────┐  │
│ │ Failure                 │ Action                                      │  │
│ ├─────────────────────────┼─────────────────────────────────────────────┤  │
│ │ 데이터 없음             │ REJECTED + NO_DATA                          │  │
│ │ 지원 안되는 자산        │ REJECTED + UNSUPPORTED_ASSET                │  │
│ │ 파싱 불가 아이디어      │ REJECTED + PARSE_ERROR                      │  │
│ │ 너무 많은 파라미터      │ REJECTED + COMPLEXITY_LIMIT (>20 params)    │  │
│ └─────────────────────────┴─────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.2 Research Agent: Definition Freezer

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AGENT: DEFINITION FREEZER                                                   │
│  Role: 전략 정의 확정 및 불변 해시 생성                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PURPOSE                                                                    │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • 모든 undefined 파라미터 채우기                                            │
│  • 전략 정의 해시 생성 (변경 감지용)                                          │
│  • 정의 불변성 강제 - 이후 수정 시 새 전략으로 취급                            │
│                                                                             │
│  CRITICAL RULE                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│  "Freeze 이후 정의 변경 = 새로운 strategy_id 발급"                           │
│  이전 전략과의 연속성 없음. 처음부터 검증 재시작.                             │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ INPUT SCHEMA                                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ {                                                                           │
│   "proposal_id": "PROP-20251223-001",                                       │
│   "structured_proposal": { ... },  // Proposer 출력                         │
│   "user_overrides": {              // 사용자가 명시적으로 설정               │
│     "stop_loss_pct": 0.02,                                                  │
│     "take_profit_pct": 0.05                                                 │
│   }                                                                         │
│ }                                                                           │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ OUTPUT SCHEMA                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ {                                                                           │
│   "strategy_id": "STRAT-a3f8c2d1",  // SHA256 해시 앞 8자리                 │
│   "proposal_id": "PROP-20251223-001",                                       │
│   "frozen_at": "2025-12-23T12:00:00Z",                                      │
│   "definition_hash": "a3f8c2d1e5b7...",                                     │
│                                                                             │
│   "frozen_definition": {                                                    │
│     "strategy_type": "MOMENTUM",                                            │
│     "asset": "BTC/USDT",                                                    │
│     "exchange": "binance",                                                  │
│     "timeframe": "1h",                                                      │
│                                                                             │
│     "signal_logic": {                                                       │
│       "type": "EMA_CROSSOVER",                                              │
│       "fast_period": 20,                                                    │
│       "slow_period": 50,                                                    │
│       "entry_condition": "fast > slow AND fast_prev <= slow_prev",          │
│       "exit_condition": "fast < slow AND fast_prev >= slow_prev"            │
│     },                                                                      │
│                                                                             │
│     "position_sizing": {                                                    │
│       "method": "FIXED_FRACTION",                                           │
│       "fraction": 0.1                                                       │
│     },                                                                      │
│                                                                             │
│     "risk_params": {                                                        │
│       "stop_loss_pct": 0.02,        // FROZEN                               │
│       "take_profit_pct": 0.05,      // FROZEN                               │
│       "max_holding_hours": 168,     // Default: 1 week                      │
│       "trailing_stop_pct": null     // Not used                             │
│     },                                                                      │
│                                                                             │
│     "execution_params": {                                                   │
│       "order_type": "LIMIT_TO_MARKET",                                      │
│       "limit_timeout_sec": 30,                                              │
│       "max_slippage_bps": 50                                                │
│     }                                                                       │
│   },                                                                        │
│                                                                             │
│   "completeness_check": {                                                   │
│     "all_params_defined": true,                                             │
│     "undefined_params": []                                                  │
│   },                                                                        │
│                                                                             │
│   "next_agent": "DATA_QA"                                                   │
│ }                                                                           │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ HASH GENERATION ALGORITHM                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ def compute_definition_hash(frozen_definition: dict) -> str:                │
│     """                                                                     │
│     결정론적 해시 생성                                                       │
│     - 키 정렬 (알파벳순)                                                     │
│     - null 값은 문자열 "null"로 변환                                         │
│     - float는 소수점 8자리 고정                                              │
│     """                                                                     │
│     canonical = json.dumps(                                                 │
│         frozen_definition,                                                  │
│         sort_keys=True,                                                     │
│         default=lambda x: "null" if x is None else round(x, 8)              │
│     )                                                                       │
│     return hashlib.sha256(canonical.encode()).hexdigest()                   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ FAILURE CONDITIONS                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ┌─────────────────────────┬─────────────────────────────────────────────┐  │
│ │ Failure                 │ Action                                      │  │
│ ├─────────────────────────┼─────────────────────────────────────────────┤  │
│ │ 필수 파라미터 없음      │ BLOCKED + 사용자에게 입력 요청              │  │
│ │ 상충되는 파라미터       │ BLOCKED + 충돌 상세 반환                    │  │
│ │ 범위 초과 값            │ BLOCKED + 허용 범위 안내                    │  │
│ └─────────────────────────┴─────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.3 Research Agent: Data QA

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AGENT: DATA QA                                                              │
│  Role: 백테스트용 데이터 품질 검증                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PURPOSE                                                                    │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • 데이터 무결성 검사 (결측, 이상치, 중복)                                   │
│  • Survivorship bias 경고                                                   │
│  • Look-ahead bias 방지 확인                                                │
│  • 데이터 충분성 검증 (최소 기간, 레짐 다양성)                               │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ INPUT SCHEMA                                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ {                                                                           │
│   "strategy_id": "STRAT-a3f8c2d1",                                          │
│   "frozen_definition": { ... },                                             │
│   "data_request": {                                                         │
│     "asset": "BTC/USDT",                                                    │
│     "exchange": "binance",                                                  │
│     "timeframe": "1h",                                                      │
│     "start_date": "2020-01-01",                                             │
│     "end_date": "2025-12-22"                                                │
│   }                                                                         │
│ }                                                                           │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ OUTPUT SCHEMA                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ {                                                                           │
│   "strategy_id": "STRAT-a3f8c2d1",                                          │
│   "qa_status": "PASSED" | "FAILED" | "WARNING",                             │
│                                                                             │
│   "data_summary": {                                                         │
│     "total_rows": 43800,                                                    │
│     "date_range": ["2020-01-01", "2025-12-22"],                             │
│     "trading_days": 2175                                                    │
│   },                                                                        │
│                                                                             │
│   "integrity_checks": {                                                     │
│     "missing_values": {                                                     │
│       "count": 12,                                                          │
│       "percentage": 0.027,                                                  │
│       "locations": ["2021-03-15 02:00", ...],                               │
│       "status": "PASSED"  // < 1% threshold                                 │
│     },                                                                      │
│     "outliers": {                                                           │
│       "method": "IQR_3x",                                                   │
│       "count": 45,                                                          │
│       "percentage": 0.103,                                                  │
│       "status": "PASSED"                                                    │
│     },                                                                      │
│     "duplicates": {                                                         │
│       "count": 0,                                                           │
│       "status": "PASSED"                                                    │
│     },                                                                      │
│     "timestamp_continuity": {                                               │
│       "gaps_detected": 3,                                                   │
│       "max_gap_hours": 4,                                                   │
│       "status": "PASSED"  // < 24h threshold                                │
│     }                                                                       │
│   },                                                                        │
│                                                                             │
│   "bias_checks": {                                                          │
│     "survivorship_bias": {                                                  │
│       "risk": "LOW",                                                        │
│       "note": "단일 자산 분석, 해당 없음"                                    │
│     },                                                                      │
│     "look_ahead_bias": {                                                    │
│       "risk": "NONE",                                                       │
│       "note": "시그널이 현재 바 close 이후 계산됨 확인"                       │
│     }                                                                       │
│   },                                                                        │
│                                                                             │
│   "sufficiency_checks": {                                                   │
│     "min_period": {                                                         │
│       "required_days": 365,                                                 │
│       "actual_days": 2175,                                                  │
│       "status": "PASSED"                                                    │
│     },                                                                      │
│     "regime_coverage": {                                                    │
│       "bull_periods": 8,                                                    │
│       "bear_periods": 5,                                                    │
│       "sideways_periods": 12,                                               │
│       "status": "PASSED"                                                    │
│     },                                                                      │
│     "volatility_regimes": {                                                 │
│       "low_vol_days": 890,                                                  │
│       "normal_vol_days": 985,                                               │
│       "high_vol_days": 300,                                                 │
│       "status": "PASSED"                                                    │
│     }                                                                       │
│   },                                                                        │
│                                                                             │
│   "warnings": [                                                             │
│     "2020-03-12~13: COVID crash 기간 변동성 극단치"                          │
│   ],                                                                        │
│                                                                             │
│   "data_path": "/cache/btc_usdt_1h_20200101_20251222.parquet",              │
│                                                                             │
│   "next_agent": "BACKTEST"                                                  │
│ }                                                                           │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ FAILURE CONDITIONS                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ┌─────────────────────────┬─────────────────────────────────────────────┐  │
│ │ Failure                 │ Action                                      │  │
│ ├─────────────────────────┼─────────────────────────────────────────────┤  │
│ │ 결측 > 5%               │ FAILED + 데이터 재수집 권고                 │  │
│ │ Gap > 24h               │ FAILED + 해당 기간 확인 필요                │  │
│ │ 데이터 < 1년            │ FAILED + 최소 기간 미달                     │  │
│ │ 레짐 다양성 부족        │ WARNING + 특정 레짐 테스트 불가 명시        │  │
│ │ Look-ahead 감지         │ FAILED + 시그널 로직 수정 필요              │  │
│ └─────────────────────────┴─────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.4 Validation Agent: Backtest

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AGENT: BACKTEST                                                             │
│  Role: 상태머신 기반 역사적 시뮬레이션                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PURPOSE                                                                    │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • 정의된 전략을 과거 데이터에서 시뮬레이션                                  │
│  • 이상적 체결 가정 (비용/슬리피지 제외)                                     │
│  • 핵심 성과 지표 산출                                                       │
│  • 레짐별 성과 분해                                                          │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ INPUT SCHEMA                                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ {                                                                           │
│   "strategy_id": "STRAT-a3f8c2d1",                                          │
│   "frozen_definition": { ... },                                             │
│   "data_path": "/cache/btc_usdt_1h_20200101_20251222.parquet",              │
│   "backtest_config": {                                                      │
│     "initial_capital": 10000,                                               │
│     "fee_rate": 0.0,           // 비용 에이전트에서 처리                     │
│     "slippage_rate": 0.0,      // 비용 에이전트에서 처리                     │
│     "margin_enabled": false                                                 │
│   }                                                                         │
│ }                                                                           │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ OUTPUT SCHEMA                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ {                                                                           │
│   "backtest_id": "BT-20251223-001",                                         │
│   "strategy_id": "STRAT-a3f8c2d1",                                          │
│   "status": "COMPLETED",                                                    │
│                                                                             │
│   "summary_metrics": {                                                      │
│     "total_return": 0.847,           // 84.7%                               │
│     "cagr": 0.142,                   // 14.2% CAGR                          │
│     "sharpe_ratio": 1.23,                                                   │
│     "sortino_ratio": 1.67,                                                  │
│     "calmar_ratio": 0.89,                                                   │
│     "max_drawdown": -0.158,          // -15.8%                              │
│     "max_drawdown_duration_days": 87,                                       │
│     "win_rate": 0.52,                                                       │
│     "profit_factor": 1.45,                                                  │
│     "avg_trade_return": 0.008,                                              │
│     "total_trades": 312,                                                    │
│     "avg_holding_hours": 42.5                                               │
│   },                                                                        │
│                                                                             │
│   "regime_breakdown": {                                                     │
│     "BULL": {                                                               │
│       "trade_count": 145,                                                   │
│       "total_return": 0.62,                                                 │
│       "sharpe_ratio": 1.89,                                                 │
│       "win_rate": 0.61                                                      │
│     },                                                                      │
│     "BEAR": {                                                               │
│       "trade_count": 82,                                                    │
│       "total_return": 0.15,                                                 │
│       "sharpe_ratio": 0.45,                                                 │
│       "win_rate": 0.38                                                      │
│     },                                                                      │
│     "SIDEWAYS": {                                                           │
│       "trade_count": 85,                                                    │
│       "total_return": 0.07,                                                 │
│       "sharpe_ratio": 0.67,                                                 │
│       "win_rate": 0.48                                                      │
│     }                                                                       │
│   },                                                                        │
│                                                                             │
│   "monthly_returns": {                                                      │
│     "2020-01": 0.023, "2020-02": -0.015, ...                                │
│   },                                                                        │
│                                                                             │
│   "trade_log_path": "/cache/bt_trades_STRAT-a3f8c2d1.parquet",              │
│   "equity_curve_path": "/cache/bt_equity_STRAT-a3f8c2d1.parquet",           │
│                                                                             │
│   "next_agent": "COST_SLIPPAGE"                                             │
│ }                                                                           │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ STATE MACHINE (Core Algorithm)                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                    ┌─────────────────┐                                      │
│                    │                 │                                      │
│                    │      IDLE       │◄────────────────────┐               │
│                    │                 │                     │               │
│                    └────────┬────────┘                     │               │
│                             │                              │               │
│                     entry_signal                      exit_signal          │
│                             │                         stop_hit             │
│                             │                         tp_hit               │
│                             │                         timeout              │
│                             ▼                              │               │
│                    ┌─────────────────┐                     │               │
│                    │                 │                     │               │
│                    │    ENTERING     │                     │               │
│                    │                 │                     │               │
│                    └────────┬────────┘                     │               │
│                             │                              │               │
│                       fill_confirmed                       │               │
│                             │                              │               │
│                             ▼                              │               │
│                    ┌─────────────────┐                     │               │
│                    │                 │                     │               │
│                    │   IN_POSITION   │─────────────────────┘               │
│                    │                 │                                      │
│                    └────────┬────────┘                                      │
│                             │                                               │
│                       exit_trigger                                          │
│                             │                                               │
│                             ▼                                               │
│                    ┌─────────────────┐                                      │
│                    │                 │                                      │
│                    │    EXITING      │─────────────► back to IDLE           │
│                    │                 │                                      │
│                    └─────────────────┘                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.5 Validation Agent: Cost/Slippage

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AGENT: COST/SLIPPAGE                                                        │
│  Role: 레짐별 거래 비용 추정 및 순수익 조정                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PURPOSE                                                                    │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • 거래소 수수료 적용                                                        │
│  • 레짐별 슬리피지 모델링 (NORMAL/VOLATILE/ILLIQUID/EVENT)                  │
│  • 백테스트 순수익 재계산                                                    │
│  • 비용 민감도 분석                                                          │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ INPUT SCHEMA                                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ {                                                                           │
│   "backtest_id": "BT-20251223-001",                                         │
│   "strategy_id": "STRAT-a3f8c2d1",                                          │
│   "trade_log_path": "/cache/bt_trades_STRAT-a3f8c2d1.parquet",              │
│   "cost_config": {                                                          │
│     "exchange": "binance",                                                  │
│     "fee_tier": "VIP0",                                                     │
│     "maker_fee_bps": 10,                                                    │
│     "taker_fee_bps": 10                                                     │
│   }                                                                         │
│ }                                                                           │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ REGIME-BASED SLIPPAGE MODEL                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │                                                                         │ │
│ │  REGIME          │ Base Slip (bps) │ Multiplier │ Conditions           │ │
│ │  ────────────────┼─────────────────┼────────────┼──────────────────────│ │
│ │  NORMAL          │ 2               │ 1.0        │ Vol < 2σ, Sprd ≤ X   │ │
│ │  VOLATILE        │ 5               │ 2.0        │ Vol > 2σ             │ │
│ │  ILLIQUID        │ 10              │ 3.0        │ Spread > 3X avg      │ │
│ │  EVENT           │ 15              │ 4.0        │ News/Macro window    │ │
│ │                                                                         │ │
│ │  Slippage = Base × Multiplier × √(OrderSize / ADV)                     │ │
│ │                                                                         │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ OUTPUT SCHEMA                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ {                                                                           │
│   "cost_slip_id": "CS-20251223-001",                                        │
│   "backtest_id": "BT-20251223-001",                                         │
│                                                                             │
│   "cost_summary": {                                                         │
│     "total_fees_paid": 312.50,                                              │
│     "total_slippage": 487.30,                                               │
│     "total_cost": 799.80,                                                   │
│     "cost_as_pct_of_gross_pnl": 0.094                                       │
│   },                                                                        │
│                                                                             │
│   "adjusted_metrics": {                                                     │
│     "gross_return": 0.847,                                                  │
│     "net_return": 0.767,                                                    │
│     "gross_sharpe": 1.23,                                                   │
│     "net_sharpe": 1.11,                                                     │
│     "return_degradation_pct": 9.4                                           │
│   },                                                                        │
│                                                                             │
│   "regime_cost_breakdown": {                                                │
│     "NORMAL": { "trades": 180, "avg_slip_bps": 3.2, "total_cost": 324 },   │
│     "VOLATILE": { "trades": 85, "avg_slip_bps": 8.7, "total_cost": 312 },  │
│     "ILLIQUID": { "trades": 32, "avg_slip_bps": 18.4, "total_cost": 142 }, │
│     "EVENT": { "trades": 15, "avg_slip_bps": 28.1, "total_cost": 21 }      │
│   },                                                                        │
│                                                                             │
│   "sensitivity_analysis": {                                                 │
│     "if_slip_2x": { "net_return": 0.687, "net_sharpe": 0.99 },             │
│     "if_slip_0.5x": { "net_return": 0.807, "net_sharpe": 1.17 }            │
│   },                                                                        │
│                                                                             │
│   "adjusted_trade_log_path": "/cache/bt_trades_adj_STRAT-a3f8c2d1.parquet",│
│                                                                             │
│   "next_agent": "EXECUTION_SIM"                                             │
│ }                                                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.6 Validation Agent: Execution Simulator

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AGENT: EXECUTION SIMULATOR                                                  │
│  Role: 다양한 체결 정책 시뮬레이션 및 비교                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EXECUTION POLICIES                                                         │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│ ┌────────────────────────────────────────────────────────────────────────┐  │
│ │                                                                        │  │
│ │ 1. MARKET_IMMEDIATE                                                    │  │
│ │    ├─ 즉시 시장가 체결                                                  │  │
│ │    ├─ 슬리피지 전액 수용                                                │  │
│ │    ├─ 체결률: 100%                                                     │  │
│ │    └─ 용도: 긴급 청산, 리스크 컷                                        │  │
│ │                                                                        │  │
│ │ 2. LIMIT_PASSIVE                                                       │  │
│ │    ├─ 지정가를 best bid/ask에 게시                                      │  │
│ │    ├─ timeout 대기 → 미체결 시 취소                                     │  │
│ │    ├─ 체결률: 60-80% (시장 상황 의존)                                   │  │
│ │    └─ 용도: 비용 최소화, 급하지 않은 진입                                │  │
│ │                                                                        │  │
│ │ 3. LIMIT_TO_MARKET                                                     │  │
│ │    ├─ 지정가로 시도 → timeout 후 시장가 전환                            │  │
│ │    ├─ 체결률: 100% (시장가 전환 포함)                                   │  │
│ │    ├─ 평균 슬리피지: LIMIT과 MARKET 사이                                │  │
│ │    └─ 용도: 체결 보장 + 비용 절감 시도                                   │  │
│ │                                                                        │  │
│ │ 4. TWAP (Time-Weighted Average Price)                                  │  │
│ │    ├─ 분할 체결 (N개 슬라이스)                                          │  │
│ │    ├─ 각 슬라이스: 시장가 또는 지정가                                    │  │
│ │    ├─ 시장 충격 분산                                                    │  │
│ │    └─ 용도: 대량 주문                                                   │  │
│ │                                                                        │  │
│ │ 5. VWAP (Volume-Weighted Average Price)                                │  │
│ │    ├─ 거래량 프로파일에 맞춰 분할                                        │  │
│ │    ├─ 유동성 높은 시간대에 더 많이 체결                                  │  │
│ │    └─ 용도: 벤치마크 대비 최적화                                         │  │
│ │                                                                        │  │
│ │ 6. ADAPTIVE                                                            │  │
│ │    ├─ 스프레드/유동성에 따라 동적 정책 선택                              │  │
│ │    ├─ tight spread → LIMIT_PASSIVE                                     │  │
│ │    ├─ wide spread → MARKET_IMMEDIATE                                   │  │
│ │    └─ 용도: 상황 적응형                                                 │  │
│ │                                                                        │  │
│ └────────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ OUTPUT SCHEMA                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ {                                                                           │
│   "execution_sim_id": "EXEC-20251223-001",                                  │
│   "backtest_id": "BT-20251223-001",                                         │
│                                                                             │
│   "policies_tested": [                                                      │
│     {                                                                       │
│       "policy": "MARKET_IMMEDIATE",                                         │
│       "metrics": {                                                          │
│         "fill_rate": 1.00,                                                  │
│         "avg_slippage_bps": 12.5,                                           │
│         "p95_slippage_bps": 45.2,                                           │
│         "avg_entry_delay_sec": 0.5,                                         │
│         "net_return": 0.72                                                  │
│       }                                                                     │
│     },                                                                      │
│     {                                                                       │
│       "policy": "LIMIT_TO_MARKET",                                          │
│       "metrics": {                                                          │
│         "fill_rate": 1.00,                                                  │
│         "avg_slippage_bps": 5.8,                                            │
│         "p95_slippage_bps": 28.1,                                           │
│         "avg_entry_delay_sec": 15.2,                                        │
│         "net_return": 0.77                                                  │
│       }                                                                     │
│     }                                                                       │
│   ],                                                                        │
│                                                                             │
│   "recommended_policy": "LIMIT_TO_MARKET",                                  │
│   "recommendation_reason": "체결률 100% 유지, 슬리피지 54% 감소",            │
│                                                                             │
│   "next_agent": "RISK_STRESS"                                               │
│ }                                                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.7 Validation Agent: Risk/Stress

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AGENT: RISK/STRESS                                                          │
│  Role: 위기 시나리오 시뮬레이션 및 극단 리스크 평가                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STRESS SCENARIOS                                                           │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │                                                                         │ │
│ │  Historical Stress Events (재현)                                        │ │
│ │  ─────────────────────────────────────────────────────────────────────  │ │
│ │  • COVID Crash (2020-03-12~13): -50% in 48h                             │ │
│ │  • LUNA Collapse (2022-05-09~12): -99%                                  │ │
│ │  • FTX Collapse (2022-11-08~10): -25%                                   │ │
│ │  • Flash Crash scenarios                                                │ │
│ │                                                                         │ │
│ │  Synthetic Stress Scenarios                                              │ │
│ │  ─────────────────────────────────────────────────────────────────────  │ │
│ │  • Volatility Spike: Vol → 5σ                                           │ │
│ │  • Liquidity Dry-up: Spread → 10x, Depth → 0.1x                         │ │
│ │  • Correlation Breakdown: All assets → ρ = 0.9                          │ │
│ │  • Gap Open: -15% overnight gap                                         │ │
│ │                                                                         │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ OUTPUT SCHEMA                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ {                                                                           │
│   "risk_stress_id": "RS-20251223-001",                                      │
│   "strategy_id": "STRAT-a3f8c2d1",                                          │
│                                                                             │
│   "var_analysis": {                                                         │
│     "var_95_daily": -0.023,        // -2.3% daily                          │
│     "var_99_daily": -0.041,        // -4.1% daily                          │
│     "cvar_95_daily": -0.035,       // -3.5% expected tail loss             │
│     "method": "HISTORICAL_SIMULATION"                                       │
│   },                                                                        │
│                                                                             │
│   "stress_results": {                                                       │
│     "COVID_CRASH": {                                                        │
│       "scenario_return": -0.28,                                             │
│       "max_intra_scenario_dd": -0.35,                                       │
│       "recovery_days": null,       // 시나리오 기간 내 미회복               │
│       "stop_loss_triggered": true,                                          │
│       "position_at_end": 0         // 청산됨                                │
│     },                                                                      │
│     "LUNA_COLLAPSE": {                                                      │
│       "scenario_return": -0.12,                                             │
│       "max_intra_scenario_dd": -0.18,                                       │
│       "recovery_days": 45,                                                  │
│       "stop_loss_triggered": true,                                          │
│       "position_at_end": 0.5                                                │
│     },                                                                      │
│     "VOL_SPIKE_5SIGMA": {                                                   │
│       "scenario_return": -0.08,                                             │
│       "max_intra_scenario_dd": -0.12,                                       │
│       "recovery_days": 12,                                                  │
│       "stop_loss_triggered": false,                                         │
│       "position_at_end": 1.0                                                │
│     }                                                                       │
│   },                                                                        │
│                                                                             │
│   "tail_risk_metrics": {                                                    │
│     "worst_day": -0.087,                                                    │
│     "worst_week": -0.142,                                                   │
│     "worst_month": -0.203,                                                  │
│     "max_consecutive_loss_days": 18,                                        │
│     "ulcer_index": 5.2                                                      │
│   },                                                                        │
│                                                                             │
│   "risk_rating": "MODERATE",       // LOW / MODERATE / HIGH / EXTREME       │
│   "risk_notes": [                                                           │
│     "COVID 시나리오에서 급격한 손실 발생",                                   │
│     "스탑로스가 급락 시 효과적으로 작동"                                     │
│   ],                                                                        │
│                                                                             │
│   "next_agent": "OVERFIT_AUDIT"                                             │
│ }                                                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.8 Validation Agent: Overfit Audit

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AGENT: OVERFIT AUDIT                                                        │
│  Role: 과최적화 탐지 및 일반화 가능성 평가                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  METHODOLOGY                                                                │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  1. Walk-Forward Analysis                                                   │
│     ┌────────────────────────────────────────────────────────────────────┐  │
│     │                                                                    │  │
│     │  [====TRAIN====][=TEST=]                                          │  │
│     │       [====TRAIN====][=TEST=]                                     │  │
│     │            [====TRAIN====][=TEST=]                                │  │
│     │                 [====TRAIN====][=TEST=]                           │  │
│     │                                                                    │  │
│     │  Train:Test Ratio = 4:1 (권장)                                    │  │
│     │  Fold 개수: 최소 5개                                               │  │
│     │                                                                    │  │
│     └────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  2. Deflated Sharpe Ratio                                                   │
│     ┌────────────────────────────────────────────────────────────────────┐  │
│     │                                                                    │  │
│     │  Multiple testing 보정                                             │  │
│     │                                                                    │  │
│     │  DSR = SR × √(1 - γ × Trials)                                     │  │
│     │                                                                    │  │
│     │  Trials = 테스트한 파라미터 조합 수                                 │  │
│     │  γ = 보정 계수 (보수적: 0.01)                                      │  │
│     │                                                                    │  │
│     │  예: SR=1.5, Trials=100                                           │  │
│     │  DSR = 1.5 × √(1 - 0.01 × 100) = 1.5 × 0 = 0                      │  │
│     │  → 무효화됨 (과최적화)                                              │  │
│     │                                                                    │  │
│     └────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  3. Randomization Test                                                      │
│     ┌────────────────────────────────────────────────────────────────────┐  │
│     │                                                                    │  │
│     │  시그널 랜덤 셔플 후 성과 비교                                      │  │
│     │                                                                    │  │
│     │  H0: 전략 성과 = 랜덤 성과                                         │  │
│     │  p-value < 0.05 → 전략이 유의미                                    │  │
│     │                                                                    │  │
│     └────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ OUTPUT SCHEMA                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ {                                                                           │
│   "overfit_audit_id": "OA-20251223-001",                                    │
│   "strategy_id": "STRAT-a3f8c2d1",                                          │
│                                                                             │
│   "walk_forward_results": {                                                 │
│     "folds": 5,                                                             │
│     "train_test_ratio": "4:1",                                              │
│     "fold_results": [                                                       │
│       {"fold": 1, "train_sharpe": 1.42, "test_sharpe": 1.18},              │
│       {"fold": 2, "train_sharpe": 1.38, "test_sharpe": 0.95},              │
│       {"fold": 3, "train_sharpe": 1.55, "test_sharpe": 1.22},              │
│       {"fold": 4, "train_sharpe": 1.29, "test_sharpe": 0.88},              │
│       {"fold": 5, "train_sharpe": 1.47, "test_sharpe": 1.05}               │
│     ],                                                                      │
│     "avg_train_sharpe": 1.42,                                               │
│     "avg_test_sharpe": 1.06,                                                │
│     "degradation_ratio": 0.25,     // 25% 성능 저하                         │
│     "status": "ACCEPTABLE"         // < 50% 저하                            │
│   },                                                                        │
│                                                                             │
│   "deflated_sharpe": {                                                      │
│     "original_sharpe": 1.23,                                                │
│     "trials_count": 15,            // 테스트한 파라미터 조합                 │
│     "deflated_sharpe": 1.08,                                                │
│     "status": "VALID"              // DSR > 0.5                             │
│   },                                                                        │
│                                                                             │
│   "randomization_test": {                                                   │
│     "n_permutations": 1000,                                                 │
│     "strategy_sharpe": 1.23,                                                │
│     "random_sharpe_mean": 0.02,                                             │
│     "random_sharpe_std": 0.31,                                              │
│     "p_value": 0.001,                                                       │
│     "status": "SIGNIFICANT"        // p < 0.05                              │
│   },                                                                        │
│                                                                             │
│   "overfit_score": 2.1,            // 1-10, 낮을수록 좋음                    │
│   "overfit_rating": "LOW",         // LOW / MEDIUM / HIGH                   │
│                                                                             │
│   "next_agent": "PORTFOLIO_CAPACITY"                                        │
│ }                                                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.9 Validation Agent: Portfolio/Capacity

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AGENT: PORTFOLIO/CAPACITY                                                   │
│  Role: 포트폴리오 통합 및 용량 제한 평가                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CAPACITY ESTIMATION                                                        │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │                                                                         │ │
│ │ Capacity = f(ADV, Impact_sensitivity, Frequency)                        │ │
│ │                                                                         │ │
│ │ 예시:                                                                   │ │
│ │ - 일평균 거래량(ADV): $10M                                              │ │
│ │ - 참여율 제한: 1% of ADV                                                │ │
│ │ - 일 거래 빈도: 2회                                                      │ │
│ │ → Capacity ≈ $50K per trade                                             │ │
│ │                                                                         │ │
│ │ 용량 초과 시: 전략 수익 감소 경고 또는 분할 실행 강제                     │ │
│ │                                                                         │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  CORRELATION-BASED STRESS EXPOSURE                                          │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │                                                                         │ │
│ │ 위기 시 상관 상승 가정:                                                  │ │
│ │ - Normal: ρ_ij (역사적 상관)                                            │ │
│ │ - Stress: ρ_stress = min(ρ_ij + 0.3, 1.0)                               │ │
│ │                                                                         │ │
│ │ Stress Exposure = √(w'Σ_stress w)                                       │ │
│ │                                                                         │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ OUTPUT SCHEMA                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ {                                                                           │
│   "portfolio_cap_id": "PC-20251223-001",                                    │
│   "strategy_id": "STRAT-a3f8c2d1",                                          │
│                                                                             │
│   "capacity_analysis": {                                                    │
│     "asset": "BTC/USDT",                                                    │
│     "avg_daily_volume_usd": 15000000000,                                    │
│     "max_participation_rate": 0.01,                                         │
│     "estimated_capacity_usd": 150000,                                       │
│     "trades_per_day": 0.15,                                                 │
│     "capacity_per_trade_usd": 1000000                                       │
│   },                                                                        │
│                                                                             │
│   "portfolio_fit": {                                                        │
│     "existing_strategies": 3,                                               │
│     "correlation_with_existing": {                                          │
│       "STRAT-b2e7a1c9": 0.42,                                               │
│       "STRAT-d4f9c3e5": -0.15,                                              │
│       "STRAT-e6a8b2d7": 0.28                                                │
│     },                                                                      │
│     "marginal_sharpe_contribution": 0.18,                                   │
│     "diversification_benefit": "MODERATE"                                   │
│   },                                                                        │
│                                                                             │
│   "stress_portfolio_metrics": {                                             │
│     "normal_portfolio_vol": 0.12,                                           │
│     "stress_portfolio_vol": 0.24,                                           │
│     "stress_max_dd": -0.32                                                  │
│   },                                                                        │
│                                                                             │
│   "allocation_recommendation": {                                            │
│     "max_allocation_pct": 0.15,    // 전체 자본의 15%                        │
│     "reason": "중간 상관, 적정 용량"                                         │
│   },                                                                        │
│                                                                             │
│   "next_agent": "ORCHESTRATOR"                                              │
│ }                                                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.10 Core Agent: Orchestrator

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AGENT: ORCHESTRATOR                                                         │
│  Role: 최종 의사결정 - Hard Gates + Soft Scoring                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DECISION FRAMEWORK                                                         │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  Phase 1: HARD GATES (Must Pass ALL)                                        │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  ┌──────────────────────┬───────────────┬────────────────────────┐   │ │
│  │  │ Gate                 │ Threshold     │ Source                 │   │ │
│  │  ├──────────────────────┼───────────────┼────────────────────────┤   │ │
│  │  │ Fill Rate            │ ≥ 95%         │ EXECUTION_SIM          │   │ │
│  │  │ Max Slippage         │ ≤ 50 bps      │ COST_SLIPPAGE          │   │ │
│  │  │ Max Drawdown         │ ≤ 15%         │ BACKTEST               │   │ │
│  │  │ Max Loss Streak      │ ≤ 30 days     │ BACKTEST               │   │ │
│  │  │ Tail Loss (p99)      │ ≤ 10%         │ RISK_STRESS            │   │ │
│  │  │ Overfit Score        │ ≤ 5.0         │ OVERFIT_AUDIT          │   │ │
│  │  │ Data QA              │ PASSED        │ DATA_QA                │   │ │
│  │  └──────────────────────┴───────────────┴────────────────────────┘   │ │
│  │                                                                        │ │
│  │  ANY gate fail → REJECT                                               │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Phase 2: SOFT SCORING (Weighted Sum)                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  ┌──────────────────────┬────────┬────────────────────────────────┐  │ │
│  │  │ Criterion            │ Weight │ Scoring Method                 │  │ │
│  │  ├──────────────────────┼────────┼────────────────────────────────┤  │ │
│  │  │ Risk-Adjusted Return │ 0.30   │ Sharpe/Sortino 순위            │  │ │
│  │  │ Tail Stability       │ 0.25   │ CVaR, Ulcer Index 역순위       │  │ │
│  │  │ Regime Diversity     │ 0.20   │ 레짐별 성과 균형도             │  │ │
│  │  │ Correlation          │ 0.15   │ 기존 전략과 낮은 상관          │  │ │
│  │  │ Complexity           │ 0.10   │ 파라미터 수 적을수록 높음      │  │ │
│  │  └──────────────────────┴────────┴────────────────────────────────┘  │ │
│  │                                                                        │ │
│  │  Final Score = Σ(Weight_i × Normalized_Score_i)                       │ │
│  │                                                                        │ │
│  │  Score ≥ 0.6 → APPROVE                                                │ │
│  │  Score ∈ [0.4, 0.6) → HOLD (추가 검토)                                │ │
│  │  Score < 0.4 → REJECT                                                 │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ OUTPUT SCHEMA                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ {                                                                           │
│   "decision_id": "DEC-20251223-001",                                        │
│   "strategy_id": "STRAT-a3f8c2d1",                                          │
│   "timestamp": "2025-12-23T14:30:00Z",                                      │
│                                                                             │
│   "hard_gate_results": {                                                    │
│     "fill_rate": {"value": 1.00, "threshold": 0.95, "passed": true},       │
│     "slippage": {"value": 5.8, "threshold": 50, "passed": true},           │
│     "max_dd": {"value": 0.158, "threshold": 0.15, "passed": false},        │
│     "loss_streak": {"value": 18, "threshold": 30, "passed": true},         │
│     "tail_loss": {"value": 0.087, "threshold": 0.10, "passed": true},      │
│     "overfit_score": {"value": 2.1, "threshold": 5.0, "passed": true},     │
│     "data_qa": {"status": "PASSED", "passed": true}                        │
│   },                                                                        │
│   "hard_gate_passed": false,                                                │
│   "failed_gates": ["max_dd"],                                               │
│                                                                             │
│   "soft_scores": null,             // Hard gate 실패 시 계산 안함           │
│                                                                             │
│   "decision": "REJECT",                                                     │
│   "decision_reason": "max_dd 15.8% > 15% threshold",                        │
│                                                                             │
│   "recommendations": [                                                      │
│     "스탑로스를 1.5%로 타이트하게 조정 고려",                               │
│     "포지션 사이즈를 8%로 축소 검토"                                         │
│   ],                                                                        │
│                                                                             │
│   "human_override_required": false,                                         │
│   "deployment_stage": null                                                  │
│ }                                                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 다음 파일: 03-data-models.md

데이터 모델, DB 스키마, 상태 전이
