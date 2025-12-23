# Ukkie-Trader 개발 계획서 Part 4: 핵심 알고리즘

---

## 5. 핵심 알고리즘

### 5.1 상태머신 기반 백테스트 엔진

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  BACKTEST ENGINE: STATE MACHINE ARCHITECTURE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  WHY STATE MACHINE?                                                         │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • 명시적 상태 전이 = 버그 감소                                              │
│  • 재현 가능한 시뮬레이션                                                    │
│  • 디버깅/감사 용이                                                          │
│  • 병렬 처리 친화적                                                          │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  STATE DEFINITIONS                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  class TradingState(Enum):                                             │ │
│  │      IDLE = "IDLE"           # 포지션 없음, 시그널 대기                 │ │
│  │      ENTERING = "ENTERING"   # 진입 주문 제출됨, 체결 대기              │ │
│  │      IN_POSITION = "IN_POSITION"  # 포지션 보유 중                     │ │
│  │      EXITING = "EXITING"     # 청산 주문 제출됨, 체결 대기              │ │
│  │      STOPPED = "STOPPED"     # 손절/강제 청산 상태                      │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  STATE TRANSITION TABLE                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────┬────────────────────┬───────────────┬──────────────────┐ │
│  │ Current State │ Event              │ Next State    │ Action           │ │
│  ├───────────────┼────────────────────┼───────────────┼──────────────────┤ │
│  │ IDLE          │ entry_signal       │ ENTERING      │ submit_order     │ │
│  │ IDLE          │ no_signal          │ IDLE          │ none             │ │
│  │ ENTERING      │ order_filled       │ IN_POSITION   │ record_entry     │ │
│  │ ENTERING      │ order_timeout      │ IDLE          │ cancel_order     │ │
│  │ ENTERING      │ order_rejected     │ IDLE          │ log_rejection    │ │
│  │ IN_POSITION   │ exit_signal        │ EXITING       │ submit_exit      │ │
│  │ IN_POSITION   │ stop_loss_hit      │ STOPPED       │ submit_exit      │ │
│  │ IN_POSITION   │ take_profit_hit    │ EXITING       │ submit_exit      │ │
│  │ IN_POSITION   │ timeout            │ EXITING       │ submit_exit      │ │
│  │ IN_POSITION   │ hold               │ IN_POSITION   │ update_pnl       │ │
│  │ EXITING       │ order_filled       │ IDLE          │ record_exit      │ │
│  │ EXITING       │ order_timeout      │ EXITING       │ retry_market     │ │
│  │ STOPPED       │ stop_filled        │ IDLE          │ record_stop      │ │
│  └───────────────┴────────────────────┴───────────────┴──────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  IMPLEMENTATION                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ```python                                                                  │
│  @dataclass                                                                 │
│  class BacktestState:                                                       │
│      """백테스트 시뮬레이션 상태"""                                          │
│      trading_state: TradingState = TradingState.IDLE                        │
│      current_bar: int = 0                                                   │
│      cash: float = 10000.0                                                  │
│      position: Optional[Position] = None                                    │
│      pending_order: Optional[Order] = None                                  │
│      equity_history: list[float] = field(default_factory=list)             │
│      trade_history: list[Trade] = field(default_factory=list)              │
│      current_regime: Regime = Regime.NORMAL                                 │
│                                                                             │
│                                                                             │
│  class BacktestEngine:                                                      │
│      """상태머신 기반 백테스트 엔진"""                                       │
│                                                                             │
│      def __init__(                                                          │
│          self,                                                              │
│          strategy: FrozenStrategy,                                          │
│          data: pl.DataFrame,                                                │
│          config: BacktestConfig                                             │
│      ):                                                                     │
│          self.strategy = strategy                                           │
│          self.data = data                                                   │
│          self.config = config                                               │
│          self.state = BacktestState(cash=config.initial_capital)            │
│          self.signal_generator = SignalGenerator(strategy)                  │
│          self.regime_detector = RegimeDetector()                            │
│                                                                             │
│      async def run(self) -> BacktestResult:                                 │
│          """전체 백테스트 실행"""                                            │
│          for bar_idx in range(len(self.data)):                              │
│              self.state.current_bar = bar_idx                               │
│              bar = self.data.row(bar_idx)                                   │
│                                                                             │
│              # 1. 레짐 감지                                                  │
│              self.state.current_regime = self.regime_detector.detect(bar)   │
│                                                                             │
│              # 2. 상태별 처리                                                │
│              await self._process_state(bar)                                 │
│                                                                             │
│              # 3. 자산 가치 기록                                             │
│              equity = self._calculate_equity(bar)                           │
│              self.state.equity_history.append(equity)                       │
│                                                                             │
│          return self._compile_results()                                     │
│                                                                             │
│      async def _process_state(self, bar: BarData) -> None:                  │
│          """현재 상태에 따른 처리"""                                         │
│          match self.state.trading_state:                                    │
│              case TradingState.IDLE:                                        │
│                  await self._handle_idle(bar)                               │
│              case TradingState.ENTERING:                                    │
│                  await self._handle_entering(bar)                           │
│              case TradingState.IN_POSITION:                                 │
│                  await self._handle_in_position(bar)                        │
│              case TradingState.EXITING:                                     │
│                  await self._handle_exiting(bar)                            │
│              case TradingState.STOPPED:                                     │
│                  await self._handle_stopped(bar)                            │
│                                                                             │
│      async def _handle_idle(self, bar: BarData) -> None:                    │
│          """IDLE 상태 처리: 진입 시그널 확인"""                               │
│          signal = self.signal_generator.check_entry(bar, self.data)         │
│          if signal.is_entry:                                                │
│              order = self._create_entry_order(bar, signal)                  │
│              self.state.pending_order = order                               │
│              self.state.trading_state = TradingState.ENTERING               │
│                                                                             │
│      async def _handle_in_position(self, bar: BarData) -> None:             │
│          """IN_POSITION 상태 처리: 청산 조건 확인"""                          │
│          pos = self.state.position                                          │
│                                                                             │
│          # 손절 확인                                                         │
│          if self._check_stop_loss(bar, pos):                                │
│              self.state.trading_state = TradingState.STOPPED                │
│              return                                                         │
│                                                                             │
│          # 익절 확인                                                         │
│          if self._check_take_profit(bar, pos):                              │
│              self._submit_exit_order(bar, "TAKE_PROFIT")                    │
│              return                                                         │
│                                                                             │
│          # 시그널 기반 청산                                                  │
│          signal = self.signal_generator.check_exit(bar, self.data)          │
│          if signal.is_exit:                                                 │
│              self._submit_exit_order(bar, "SIGNAL")                         │
│              return                                                         │
│                                                                             │
│          # 타임아웃 확인                                                     │
│          if self._check_timeout(bar, pos):                                  │
│              self._submit_exit_order(bar, "TIMEOUT")                        │
│                                                                             │
│  ```                                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 레짐 감지 알고리즘

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  REGIME DETECTION ALGORITHM                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  REGIME CLASSIFICATION                                                      │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  ┌────────────┬────────────────────────────────────────────────────────┐   │
│  │ Regime     │ Detection Criteria                                     │   │
│  ├────────────┼────────────────────────────────────────────────────────┤   │
│  │            │ • Realized Vol(20) < 2σ historical                     │   │
│  │ NORMAL     │ • Spread ≤ 1.5x average                                │   │
│  │            │ • Order book depth ≥ 0.5x average                      │   │
│  │            │ • No scheduled events in next 4h                       │   │
│  ├────────────┼────────────────────────────────────────────────────────┤   │
│  │            │ • Realized Vol(20) > 2σ historical                     │   │
│  │ VOLATILE   │ • OR Intraday range > 3x ATR                          │   │
│  │            │ • OR VIX equivalent > 30 (for crypto: VIX-like index) │   │
│  ├────────────┼────────────────────────────────────────────────────────┤   │
│  │            │ • Spread > 3x average                                  │   │
│  │ ILLIQUID   │ • OR Order book depth < 0.3x average                  │   │
│  │            │ • OR Fill time > 5x normal                            │   │
│  ├────────────┼────────────────────────────────────────────────────────┤   │
│  │            │ • Scheduled macro event (FOMC, CPI, etc)               │   │
│  │ EVENT      │ • Major crypto event (halving, merge, etc)            │   │
│  │            │ • Breaking news detected                               │   │
│  └────────────┴────────────────────────────────────────────────────────┘   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  IMPLEMENTATION                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ```python                                                                  │
│  class RegimeDetector:                                                      │
│      """레짐 감지기"""                                                       │
│                                                                             │
│      def __init__(                                                          │
│          self,                                                              │
│          vol_lookback: int = 20,                                            │
│          vol_threshold_sigma: float = 2.0,                                  │
│          spread_threshold_mult: float = 3.0,                                │
│          depth_threshold_mult: float = 0.3                                  │
│      ):                                                                     │
│          self.vol_lookback = vol_lookback                                   │
│          self.vol_threshold = vol_threshold_sigma                           │
│          self.spread_threshold = spread_threshold_mult                      │
│          self.depth_threshold = depth_threshold_mult                        │
│          self.historical_vol: deque = deque(maxlen=252)  # 1년              │
│          self.historical_spread: deque = deque(maxlen=100)                  │
│                                                                             │
│      def detect(                                                            │
│          self,                                                              │
│          bar: BarData,                                                      │
│          orderbook: Optional[OrderBook] = None,                             │
│          scheduled_events: list[Event] = None                               │
│      ) -> Regime:                                                           │
│          """현재 바의 레짐 판단"""                                           │
│                                                                             │
│          # 1. 이벤트 체크 (최우선)                                           │
│          if self._has_imminent_event(scheduled_events):                     │
│              return Regime.EVENT                                            │
│                                                                             │
│          # 2. 유동성 체크                                                    │
│          if orderbook and self._is_illiquid(bar, orderbook):                │
│              return Regime.ILLIQUID                                         │
│                                                                             │
│          # 3. 변동성 체크                                                    │
│          if self._is_volatile(bar):                                         │
│              return Regime.VOLATILE                                         │
│                                                                             │
│          return Regime.NORMAL                                               │
│                                                                             │
│      def _is_volatile(self, bar: BarData) -> bool:                          │
│          """변동성 레짐 판단"""                                              │
│          current_vol = self._calculate_realized_vol(bar)                    │
│                                                                             │
│          if len(self.historical_vol) < 50:                                  │
│              return False                                                   │
│                                                                             │
│          vol_mean = np.mean(self.historical_vol)                            │
│          vol_std = np.std(self.historical_vol)                              │
│                                                                             │
│          return current_vol > vol_mean + self.vol_threshold * vol_std       │
│                                                                             │
│      def _is_illiquid(                                                      │
│          self,                                                              │
│          bar: BarData,                                                      │
│          orderbook: OrderBook                                               │
│      ) -> bool:                                                             │
│          """유동성 부족 레짐 판단"""                                         │
│          current_spread = orderbook.spread_bps                              │
│          avg_spread = np.mean(self.historical_spread) if self.historical_spread else current_spread  │
│                                                                             │
│          # 스프레드 기준                                                     │
│          if current_spread > self.spread_threshold * avg_spread:            │
│              return True                                                    │
│                                                                             │
│          # Depth 기준 (선택적)                                               │
│          if hasattr(orderbook, 'total_depth'):                              │
│              avg_depth = self._get_avg_depth()                              │
│              if orderbook.total_depth < self.depth_threshold * avg_depth:   │
│                  return True                                                │
│                                                                             │
│          return False                                                       │
│                                                                             │
│  ```                                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 레짐별 비용 모델

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  REGIME-BASED COST MODEL                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MODEL FORMULATION                                                          │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  Total Cost = Fixed Fee + Variable Slippage                                 │
│                                                                             │
│  Fixed Fee = Trade Size × Fee Rate (maker/taker)                            │
│                                                                             │
│  Slippage = Base Slippage × Regime Multiplier × Size Factor                 │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                                                                       │  │
│  │  Size Factor = √(Order Size / ADV)                                   │  │
│  │                                                                       │  │
│  │  - Square root: 시장 충격은 사이즈에 비례하지만 선형은 아님           │  │
│  │  - ADV: Average Daily Volume (20일 이동평균)                         │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  REGIME PARAMETERS                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────┬────────────┬────────────┬─────────────────────────────┐    │
│  │ Regime     │ Base (bps) │ Multiplier │ 95th Percentile Factor     │    │
│  ├────────────┼────────────┼────────────┼─────────────────────────────┤    │
│  │ NORMAL     │ 2          │ 1.0        │ 1.5                         │    │
│  │ VOLATILE   │ 5          │ 2.0        │ 3.0                         │    │
│  │ ILLIQUID   │ 10         │ 3.0        │ 5.0                         │    │
│  │ EVENT      │ 15         │ 4.0        │ 8.0                         │    │
│  └────────────┴────────────┴────────────┴─────────────────────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  IMPLEMENTATION                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ```python                                                                  │
│  @dataclass                                                                 │
│  class CostModelParams:                                                     │
│      """비용 모델 파라미터"""                                                │
│      base_slippage_bps: dict[Regime, float] = field(default_factory=lambda: {  │
│          Regime.NORMAL: 2.0,                                                │
│          Regime.VOLATILE: 5.0,                                              │
│          Regime.ILLIQUID: 10.0,                                             │
│          Regime.EVENT: 15.0                                                 │
│      })                                                                     │
│      regime_multiplier: dict[Regime, float] = field(default_factory=lambda: {  │
│          Regime.NORMAL: 1.0,                                                │
│          Regime.VOLATILE: 2.0,                                              │
│          Regime.ILLIQUID: 3.0,                                              │
│          Regime.EVENT: 4.0                                                  │
│      })                                                                     │
│      maker_fee_bps: float = 10.0                                            │
│      taker_fee_bps: float = 10.0                                            │
│                                                                             │
│                                                                             │
│  class CostModel:                                                           │
│      """레짐 인식 비용 모델"""                                               │
│                                                                             │
│      def __init__(self, params: CostModelParams = None):                    │
│          self.params = params or CostModelParams()                          │
│                                                                             │
│      def estimate_cost(                                                     │
│          self,                                                              │
│          trade_size_usd: float,                                             │
│          regime: Regime,                                                    │
│          adv_usd: float,                                                    │
│          is_maker: bool = False                                             │
│      ) -> CostEstimate:                                                     │
│          """거래 비용 추정"""                                                │
│                                                                             │
│          # 1. 고정 수수료                                                    │
│          fee_bps = self.params.maker_fee_bps if is_maker else self.params.taker_fee_bps  │
│          fixed_fee = trade_size_usd * fee_bps / 10000                       │
│                                                                             │
│          # 2. 슬리피지                                                       │
│          base_slip = self.params.base_slippage_bps[regime]                  │
│          multiplier = self.params.regime_multiplier[regime]                 │
│          size_factor = math.sqrt(trade_size_usd / adv_usd)                  │
│                                                                             │
│          slippage_bps = base_slip * multiplier * size_factor                │
│          slippage_usd = trade_size_usd * slippage_bps / 10000               │
│                                                                             │
│          return CostEstimate(                                               │
│              fixed_fee_usd=fixed_fee,                                       │
│              slippage_usd=slippage_usd,                                     │
│              total_cost_usd=fixed_fee + slippage_usd,                       │
│              total_cost_bps=fee_bps + slippage_bps,                         │
│              regime=regime                                                  │
│          )                                                                  │
│                                                                             │
│      def estimate_cost_distribution(                                        │
│          self,                                                              │
│          trade_size_usd: float,                                             │
│          regime: Regime,                                                    │
│          adv_usd: float,                                                    │
│          n_simulations: int = 1000                                          │
│      ) -> CostDistribution:                                                 │
│          """비용 분포 시뮬레이션 (Monte Carlo)"""                             │
│                                                                             │
│          base_estimate = self.estimate_cost(                                │
│              trade_size_usd, regime, adv_usd, is_maker=False                │
│          )                                                                  │
│                                                                             │
│          # 슬리피지에 불확실성 추가                                          │
│          p95_factor = self._get_p95_factor(regime)                          │
│          slip_samples = np.random.lognormal(                                │
│              mean=np.log(base_estimate.slippage_usd),                       │
│              sigma=0.5,  # 변동성                                            │
│              size=n_simulations                                             │
│          )                                                                  │
│                                                                             │
│          total_costs = base_estimate.fixed_fee_usd + slip_samples           │
│                                                                             │
│          return CostDistribution(                                           │
│              mean=np.mean(total_costs),                                     │
│              median=np.median(total_costs),                                 │
│              p95=np.percentile(total_costs, 95),                            │
│              p99=np.percentile(total_costs, 99),                            │
│              samples=total_costs                                            │
│          )                                                                  │
│                                                                             │
│  ```                                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.4 Walk-Forward 과최적화 감사

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  WALK-FORWARD ANALYSIS & DEFLATED SHARPE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  WALK-FORWARD METHODOLOGY                                                   │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                                                                       │  │
│  │  Timeline: |====== TRAIN ======|== TEST ==|                          │  │
│  │                                                                       │  │
│  │  Fold 1:   [=====TRAIN=====][TEST]                                   │  │
│  │  Fold 2:        [=====TRAIN=====][TEST]                              │  │
│  │  Fold 3:             [=====TRAIN=====][TEST]                         │  │
│  │  Fold 4:                  [=====TRAIN=====][TEST]                    │  │
│  │  Fold 5:                       [=====TRAIN=====][TEST]               │  │
│  │                                                                       │  │
│  │  Ratio: 80% Train / 20% Test (configurable)                          │  │
│  │  Overlap: None (anchored) or Rolling                                 │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  DEFLATED SHARPE RATIO                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                                                                       │  │
│  │  문제: 많은 전략을 테스트하면 우연히 좋은 결과가 나올 확률 증가       │  │
│  │                                                                       │  │
│  │  해결: Deflated Sharpe Ratio (DSR)                                   │  │
│  │                                                                       │  │
│  │  DSR = SR × √(1 - γ × N)                                             │  │
│  │                                                                       │  │
│  │  Where:                                                               │  │
│  │  - SR: 관측된 Sharpe Ratio                                           │  │
│  │  - γ: 보정 계수 (0.01 권장)                                          │  │
│  │  - N: 테스트한 전략/파라미터 조합 수                                  │  │
│  │                                                                       │  │
│  │  예시:                                                                │  │
│  │  - SR = 1.5, N = 50 → DSR = 1.5 × √(1 - 0.5) = 1.06                 │  │
│  │  - SR = 1.5, N = 100 → DSR = 1.5 × √(0) = 0 (무효)                  │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  IMPLEMENTATION                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ```python                                                                  │
│  class OverfitAuditor:                                                      │
│      """과최적화 감사 에이전트"""                                            │
│                                                                             │
│      def __init__(                                                          │
│          self,                                                              │
│          n_folds: int = 5,                                                  │
│          train_ratio: float = 0.8,                                          │
│          deflation_gamma: float = 0.01,                                     │
│          n_permutations: int = 1000                                         │
│      ):                                                                     │
│          self.n_folds = n_folds                                             │
│          self.train_ratio = train_ratio                                     │
│          self.gamma = deflation_gamma                                       │
│          self.n_permutations = n_permutations                               │
│                                                                             │
│      async def audit(                                                       │
│          self,                                                              │
│          strategy: FrozenStrategy,                                          │
│          data: pl.DataFrame,                                                │
│          trials_count: int                                                  │
│      ) -> OverfitAuditResult:                                               │
│          """과최적화 감사 실행"""                                            │
│                                                                             │
│          # 1. Walk-Forward 분석                                              │
│          wf_results = await self._walk_forward_analysis(strategy, data)     │
│                                                                             │
│          # 2. Deflated Sharpe 계산                                           │
│          ds_results = self._calculate_deflated_sharpe(                      │
│              wf_results.avg_test_sharpe,                                    │
│              trials_count                                                   │
│          )                                                                  │
│                                                                             │
│          # 3. Randomization Test                                             │
│          rand_results = await self._randomization_test(strategy, data)      │
│                                                                             │
│          # 4. 종합 점수 계산                                                 │
│          overfit_score = self._calculate_overfit_score(                     │
│              wf_results, ds_results, rand_results                           │
│          )                                                                  │
│                                                                             │
│          return OverfitAuditResult(                                         │
│              walk_forward_results=wf_results,                               │
│              deflated_sharpe=ds_results,                                    │
│              randomization_test=rand_results,                               │
│              overfit_score=overfit_score,                                   │
│              overfit_rating=self._score_to_rating(overfit_score)            │
│          )                                                                  │
│                                                                             │
│      async def _walk_forward_analysis(                                      │
│          self,                                                              │
│          strategy: FrozenStrategy,                                          │
│          data: pl.DataFrame                                                 │
│      ) -> WalkForwardResults:                                               │
│          """Walk-Forward 분석 실행"""                                        │
│          n_rows = len(data)                                                 │
│          fold_size = n_rows // self.n_folds                                 │
│          train_size = int(fold_size * self.train_ratio)                     │
│                                                                             │
│          fold_results = []                                                  │
│                                                                             │
│          for fold_idx in range(self.n_folds):                               │
│              start_idx = fold_idx * fold_size                               │
│              train_end = start_idx + train_size                             │
│              test_end = start_idx + fold_size                               │
│                                                                             │
│              train_data = data.slice(start_idx, train_size)                 │
│              test_data = data.slice(train_end, fold_size - train_size)      │
│                                                                             │
│              # Train에서 백테스트                                            │
│              train_result = await self._backtest(strategy, train_data)      │
│              # Test에서 백테스트 (파라미터 고정)                              │
│              test_result = await self._backtest(strategy, test_data)        │
│                                                                             │
│              fold_results.append(FoldResult(                                │
│                  fold=fold_idx + 1,                                         │
│                  train_sharpe=train_result.sharpe,                          │
│                  test_sharpe=test_result.sharpe                             │
│              ))                                                             │
│                                                                             │
│          avg_train = np.mean([f.train_sharpe for f in fold_results])        │
│          avg_test = np.mean([f.test_sharpe for f in fold_results])          │
│          degradation = 1 - (avg_test / avg_train) if avg_train > 0 else 1   │
│                                                                             │
│          return WalkForwardResults(                                         │
│              folds=self.n_folds,                                            │
│              fold_results=fold_results,                                     │
│              avg_train_sharpe=avg_train,                                    │
│              avg_test_sharpe=avg_test,                                      │
│              degradation_ratio=degradation,                                 │
│              status="ACCEPTABLE" if degradation < 0.5 else "CONCERNING"     │
│          )                                                                  │
│                                                                             │
│      def _calculate_deflated_sharpe(                                        │
│          self,                                                              │
│          observed_sharpe: float,                                            │
│          trials: int                                                        │
│      ) -> DeflatedSharpeResult:                                             │
│          """Deflated Sharpe Ratio 계산"""                                   │
│          deflation_factor = max(0, 1 - self.gamma * trials)                 │
│          dsr = observed_sharpe * math.sqrt(deflation_factor)                │
│                                                                             │
│          return DeflatedSharpeResult(                                       │
│              original_sharpe=observed_sharpe,                               │
│              trials_count=trials,                                           │
│              deflated_sharpe=dsr,                                           │
│              status="VALID" if dsr > 0.5 else "INVALID"                     │
│          )                                                                  │
│                                                                             │
│  ```                                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.5 UCB1 기반 에이전트 예산 배분

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  UCB1-BASED AGENT COMPUTE BUDGET ALLOCATION                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PROBLEM                                                                    │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • 여러 에이전트가 제한된 컴퓨팅 자원을 경쟁                                 │
│  • 어떤 에이전트에 더 많은 자원을 할당할지 결정 필요                         │
│  • Exploration (새 에이전트 시도) vs Exploitation (성과 좋은 에이전트)       │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  UCB1 ALGORITHM                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                                                                       │  │
│  │  UCB1 Score = x̄_i + c × √(ln(N) / n_i)                              │  │
│  │                                                                       │  │
│  │  Where:                                                               │  │
│  │  - x̄_i: 에이전트 i의 평균 보상 (예: 발견한 문제 수)                  │  │
│  │  - N: 전체 시행 횟수                                                  │  │
│  │  - n_i: 에이전트 i의 시행 횟수                                        │  │
│  │  - c: 탐색 계수 (√2 권장)                                            │  │
│  │                                                                       │  │
│  │  높은 UCB → 더 많은 예산 할당                                         │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  AGENT REWARD DEFINITIONS                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┬──────────────────────────────────────────────────┐ │
│  │ Agent               │ Reward Metric                                    │ │
│  ├─────────────────────┼──────────────────────────────────────────────────┤ │
│  │ DataQA              │ 발견된 데이터 문제 수 / 시간                      │ │
│  │ Backtest            │ 시뮬레이션 정확도 (실제 vs 예측)                  │ │
│  │ CostSlippage        │ 비용 예측 정확도                                  │ │
│  │ RiskStress          │ 위기 예측 정확도                                  │ │
│  │ OverfitAudit        │ 과최적화 탐지율 (True Positive Rate)             │ │
│  │ Orchestrator        │ 승인 전략의 실제 성과                             │ │
│  └─────────────────────┴──────────────────────────────────────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  IMPLEMENTATION                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ```python                                                                  │
│  class UCBBudgetAllocator:                                                  │
│      """UCB1 기반 에이전트 예산 배분기"""                                    │
│                                                                             │
│      def __init__(                                                          │
│          self,                                                              │
│          agents: list[str],                                                 │
│          exploration_coef: float = math.sqrt(2),                            │
│          min_trials: int = 5                                                │
│      ):                                                                     │
│          self.agents = agents                                               │
│          self.c = exploration_coef                                          │
│          self.min_trials = min_trials                                       │
│                                                                             │
│          # 에이전트별 통계                                                   │
│          self.rewards: dict[str, list[float]] = {a: [] for a in agents}     │
│          self.trials: dict[str, int] = {a: 0 for a in agents}               │
│          self.total_trials = 0                                              │
│                                                                             │
│      def select_agent(self) -> str:                                         │
│          """다음에 실행할 에이전트 선택"""                                   │
│          # 초기 탐색: 모든 에이전트 최소 횟수 실행                            │
│          for agent in self.agents:                                          │
│              if self.trials[agent] < self.min_trials:                       │
│                  return agent                                               │
│                                                                             │
│          # UCB1 점수 계산                                                    │
│          ucb_scores = {}                                                    │
│          for agent in self.agents:                                          │
│              mean_reward = np.mean(self.rewards[agent])                     │
│              exploration = self.c * math.sqrt(                              │
│                  math.log(self.total_trials) / self.trials[agent]           │
│              )                                                              │
│              ucb_scores[agent] = mean_reward + exploration                  │
│                                                                             │
│          return max(ucb_scores, key=ucb_scores.get)                         │
│                                                                             │
│      def update(self, agent: str, reward: float) -> None:                   │
│          """에이전트 실행 결과 업데이트"""                                   │
│          self.rewards[agent].append(reward)                                 │
│          self.trials[agent] += 1                                            │
│          self.total_trials += 1                                             │
│                                                                             │
│      def get_allocation(self, total_budget: float) -> dict[str, float]:     │
│          """현재 UCB 점수 기반 예산 배분"""                                  │
│          if self.total_trials < len(self.agents) * self.min_trials:         │
│              # 균등 배분                                                     │
│              return {a: total_budget / len(self.agents) for a in self.agents}  │
│                                                                             │
│          ucb_scores = {}                                                    │
│          for agent in self.agents:                                          │
│              mean_reward = np.mean(self.rewards[agent])                     │
│              exploration = self.c * math.sqrt(                              │
│                  math.log(self.total_trials) / self.trials[agent]           │
│              )                                                              │
│              ucb_scores[agent] = max(0.1, mean_reward + exploration)  # 최소 10%  │
│                                                                             │
│          # 정규화                                                            │
│          total_score = sum(ucb_scores.values())                             │
│          return {                                                           │
│              agent: total_budget * score / total_score                      │
│              for agent, score in ucb_scores.items()                         │
│          }                                                                  │
│                                                                             │
│  ```                                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 다음 파일: 05-cli-interface.md

CLI 인터페이스 설계 (ASCII 오랑우탄 로고, 주요 커맨드)
