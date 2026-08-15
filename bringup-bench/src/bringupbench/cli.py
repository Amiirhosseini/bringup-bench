"""Bringup Bench CLI."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from bringupbench import __version__
from bringupbench.agent.planner import BringupPlanner, ToolExecutor
from bringupbench.config import load_config
from bringupbench.diagnose.engine import findings_markdown
from bringupbench.models import AgentAction
from bringupbench.sim.board import SCENARIOS

app = typer.Typer(name="bringup", help="Agentic MCU board bring-up toolkit", no_args_is_help=True)
console = Console()


@app.callback()
def main(
    ctx: typer.Context,
    board: Optional[str] = typer.Option(None, "--board"),
    scenario: Optional[str] = typer.Option(None, "--scenario", "-s"),
) -> None:
    ctx.ensure_object(dict)
    cfg = load_config()
    if board:
        cfg.board = board
    if scenario:
        cfg.scenario = scenario
    ctx.obj["config"] = cfg


@app.command()
def version() -> None:
    console.print(__version__)


@app.command("health")
def health_cmd(ctx: typer.Context) -> None:
    """Diagnose clocks, buses, and pinmux."""
    exe = ToolExecutor(ctx.obj["config"])
    snap = exe.snapshot()
    console.print(f"[bold]{snap.board}[/bold]  {snap.mcu}  scenario={snap.scenario}")
    console.print(findings_markdown(snap.findings))


@app.command("trace")
def trace_cmd(ctx: typer.Context) -> None:
    """Print capture events."""
    exe = ToolExecutor(ctx.obj["config"])
    cap = exe.sim.capture()
    table = Table(title=f"Capture {cap.scenario} ({cap.duration_us} µs)")
    table.add_column("t_us")
    table.add_column("bus")
    table.add_column("ch")
    table.add_column("kind")
    table.add_column("detail")
    for e in cap.events:
        table.add_row(str(e.t_us), e.bus.value, e.channel, e.kind, e.detail)
    console.print(table)


@app.command("clocks")
def clocks_cmd(ctx: typer.Context) -> None:
    """Show clock tree."""
    exe = ToolExecutor(ctx.obj["config"])
    table = Table(title="Clock tree")
    table.add_column("name")
    table.add_column("src")
    table.add_column("Hz")
    table.add_column("enabled")
    table.add_column("consumers")
    for c in exe.sim.clocks():
        table.add_row(c.name, c.source, f"{c.hz:,}", str(c.enabled), ", ".join(c.consumers))
    console.print(table)


@app.command("plan")
def plan_cmd(ctx: typer.Context, goal: str = typer.Argument(...)) -> None:
    """Generate an agentic bring-up plan."""
    cfg = ctx.obj["config"]
    exe = ToolExecutor(cfg)
    plan = BringupPlanner(cfg).plan(goal, exe.snapshot())
    console.print_json(plan.model_dump_json())


@app.command("run")
def run_cmd(
    ctx: typer.Context,
    goal: str = typer.Argument(...),
    execute: bool = typer.Option(False, "--execute"),
) -> None:
    """Plan and optionally execute read-only tools."""
    cfg = ctx.obj["config"]
    exe = ToolExecutor(cfg)
    snap = exe.snapshot()
    plan = BringupPlanner(cfg).plan(goal, snap)
    results = []
    if execute:
        for step in plan.steps:
            results.append({"action": step.name, "result": exe.execute(step, snap)})
    console.print_json(json.dumps({"plan": plan.model_dump(mode="json"), "results": results}, default=str))


@app.command("stubs")
def stubs_cmd(
    ctx: typer.Context,
    out: Path = typer.Option(Path("generated"), "--out"),
) -> None:
    """Write C driver stubs from hardware truth."""
    exe = ToolExecutor(ctx.obj["config"])
    files = exe.execute(AgentAction(name="generate_stubs"))
    out.mkdir(parents=True, exist_ok=True)
    assert isinstance(files, dict)
    for name, body in files.items():
        path = out / name
        path.write_text(body, encoding="utf-8")
        console.print(f"wrote {path}")


@app.command("scenarios")
def scenarios_cmd() -> None:
    for key, meta in SCENARIOS.items():
        console.print(f"[bold]{key}[/bold]  {meta['label']}")


@app.command("serve")
def serve_cmd(ctx: typer.Context, host: Optional[str] = None, port: Optional[int] = None) -> None:
    from bringupbench.api import create_app

    cfg = ctx.obj["config"]
    uvicorn.run(create_app(cfg), host=host or cfg.api_host, port=port or cfg.api_port)


@app.command("mcp")
def mcp_cmd() -> None:
    from bringupbench.agent.mcp_server import main as mcp_main

    mcp_main()


@app.command("install-hermes-skills")
def install_skills(
    dest: Path = typer.Option(Path.home() / ".hermes" / "skills" / "embedded"),
) -> None:
    candidates = [
        Path.cwd() / "hermes" / "skills",
        Path(__file__).resolve().parents[3] / "hermes" / "skills",
    ]
    root = next((p for p in candidates if p.exists()), None)
    if root is None:
        console.print("[red]Could not locate hermes/skills[/red]")
        raise typer.Exit(1)
    dest.mkdir(parents=True, exist_ok=True)
    for skill_dir in root.iterdir():
        if skill_dir.is_dir():
            target = dest / skill_dir.name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(skill_dir, target)
            console.print(f"Installed {target}")


if __name__ == "__main__":
    app()
