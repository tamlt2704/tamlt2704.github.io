# Chapter 14: "Build the CLI"

[← Chapter 13: Async](chapter-13-async.md) | [Chapter 15: Database →](chapter-15-database.md)

---

## The Request

Dani (designer, strong opinions about UX):

> "I'm tired of managing the bot through Slack. I want a proper CLI tool. `pulsebot status`, `pulsebot deploy production`, `pulsebot tickets list --priority high`. Make it pretty. Colors. Tables. Progress bars. I want to feel like a hacker."

---

## argparse: The Standard Library Way

```python
import argparse


def main():
    parser = argparse.ArgumentParser(
        prog="pulsebot",
        description="PulseBot management CLI",
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # pulsebot status
    status_parser = subparsers.add_parser("status", help="Check bot status")
    status_parser.add_argument("--verbose", "-v", action="store_true")
    
    # pulsebot deploy <environment>
    deploy_parser = subparsers.add_parser("deploy", help="Deploy the bot")
    deploy_parser.add_argument("environment", choices=["staging", "production"])
    deploy_parser.add_argument("--dry-run", action="store_true")
    
    # pulsebot tickets list --priority high
    tickets_parser = subparsers.add_parser("tickets", help="Manage tickets")
    tickets_sub = tickets_parser.add_subparsers(dest="action")
    
    list_parser = tickets_sub.add_parser("list")
    list_parser.add_argument("--priority", choices=["low", "medium", "high", "critical"])
    list_parser.add_argument("--limit", type=int, default=20)
    
    args = parser.parse_args()
    
    match args.command:
        case "status":
            show_status(verbose=args.verbose)
        case "deploy":
            deploy(args.environment, dry_run=args.dry_run)
        case "tickets":
            handle_tickets(args)
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
```

```bash
$ pulsebot --help
usage: pulsebot [-h] {status,deploy,tickets} ...

PulseBot management CLI

positional arguments:
  {status,deploy,tickets}
    status              Check bot status
    deploy              Deploy the bot
    tickets             Manage tickets

$ pulsebot deploy production --dry-run
```

---

## click: The Better Way

```bash
pip install click
```

click uses decorators instead of manual parser construction:

```python
import click


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """PulseBot management CLI."""
    pass


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed info")
def status(verbose: bool):
    """Check bot status."""
    click.echo("✅ Bot is running")
    if verbose:
        click.echo(f"  Uptime: 3 days, 4 hours")
        click.echo(f"  Messages processed: 12,847")
        click.echo(f"  Active channels: 5")


@cli.command()
@click.argument("environment", type=click.Choice(["staging", "production"]))
@click.option("--dry-run", is_flag=True, help="Show what would happen")
@click.confirmation_option(prompt="Are you sure you want to deploy?")
def deploy(environment: str, dry_run: bool):
    """Deploy the bot to an environment."""
    if dry_run:
        click.echo(f"Would deploy to {environment}")
        return
    
    click.echo(f"🚀 Deploying to {environment}...")
    # ... deployment logic
    click.secho("✅ Deployed successfully!", fg="green", bold=True)


@cli.group()
def tickets():
    """Manage support tickets."""
    pass


@tickets.command("list")
@click.option("--priority", type=click.Choice(["low", "medium", "high", "critical"]))
@click.option("--limit", default=20, help="Max tickets to show")
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table")
def list_tickets(priority: str | None, limit: int, fmt: str):
    """List support tickets."""
    tickets = fetch_tickets(priority=priority, limit=limit)
    
    if fmt == "json":
        click.echo(json.dumps(tickets, indent=2))
    else:
        for t in tickets:
            color = {"high": "red", "medium": "yellow", "low": "green"}.get(t["priority"], "white")
            click.secho(f"  [{t['id']}] {t['title']} ({t['priority']})", fg=color)


if __name__ == "__main__":
    cli()
```

```bash
$ pulsebot status -v
✅ Bot is running
  Uptime: 3 days, 4 hours
  Messages processed: 12,847
  Active channels: 5

$ pulsebot tickets list --priority high
  [T-042] Bot crashes on Tuesday (high)
  [T-039] Slow response in #support (high)
```

---

## click Features

### Input Prompts

```python
@cli.command()
@click.option("--name", prompt="Bot name", help="Name for the new bot")
@click.option("--token", prompt=True, hide_input=True, help="Slack token")
def init(name: str, token: str):
    """Initialize a new bot configuration."""
    click.echo(f"Creating bot '{name}'...")
    save_config({"name": name, "token": token})
    click.secho("✅ Config saved!", fg="green")
```

### File Arguments

```python
@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.argument("output", type=click.File("w"), default="-")  # default: stdout
def export(config_file: str, output):
    """Export config to stdout or file."""
    config = load_config(config_file)
    json.dump(config, output, indent=2)
```

### Progress Bars

```python
@cli.command()
@click.argument("channel")
def backlog(channel: str):
    """Process message backlog."""
    messages = fetch_all_messages(channel)
    
    with click.progressbar(messages, label="Processing") as bar:
        for msg in bar:
            process_message(msg)
    
    click.secho("✅ Backlog processed!", fg="green")
```

---

## rich: Beautiful Terminal Output

```bash
pip install rich
```

### Tables

```python
from rich.console import Console
from rich.table import Table

console = Console()


def show_tickets(tickets: list[dict]):
    table = Table(title="Support Tickets")
    
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Priority", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Reporter", style="dim")
    
    for t in tickets:
        priority_color = {
            "critical": "red bold",
            "high": "red",
            "medium": "yellow",
            "low": "green",
        }.get(t["priority"], "white")
        
        table.add_row(
            t["id"],
            t["title"],
            f"[{priority_color}]{t['priority']}[/]",
            t["status"],
            t["reporter"],
        )
    
    console.print(table)
```

### Panels and Formatting

```python
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint


def show_status(bot_info: dict):
    status_text = Text()
    status_text.append("● ", style="green bold")
    status_text.append("Running", style="green")
    status_text.append(f" — uptime {bot_info['uptime']}")
    
    panel = Panel(
        status_text,
        title="PulseBot Status",
        border_style="blue",
    )
    console.print(panel)


# Rich print with markup
rprint("[bold green]✅ Success![/] Bot deployed to production")
rprint("[red]❌ Error:[/] Connection refused")
rprint("[dim]Hint: Check your SLACK_TOKEN environment variable[/]")
```

### Progress with Rich

```python
from rich.progress import Progress, SpinnerColumn, TextColumn


def deploy_with_progress(environment: str):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        task = progress.add_task("Running tests...", total=None)
        run_tests()
        
        progress.update(task, description="Building image...")
        build_image()
        
        progress.update(task, description="Pushing to registry...")
        push_image()
        
        progress.update(task, description="Restarting service...")
        restart_service(environment)
    
    console.print("[bold green]✅ Deployed![/]")
```

---

## stdin/stdout: Unix Philosophy

Make your CLI composable with pipes:

```python
import sys
import json


@cli.command()
@click.option("--format", "fmt", type=click.Choice(["json", "text"]), default="text")
def export_tickets(fmt: str):
    """Export tickets to stdout (pipe-friendly)."""
    tickets = fetch_all_tickets()
    
    if fmt == "json":
        # Machine-readable output goes to stdout
        json.dump(tickets, sys.stdout, indent=2)
    else:
        for t in tickets:
            # One record per line — grep-friendly
            click.echo(f"{t['id']}\t{t['priority']}\t{t['title']}")


@cli.command()
def import_tickets():
    """Import tickets from stdin."""
    # Read from pipe: cat tickets.json | pulsebot import-tickets
    if not sys.stdin.isatty():
        data = json.load(sys.stdin)
        for ticket in data:
            create_ticket(ticket)
        click.echo(f"Imported {len(data)} tickets", err=True)  # status to stderr
    else:
        click.echo("No input. Pipe JSON to this command.", err=True)
```

```bash
# Composable CLI
$ pulsebot export-tickets --format json | jq '.[] | select(.priority == "high")'
$ pulsebot export-tickets | grep "critical" | wc -l
$ cat new_tickets.json | pulsebot import-tickets
```

---

## Putting It Together: The Full CLI

```python
import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="pulsebot")
@click.option("--config", "-c", type=click.Path(), default="config.yaml")
@click.pass_context
def cli(ctx, config: str):
    """PulseBot — Slack bot management CLI."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config)


@cli.command()
@click.pass_context
def status(ctx):
    """Show bot status."""
    config = ctx.obj["config"]
    info = get_bot_status(config)
    
    table = Table(show_header=False, box=None)
    table.add_row("Status", f"[green]● Running[/]" if info["running"] else "[red]● Stopped[/]")
    table.add_row("Uptime", info["uptime"])
    table.add_row("Messages", f"{info['messages_processed']:,}")
    table.add_row("Channels", ", ".join(info["channels"]))
    
    console.print(Panel(table, title="PulseBot", border_style="blue"))


@cli.group()
def tickets():
    """Manage support tickets."""
    pass


@tickets.command("list")
@click.option("--priority", "-p", type=click.Choice(["low", "medium", "high", "critical"]))
@click.option("--status", "-s", type=click.Choice(["open", "closed", "all"]), default="open")
@click.option("--limit", "-n", default=20)
@click.pass_context
def list_tickets(ctx, priority, status, limit):
    """List tickets with optional filters."""
    tickets = fetch_tickets(ctx.obj["config"], priority=priority, status=status, limit=limit)
    show_tickets_table(tickets)


@tickets.command("create")
@click.option("--title", "-t", prompt="Title")
@click.option("--priority", "-p", type=click.Choice(["low", "medium", "high", "critical"]), default="medium")
def create_ticket(title, priority):
    """Create a new ticket."""
    ticket = create_new_ticket(title=title, priority=priority)
    console.print(f"[green]✅ Created ticket {ticket['id']}[/]")


if __name__ == "__main__":
    cli()
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Tool                            │ Best For
────────────────────────────────┼──────────────────────────────────────
argparse                        │ Simple scripts, no dependencies
click                           │ Complex CLIs, subcommands, prompts
rich                            │ Beautiful output, tables, progress
────────────────────────────────┼──────────────────────────────────────
click Patterns                  │
────────────────────────────────┼──────────────────────────────────────
@click.group()                  │ Command group (subcommands)
@cli.command()                  │ Add a command
@click.argument("name")         │ Positional argument
@click.option("--flag", "-f")   │ Optional flag
@click.pass_context             │ Share state between commands
click.echo() / click.secho()    │ Output (with optional color)
click.confirm()                 │ Yes/no prompt
click.progressbar()             │ Progress bar
────────────────────────────────┼──────────────────────────────────────
rich Patterns                   │
────────────────────────────────┼──────────────────────────────────────
Console().print()               │ Rich formatted output
Table()                         │ Formatted tables
Panel()                         │ Bordered panels
Progress()                      │ Advanced progress bars
"[bold red]text[/]"             │ Inline markup
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Dani loves the CLI. It's beautiful. But there's a problem — all the ticket data lives in memory. Restart the bot and everything is gone. Rina: "We need a real database. Store tickets, messages, user preferences — persistently." Time to talk to PostgreSQL.

---

[← Chapter 13: Async](chapter-13-async.md) | [Chapter 15: Database →](chapter-15-database.md)
