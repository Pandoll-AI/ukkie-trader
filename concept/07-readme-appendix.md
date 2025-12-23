# Ukkie-Trader 개발 계획서 Part 7: README 구조 및 부록

---

## 11. README.md 구조

```markdown
# 🦧 Ukkie-Trader

```
                            ██████████                          
                        ████▓▓▓▓▓▓▓▓▓▓████                      
                      ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██                    
                    ██▓▓▓▓██████████████▓▓▓▓██                  
                  ██▓▓████              ████▓▓██                
                ██▓▓██    ████    ████    ██▓▓██                
                ██▓▓██    ████    ████    ██▓▓██                
                ██▓▓██                    ██▓▓██                
                  ██▓▓████    ████    ████▓▓██                  
                    ██▓▓▓▓████████████▓▓▓▓██                    
                ████  ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓██  ████                  
              ██▓▓██    ████████████    ██▓▓██                  
              ██▓▓▓▓██                ██▓▓▓▓██                  
                ██▓▓▓▓████████████████▓▓▓▓██                    
                  ████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████                      
                      ████████████████                          
```

> **"신중한 오랑우탄처럼 거래하라"**
> 
> 오랑우탄은 영장류 중 가장 신중한 동물입니다. 나무 사이를 이동할 때 항상 다음 가지를 
> 확인하고, 안전이 보장될 때만 움직입니다. Ukkie-Trader는 이 철학을 트레이딩에 적용합니다.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

---

## 🎯 핵심 원칙

| 원칙 | 설명 |
|------|------|
| 🔒 **Definition-First** | 모든 파라미터가 정의되기 전에는 거래 없음 |
| 🔍 **Multi-Agent Validation** | 10개 에이전트가 독립적으로 검증 |
| 🌤️ **Regime-Aware** | 시장 상태(변동성, 유동성)에 따른 전략 조정 |
| 🐢 **Progressive Deployment** | Shadow → Paper → Live → Production |

---

## ⚡ 빠른 시작

### 설치

```bash
# pipx 권장 (격리된 환경)
pipx install ukkie-trader

# 또는 pip
pip install ukkie-trader
```

### 첫 번째 전략

```bash
# 1. 전략 제안
ukkie-trader propose --idea "BTC EMA crossover" --asset BTC/USDT --timeframe 1h

# 2. 정의 동결
ukkie-trader freeze PROP-20251223-001 --stop-loss 0.02 --take-profit 0.05

# 3. 검증 실행
ukkie-trader validate STRAT-a3f8c2d1

# 4. 결정 확인
ukkie-trader decide STRAT-a3f8c2d1

# 5. Shadow 배포
ukkie-trader deploy STRAT-a3f8c2d1 --stage shadow
```

---

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI (Typer + Rich)                     │
├─────────────────────────────────────────────────────────────┤
│                         AGENTS                              │
│  ┌──────────┐ ┌────────┐ ┌────────┐ ┌──────────┐           │
│  │ Proposer │→│Freezer │→│ DataQA │→│ Backtest │→ ...      │
│  └──────────┘ └────────┘ └────────┘ └──────────┘           │
│                         ↓                                   │
│                   ORCHESTRATOR                              │
│              (Hard Gates + Soft Scoring)                    │
├─────────────────────────────────────────────────────────────┤
│                    DOMAIN LAYER                             │
│  Strategy │ Position │ Order │ Risk │ Backtest Engine       │
├─────────────────────────────────────────────────────────────┤
│                  INFRASTRUCTURE                             │
│  SQLite │ Exchange Adapters │ Data Cache │ Logging          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 10개 에이전트

### Research Phase
1. **Proposer** - 전략 아이디어 구조화
2. **Definition Freezer** - 파라미터 동결 & 해시 생성
3. **Data QA** - 데이터 품질 검증

### Validation Phase
4. **Backtest** - 역사적 시뮬레이션
5. **Cost/Slippage** - 거래 비용 추정
6. **Execution Sim** - 체결 정책 시뮬레이션
7. **Risk/Stress** - 위기 시나리오 테스트
8. **Overfit Audit** - 과최적화 탐지
9. **Portfolio/Capacity** - 포트폴리오 적합성

### Decision
10. **Orchestrator** - 최종 승인/거부 결정

---

## 📊 Hard Gates (통과 필수)

| Gate | Threshold | Source |
|------|-----------|--------|
| Fill Rate | ≥ 95% | Execution Sim |
| Slippage | ≤ 50 bps | Cost/Slippage |
| Max Drawdown | ≤ 15% | Backtest |
| Loss Streak | ≤ 30 days | Backtest |
| Tail Loss (p99) | ≤ 10% | Risk/Stress |

---

## 🛠️ 주요 CLI 명령어

```bash
ukkie-trader propose      # 새 전략 제안
ukkie-trader freeze       # 정의 동결
ukkie-trader validate     # 검증 파이프라인 실행
ukkie-trader decide       # 오케스트레이터 결정
ukkie-trader deploy       # 배포 (shadow/paper/live)
ukkie-trader monitor      # 실시간 모니터링
ukkie-trader kill         # 긴급 중지
```

---

## ⚠️ 면책 조항

이 소프트웨어는 교육 및 연구 목적으로 제공됩니다. 실제 자금으로 거래할 경우 
손실이 발생할 수 있습니다. 투자 결정에 대한 책임은 전적으로 사용자에게 있습니다.

---

## 📜 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일 참조

---

## 🤝 기여

기여를 환영합니다! [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

---

*신중한 오랑우탄처럼 거래하세요.* 🦧
```

---

## 12. 부록

### 12.1 용어집

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  GLOSSARY                                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TRADING TERMS                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  ADV (Average Daily Volume)                                                 │
│    일평균 거래량. 자산의 유동성 측정 지표.                                    │
│                                                                             │
│  Basis Point (bps)                                                          │
│    0.01%. 1 bps = 0.0001. 비용/수익률 미세 측정에 사용.                      │
│                                                                             │
│  CAGR (Compound Annual Growth Rate)                                         │
│    연평균 복리 수익률. 전략의 장기 성과 측정.                                 │
│                                                                             │
│  Calmar Ratio                                                               │
│    CAGR / Max Drawdown. 위험 대비 수익률.                                   │
│                                                                             │
│  CVaR (Conditional Value at Risk)                                           │
│    Expected Shortfall. VaR 초과 손실의 평균.                                │
│                                                                             │
│  Drawdown                                                                   │
│    고점 대비 하락폭. Max Drawdown은 최대 낙폭.                               │
│                                                                             │
│  Fill Rate                                                                  │
│    주문 체결률. 제출된 주문 중 체결된 비율.                                  │
│                                                                             │
│  Profit Factor                                                              │
│    총 이익 / 총 손실. 1 이상이면 수익.                                       │
│                                                                             │
│  Sharpe Ratio                                                               │
│    (Return - Risk-free) / Volatility. 위험 조정 수익률.                     │
│                                                                             │
│  Slippage                                                                   │
│    예상 체결가와 실제 체결가의 차이.                                         │
│                                                                             │
│  Sortino Ratio                                                              │
│    Sharpe와 유사하나 하방 변동성만 고려.                                     │
│                                                                             │
│  Ulcer Index                                                                │
│    Drawdown 기간과 깊이를 결합한 고통 지수.                                  │
│                                                                             │
│  VaR (Value at Risk)                                                        │
│    특정 신뢰수준에서 예상되는 최대 손실.                                     │
│                                                                             │
│  Win Rate                                                                   │
│    수익 거래 비율. 승률.                                                     │
│                                                                             │
│  SYSTEM TERMS                                                               │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  Agent                                                                      │
│    특정 검증 작업을 수행하는 독립 모듈.                                      │
│                                                                             │
│  Definition Hash                                                            │
│    전략 정의의 SHA256 해시. 변경 감지용.                                     │
│                                                                             │
│  Frozen Strategy                                                            │
│    모든 파라미터가 확정되어 불변인 전략 정의.                                │
│                                                                             │
│  Hard Gate                                                                  │
│    통과 필수 조건. 하나라도 실패하면 거부.                                   │
│                                                                             │
│  Kill Switch                                                                │
│    긴급 상황 시 모든 거래를 즉시 중단.                                       │
│                                                                             │
│  Orchestrator                                                               │
│    모든 에이전트 결과를 종합하여 최종 결정.                                  │
│                                                                             │
│  Proposal                                                                   │
│    초기 전략 아이디어. 아직 파라미터 미확정.                                 │
│                                                                             │
│  Regime                                                                     │
│    시장 상태. NORMAL, VOLATILE, ILLIQUID, EVENT.                            │
│                                                                             │
│  Shadow Trading                                                             │
│    실제 거래 없이 시그널만 로깅.                                             │
│                                                                             │
│  Soft Score                                                                 │
│    가중치 기반 종합 점수. 높을수록 우수.                                     │
│                                                                             │
│  Walk-Forward                                                               │
│    시간순 분할로 과최적화 검증.                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 12.2 기술 참조

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TECHNICAL REFERENCES                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PAPERS & BOOKS                                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  [1] Bailey, D. H., & López de Prado, M. (2014).                            │
│      "The Deflated Sharpe Ratio: Correcting for Selection Bias,             │
│      Backtest Overfitting and Non-Normality."                               │
│      Journal of Portfolio Management.                                       │
│                                                                             │
│  [2] López de Prado, M. (2018).                                             │
│      "Advances in Financial Machine Learning."                              │
│      Wiley.                                                                 │
│                                                                             │
│  [3] Chan, E. (2013).                                                       │
│      "Algorithmic Trading: Winning Strategies and Their Rationale."         │
│      Wiley.                                                                 │
│                                                                             │
│  [4] Aronson, D. (2006).                                                    │
│      "Evidence-Based Technical Analysis."                                   │
│      Wiley.                                                                 │
│                                                                             │
│  LIBRARIES & TOOLS                                                          │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  • CCXT: Unified cryptocurrency exchange API                                │
│    https://github.com/ccxt/ccxt                                             │
│                                                                             │
│  • Polars: Fast DataFrame library                                           │
│    https://www.pola.rs/                                                     │
│                                                                             │
│  • Typer: CLI framework                                                     │
│    https://typer.tiangolo.com/                                              │
│                                                                             │
│  • Rich: Terminal formatting                                                │
│    https://rich.readthedocs.io/                                             │
│                                                                             │
│  • Hypothesis: Property-based testing                                       │
│    https://hypothesis.readthedocs.io/                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 12.3 FAQ

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  FREQUENTLY ASKED QUESTIONS                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Q: 왜 오랑우탄인가요?                                                       │
│  ─────────────────────────────────────────────────────────────────────────  │
│  A: 오랑우탄은 영장류 중 가장 신중합니다. 나무 사이를 이동할 때 항상 다음     │
│     가지를 테스트하고, 안전이 확인될 때만 움직입니다. 이 철학이 트레이딩에    │
│     적합합니다. 또한 "Ukkie"는 오랑우탄의 귀여운 별명입니다.                 │
│                                                                             │
│  Q: 왜 10개나 되는 에이전트가 필요한가요?                                     │
│  ─────────────────────────────────────────────────────────────────────────  │
│  A: 각 에이전트는 다른 관점에서 전략을 검증합니다. 백테스트만으로는 비용,     │
│     실행, 리스크, 과최적화 등을 포착할 수 없습니다. 다중 관점 검증이         │
│     생존 확률을 높입니다.                                                    │
│                                                                             │
│  Q: Hard Gate와 Soft Score의 차이는?                                        │
│  ─────────────────────────────────────────────────────────────────────────  │
│  A: Hard Gate는 "필수 조건"입니다. 하나라도 실패하면 전략은 거부됩니다.      │
│     Soft Score는 "우선순위"입니다. 여러 전략이 Hard Gate를 통과했을 때       │
│     어떤 것이 더 나은지 비교합니다.                                          │
│                                                                             │
│  Q: Shadow와 Paper 트레이딩의 차이는?                                        │
│  ─────────────────────────────────────────────────────────────────────────  │
│  A: Shadow는 시그널만 로깅하고 주문을 제출하지 않습니다. Paper는 실제로      │
│     Testnet에 주문을 제출하지만 실제 자금은 사용하지 않습니다.               │
│                                                                             │
│  Q: 실거래까지 얼마나 걸리나요?                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│  A: 권장 경로: Shadow 2주 → Paper 4주 → Live (소액) 4주 → Production.        │
│     최소 10주. 조급함은 손실의 지름길입니다.                                 │
│                                                                             │
│  Q: 어떤 전략이 지원되나요?                                                  │
│  ─────────────────────────────────────────────────────────────────────────  │
│  A: v1.0에서는 단일 자산 모멘텀/평균회귀 전략만 지원합니다. 향후 다중 자산,  │
│     선물, 옵션 전략을 추가할 계획입니다.                                     │
│                                                                             │
│  Q: 과최적화를 어떻게 방지하나요?                                            │
│  ─────────────────────────────────────────────────────────────────────────  │
│  A: 세 가지 방법:                                                            │
│     1. Walk-Forward 분석: 시간순 분할로 테스트                               │
│     2. Deflated Sharpe: 테스트 횟수에 따른 보정                              │
│     3. Randomization Test: 우연 대비 통계적 유의성 확인                      │
│                                                                             │
│  Q: Kill Switch는 언제 작동하나요?                                           │
│  ─────────────────────────────────────────────────────────────────────────  │
│  A: 다음 조건 중 하나라도 충족 시:                                            │
│     - MDD > 10% (설정 가능)                                                  │
│     - 연속 손실 5회 이상                                                     │
│     - 데이터 지연 5분 이상                                                   │
│     - 스프레드 평소 3배 이상                                                 │
│     - 수동 트리거 (`ukkie-trader kill`)                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 12.4 변경 이력

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CHANGE LOG                                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [v0.1.0-DRAFT] - 2025-12-23                                                │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Initial draft of development plan document.                                │
│                                                                             │
│  Added:                                                                     │
│  - Project overview and philosophy                                          │
│  - System architecture                                                      │
│  - 10 agent specifications                                                  │
│  - Data models and DB schema                                                │
│  - Core algorithms (state machine, cost model, UCB1)                        │
│  - CLI interface design                                                     │
│  - Deployment and packaging                                                 │
│  - Testing strategy                                                         │
│  - Development roadmap                                                      │
│  - README structure                                                         │
│  - Glossary and appendices                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 문서 종료

이 개발 계획서는 Ukkie-Trader 프로젝트의 전체 청사진을 담고 있습니다.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                           ██████████                                        │
│                       ████▓▓▓▓▓▓▓▓▓▓████                                    │
│                     ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██                                  │
│                   ██▓▓▓▓██████████████▓▓▓▓██                                │
│                 ██▓▓████              ████▓▓██                              │
│               ██▓▓██    ████    ████    ██▓▓██                              │
│               ██▓▓██    ████    ████    ██▓▓██                              │
│               ██▓▓██                    ██▓▓██                              │
│                 ██▓▓████    ████    ████▓▓██                                │
│                   ██▓▓▓▓████████████▓▓▓▓██                                  │
│               ████  ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓██  ████                                │
│             ██▓▓██    ████████████    ██▓▓██                                │
│             ██▓▓▓▓██                ██▓▓▓▓██                                │
│               ██▓▓▓▓████████████████▓▓▓▓██                                  │
│                 ████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████                                    │
│                     ████████████████                                        │
│                                                                             │
│                      🦧 Happy Trading! 🦧                                   │
│                                                                             │
│               "신중한 오랑우탄처럼 거래하라"                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```
