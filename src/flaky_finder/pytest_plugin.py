import pytest
from rich.console import Console
from rich.table import Table
from flaky_finder.visitor import analyze_code

console = Console()


def pytest_addoption(parser):
    """Add command line flags to pytest."""
    group = parser.getgroup("flaky-finder")
    group.addoption(
        "--check-flaky",
        action="store_true",
        default=False,
        help="Run AST static analysis to detect potential flaky test patterns before running tests.",
    )
    group.addoption(
        "--flaky-fail",
        action="store_true",
        default=False,
        help="Fail the pytest execution if any flaky patterns are detected.",
    )


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "flaky_check: static analysis for flaky test detection"
    )


def pytest_collection_modifyitems(session, config, items):
    """Intercept collected pytest items and analyze their AST source code."""
    if not config.getoption("--check-flaky"):
        return

    console.print(
        "\n[bold cyan]🔍 Running Flaky Test Diagnostic (flaky-finder)...[/bold cyan]\n"
    )

    total_issues = 0
    analyzed_files = set()

    for item in items:
        file_path = item.path
        if file_path in analyzed_files:
            continue

        analyzed_files.add(file_path)

        try:
            content = file_path.read_text(encoding="utf-8")
            issues = analyze_code(content)

            if issues:
                total_issues += len(issues)
                table = Table(title=f"Flaky Patterns in {file_path.name}")
                table.add_column("Line", style="cyan", justify="right")
                table.add_column("Rule ID", style="magenta")
                table.add_column("Diagnostic Message", style="white")

                for issue in issues:
                    table.add_row(
                        str(issue.line), issue.rule_id, issue.message
                    )

                console.print(table)
                console.print()
        except Exception as e:
            console.print(f"[red]Error parsing {file_path}: {e}[/red]")

    if total_issues > 0:
        console.print(
            f"[bold red]❌ Flaky Finder flagged {total_issues} potential issue(s).[/bold red]\n"
        )
        # If --flaky-fail flag is set, stop pytest execution immediately with exit code 1
        if config.getoption("--flaky-fail"):
            pytest.exit(
                f"Stopping execution: {total_issues} flaky test pattern(s) detected.",
                returncode=1,
            )