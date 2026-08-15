"""Root-cause engine for bring-up captures."""

from __future__ import annotations

from bringupbench.models import BoardSnapshot, BusKind, Finding
from bringupbench.sim.board import BoardSim


def diagnose(sim: BoardSim) -> BoardSnapshot:
    clocks = sim.clocks()
    peripherals = sim.peripherals()
    capture = sim.capture()
    findings: list[Finding] = []

    clock_by_name = {c.name: c for c in clocks}
    for p in peripherals:
        node = clock_by_name.get(p.clock)
        if node is not None and node.gated and not node.enabled:
            findings.append(
                Finding(
                    severity="critical",
                    code="clock.gated",
                    title=f"{p.instance} clock gate off",
                    detail=f"{p.clock} is gated; {p.name} will not clock",
                    resource=p.name,
                    suggested_action=f"Enable {p.clock} in RCC before first transaction",
                    evidence=[f"clock {p.clock} enabled={node.enabled}"],
                )
            )

        if p.kind == BusKind.I2C:
            fw = int(p.firmware_config.get("addr", 0))
            hw = int(p.hardware_config.get("addr", 0))
            if fw != hw:
                findings.append(
                    Finding(
                        severity="critical",
                        code="i2c.addr_mismatch",
                        title="I2C address mismatch",
                        detail=f"Firmware talks to 0x{fw:02X}, device strapped at 0x{hw:02X}",
                        resource=p.name,
                        suggested_action="Fix 7-bit address (ADDR pin / datasheet vs driver)",
                        evidence=[
                            e.detail
                            for e in capture.events
                            if e.kind in {"ADDR", "NACK"} and e.bus == BusKind.I2C
                        ],
                    )
                )

        if p.kind == BusKind.SPI:
            fw_mode = int(p.firmware_config.get("mode", 0))
            hw_mode = int(p.hardware_config.get("mode", 0))
            if fw_mode != hw_mode:
                findings.append(
                    Finding(
                        severity="critical",
                        code="spi.mode_mismatch",
                        title="SPI CPOL/CPHA mismatch",
                        detail=f"Driver mode {fw_mode}, device expects mode {hw_mode}",
                        resource=p.name,
                        suggested_action="Set SPI_CR1 CPOL/CPHA for mode 0 (sample on rising, idle low)",
                        evidence=[
                            e.detail
                            for e in capture.events
                            if e.bus == BusKind.SPI and e.kind == "RX"
                        ],
                    )
                )

        if p.kind == BusKind.UART:
            fw_b = int(p.firmware_config.get("baud", 0))
            hw_b = int(p.hardware_config.get("baud", 0))
            if fw_b != hw_b:
                findings.append(
                    Finding(
                        severity="warn",
                        code="uart.baud_mismatch",
                        title="UART baud mismatch",
                        detail=f"Firmware {fw_b} vs fixture/host {hw_b}",
                        resource=p.name,
                        suggested_action="Match USART_BRR to the factory fixture baud",
                        evidence=[
                            e.detail
                            for e in capture.events
                            if e.bus == BusKind.UART and e.kind in {"FRAMING_ERROR", "GARBAGE"}
                        ],
                    )
                )

        if p.kind == BusKind.GPIO:
            fw_mux = str(p.firmware_config.get("mux", ""))
            hw_mux = str(p.hardware_config.get("mux", ""))
            if fw_mux != hw_mux:
                findings.append(
                    Finding(
                        severity="warn",
                        code="gpio.pinmux",
                        title="EXTI pin mux wrong",
                        detail=f"Firmware mux {fw_mux}, schematic {hw_mux}",
                        resource=p.name,
                        suggested_action="Remap INT1 to PB4 EXTI; do not share with SPI CS",
                        evidence=[
                            e.detail
                            for e in capture.events
                            if e.bus == BusKind.GPIO
                        ],
                    )
                )

    nacks = [e for e in capture.events if e.kind == "NACK"]
    if nacks and not any(f.code == "i2c.addr_mismatch" for f in findings):
        findings.append(
            Finding(
                severity="critical",
                code="i2c.nack",
                title="I2C NACK",
                detail=nacks[0].detail,
                resource="I2C1",
                suggested_action="Scan bus, check pull-ups, confirm 7-bit address",
                evidence=[nacks[0].detail],
            )
        )

    idle_sck = [e for e in capture.events if e.bus == BusKind.SPI and e.kind == "IDLE"]
    if idle_sck and not any(f.code == "clock.gated" for f in findings):
        findings.append(
            Finding(
                severity="critical",
                code="spi.no_clock",
                title="SPI SCK idle during CS",
                detail=idle_sck[0].detail,
                resource="SPI1",
                suggested_action="Enable SPI1 clock and confirm AF on SCK pin",
                evidence=[idle_sck[0].detail],
            )
        )

    rank = {"info": 0, "warn": 1, "critical": 2}
    findings.sort(key=lambda f: (-rank[f.severity], f.code, f.resource))
    return BoardSnapshot(
        board=sim.board,
        mcu=sim.mcu,
        scenario=sim.scenario,
        clocks=clocks,
        peripherals=peripherals,
        capture=capture,
        findings=findings,
    )


def findings_markdown(findings: list[Finding]) -> str:
    if not findings:
        return "No findings. Buses look clean."
    lines = ["| Severity | Code | Resource | Title |", "|---|---|---|---|"]
    for f in findings:
        lines.append(f"| {f.severity} | `{f.code}` | `{f.resource}` | {f.title} |")
    return "\n".join(lines)
