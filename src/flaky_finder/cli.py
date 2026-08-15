from pathlib import Path
import click
from rich.console import Console
from rich.table import Table

from flaky_finder.visitor import analyze_code

console = Console()


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
def main(paths):
    """Flaky Finder: Diagnose potential flaky tests via AST analysis."""
    if not paths:
        console.print("[yellow]Please provide target files or directories.[/yellow]")
        return

    total_issues = 0

    for path_str in paths:
        path = Path(path_str)
        target_files = path.rglob("*.py") if path.is_dir() else [path]

        for file_path in target_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                issues = analyze_code(content)
                if issues:
                    total_issues += len(issues)
                    table = Table(title=f"Issues in {file_path}")
                    table.add_column("Line", style="cyan", justify="right")
                    table.add_column("Rule", style="magenta")
                    table.add_column("Diagnostic Message", style="white")

                    for issue in issues:
                        table.add_row(
                            str(issue.line), issue.rule_id, issue.message
                        )

                    console.print(table)
                    console.print()
            except Exception as e:
                console.print(f"[red]Error parsing {file_path}: {e}[/red]")

    if total_issues == 0:
        console.print("[bold green]✨ No obvious flaky patterns found![/bold green]")
    else:
        console.print(
            f"[bold red]❌ Found {total_issues} potential issues.[/bold red]"
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()