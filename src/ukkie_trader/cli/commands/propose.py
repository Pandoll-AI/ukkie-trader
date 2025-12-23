import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

app = typer.Typer(help="Propose a new trading strategy")
console = Console()

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    idea: str = typer.Option(None, "--idea", help="Description of the strategy idea"),
    asset: str = typer.Option(None, "--asset", help="Target asset (e.g., BTC/USDT)"),
    timeframe: str = typer.Option(None, "--timeframe", help="Trading timeframe"),
):
    """
    Propose a new strategy idea for validation.
    """
    if ctx.invoked_subcommand is not None:
        return

    console.print(Panel("[bold yellow]🦧 Strategy Proposer[/bold yellow]", border_style="yellow"))
    
    if not idea:
        idea = Prompt.ask("Describe your strategy idea")
    
    if not asset:
        asset = Prompt.ask("Select asset", choices=["BTC/USDT", "ETH/USDT", "SOL/USDT"], default="BTC/USDT")
        
    if not timeframe:
        timeframe = Prompt.ask("Select timeframe", choices=["1h", "4h", "1d"], default="1h")
        
    console.print("\n[bold green]✓ Proposal Created[/bold green]")
    console.print(f"Proposal ID: [cyan]PROP-20251223-001[/cyan]")
    console.print(f"Status: [yellow]PROPOSED[/yellow]")
    console.print(f"Asset: [white]{asset}[/white]")
    console.print(f"Timeframe: [white]{timeframe}[/white]")
    console.print(f"Idea: [italic]{idea}[/italic]")
    
    console.print("\nNext step: [bold cyan]ukkie-trader freeze PROP-20251223-001[/bold cyan]")
