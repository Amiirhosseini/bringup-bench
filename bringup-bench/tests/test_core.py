"""Core simulator and planner tests."""

from __future__ import annotations

from bringupbench.agent.planner import BringupPlanner, ToolExecutor
from bringupbench.codegen.stubs import generate_stubs
from bringupbench.config import AppConfig
from bringupbench.diagnose.engine import diagnose
from bringupbench.models import AgentAction
from bringupbench.sim.board import BoardSim, SCENARIOS


def test_first_power_has_critical_findings():
    snap = diagnose(BoardSim(scenario="first-power"))
    codes = {f.code for f in snap.findings}
    assert "i2c.addr_mismatch" in codes
    assert "spi.mode_mismatch" in codes
    assert "uart.baud_mismatch" in codes
    assert "gpio.pinmux" in codes


def test_clean_has_no_critical():
    snap = diagnose(BoardSim(scenario="clean"))
    assert not any(f.severity == "critical" for f in snap.findings)


def test_clock_gate_flags_spi():
    snap = diagnose(BoardSim(scenario="clock-gate"))
    assert any(f.code == "clock.gated" for f in snap.findings)


def test_i2c_nack_in_trace():
    cap = BoardSim(scenario="first-power").capture()
    assert any(e.kind == "NACK" for e in cap.events)


def test_clean_i2c_whoami():
    cap = BoardSim(scenario="clean").capture()
    who = [e for e in cap.events if e.bus.value == "i2c" and e.byte == 0x54]
    assert who


def test_planner_i2c_goal():
    cfg = AppConfig(scenario="first-power")
    snap = diagnose(BoardSim(scenario="first-power"))
    plan = BringupPlanner(cfg).plan("i2c nack on opt3001", snap)
    names = [s.name for s in plan.steps]
    assert "i2c_scan" in names
    assert "fix_i2c_addr" in names


def test_generate_stubs_use_hardware_addr():
    snap = diagnose(BoardSim(scenario="first-power"))
    files = generate_stubs(snap)
    assert "0x44" in files["opt3001.c"]
    assert "spi_set_mode" in files["imu_lsm6.c"]
    assert "57600" in files["console.c"]


def test_executor_i2c_scan():
    exe = ToolExecutor(AppConfig(scenario="first-power"))
    result = exe.execute(AgentAction(name="i2c_scan"))
    assert "0x44" in result["responding"]


def test_scenarios_exist():
    assert set(SCENARIOS) >= {"first-power", "clock-gate", "clean"}
