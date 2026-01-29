import typer
import logging
from pathlib import Path
from ..core.engine import AnalysisEngine
from ..config import LOG_LEVEL

app = typer.Typer()

logging.basicConfig(level=getattr(logging, LOG_LEVEL))

@app.command()
def analyze(
    input_path: str = typer.Option(..., help="Path to input CSV/XLSX"),
    supplier: str = typer.Option(..., help="Supplier ID/Name (e.g. 'amtech')"),
    skip_browser: bool = typer.Option(True, help="Skip browser verification phase")
):
    """
    Runs the FBA Product Analysis Agent.
    """
    engine = AnalysisEngine()
    try:
        output_dir = engine.run_analysis(input_path, supplier, skip_browser)
        typer.echo(f"Success! Output generated at: {output_dir}")
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
