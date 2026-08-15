"""Natural-language bring-up planner."""

from __future__ import annotations

from typing import Any

from bringupbench.codegen.stubs import generate_stubs
from bringupbench.config import AppConfig
from bringupbench.diagnose.engine import diagnose, findings_markdown
from bringupbench.models import AgentAction, AgentPlan, BoardSnapshot
from bringupbench.sim.board import BoardSim, SCENARIOS


class BringupPlanner:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def plan(self, goal: str, snapshot: BoardSnapshot) -> AgentPlan:
        g = goal.lower()
        steps: list[AgentAction] = []
        risks: list[str] = []

        if any(k in g for k in ("health", "status", "diagnose", "why", "fail", "bring")):
            steps.append(AgentAction(name="capture_trace", rationale="Record I2C/SPI/UART/GPIO window"))
            steps.append(AgentAction(name="diagnose", rationale="Rank findings from clocks + buses"))

        if any(k in g for k in ("i2c", "nack", "address", "opt3001", "light")):
            steps.append(
                AgentAction(
                    name="i2c_scan",
                    rationale="Scan 7-bit addresses; compare to firmware addr",
                )
            )
            if any(f.code == "i2c.addr_mismatch" for f in snapshot.findings):
                steps.append(
                    AgentAction(
                        name="fix_i2c_addr",
                        args={"addr": 0x44},
                        rationale="Datasheet ADDR pin low → 0x44, not 0x45",
                    )
                )

        if any(k in g for k in ("spi", "cpol", "cpha", "imu", "mode")):
            steps.append(
                AgentAction(
                    name="check_spi_mode",
                    rationale="Compare CPOL/CPHA to IMU datasheet (mode 0)",
                )
            )

        if any(k in g for k in ("uart", "baud", "console", "framing")):
            steps.append(
                AgentAction(
                    name="match_uart_baud",
                    args={"baud": 57600},
                    rationale="Factory fixture is 57600 8N1",
                )
            )

        if any(k in g for k in ("clock", "gate", "rcc", "sck")):
            steps.append(
                AgentAction(
                    name="enable_clocks",
                    rationale="Ungate I2C1/SPI1/USART2 before first xfer",
                )
            )

        if any(k in g for k in ("gpio", "exti", "interrupt", "pinmux", "mux")):
            steps.append(
                AgentAction(
                    name="fix_pinmux",
                    rationale="Map IMU INT1 to PB4 EXTI, keep PA4 as SPI CS",
                )
            )

        if any(k in g for k in ("stub", "driver", "codegen", "c code", "firmware")):
            steps.append(
                AgentAction(
                    name="generate_stubs",
                    rationale="Emit reviewable C whoami/init stubs from hardware truth",
                )
            )
            risks.append("Generated C is a starting point — review clocks and pinmux before flash")

        if not steps:
            steps = [
                AgentAction(name="capture_trace", rationale="Default: look at buses first"),
                AgentAction(name="diagnose", rationale="Surface ranked findings"),
            ]

        return AgentPlan(goal=goal, steps=steps[: self.config.agent.max_plan_steps], risks=risks)


class ToolExecutor:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.sim = BoardSim(board=config.board, scenario=config.scenario)

    def snapshot(self) -> BoardSnapshot:
        return diagnose(self.sim)

    def execute(self, action: AgentAction, snapshot: BoardSnapshot | None = None) -> dict[str, Any]:
        snap = snapshot or self.snapshot()
        name = action.name

        if name == "capture_trace":
            cap = snap.capture
            return {
                "scenario": cap.scenario,
                "duration_us": cap.duration_us,
                "events": [e.model_dump(mode="json") for e in cap.events],
            }
        if name == "diagnose":
            return {
                "findings_markdown": findings_markdown(snap.findings),
                "findings": [f.model_dump(mode="json") for f in snap.findings],
            }
        if name == "i2c_scan":
            addrs = sorted(
                {
                    int(p.hardware_config["addr"])
                    for p in snap.peripherals
                    if p.kind.value == "i2c" and p.hardware_config.get("addr") is not None
                }
            )
            return {"responding": [f"0x{a:02X}" for a in addrs], "firmware_expected": "see findings"}
        if name == "list_clocks":
            return [c.model_dump(mode="json") for c in snap.clocks]
        if name == "generate_stubs":
            return generate_stubs(snap)
        if name in {
            "fix_i2c_addr",
            "check_spi_mode",
            "match_uart_baud",
            "enable_clocks",
            "fix_pinmux",
        }:
            return {
                "status": "planned",
                "action": name,
                "args": action.args,
                "note": "Assist mode: apply in firmware, then re-run scenario=clean to verify",
            }
        if name == "list_scenarios":
            return {k: v["label"] for k, v in SCENARIOS.items()}
        raise ValueError(f"Unknown action: {name}")
