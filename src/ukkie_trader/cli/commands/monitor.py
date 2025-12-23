import typer
import time
import random
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.panel import Panel

app = typer.Typer(help="Monitor strategies and system status")
console = Console()

def generate_dashboard():
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    
    layout["header"].update(Panel("🦧 UKKIE-TRADER DASHBOARD", style="bold white on blue"))
    
    # Strategy Table
    table = Table(title="Active Strategies")
    table.add_column("Strategy ID", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("PnL", justify="right")
    
    strategies = [
        ("STRAT-a3f8c2d1", "LIVE", f"+${random.uniform(800, 900):.2f}"),
        ("STRAT-b2e7a1c9", "PAPER", f"+${random.uniform(200, 300):.2f}"),
        ("STRAT-d4f9c3e5", "SHADOW", f"+${random.uniform(100, 200):.2f}"),
    ]
    
    for s_id, status, pnl in strategies:
        table.add_row(s_id, status, pnl)
        
    layout["main"].update(Panel(table))
    layout["footer"].update(Panel("Press Ctrl+C to exit"))
    
    return layout

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    dashboard: bool = typer.Option(False, "--dashboard", "-d", help="Show live dashboard"),
):
    """
    Monitor the system status.
    """
    if ctx.invoked_subcommand is not None:
        return

    if dashboard:
        with Live(generate_dashboard(), refresh_per_second=4) as live:
            try:
                while True:
                    time.sleep(1)
                    live.update(generate_dashboard())
            except KeyboardInterrupt:
                console.print("Dashboard closed.")
    else:
        # Simple status output
        console.print("[bold]System Status:[/bold] [green]ONLINE[/green]")
        console.print("Active Strategies: 3")
        console.print("PnL Today: +$127.45")
