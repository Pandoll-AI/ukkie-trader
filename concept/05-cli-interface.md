# Ukkie-Trader 개발 계획서 Part 5: CLI 인터페이스 설계

---

## 6. CLI 인터페이스 설계

### 6.1 시작 화면

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  STARTUP SPLASH SCREEN                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ╔════════════════════════════════════════════════════════════════════════╗ │
│  ║                                                                        ║ │
│  ║                           ██████████                                   ║ │
│  ║                       ████▓▓▓▓▓▓▓▓▓▓████                               ║ │
│  ║                     ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██                             ║ │
│  ║                   ██▓▓▓▓██████████████▓▓▓▓██                           ║ │
│  ║                 ██▓▓████              ████▓▓██                         ║ │
│  ║               ██▓▓██    ████    ████    ██▓▓██                         ║ │
│  ║               ██▓▓██    ████    ████    ██▓▓██                         ║ │
│  ║               ██▓▓██                    ██▓▓██                         ║ │
│  ║                 ██▓▓████    ████    ████▓▓██                           ║ │
│  ║                   ██▓▓▓▓████████████▓▓▓▓██                             ║ │
│  ║               ████  ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓██  ████                           ║ │
│  ║             ██▓▓██    ████████████    ██▓▓██                           ║ │
│  ║             ██▓▓▓▓██                ██▓▓▓▓██                           ║ │
│  ║               ██▓▓▓▓████████████████▓▓▓▓██                             ║ │
│  ║                 ████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████                               ║ │
│  ║                     ████████████████                                   ║ │
│  ║                                                                        ║ │
│  ║            ╦ ╦╦╔═╦╔═╦╔═╗  ╔╦╗╦═╗╔═╗╔╦╗╔═╗╦═╗                           ║ │
│  ║            ║ ║╠╩╗╠╩╗║║╣    ║ ╠╦╝╠═╣ ║║║╣ ╠╦╝                           ║ │
│  ║            ╚═╝╩ ╩╩ ╩╩╚═╝   ╩ ╩╚═╩ ╩═╩╝╚═╝╩╚═                           ║ │
│  ║                                                                        ║ │
│  ║                  "신중한 오랑우탄처럼 거래하라"                          ║ │
│  ║                                                                        ║ │
│  ║            ─────────────────────────────────────                       ║ │
│  ║                      v0.1.0 | Python 3.11+                             ║ │
│  ║            ─────────────────────────────────────                       ║ │
│  ║                                                                        ║ │
│  ╚════════════════════════════════════════════════════════════════════════╝ │
│                                                                             │
│  Loading configuration... ████████████████████████████████████ 100%         │
│  Connecting to exchange... ✓                                                │
│  Initializing agents... ✓                                                   │
│                                                                             │
│  Type 'help' for available commands or 'exit' to quit.                      │
│                                                                             │
│  🦧 ukkie>                                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 명령어 구조

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  COMMAND HIERARCHY                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ukkie-trader                                                               │
│  │                                                                          │
│  ├── propose      # 새 전략 제안                                            │
│  │   ├── --idea "description"                                               │
│  │   ├── --asset BTC/USDT                                                   │
│  │   ├── --timeframe 1h                                                     │
│  │   └── --from-file strategy.yaml                                          │
│  │                                                                          │
│  ├── freeze       # 전략 정의 동결                                          │
│  │   ├── <proposal_id>                                                      │
│  │   ├── --stop-loss 0.02                                                   │
│  │   ├── --take-profit 0.05                                                 │
│  │   └── --interactive                                                      │
│  │                                                                          │
│  ├── validate     # 전략 검증 실행                                          │
│  │   ├── <strategy_id>                                                      │
│  │   ├── --agents all|backtest,cost,risk                                    │
│  │   ├── --start-date 2020-01-01                                            │
│  │   ├── --end-date 2025-12-22                                              │
│  │   └── --parallel                                                         │
│  │                                                                          │
│  ├── decide       # 오케스트레이터 결정 요청                                 │
│  │   ├── <strategy_id>                                                      │
│  │   ├── --force                                                            │
│  │   └── --explain                                                          │
│  │                                                                          │
│  ├── deploy       # 전략 배포                                               │
│  │   ├── <strategy_id>                                                      │
│  │   ├── --stage shadow|paper|live                                          │
│  │   └── --capital 1000                                                     │
│  │                                                                          │
│  ├── monitor      # 실시간 모니터링                                         │
│  │   ├── --dashboard                                                        │
│  │   ├── --strategy <strategy_id>                                           │
│  │   └── --refresh 5                                                        │
│  │                                                                          │
│  ├── kill         # 긴급 중지                                               │
│  │   ├── <strategy_id>                                                      │
│  │   ├── --all                                                              │
│  │   └── --reason "description"                                             │
│  │                                                                          │
│  ├── list         # 목록 조회                                               │
│  │   ├── strategies                                                         │
│  │   ├── proposals                                                          │
│  │   ├── positions                                                          │
│  │   └── orders                                                             │
│  │                                                                          │
│  ├── show         # 상세 정보                                               │
│  │   ├── strategy <id>                                                      │
│  │   ├── backtest <id>                                                      │
│  │   ├── decision <id>                                                      │
│  │   └── position <id>                                                      │
│  │                                                                          │
│  ├── config       # 설정 관리                                               │
│  │   ├── show                                                               │
│  │   ├── set <key> <value>                                                  │
│  │   └── edit                                                               │
│  │                                                                          │
│  └── shell        # 대화형 셸 진입                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 주요 커맨드 상세

#### 6.3.1 propose 커맨드

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  COMMAND: propose                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PURPOSE: 새로운 전략 아이디어 제안                                          │
│                                                                             │
│  USAGE:                                                                     │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  # 대화형 모드                                                               │
│  $ ukkie-trader propose                                                     │
│                                                                             │
│  🦧 Strategy Proposer                                                       │
│  ──────────────────────────────────────────────────────                     │
│                                                                             │
│  ? Describe your strategy idea:                                             │
│  > BTC 20/50 EMA crossover momentum strategy                                │
│                                                                             │
│  ? Select asset: (Use arrow keys)                                           │
│    ❯ BTC/USDT                                                               │
│      ETH/USDT                                                               │
│      SOL/USDT                                                               │
│      Custom...                                                              │
│                                                                             │
│  ? Select timeframe:                                                        │
│    ❯ 1h                                                                     │
│      4h                                                                     │
│      1d                                                                     │
│                                                                             │
│  ? Maximum position size (% of capital): 10                                 │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ ✓ Proposal Created                                                   │   │
│  │                                                                      │   │
│  │ Proposal ID: PROP-20251223-001                                       │   │
│  │ Status: PROPOSED                                                     │   │
│  │ Asset: BTC/USDT                                                      │   │
│  │ Timeframe: 1h                                                        │   │
│  │ Data Available: 2020-01-01 to 2025-12-22 (5 years)                   │   │
│  │                                                                      │   │
│  │ Next step: ukkie-trader freeze PROP-20251223-001                     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  # 파일에서 로드                                                             │
│  $ ukkie-trader propose --from-file strategy.yaml                           │
│                                                                             │
│  # 원라이너                                                                  │
│  $ ukkie-trader propose \                                                   │
│      --idea "RSI oversold bounce strategy" \                                │
│      --asset ETH/USDT \                                                     │
│      --timeframe 4h                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 6.3.2 validate 커맨드

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  COMMAND: validate                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PURPOSE: 전략 검증 파이프라인 실행                                          │
│                                                                             │
│  USAGE:                                                                     │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  $ ukkie-trader validate STRAT-a3f8c2d1                                     │
│                                                                             │
│  🦧 Validation Pipeline                                                     │
│  ──────────────────────────────────────────────────────                     │
│                                                                             │
│  Strategy: STRAT-a3f8c2d1 (BTC/USDT 1h EMA Crossover)                       │
│  Period: 2020-01-01 to 2025-12-22                                           │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Agent Progress                                                       │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │ ✓ Data QA           [████████████████████] 100%  PASSED            │    │
│  │ ✓ Backtest          [████████████████████] 100%  COMPLETED         │    │
│  │ ✓ Cost/Slippage     [████████████████████] 100%  COMPLETED         │    │
│  │ ◐ Execution Sim     [██████████░░░░░░░░░░]  52%  RUNNING           │    │
│  │ ○ Risk/Stress       [░░░░░░░░░░░░░░░░░░░░]   0%  PENDING           │    │
│  │ ○ Overfit Audit     [░░░░░░░░░░░░░░░░░░░░]   0%  PENDING           │    │
│  │ ○ Portfolio/Cap     [░░░░░░░░░░░░░░░░░░░░]   0%  PENDING           │    │
│  │                                                                     │    │
│  │ Elapsed: 2m 34s | ETA: 3m 12s                                       │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  # 완료 후 요약                                                              │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Validation Summary                                                   │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │ ┌─────────────────┬────────────┬────────────┬───────────────────┐  │    │
│  │ │ Agent           │ Status     │ Duration   │ Key Finding       │  │    │
│  │ ├─────────────────┼────────────┼────────────┼───────────────────┤  │    │
│  │ │ Data QA         │ ✓ PASSED   │ 12s        │ 0.03% missing     │  │    │
│  │ │ Backtest        │ ✓ COMPLETED│ 1m 45s     │ SR: 1.23          │  │    │
│  │ │ Cost/Slippage   │ ✓ COMPLETED│ 28s        │ Net SR: 1.11      │  │    │
│  │ │ Execution Sim   │ ✓ COMPLETED│ 1m 02s     │ Fill: 100%        │  │    │
│  │ │ Risk/Stress     │ ✓ COMPLETED│ 45s        │ Rating: MODERATE  │  │    │
│  │ │ Overfit Audit   │ ✓ COMPLETED│ 2m 15s     │ Score: 2.1 (LOW)  │  │    │
│  │ │ Portfolio/Cap   │ ✓ COMPLETED│ 18s        │ Alloc: 15%        │  │    │
│  │ └─────────────────┴────────────┴────────────┴───────────────────┘  │    │
│  │                                                                     │    │
│  │ Total Duration: 6m 45s                                              │    │
│  │                                                                     │    │
│  │ Next step: ukkie-trader decide STRAT-a3f8c2d1                       │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 6.3.3 monitor 커맨드 (대시보드)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  COMMAND: monitor --dashboard                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║  🦧 UKKIE-TRADER DASHBOARD                     2025-12-23 14:32:15 UTC ║  │
│  ╠═══════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                       ║  │
│  ║  PORTFOLIO OVERVIEW                                                   ║  │
│  ║  ─────────────────────────────────────────────────────────────────── ║  │
│  ║  Total Equity: $12,847.32 (+28.47%)    Today: +$127.45 (+1.00%)      ║  │
│  ║                                                                       ║  │
│  ║  ┌─────────────────────────────────────────────────────────────────┐ ║  │
│  ║  │ Equity Curve (30d)                                              │ ║  │
│  ║  │                                                        ╭──────╮ │ ║  │
│  ║  │                                                   ╭────╯      │ │ ║  │
│  ║  │                                              ╭────╯           │ │ ║  │
│  ║  │                                    ╭─────────╯                │ │ ║  │
│  ║  │                        ╭───────────╯                          │ │ ║  │
│  ║  │  ╭──────────────────────╯                                     │ │ ║  │
│  ║  │  │                                                            │ │ ║  │
│  ║  │  $10K ─────────────────────────────────────────────────── $13K│ │ ║  │
│  ║  └─────────────────────────────────────────────────────────────────┘ ║  │
│  ║                                                                       ║  │
│  ║  ACTIVE STRATEGIES                                                    ║  │
│  ║  ─────────────────────────────────────────────────────────────────── ║  │
│  ║  ┌───────────────┬────────┬─────────┬────────┬────────┬───────────┐ ║  │
│  ║  │ Strategy      │ Stage  │ PnL     │ Trades │ Win %  │ Status    │ ║  │
│  ║  ├───────────────┼────────┼─────────┼────────┼────────┼───────────┤ ║  │
│  ║  │ STRAT-a3f8c2d1│ LIVE   │ +$847   │ 45     │ 52.2%  │ 🟢 ACTIVE │ ║  │
│  ║  │ STRAT-b2e7a1c9│ PAPER  │ +$234   │ 28     │ 48.1%  │ 🟢 ACTIVE │ ║  │
│  ║  │ STRAT-d4f9c3e5│ SHADOW │ +$156   │ 32     │ 51.5%  │ 🟢 ACTIVE │ ║  │
│  ║  └───────────────┴────────┴─────────┴────────┴────────┴───────────┘ ║  │
│  ║                                                                       ║  │
│  ║  CURRENT POSITIONS                                                    ║  │
│  ║  ─────────────────────────────────────────────────────────────────── ║  │
│  ║  ┌───────────┬────────┬───────────┬───────────┬─────────┬─────────┐ ║  │
│  ║  │ Asset     │ Side   │ Entry     │ Current   │ PnL     │ Time    │ ║  │
│  ║  ├───────────┼────────┼───────────┼───────────┼─────────┼─────────┤ ║  │
│  ║  │ BTC/USDT  │ LONG   │ $98,234   │ $98,567   │ +$33.30 │ 4h 23m  │ ║  │
│  ║  └───────────┴────────┴───────────┴───────────┴─────────┴─────────┘ ║  │
│  ║                                                                       ║  │
│  ║  SYSTEM STATUS                                                        ║  │
│  ║  ─────────────────────────────────────────────────────────────────── ║  │
│  ║  Exchange: 🟢 Connected    Data Feed: 🟢 Live    Agents: 🟢 Ready    ║  │
│  ║                                                                       ║  │
│  ║  [Q]uit  [R]efresh  [K]ill Strategy  [D]etails  [H]elp               ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 6.3.4 kill 커맨드

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  COMMAND: kill                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PURPOSE: 긴급 전략 중지 및 포지션 청산                                      │
│                                                                             │
│  USAGE:                                                                     │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  $ ukkie-trader kill STRAT-a3f8c2d1 --reason "Manual stop - market uncertainty"  │
│                                                                             │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║  ⚠️  KILL SWITCH ACTIVATED                                             ║  │
│  ╠═══════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                       ║  │
│  ║  Strategy: STRAT-a3f8c2d1                                             ║  │
│  ║  Reason: Manual stop - market uncertainty                             ║  │
│  ║                                                                       ║  │
│  ║  ⚠️  This will:                                                        ║  │
│  ║     1. Immediately close all open positions                           ║  │
│  ║     2. Cancel all pending orders                                      ║  │
│  ║     3. Disable the strategy from trading                              ║  │
│  ║     4. Record this action in the audit log                            ║  │
│  ║                                                                       ║  │
│  ║  Current Positions:                                                   ║  │
│  ║  ┌───────────┬────────┬───────────┬───────────┐                      ║  │
│  ║  │ Asset     │ Side   │ Size      │ Unrealized│                      ║  │
│  ║  ├───────────┼────────┼───────────┼───────────┤                      ║  │
│  ║  │ BTC/USDT  │ LONG   │ 0.05 BTC  │ +$33.30   │                      ║  │
│  ║  └───────────┴────────┴───────────┴───────────┘                      ║  │
│  ║                                                                       ║  │
│  ║  ? Are you sure you want to proceed? (y/N)                            ║  │
│  ║                                                                       ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                             │
│  # 확인 후                                                                   │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ ✓ Kill Switch Executed                                                │  │
│  │                                                                       │  │
│  │ Actions Taken:                                                        │  │
│  │ • Cancelled 0 pending orders                                          │  │
│  │ • Closed 1 position at market                                         │  │
│  │   - BTC/USDT: Sold 0.05 @ $98,512 (slippage: 3.2 bps)                │  │
│  │ • Strategy status: PAUSED                                             │  │
│  │                                                                       │  │
│  │ Audit ID: AUDIT-20251223-142156                                       │  │
│  │ Timestamp: 2025-12-23T14:21:56Z                                       │  │
│  │                                                                       │  │
│  │ To reactivate: ukkie-trader deploy STRAT-a3f8c2d1 --stage live       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  # 전체 중지                                                                 │
│  $ ukkie-trader kill --all --reason "System maintenance"                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.4 인터랙티브 셸

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  INTERACTIVE SHELL                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  $ ukkie-trader shell                                                       │
│                                                                             │
│  ╔════════════════════════════════════════════════════════════════════════╗ │
│  ║  🦧 Ukkie-Trader Interactive Shell v0.1.0                              ║ │
│  ║  Type 'help' for commands, 'exit' to quit                              ║ │
│  ╚════════════════════════════════════════════════════════════════════════╝ │
│                                                                             │
│  🦧 ukkie> help                                                             │
│                                                                             │
│  Available Commands:                                                        │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  Strategy Management:                                                       │
│    propose      Create a new strategy proposal                              │
│    freeze       Freeze a proposal into a strategy                           │
│    validate     Run validation pipeline                                     │
│    decide       Get orchestrator decision                                   │
│    deploy       Deploy strategy to stage                                    │
│    kill         Emergency stop                                              │
│                                                                             │
│  Monitoring:                                                                │
│    status       Show system status                                          │
│    positions    List current positions                                      │
│    orders       List pending orders                                         │
│    performance  Show performance metrics                                    │
│                                                                             │
│  Data:                                                                      │
│    list         List strategies/proposals/backtests                         │
│    show         Show detailed information                                   │
│    export       Export data to file                                         │
│                                                                             │
│  System:                                                                    │
│    config       Manage configuration                                        │
│    logs         View recent logs                                            │
│    clear        Clear screen                                                │
│    exit         Exit shell                                                  │
│                                                                             │
│  🦧 ukkie> status                                                           │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ System Status                                                        │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │ Uptime:        4h 23m 12s                                           │    │
│  │ Active Strats: 3                                                    │    │
│  │ Open Positions:1                                                    │    │
│  │ Today's PnL:   +$127.45 (+1.00%)                                    │    │
│  │                                                                     │    │
│  │ Components:                                                         │    │
│  │   Exchange    🟢 binance (latency: 45ms)                            │    │
│  │   Data Feed   🟢 streaming (last: 2s ago)                           │    │
│  │   Orchestrator🟢 ready                                              │    │
│  │   Database    🟢 sqlite (size: 234MB)                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  🦧 ukkie> show strategy STRAT-a3f8c2d1                                     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Strategy: STRAT-a3f8c2d1                                            │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │ Definition:                                                         │    │
│  │   Type:      MOMENTUM                                               │    │
│  │   Asset:     BTC/USDT                                               │    │
│  │   Timeframe: 1h                                                     │    │
│  │   Signal:    EMA Crossover (20/50)                                  │    │
│  │   Stop Loss: 2%                                                     │    │
│  │   Take Profit: 5%                                                   │    │
│  │                                                                     │    │
│  │ Performance (Backtest):                                             │    │
│  │   Sharpe:    1.23                                                   │    │
│  │   Max DD:    15.8%                                                  │    │
│  │   Win Rate:  52.2%                                                  │    │
│  │   CAGR:      14.2%                                                  │    │
│  │                                                                     │    │
│  │ Current Status:                                                     │    │
│  │   Stage:     LIVE                                                   │    │
│  │   Allocated: $1,000                                                 │    │
│  │   Live PnL:  +$847.32 (+84.7%)                                      │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  🦧 ukkie> exit                                                             │
│                                                                             │
│  🦧 Goodbye! Trade wisely, like an orangutan.                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.5 출력 포맷 옵션

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  OUTPUT FORMAT OPTIONS                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Global Flags:                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│  --format, -f     Output format: table (default), json, yaml, csv          │
│  --quiet, -q      Minimal output (IDs only)                                 │
│  --verbose, -v    Detailed output with debug info                           │
│  --no-color       Disable colored output                                    │
│  --output, -o     Write output to file                                      │
│                                                                             │
│  Examples:                                                                  │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  # JSON 출력 (스크립팅용)                                                    │
│  $ ukkie-trader list strategies --format json                               │
│  [                                                                          │
│    {                                                                        │
│      "strategy_id": "STRAT-a3f8c2d1",                                       │
│      "status": "LIVE",                                                      │
│      "asset": "BTC/USDT",                                                   │
│      "pnl": 847.32                                                          │
│    }                                                                        │
│  ]                                                                          │
│                                                                             │
│  # CSV 출력                                                                  │
│  $ ukkie-trader list positions --format csv -o positions.csv                │
│                                                                             │
│  # 조용한 출력 (ID만)                                                        │
│  $ ukkie-trader propose --quiet                                             │
│  PROP-20251223-001                                                          │
│                                                                             │
│  # 파이프라인 조합                                                           │
│  $ ukkie-trader list strategies -f json | jq '.[] | select(.pnl > 0)'       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 다음 파일: 06-deployment-testing.md

배포, 테스트 전략, 개발 로드맵
