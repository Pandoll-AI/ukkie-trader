# Ukkie-Trader 개발 계획서 Part 6: 배포, 테스트, 로드맵

---

## 7. 외부 인터페이스

### 7.1 거래소 연동

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  EXCHANGE INTEGRATION ARCHITECTURE                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         EXCHANGE ADAPTER                             │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │ Abstract Interface                                           │    │   │
│  │  │                                                              │    │   │
│  │  │ • fetch_ohlcv(symbol, timeframe, since, limit)              │    │   │
│  │  │ • fetch_ticker(symbol)                                       │    │   │
│  │  │ • fetch_order_book(symbol, limit)                           │    │   │
│  │  │ • create_order(symbol, type, side, amount, price)           │    │   │
│  │  │ • cancel_order(order_id, symbol)                            │    │   │
│  │  │ • fetch_order(order_id, symbol)                             │    │   │
│  │  │ • fetch_balance()                                            │    │   │
│  │  │ • watch_trades(symbol, callback)                            │    │   │
│  │  │ • watch_order_book(symbol, callback)                        │    │   │
│  │  │                                                              │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                              │                                       │   │
│  │              ┌───────────────┼───────────────┐                      │   │
│  │              ▼               ▼               ▼                      │   │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐       │   │
│  │  │ BinanceAdapter  │ │   OKXAdapter    │ │  MockAdapter    │       │   │
│  │  │                 │ │                 │ │ (Testing)       │       │   │
│  │  │ • CCXT wrapper  │ │ • CCXT wrapper  │ │ • Simulated     │       │   │
│  │  │ • Rate limiting │ │ • Rate limiting │ │ • Deterministic │       │   │
│  │  │ • Error retry   │ │ • Error retry   │ │                 │       │   │
│  │  └─────────────────┘ └─────────────────┘ └─────────────────┘       │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Data Providers:                                                            │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  ├── BinanceDataProvider                                                    │
│  ├── OKXDataProvider                                                        │
│  ├── CSVFileProvider (백테스트용 로컬 파일)                                  │
│  └── MockDataProvider (테스트용)                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 설정 파일 형식

```yaml
# ~/.config/ukkie-trader/config.yaml

general:
  db_path: ~/.ukkie-trader/ukkie.db
  log_level: INFO
  timezone: UTC

data:
  primary_provider: binance
  fallback_provider: csv
  cache_dir: ~/.ukkie-trader/cache
  max_cache_age_hours: 24

providers:
  binance:
    api_key: ${BINANCE_API_KEY}
    api_secret: ${BINANCE_API_SECRET}
    testnet: false
  
  okx:
    api_key: ${OKX_API_KEY}
    passphrase: ${OKX_PASSPHRASE}
    
  csv:
    data_dir: ~/trading-data

policy:
  # Hard Gates
  min_fill_rate: 0.95
  max_slippage_bps: 50
  max_mdd: 0.15
  max_loss_streak_days: 30
  max_tail_loss: 0.10
  
  # Soft Scoring Weights
  soft_weights:
    risk_return: 0.3
    tail_stability: 0.25
    regime_diversity: 0.2
    correlation: 0.15
    complexity: 0.1
  
  hold_threshold: 0.5

deployment:
  default_stage: SHADOW
  prod_requires_human_approval: true
  initial_capacity_multiplier: 0.3
  
  kill_switch:
    mdd_trigger: 0.10
    consecutive_loss_trigger: 5
    data_delay_seconds: 300
    spread_multiplier_trigger: 3.0

monitoring:
  refresh_interval_seconds: 60
  alert_channels:
    - type: console
    - type: slack
      webhook_url: ${SLACK_WEBHOOK_URL}
```

---

## 8. 배포 및 패키징

### 8.1 pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "ukkie-trader"
version = "0.1.0"
description = "AI Trading Bot - Trade like a deliberate orangutan"
readme = "README.md"
license = "MIT"
requires-python = ">=3.11"
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
keywords = ["trading", "crypto", "ai", "backtesting", "automation"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Financial and Insurance Industry",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Office/Business :: Financial :: Investment",
]

dependencies = [
    # Core
    "typer>=0.9.0",
    "rich>=13.0.0",
    "textual>=0.40.0",
    "pydantic>=2.0.0",
    
    # Data Processing
    "polars>=0.19.0",
    "numpy>=1.24.0",
    "scipy>=1.11.0",
    "pyarrow>=13.0.0",
    
    # Exchange Integration
    "ccxt>=4.0.0",
    "aiohttp>=3.8.0",
    "websockets>=11.0",
    
    # Configuration
    "pyyaml>=6.0",
    "python-dotenv>=1.0.0",
    
    # Logging
    "structlog>=23.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "hypothesis>=6.80.0",
    "mypy>=1.5.0",
    "ruff>=0.1.0",
    "pre-commit>=3.4.0",
]

docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
    "mkdocstrings[python]>=0.23.0",
]

[project.scripts]
ukkie-trader = "ukkie_trader.cli.app:main"

[project.urls]
Homepage = "https://github.com/yourname/ukkie-trader"
Documentation = "https://ukkie-trader.readthedocs.io"
Repository = "https://github.com/yourname/ukkie-trader"
Issues = "https://github.com/yourname/ukkie-trader/issues"

[tool.hatch.build.targets.wheel]
packages = ["src/ukkie_trader"]

[tool.ruff]
target-version = "py311"
line-length = 88
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by formatter)
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.isort]
known-first-party = ["ukkie_trader"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-v --cov=ukkie_trader --cov-report=term-missing"

[tool.coverage.run]
source = ["src/ukkie_trader"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

### 8.2 설치 방법

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  INSTALLATION METHODS                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  METHOD 1: pipx (권장 - 격리된 환경)                                         │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  # pipx 설치 (없는 경우)                                                     │
│  $ pip install pipx                                                         │
│  $ pipx ensurepath                                                          │
│                                                                             │
│  # ukkie-trader 설치                                                        │
│  $ pipx install ukkie-trader                                                │
│                                                                             │
│  # 또는 GitHub에서 직접                                                      │
│  $ pipx install git+https://github.com/yourname/ukkie-trader.git            │
│                                                                             │
│  # 업그레이드                                                                │
│  $ pipx upgrade ukkie-trader                                                │
│                                                                             │
│  METHOD 2: pip (가상환경 내)                                                 │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  $ python -m venv .venv                                                     │
│  $ source .venv/bin/activate                                                │
│  $ pip install ukkie-trader                                                 │
│                                                                             │
│  METHOD 3: 개발 모드                                                         │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  $ git clone https://github.com/yourname/ukkie-trader.git                   │
│  $ cd ukkie-trader                                                          │
│  $ pip install -e ".[dev]"                                                  │
│                                                                             │
│  INITIAL SETUP                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  # 설정 초기화                                                               │
│  $ ukkie-trader config init                                                 │
│                                                                             │
│  # API 키 설정                                                               │
│  $ export BINANCE_API_KEY="your-api-key"                                    │
│  $ export BINANCE_API_SECRET="your-api-secret"                              │
│                                                                             │
│  # 또는 .env 파일                                                            │
│  $ cat > ~/.config/ukkie-trader/.env << EOF                                 │
│  BINANCE_API_KEY=your-api-key                                               │
│  BINANCE_API_SECRET=your-api-secret                                         │
│  EOF                                                                        │
│                                                                             │
│  # 연결 테스트                                                               │
│  $ ukkie-trader status                                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. 테스트 전략

### 9.1 테스트 피라미드

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TESTING PYRAMID                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                           ╱╲                                                │
│                          ╱  ╲                                               │
│                         ╱ E2E╲                                              │
│                        ╱──────╲           ~5%                               │
│                       ╱        ╲                                            │
│                      ╱Integration╲                                          │
│                     ╱────────────╲        ~20%                              │
│                    ╱              ╲                                         │
│                   ╱   Unit Tests   ╲                                        │
│                  ╱──────────────────╲     ~75%                              │
│                 ╱                    ╲                                      │
│                ╱   Property-Based    ╲                                      │
│               ╱──────────────────────╲   (Cross-cutting)                    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  COVERAGE TARGETS                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────────┬──────────┬────────────────────────────────┐    │
│  │ Component              │ Target   │ Critical Paths                 │    │
│  ├────────────────────────┼──────────┼────────────────────────────────┤    │
│  │ Domain Logic           │ 95%+     │ Signal generation, Risk calc   │    │
│  │ Agents                 │ 90%+     │ Orchestrator decisions         │    │
│  │ Backtest Engine        │ 95%+     │ State transitions, PnL calc    │    │
│  │ Exchange Adapters      │ 85%+     │ Order execution, Error handling│    │
│  │ CLI                    │ 70%+     │ Critical commands              │    │
│  │ Infrastructure         │ 80%+     │ DB operations, Config loading  │    │
│  └────────────────────────┴──────────┴────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 테스트 카테고리

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TEST CATEGORIES                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  UNIT TESTS                                                                 │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  tests/unit/                                                                │
│  ├── domain/                                                                │
│  │   ├── test_signal_generator.py                                          │
│  │   ├── test_position_sizing.py                                           │
│  │   ├── test_risk_calculator.py                                           │
│  │   └── test_regime_detector.py                                           │
│  ├── agents/                                                                │
│  │   ├── test_proposer.py                                                  │
│  │   ├── test_freezer.py                                                   │
│  │   ├── test_backtest_agent.py                                            │
│  │   ├── test_cost_slip_agent.py                                           │
│  │   ├── test_overfit_auditor.py                                           │
│  │   └── test_orchestrator.py                                              │
│  └── utils/                                                                 │
│      ├── test_math_helpers.py                                              │
│      └── test_time_helpers.py                                              │
│                                                                             │
│  INTEGRATION TESTS                                                          │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  tests/integration/                                                         │
│  ├── test_validation_pipeline.py    # 에이전트 파이프라인 전체              │
│  ├── test_backtest_to_decision.py   # 백테스트 → 결정 흐름                  │
│  ├── test_exchange_adapter.py       # 거래소 연동 (Testnet)                 │
│  ├── test_data_providers.py         # 데이터 소스 전환                      │
│  └── test_cli_commands.py           # CLI 명령어 통합                       │
│                                                                             │
│  E2E TESTS                                                                  │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  tests/e2e/                                                                 │
│  ├── test_full_workflow.py          # 제안 → 검증 → 배포 전체               │
│  ├── test_paper_trading.py          # Paper 트레이딩 시나리오               │
│  └── test_kill_switch.py            # 긴급 중지 시나리오                    │
│                                                                             │
│  PROPERTY-BASED TESTS (Hypothesis)                                          │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  tests/property/                                                            │
│  ├── test_backtest_invariants.py    # 백테스트 불변 조건                    │
│  │   • equity >= 0 always                                                  │
│  │   • position_size <= max_position                                       │
│  │   • trade_count = entry_count = exit_count                              │
│  ├── test_state_machine.py          # 상태 전이 속성                        │
│  │   • 모든 상태에서 valid 전이만 가능                                      │
│  │   • 순환 없는 종료 보장                                                  │
│  └── test_cost_model.py             # 비용 모델 속성                        │
│      • cost >= 0 always                                                    │
│      • VOLATILE cost > NORMAL cost                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.3 테스트 예시

```python
# tests/unit/agents/test_orchestrator.py

import pytest
from ukkie_trader.agents.orchestrator import Orchestrator
from ukkie_trader.domain.models import (
    HardGateResult,
    DecisionOutcome,
)


class TestOrchestratorHardGates:
    """오케스트레이터 Hard Gate 테스트"""
    
    @pytest.fixture
    def orchestrator(self):
        return Orchestrator()
    
    def test_all_gates_pass(self, orchestrator):
        """모든 게이트 통과 시 APPROVE"""
        gate_results = {
            "fill_rate": HardGateResult(value=0.98, threshold=0.95, passed=True),
            "slippage": HardGateResult(value=30, threshold=50, passed=True),
            "max_dd": HardGateResult(value=0.12, threshold=0.15, passed=True),
            "loss_streak": HardGateResult(value=15, threshold=30, passed=True),
            "tail_loss": HardGateResult(value=0.08, threshold=0.10, passed=True),
        }
        
        result = orchestrator.check_hard_gates(gate_results)
        
        assert result.passed is True
        assert result.failed_gates == []
    
    def test_single_gate_fail_rejects(self, orchestrator):
        """단일 게이트 실패 시 REJECT"""
        gate_results = {
            "fill_rate": HardGateResult(value=0.98, threshold=0.95, passed=True),
            "slippage": HardGateResult(value=30, threshold=50, passed=True),
            "max_dd": HardGateResult(value=0.18, threshold=0.15, passed=False),  # FAIL
            "loss_streak": HardGateResult(value=15, threshold=30, passed=True),
            "tail_loss": HardGateResult(value=0.08, threshold=0.10, passed=True),
        }
        
        result = orchestrator.check_hard_gates(gate_results)
        
        assert result.passed is False
        assert "max_dd" in result.failed_gates
    
    def test_multiple_gates_fail(self, orchestrator):
        """다중 게이트 실패 시 모두 기록"""
        gate_results = {
            "fill_rate": HardGateResult(value=0.90, threshold=0.95, passed=False),
            "slippage": HardGateResult(value=60, threshold=50, passed=False),
            "max_dd": HardGateResult(value=0.12, threshold=0.15, passed=True),
        }
        
        result = orchestrator.check_hard_gates(gate_results)
        
        assert result.passed is False
        assert set(result.failed_gates) == {"fill_rate", "slippage"}


class TestOrchestratorSoftScoring:
    """오케스트레이터 Soft Scoring 테스트"""
    
    @pytest.fixture
    def orchestrator(self):
        return Orchestrator()
    
    def test_high_score_approves(self, orchestrator):
        """높은 점수 시 APPROVE"""
        metrics = {
            "sharpe": 1.5,
            "sortino": 2.0,
            "cvar": -0.03,
            "regime_diversity": 0.8,
            "correlation": 0.2,
            "param_count": 5,
        }
        
        score = orchestrator.calculate_soft_score(metrics)
        decision = orchestrator.score_to_decision(score)
        
        assert score >= 0.6
        assert decision == DecisionOutcome.APPROVE
    
    def test_medium_score_holds(self, orchestrator):
        """중간 점수 시 HOLD"""
        metrics = {
            "sharpe": 0.8,
            "sortino": 1.0,
            "cvar": -0.06,
            "regime_diversity": 0.5,
            "correlation": 0.5,
            "param_count": 12,
        }
        
        score = orchestrator.calculate_soft_score(metrics)
        decision = orchestrator.score_to_decision(score)
        
        assert 0.4 <= score < 0.6
        assert decision == DecisionOutcome.HOLD
    
    def test_low_score_rejects(self, orchestrator):
        """낮은 점수 시 REJECT"""
        metrics = {
            "sharpe": 0.3,
            "sortino": 0.4,
            "cvar": -0.12,
            "regime_diversity": 0.2,
            "correlation": 0.8,
            "param_count": 25,
        }
        
        score = orchestrator.calculate_soft_score(metrics)
        decision = orchestrator.score_to_decision(score)
        
        assert score < 0.4
        assert decision == DecisionOutcome.REJECT


# tests/property/test_backtest_invariants.py

from hypothesis import given, strategies as st, assume
import polars as pl
from ukkie_trader.domain.backtest.engine import BacktestEngine


class TestBacktestInvariants:
    """백테스트 불변 조건 Property 테스트"""
    
    @given(
        initial_capital=st.floats(min_value=100, max_value=1_000_000),
        n_bars=st.integers(min_value=100, max_value=10000),
    )
    def test_equity_never_negative(self, initial_capital, n_bars):
        """자산은 항상 0 이상"""
        # Generate random OHLCV data
        data = self._generate_random_ohlcv(n_bars)
        strategy = self._create_simple_strategy()
        
        engine = BacktestEngine(
            strategy=strategy,
            data=data,
            config={"initial_capital": initial_capital}
        )
        
        result = engine.run_sync()
        
        # Invariant: equity >= 0 always
        assert all(e >= 0 for e in result.equity_curve)
    
    @given(
        position_fraction=st.floats(min_value=0.01, max_value=0.5),
    )
    def test_position_size_within_limits(self, position_fraction):
        """포지션 크기는 제한 내"""
        data = self._generate_random_ohlcv(500)
        strategy = self._create_strategy_with_sizing(position_fraction)
        
        engine = BacktestEngine(strategy=strategy, data=data)
        result = engine.run_sync()
        
        # Invariant: position_size <= max_position
        max_position = position_fraction * result.summary.initial_capital
        for trade in result.trades:
            assert trade.position_size <= max_position * 1.01  # 1% tolerance
    
    @given(st.data())
    def test_entry_exit_count_match(self, data):
        """진입 횟수 = 청산 횟수"""
        n_bars = data.draw(st.integers(min_value=200, max_value=5000))
        ohlcv = self._generate_random_ohlcv(n_bars)
        strategy = self._create_simple_strategy()
        
        engine = BacktestEngine(strategy=strategy, data=ohlcv)
        result = engine.run_sync()
        
        # If not in position at end, counts must match
        if not result.has_open_position:
            entry_count = sum(1 for t in result.trades if t.is_entry)
            exit_count = sum(1 for t in result.trades if t.is_exit)
            assert entry_count == exit_count
```

---

## 10. 개발 로드맵

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DEVELOPMENT ROADMAP                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 1: MVP - 백테스트 파이프라인 (8주)                                    │
│  ═══════════════════════════════════════════════════════════════════════════│
│                                                                             │
│  Week 1-2: Foundation                                                       │
│  ─────────────────────────────────────────────────────────────────────────  │
│  [■] 프로젝트 구조 설정                                                      │
│  [■] pyproject.toml, 의존성                                                  │
│  [■] 기본 CLI 스켈레톤 (Typer)                                               │
│  [■] 로깅/설정 인프라                                                        │
│  [■] SQLite 스키마 & Pydantic 모델                                           │
│                                                                             │
│  Week 3-4: Core Domain                                                      │
│  ─────────────────────────────────────────────────────────────────────────  │
│  [■] 상태머신 백테스트 엔진                                                   │
│  [■] 시그널 생성기 (EMA, RSI, Bollinger)                                     │
│  [■] 레짐 감지기                                                             │
│  [■] 포지션/주문 관리자                                                       │
│  [■] 리스크 계산기                                                           │
│                                                                             │
│  Week 5-6: Research Agents                                                  │
│  ─────────────────────────────────────────────────────────────────────────  │
│  [■] Proposer 에이전트                                                       │
│  [■] Definition Freezer 에이전트                                             │
│  [■] Data QA 에이전트                                                        │
│  [■] Backtest 에이전트                                                       │
│  [■] CSV 데이터 프로바이더                                                   │
│                                                                             │
│  Week 7-8: Validation Agents + Orchestrator                                 │
│  ─────────────────────────────────────────────────────────────────────────  │
│  [■] Cost/Slippage 에이전트                                                  │
│  [■] Risk/Stress 에이전트                                                    │
│  [■] Overfit Audit 에이전트                                                  │
│  [■] Portfolio/Capacity 에이전트                                             │
│  [■] Orchestrator (Hard Gates + Soft Scoring)                               │
│  [■] CLI: propose, freeze, validate, decide                                 │
│                                                                             │
│  Milestone: 오프라인 백테스트 완전 동작                                       │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 2: Shadow Trading (6주)                                              │
│  ═══════════════════════════════════════════════════════════════════════════│
│                                                                             │
│  Week 9-10: Exchange Integration                                            │
│  ─────────────────────────────────────────────────────────────────────────  │
│  [ ] CCXT 기반 Binance 어댑터                                                │
│  [ ] 실시간 데이터 스트리밍 (WebSocket)                                      │
│  [ ] 주문 제출/조회/취소                                                      │
│  [ ] Rate limiting & Error retry                                            │
│                                                                             │
│  Week 11-12: Execution Simulator                                            │
│  ─────────────────────────────────────────────────────────────────────────  │
│  [ ] Execution Simulator 에이전트                                            │
│  [ ] 실행 정책 (MARKET, LIMIT, TWAP 등)                                      │
│  [ ] 실시간 슬리피지 추적                                                    │
│                                                                             │
│  Week 13-14: Shadow Mode                                                    │
│  ─────────────────────────────────────────────────────────────────────────  │
│  [ ] Shadow 트레이딩 로직                                                    │
│  [ ] 시그널 로깅 (실제 거래 없음)                                            │
│  [ ] 가상 PnL 추적                                                           │
│  [ ] 모니터링 대시보드                                                       │
│  [ ] CLI: deploy --stage shadow, monitor                                    │
│                                                                             │
│  Milestone: 실시간 시그널 로깅, 거래 없음                                     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 3: Paper Trading (4주)                                               │
│  ═══════════════════════════════════════════════════════════════════════════│
│                                                                             │
│  Week 15-16: Paper Mode                                                     │
│  ─────────────────────────────────────────────────────────────────────────  │
│  [ ] 거래소 Testnet 연동                                                     │
│  [ ] Paper 포지션 관리                                                       │
│  [ ] 실시간 PnL 추적                                                         │
│  [ ] 알림 시스템 (Slack/Console)                                             │
│                                                                             │
│  Week 17-18: Risk Management                                                │
│  ─────────────────────────────────────────────────────────────────────────  │
│  [ ] Kill Switch 구현                                                        │
│  [ ] 자동 손절                                                               │
│  [ ] 레짐 기반 포지션 조정                                                   │
│  [ ] CLI: kill                                                              │
│                                                                             │
│  Milestone: Testnet에서 실제 주문 실행                                       │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 4: Production (TBD - 규제 검토 필요)                                  │
│  ═══════════════════════════════════════════════════════════════════════════│
│                                                                             │
│  [ ] 실거래 모드                                                             │
│  [ ] 점진적 자본 확대                                                        │
│  [ ] 24/7 운영 안정성                                                        │
│  [ ] 규제 준수 검토                                                          │
│  [ ] 세금/회계 리포팅                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 10.1 마일스톤 정의

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  MILESTONE DEFINITIONS                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  M1: MVP Complete (Week 8)                                                  │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Success Criteria:                                                          │
│  ✓ 전략 제안 → 검증 → 결정 파이프라인 완전 동작                              │
│  ✓ 최소 2년 이상 BTC 데이터 백테스트 가능                                    │
│  ✓ 10개 에이전트 모두 구현                                                   │
│  ✓ CLI 주요 명령어 동작                                                      │
│  ✓ 단위 테스트 커버리지 80% 이상                                             │
│                                                                             │
│  M2: Shadow Trading (Week 14)                                               │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Success Criteria:                                                          │
│  ✓ Binance 실시간 데이터 수신                                                │
│  ✓ 시그널 생성 및 로깅 (거래 없음)                                           │
│  ✓ 2주간 Shadow 모드 안정 운영                                              │
│  ✓ 모니터링 대시보드 동작                                                    │
│                                                                             │
│  M3: Paper Trading (Week 18)                                                │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Success Criteria:                                                          │
│  ✓ Testnet 주문 실행                                                        │
│  ✓ Kill Switch 동작 확인                                                    │
│  ✓ 4주간 Paper 모드 안정 운영                                               │
│  ✓ 백테스트 대비 성과 비교 리포트                                            │
│                                                                             │
│  M4: Production Ready (TBD)                                                 │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Success Criteria:                                                          │
│  ✓ 법적/규제 검토 완료                                                       │
│  ✓ 실거래 최소 $100 성공                                                     │
│  ✓ 24시간 무중단 운영                                                        │
│  ✓ 장애 복구 절차 문서화                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 다음 파일: 07-readme-appendix.md

README.md 구조, 부록, 용어집
