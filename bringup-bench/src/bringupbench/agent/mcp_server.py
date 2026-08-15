"""MCP server for Hermes and other agents."""

from __future__ import annotations

import json
from typing import Any

from bringupbench.agent.planner import BringupPlanner, ToolExecutor
from bringupbench.config import load_config
from bringupbench.diagnose.engine import findings_markdown
from bringupbench.models import AgentAction
from bringupbench.sim.board import BoardSim, SCENARIOS


def create_mcp_server() -> Any:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("bringup-bench")
    config = load_config()
    planner = BringupPlanner(config)
    executor = ToolExecutor(config)

    @mcp.tool()
    def board_health(scenario: str | None = None) -> str:
        """Diagnose the simulated MCU board. Optional scenario: first-power, clock-gate, clean."""
        if scenario:
            executor.sim = BoardSim(board=config.board, scenario=scenario)
        snap = executor.snapshot()
        return json.dumps(
            {
                "board": snap.board,
                "mcu": snap.mcu,
                "scenario": snap.scenario,
                "findings_markdown": findings_markdown(snap.findings),
                "findings": [f.model_dump(mode="json") for f in snap.findings],
            },
            indent=2,
        )

    @mcp.tool()
    def capture_trace(scenario: str | None = None) -> str:
        """Return logic-analyzer-style events for I2C/SPI/UART/GPIO."""
        if scenario:
            executor.sim = BoardSim(board=config.board, scenario=scenario)
        cap = executor.sim.capture()
        return cap.model_dump_json(indent=2)

    @mcp.tool()
    def plan_bringup(goal: str) -> str:
        """Turn a natural-language bring-up goal into an inspectable plan."""
        snap = executor.snapshot()
        return planner.plan(goal, snap).model_dump_json(indent=2)

    @mcp.tool()
    def generate_driver_stubs() -> str:
        """Emit C whoami/init stubs from hardware truth (review before flash)."""
        result = executor.execute(AgentAction(name="generate_stubs"))
        return json.dumps(result, indent=2)

    @mcp.tool()
    def i2c_scan() -> str:
        """List I2C addresses that ACK on the simulated bus."""
        result = executor.execute(AgentAction(name="i2c_scan"))
        return json.dumps(result, indent=2)

    @mcp.tool()
    def list_scenarios() -> str:
        """List built-in bring-up scenarios."""
        return json.dumps({k: v["label"] for k, v in SCENARIOS.items()}, indent=2)

    return mcp


def main() -> None:
    create_mcp_server().run()


if __name__ == "__main__":
    main()
