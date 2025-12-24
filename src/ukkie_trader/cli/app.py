import typer
from rich.console import Console
from ukkie_trader import __version__
from rich.panel import Panel
from rich.text import Text
from typing import Optional, List
from datetime import datetime
import asyncio

# Import commands (to be created)
# from ukkie_trader.cli.commands import strategy

app = typer.Typer(
    help="Ukkie Trader: The Deliberate Orangutan Trading Bot",
    add_completion=False,
)

console = Console()

def show_splash():
    splash = Text("\nUKKIE TRADER\n", style="bold orange1")
    splash.append("The Deliberate Orangutan\n", style="italic gray50")
    splash.append("-" * 30 + "\n", style="gray30")
    splash.append("1. Deliberation\n2. Observer from Above\n3. Selective Picking\n", style="bold")
    
    console.print(Panel(splash, border_style="orange1", expand=False))

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(None, "--version", "-v", help="Show version"),
):
    if version:
        console.print(f"Ukkie Trader v{__version__}")
        raise typer.Exit()
    
    if ctx.invoked_subcommand is None:
        show_splash()
        console.print("\nUse [bold]ukkie --help[/bold] for available commands.")

# Instead of importing, we'll define a few commands here for the initial setup
# and then move them to separate files as the project grows.

@app.command()
def zen():
    """
    🍌 Print the Zen of Ukkie Trader (Korean).
    """
    zen_text = """
# 🍌 1) 퀀트 전략 = “바나나 냄새 나는 규칙” 찾기 (우끼우끼)

[bold white]퀀트는 어려운 수학이 핵심이 아니라, 규칙이 핵심이다. 우끼우끼.[/bold white]

## 오랑우탄이 보는 전략의 뼈대는 딱 4개:

[green]• 언제 들어가? (진입)[/green]
[green]• 언제 나가? (청산)[/green]
[green]• 얼마나 들어가? (사이징)[/green]
[green]• 언제 멈춰? (리스크 컷)[/green]

[italic yellow]“바나나 냄새 나면 들고 간다. 냄새 없으면 던진다. 우끼우끼.”[/italic yellow]

# 🍌 2) 좋은 전략 조건: 오랑우탄 체크리스트

## A. 엣지는 “진짜 바나나”여야 한다
[white]겉으로 노란 돌멩이 = 바나나 아님[/white]
[white]수수료/슬리피지/임팩트 다 빼고도 남아야 엣지다[/white]
[italic yellow]“먹었는데 배 안 차면 가짜다. 우끼우끼.”[/italic yellow]

## B. 리스크는 “생존”이 먼저다
[white]수익률 보기 전에 먼저 보는 것:[/white]
[white]• MDD(한 번에 얼마나 깨지나)[/white]
[white]• 연속 손실 구간(얼마나 오래 굶나)[/white]
[white]• 꼬리 리스크(갑자기 절벽에서 떨어지나)[/white]
[italic yellow]“한 방에 죽으면 나쁜 전략. 오래 살아남으면 좋은 전략. 우끼우끼.”[/italic yellow]

## C. 실행이 쉬워야 한다 (손이 닿아야 먹는다)
[white]신호가 좋아도 체결이 안 되면 그냥 상상이다.[/white]
[italic yellow]“나무 위에서 바나나 봤는데 손이 안 닿으면 굶는다. 우끼우끼.”[/italic yellow]

# 🍌 3) 오랑우탄이 좋아하는 단순 강한 뼈대 3개

## 1) 모멘텀(추세추종)
[white]오르면 더 오르고, 내리면 더 내리는 경향을 탄다[/white]
[italic yellow]“무리(추세) 따라가면 산다. 근데 숲이 가만히면 계속 헛친다.”[/italic yellow]

## 2) 평균회귀(Mean Reversion)
[white]너무 벌어지면 다시 붙는 성질을 먹는다[/white]
[italic yellow]“가지 휘면 원래 돌아오는데, 부러지는 순간이면 같이 떨어진다.”[/italic yellow]

## 3) 캐리/펀딩/베이시스
[white]구조적으로 돈이 새는 곳을 받아먹는 느낌[/white]
[italic yellow]“매일 바나나 조금씩 주는 나무도, 어느 날 독나무로 바뀐다.”[/italic yellow]

# 🍌 4) 오랑우탄식 초간단 전략 설계 예시

[white]신호: 24시간 돌파(추세) + IV가 기준보다 높음[/white]
[white]진입: 상방 돌파면 롱 / 하방 돌파면 숏[/white]
[white]청산: 반대 돌파 + 변동성 죽으면 청산[/white]
[white]사이징: 변동성 타겟팅(조용하면 크게, 시끄러우면 작게)[/white]

[bold green]오랑우탄 한 줄 요약:[/bold green]
[italic yellow]“움직일 때만 타고, 시끄러우면 작게 타고, 이상하면 나무에서 내려온다. 우끼우끼.”[/italic yellow]

# 🍌 5) 오랑우탄이 빠지는 함정 5개
[red]• 백테스트가 너무 좋음 → 과최적화 가능성 큼[/red]
[red]• 거래비용을 장식으로 넣음 → 실전에서 사망[/red]
    """
    from rich.markdown import Markdown
    console.print(Panel(Markdown(zen_text), title="🍌 Zen of Ukkie", border_style="purple"))

@app.command()
def propose(
    name: str = typer.Option(..., help="Strategy name"),
    asset: str = typer.Option("BTC/USDT", help="Trading asset"),
    exchange: str = typer.Option("Binance", help="Exchange"),
):
    """Propose a new strategy idea."""
    from ukkie_trader.agents.proposer import ProposerAgent, ProposerInput
    from ukkie_trader.infra.db.sqlite import Database, StrategyRepository
    
    agent = ProposerAgent()
    db = Database()
    repo = StrategyRepository(db)
    
    async def _run():
        input_data = ProposerInput(
            name=name,
            asset=asset,
            exchange=exchange,
            raw_idea={"strategy_type": "TREND_FOLLOWING"} # Default for MVP
        )
        proposal = await agent.run(input_data)
        repo.save_proposal(proposal)
        console.print(f"[green]✔[/green] Proposal created: [bold]{proposal.proposal_id}[/bold]")
        console.print(f"Name: {proposal.name} | Asset: {proposal.asset} | Status: {proposal.status}")

    asyncio.run(_run())

@app.command()
def freeze(
    proposal_id: str = typer.Argument(..., help="ID of the proposal to freeze"),
):
    """Freeze a strategy proposal to create an immutable definition."""
    from ukkie_trader.agents.freezer import FreezerAgent
    from ukkie_trader.infra.db.sqlite import Database, StrategyRepository
    
    db = Database()
    repo = StrategyRepository(db)
    
    # 1. Fetch proposal
    # (Simulating fetch since repo.get_proposals returns list)
    rows = repo.get_proposals()
    proposal_row = next((r for r in rows if r["proposal_id"] == proposal_id), None)
    
    if not proposal_row:
        console.print(f"[red]Error:[/red] Proposal {proposal_id} not found.")
        raise typer.Exit()

    from ukkie_trader.domain.strategy.definition import StrategyProposal
    import json
    
    proposal = StrategyProposal(
        proposal_id=proposal_row["proposal_id"],
        name=proposal_row["name"],
        asset=proposal_row["asset"],
        exchange=proposal_row["exchange"],
        raw_idea=json.loads(proposal_row["raw_idea"]),
        status=proposal_row["status"]
    )
    
    # 2. Run Freezer
    agent = FreezerAgent()
    
    async def _run():
        frozen = await agent.run(proposal)
        repo.save_frozen_strategy(frozen)
        console.print(f"[green]✔[/green] Strategy frozen: [bold]{frozen.strategy_id}[/bold]")
        console.print(f"Hash: [blue]{frozen.definition_hash[:16]}...[/blue]")
        console.print(f"Status: {frozen.status}")

    asyncio.run(_run())

@app.command()
def list():
    """List all proposals and frozen strategies."""
    from ukkie_trader.infra.db.sqlite import Database, StrategyRepository
    db = Database()
    repo = StrategyRepository(db)
    
    proposals = repo.get_proposals()
    
    from rich.table import Table
    table = Table(title="Ukkie Trader - Strategies")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Asset")
    table.add_column("Status", style="green")
    
    for p in proposals:
        table.add_row(p["proposal_id"], p["name"], p["asset"], p["status"])
    
    console.print(table)

@app.command()
def validate(
    strategy_id: str = typer.Argument(..., help="ID of the strategy to validate"),
):
    """Run the 10-agent validation pipeline (MVP: Data QA, Backtest, Orchestrator)."""
    from ukkie_trader.infra.db.sqlite import Database, StrategyRepository
    from ukkie_trader.agents.data_qa import DataQAAgent, DataQAInput
    from ukkie_trader.agents.backtest import BacktestAgent, BacktestInput
    from ukkie_trader.agents.cost_slippage import CostSlippageAgent, CostSlippageInput
    from ukkie_trader.agents.overfit_audit import OverfitAuditAgent, OverfitAuditInput
    from ukkie_trader.agents.orchestrator import OrchestratorAgent, OrchestratorInput
    from ukkie_trader.domain.strategy.definition import FrozenStrategy, FrozenDefinition
    import pandas as pd
    import numpy as np
    
    db = Database()
    repo = StrategyRepository(db)
    
    # 1. Fetch Frozen Strategy
    with db._get_connection() as conn:
        row = conn.execute("SELECT * FROM frozen_strategies WHERE strategy_id = ?", (strategy_id,)).fetchone()
    
    if not row:
        console.print(f"[red]Error:[/red] Strategy {strategy_id} not found.")
        raise typer.Exit()
        
    import json
    # Use pydantic to parse JSON
    frozen_def_dict = json.loads(row["frozen_definition"])
    frozen_def = FrozenDefinition.model_validate(frozen_def_dict)
    
    strategy = FrozenStrategy(
        strategy_id=row["strategy_id"],
        proposal_id=row["proposal_id"],
        definition_hash=row["definition_hash"],
        frozen_definition=frozen_def,
        frozen_at=datetime.fromisoformat(row["frozen_at"]),
        status=row["status"]
    )
    
    # 2. Mock Market Data (Still using mock for local CLI validation speed)
    dates = pd.date_range(start="2023-01-01", periods=1100, freq="h")
    prices = 20000 + np.cumsum(np.random.standard_normal(1100) * 100)
    df = pd.DataFrame({"close": prices, "volume": np.random.randint(100, 1000, 1100)}, index=dates)
    returns = np.diff(np.log(df['close'].values))
    
    async def _run_pipeline():
        with console.status("[bold green]Running 10-Agent Validation Pipeline...") as status:
            # Agent 1: Data QA
            status.update("[bold blue]Agent 1: Data QA...")
            qa_agent = DataQAAgent()
            qa_result = await qa_agent.run(DataQAInput(strategy=strategy, data=df))
            console.print(f"  [green]✔[/green] Data QA: {qa_result.qa_status}")
            
            # Agent 2: Backtest
            status.update("[bold blue]Agent 2: Backtest Engine...")
            bt_agent = BacktestAgent()
            bt_result = await bt_agent.run(BacktestInput(strategy=strategy, data=df))
            console.print(f"  [green]✔[/green] Backtest: Return {bt_result.summary_metrics.total_return:.2f}%")
            
            # Agent 3: Cost/Slippage
            status.update("[bold blue]Agent 3: Cost/Slippage Impact...")
            cost_agent = CostSlippageAgent()
            cost_result = await cost_agent.run(CostSlippageInput(strategy=strategy, backtest_result=bt_result))
            console.print(f"  [green]✔[/green] Cost Impact: -{cost_result['cost_summary']['total_impact_usd']:.2f} USD")

            # Agent 4: Overfit Audit
            status.update("[bold blue]Agent 4: Overfit Audit (DSR)...")
            overfit_agent = OverfitAuditAgent()
            overfit_result = await overfit_agent.run(OverfitAuditInput(
                strategy=strategy, 
                backtest_result=bt_result, 
                returns=returns.tolist()
            ))
            rating_color = "green" if overfit_result["overfit_rating"] == "LOW" else "yellow"
            console.print(f"  [green]✔[/green] Overfit Audit: [{rating_color}]Rating {overfit_result['overfit_rating']}[/{rating_color}] (DSR: {overfit_result['deflated_sharpe']:.2f})")

            # Agent 10: Orchestrator
            status.update("[bold blue]Agent 10: Orchestrator (Decision)...")
            orch_agent = OrchestratorAgent()
            # In real, would pass all results
            decision = await orch_agent.run(OrchestratorInput(strategy=strategy, backtest_result=bt_result))
            
            from rich.table import Table
            gate_table = Table(title="Hard Gates Analysis")
            gate_table.add_column("Metric")
            gate_table.add_column("Value")
            gate_table.add_column("Threshold")
            gate_table.add_column("Status")
            
            for gate in decision.hard_gate_results:
                status_str = "[green]PASS[/green]" if gate.passed else "[red]FAIL[/red]"
                gate_table.add_row(gate.metric, f"{gate.value:.2f}", f"{gate.threshold:.2f}", status_str)
            
            console.print(gate_table)
            
            final_style = "bold green" if decision.hard_gate_passed else "bold red"
            console.print(Panel(f"FINAL DECISION: [white on {final_style.split()[-1]}] {decision.decision} [/white on {final_style.split()[-1]}]", border_style=final_style))

    asyncio.run(_run_pipeline())

if __name__ == "__main__":
    app()
