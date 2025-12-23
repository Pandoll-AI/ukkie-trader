import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from typing import Optional
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
        console.print("Ukkie Trader v1.0.0")
        raise typer.Exit()
    
    if ctx.invoked_subcommand is None:
        show_splash()
        console.print("\nUse [bold]ukkie --help[/bold] for available commands.")

# Instead of importing, we'll define a few commands here for the initial setup
# and then move them to separate files as the project grows.

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
