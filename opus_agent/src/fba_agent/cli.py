"""
FBA Agent CLI.

Command-line interface for the FBA Product Analysis Agent.
"""

import sys
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fba_agent import FBAAgent, Config

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="FBA Agent")
def cli():
    """FBA Product Analysis Agent - Deterministic FBA arbitrage analysis."""
    pass


@cli.command()
@click.option('--input', '-i', 'input_path', required=True, help='Path to input file (CSV/XLSX)')
@click.option('--supplier', '-s', 'supplier_id', help='Supplier identifier (auto-detected if not provided)')
@click.option('--output-dir', '-o', 'output_dir', help='Output directory (default: ./runs)')
@click.option('--skip-browser/--no-skip-browser', default=True, help='Skip browser verification (default: skip)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def analyze(input_path: str, supplier_id: str, output_dir: str, skip_browser: bool, verbose: bool):
    """
    Analyze a financial report for FBA opportunities.
    
    Example:
        python -m fba_agent analyze --input "C:\\path\\part_1_jan.xlsx" --skip-browser
    """
    try:
        config = Config()
        agent = FBAAgent(config)
        
        console.print(Panel.fit(
            f"[bold blue]FBA Product Analysis Agent[/bold blue]\n"
            f"Input: {input_path}",
            title="Starting Analysis"
        ))
        
        result = agent.analyze(
            input_path=input_path,
            supplier_id=supplier_id,
            output_dir=output_dir,
            skip_browser=skip_browser,
            verbose=verbose
        )
        
        # Display results
        summary = result['summary']
        
        console.print("\n[bold green]✅ Analysis Complete![/bold green]\n")
        
        # Show bucket counts
        table = Table(title="Bucket Distribution")
        table.add_column("Bucket", style="cyan")
        table.add_column("Count", justify="right")
        
        for bucket, count in summary.get('bucket_counts', {}).items():
            table.add_row(bucket, str(count))
        
        table.add_row("[bold]TOTAL[/bold]", f"[bold]{summary.get('row_count', 0)}[/bold]")
        console.print(table)
        
        # Show artifacts
        console.print("\n[bold]Generated Artifacts:[/bold]")
        for name, path in result.get('artifacts', {}).items():
            console.print(f"  • {name}: {path}")
        
        console.print(f"\n[dim]Run ID: {result['run_id']}[/dim]")
        console.print(f"[dim]Time: {summary.get('timing_ms', 0)}ms[/dim]")
        
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option('--run-id', '-r', required=True, help='Run ID to query')
@click.option('--min-confidence', '-c', default=70, help='Minimum confidence score')
@click.option('--limit', '-l', default=20, help='Maximum results to show')
@click.option('--bucket', '-b', help='Filter by bucket (VERIFIED, HIGHLY_LIKELY, etc.)')
def top(run_id: str, min_confidence: int, limit: int, bucket: str):
    """
    Show top candidates from a previous run.
    
    Example:
        python -m fba_agent top --run-id 20260104_153000 --min-confidence 80 --limit 30
    """
    try:
        config = Config()
        agent = FBAAgent(config)
        
        candidates = agent.get_top_candidates(
            run_id=run_id,
            min_confidence=min_confidence,
            limit=limit,
            bucket_filter=bucket
        )
        
        if not candidates:
            console.print(f"[yellow]No candidates found matching criteria[/yellow]")
            return
        
        table = Table(title=f"Top {len(candidates)} Candidates (Run: {run_id})")
        table.add_column("RowID", style="cyan", justify="right")
        table.add_column("Bucket", style="green")
        table.add_column("Conf", justify="right")
        table.add_column("Supplier Title")
        table.add_column("Adj Profit", justify="right")
        table.add_column("Evidence")
        
        for c in candidates:
            sup_title = c.get('supplier_attributes', {}).get('raw_title', '')[:40]
            table.add_row(
                str(c.get('row_id', '')),
                c.get('bucket', '')[:12],
                str(c.get('confidence', '')),
                sup_title + "..." if len(sup_title) == 40 else sup_title,
                f"£{c.get('adjusted_profit', 0):.2f}",
                c.get('key_match_evidence', '')[:30]
            )
        
        console.print(table)
        
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] Run not found: {run_id}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
@click.option('--run-id', '-r', required=True, help='Run ID to query')
@click.option('--rowid', '-i', required=True, type=int, help='RowID to explain')
def explain(run_id: str, rowid: int):
    """
    Explain the decision for a specific row.
    
    Example:
        python -m fba_agent explain --run-id 20260104_153000 --rowid 626
    """
    try:
        config = Config()
        agent = FBAAgent(config)
        
        record = agent.explain_row(run_id, rowid)
        
        console.print(Panel.fit(
            f"[bold]RowID {rowid}[/bold] - Run {run_id}",
            title="Row Explanation"
        ))
        
        # Basic info
        console.print(f"\n[bold]Decision:[/bold]")
        console.print(f"  Bucket: [cyan]{record.get('bucket')}[/cyan]")
        console.print(f"  Confidence: {record.get('confidence')}")
        console.print(f"  Pack Verdict: {record.get('pack_verdict')}")
        console.print(f"  Adjusted Profit: £{record.get('adjusted_profit', 0):.2f}")
        console.print(f"  RSU: {record.get('rsu', 1)}")
        
        # Match checks
        checks = record.get('match_checks', {})
        console.print(f"\n[bold]Match Checks:[/bold]")
        console.print(f"  Exact EAN Match: {'✅' if checks.get('is_exact_ean_strict') else '❌'}")
        console.print(f"  Brand Match: {'✅' if checks.get('brand_match') else '❌'}")
        console.print(f"  Product Match: {'✅' if checks.get('product_type_match') else '❌'}")
        console.print(f"  Pack Match: {'✅' if checks.get('pack_match') else '❌'}")
        
        # Titles
        sup_attrs = record.get('supplier_attributes', {})
        amz_attrs = record.get('amazon_attributes', {})
        console.print(f"\n[bold]Supplier Title:[/bold] {sup_attrs.get('raw_title', '')[:80]}")
        console.print(f"[bold]Amazon Title:[/bold] {amz_attrs.get('raw_title', '')[:80]}")
        
        # Trap detections
        traps = record.get('trap_detections', [])
        if traps:
            console.print(f"\n[bold]Trap Detections:[/bold]")
            for trap in traps:
                console.print(f"  • {trap.get('trap_type')}: {trap.get('pattern_matched')} → {trap.get('action_taken')}")
        
        # Evidence
        console.print(f"\n[bold]Key Match Evidence:[/bold] {record.get('key_match_evidence', '-')}")
        console.print(f"[bold]Filter Reason:[/bold] {record.get('filter_reason', '-')}")
        
        if record.get('required_next_action'):
            console.print(f"[bold]Required Action:[/bold] {record.get('required_next_action')}")
        
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@cli.command('export')
@click.option('--run-id', '-r', required=True, help='Run ID to export')
@click.option('--format', '-f', 'fmt', type=click.Choice(['md', 'csv', 'json']), default='md', help='Export format')
@click.option('--output', '-o', 'output_path', help='Output file path')
def export_cmd(run_id: str, fmt: str, output_path: str):
    """
    Export results in different formats.
    
    Example:
        python -m fba_agent export --run-id 20260104_153000 --format csv
    """
    try:
        config = Config()
        run_dir = config.default_output_dir / run_id
        
        if not run_dir.exists():
            console.print(f"[bold red]Error:[/bold red] Run not found: {run_id}")
            sys.exit(1)
        
        if fmt == 'md':
            source = run_dir / f"PHASEA_MANUAL_REPORT_{run_id[:8]}.md"
            # Find the actual report file
            for f in run_dir.glob("PHASEA_MANUAL_REPORT_*.md"):
                source = f
                break
        elif fmt == 'csv':
            source = run_dir / "coverage_ledger.csv"
        elif fmt == 'json':
            source = run_dir / "run_summary.json"
        
        if not source.exists():
            console.print(f"[bold red]Error:[/bold red] Source file not found: {source}")
            sys.exit(1)
        
        if output_path:
            import shutil
            shutil.copy(source, output_path)
            console.print(f"[green]✅ Exported to: {output_path}[/green]")
        else:
            console.print(source.read_text(encoding='utf-8'))
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@cli.command('list-runs')
def list_runs():
    """
    List all previous runs.
    
    Example:
        python -m fba_agent list-runs
    """
    try:
        config = Config()
        agent = FBAAgent(config)
        
        runs = agent.list_runs()
        
        if not runs:
            console.print("[yellow]No runs found.[/yellow]")
            return
        
        table = Table(title="Previous Runs")
        table.add_column("Run ID", style="cyan")
        table.add_column("Input File")
        table.add_column("Rows", justify="right")
        table.add_column("Valid", justify="center")
        table.add_column("Created")
        
        for run in runs:
            table.add_row(
                run.get('run_id', ''),
                Path(run.get('input_file', '')).name[:30],
                str(run.get('row_count', 0)),
                "✅" if run.get('validation_passed') else "❌",
                run.get('created_at', '')[:19]
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
