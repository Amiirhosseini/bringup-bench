"""Deterministic MCU + bus simulator for board bring-up."""

from __future__ import annotations

from bringupbench.models import BusKind, Capture, ClockNode, Peripheral, TraceEvent


def _clock_tree(*, i2c1_gated: bool = False, spi1_gated: bool = False) -> list[ClockNode]:
    return [
        ClockNode(name="HSE", source="xtal", hz=8_000_000, consumers=["PLL"]),
        ClockNode(name="PLL", source="HSE", hz=96_000_000, consumers=["SYSCLK"]),
        ClockNode(name="SYSCLK", source="PLL", hz=96_000_000, consumers=["AHB"]),
        ClockNode(name="AHB", source="SYSCLK", hz=96_000_000, consumers=["APB1", "APB2"]),
        ClockNode(name="APB1", source="AHB", hz=48_000_000, consumers=["I2C1", "USART2"]),
        ClockNode(name="APB2", source="AHB", hz=96_000_000, consumers=["SPI1"]),
        ClockNode(
            name="I2C1",
            source="APB1",
            hz=48_000_000,
            gated=True,
            enabled=not i2c1_gated,
            consumers=["opt3001"],
        ),
        ClockNode(
            name="SPI1",
            source="APB2",
            hz=96_000_000,
            gated=True,
            enabled=not spi1_gated,
            consumers=["imu-lsm6"],
        ),
        ClockNode(
            name="USART2",
            source="APB1",
            hz=48_000_000,
            gated=True,
            enabled=True,
            consumers=["console"],
        ),
    ]


def _peripherals(
    *,
    i2c_fw_addr: int = 0x45,
    i2c_hw_addr: int = 0x44,
    spi_fw_mode: int = 3,
    spi_hw_mode: int = 0,
    uart_fw_baud: int = 115200,
    uart_hw_baud: int = 57600,
    pinmux_ok: bool = False,
) -> list[Peripheral]:
    return [
        Peripheral(
            name="opt3001",
            kind=BusKind.I2C,
            instance="I2C1",
            address=i2c_hw_addr,
            pins={"scl": "PB8", "sda": "PB9"},
            clock="I2C1",
            firmware_config={"addr": i2c_fw_addr, "speed_hz": 400_000},
            hardware_config={"addr": i2c_hw_addr, "whoami": 0x54},
            notes="Ambient light sensor on I2C1",
        ),
        Peripheral(
            name="imu-lsm6",
            kind=BusKind.SPI,
            instance="SPI1",
            address=None,
            pins={"sck": "PA5", "miso": "PA6", "mosi": "PA7", "cs": "PA4"},
            clock="SPI1",
            firmware_config={"mode": spi_fw_mode, "mhz": 8, "whoami_reg": 0x0F},
            hardware_config={"mode": spi_hw_mode, "whoami": 0x6A},
            notes="6-axis IMU, SPI mode 0",
        ),
        Peripheral(
            name="console",
            kind=BusKind.UART,
            instance="USART2",
            pins={"tx": "PA2", "rx": "PA3"},
            clock="USART2",
            firmware_config={"baud": uart_fw_baud, "parity": "none"},
            hardware_config={"baud": uart_hw_baud, "parity": "none"},
            notes="Host UART for logs / factory fixture",
        ),
        Peripheral(
            name="imu-int1",
            kind=BusKind.GPIO,
            instance="EXTI4",
            pins={"int": "PB4"},
            clock="AHB",
            firmware_config={"mux": "PB4-EXTI" if pinmux_ok else "PA4-SPI_CS"},
            hardware_config={"mux": "PB4-EXTI"},
            notes="IMU data-ready interrupt",
        ),
    ]


def _i2c_events(*, nack: bool, t0: int = 0) -> list[TraceEvent]:
    events = [
        TraceEvent(t_us=t0, bus=BusKind.I2C, channel="SCL/SDA", kind="START", detail="START"),
        TraceEvent(
            t_us=t0 + 12,
            bus=BusKind.I2C,
            channel="SDA",
            kind="ADDR",
            detail="0x45 WRITE" if nack else "0x44 WRITE",
            byte=0x8A if nack else 0x88,
            ack=not nack,
        ),
    ]
    if nack:
        events.append(
            TraceEvent(
                t_us=t0 + 22,
                bus=BusKind.I2C,
                channel="SDA",
                kind="NACK",
                detail="slave NACK on address",
                ack=False,
            )
        )
        events.append(
            TraceEvent(t_us=t0 + 28, bus=BusKind.I2C, channel="SCL/SDA", kind="STOP", detail="STOP")
        )
        return events
    events.extend(
        [
            TraceEvent(
                t_us=t0 + 22,
                bus=BusKind.I2C,
                channel="SDA",
                kind="ACK",
                detail="addr ACK",
                ack=True,
            ),
            TraceEvent(
                t_us=t0 + 34,
                bus=BusKind.I2C,
                channel="SDA",
                kind="DATA",
                detail="reg 0x7E (DEVICE_ID)",
                byte=0x7E,
                ack=True,
            ),
            TraceEvent(t_us=t0 + 48, bus=BusKind.I2C, channel="SCL/SDA", kind="RESTART", detail="Sr"),
            TraceEvent(
                t_us=t0 + 58,
                bus=BusKind.I2C,
                channel="SDA",
                kind="ADDR",
                detail="0x44 READ",
                byte=0x89,
                ack=True,
            ),
            TraceEvent(
                t_us=t0 + 72,
                bus=BusKind.I2C,
                channel="SDA",
                kind="DATA",
                detail="WHO_AM_I=0x54",
                byte=0x54,
                ack=True,
            ),
            TraceEvent(t_us=t0 + 84, bus=BusKind.I2C, channel="SCL/SDA", kind="STOP", detail="STOP"),
        ]
    )
    return events


def _spi_events(*, mode_mismatch: bool, clock_gated: bool, t0: int = 200) -> list[TraceEvent]:
    if clock_gated:
        return [
            TraceEvent(
                t_us=t0,
                bus=BusKind.SPI,
                channel="SCK",
                kind="IDLE",
                detail="SCK stuck low — SPI1 clock gate off",
                level=0,
            ),
            TraceEvent(
                t_us=t0 + 40,
                bus=BusKind.SPI,
                channel="CS",
                kind="CS",
                detail="CS asserted but no clocks",
                level=0,
            ),
        ]
    miso = 0x00 if mode_mismatch else 0x6A
    return [
        TraceEvent(
            t_us=t0,
            bus=BusKind.SPI,
            channel="CS",
            kind="CS",
            detail="CS low",
            level=0,
        ),
        TraceEvent(
            t_us=t0 + 8,
            bus=BusKind.SPI,
            channel="MOSI",
            kind="TX",
            detail="WHO_AM_I read 0x8F",
            byte=0x8F,
        ),
        TraceEvent(
            t_us=t0 + 16,
            bus=BusKind.SPI,
            channel="MISO",
            kind="RX",
            detail=("0x00 (mode 3 vs device mode 0)" if mode_mismatch else "WHO_AM_I=0x6A"),
            byte=miso,
        ),
        TraceEvent(
            t_us=t0 + 24,
            bus=BusKind.SPI,
            channel="CS",
            kind="CS",
            detail="CS high",
            level=1,
        ),
    ]


def _uart_events(*, baud_mismatch: bool, t0: int = 400) -> list[TraceEvent]:
    if baud_mismatch:
        return [
            TraceEvent(
                t_us=t0,
                bus=BusKind.UART,
                channel="TX",
                kind="FRAME",
                detail="host 115200, fixture 57600",
                byte=0x55,
            ),
            TraceEvent(
                t_us=t0 + 90,
                bus=BusKind.UART,
                channel="RX",
                kind="FRAMING_ERROR",
                detail="stop bit sampled mid-bit",
            ),
            TraceEvent(
                t_us=t0 + 180,
                bus=BusKind.UART,
                channel="RX",
                kind="GARBAGE",
                detail="received 0xC3 expected 'U'",
                byte=0xC3,
            ),
        ]
    return [
        TraceEvent(
            t_us=t0,
            bus=BusKind.UART,
            channel="TX",
            kind="FRAME",
            detail="OK 57600 8N1",
            byte=0x55,
        ),
        TraceEvent(
            t_us=t0 + 180,
            bus=BusKind.UART,
            channel="RX",
            kind="FRAME",
            detail="echo 'U'",
            byte=0x55,
        ),
    ]


def _gpio_events(*, mux_wrong: bool, t0: int = 700) -> list[TraceEvent]:
    if mux_wrong:
        return [
            TraceEvent(
                t_us=t0,
                bus=BusKind.GPIO,
                channel="PB4",
                kind="IDLE",
                detail="INT1 high, EXTI not mapped (AF still SPI_CS on PA4)",
                level=1,
            )
        ]
    return [
        TraceEvent(
            t_us=t0,
            bus=BusKind.GPIO,
            channel="PB4",
            kind="IRQ",
            detail="falling edge → EXTI4",
            level=0,
        )
    ]


SCENARIOS = {
    "first-power": {
        "label": "First power — typical bring-up faults",
        "i2c_nack": True,
        "spi_mode_mismatch": True,
        "spi_clock_gated": False,
        "uart_baud_mismatch": True,
        "pinmux_ok": False,
        "i2c1_gated": False,
    },
    "clock-gate": {
        "label": "SPI1 clock gate left off after reset",
        "i2c_nack": False,
        "spi_mode_mismatch": False,
        "spi_clock_gated": True,
        "uart_baud_mismatch": False,
        "pinmux_ok": True,
        "i2c1_gated": False,
    },
    "clean": {
        "label": "Healthy board after bring-up",
        "i2c_nack": False,
        "spi_mode_mismatch": False,
        "spi_clock_gated": False,
        "uart_baud_mismatch": False,
        "pinmux_ok": True,
        "i2c1_gated": False,
    },
}


class BoardSim:
    """In-memory MCU + attached sensors."""

    def __init__(self, board: str = "nucleo-f411-devkit", scenario: str = "first-power") -> None:
        if scenario not in SCENARIOS:
            raise KeyError(f"Unknown scenario: {scenario}. Choose from {list(SCENARIOS)}")
        self.board = board
        self.mcu = "STM32F411CEU6"
        self.scenario = scenario
        self._cfg = SCENARIOS[scenario]

    def clocks(self) -> list[ClockNode]:
        return _clock_tree(
            i2c1_gated=bool(self._cfg["i2c1_gated"]),
            spi1_gated=bool(self._cfg["spi_clock_gated"]),
        )

    def peripherals(self) -> list[Peripheral]:
        return _peripherals(
            i2c_fw_addr=0x45 if self._cfg["i2c_nack"] else 0x44,
            spi_fw_mode=3 if self._cfg["spi_mode_mismatch"] else 0,
            uart_fw_baud=115200 if self._cfg["uart_baud_mismatch"] else 57600,
            uart_hw_baud=57600,
            pinmux_ok=bool(self._cfg["pinmux_ok"]),
        )

    def capture(self) -> Capture:
        events: list[TraceEvent] = []
        events.extend(_i2c_events(nack=bool(self._cfg["i2c_nack"])))
        events.extend(
            _spi_events(
                mode_mismatch=bool(self._cfg["spi_mode_mismatch"]),
                clock_gated=bool(self._cfg["spi_clock_gated"]),
            )
        )
        events.extend(_uart_events(baud_mismatch=bool(self._cfg["uart_baud_mismatch"])))
        events.extend(_gpio_events(mux_wrong=not bool(self._cfg["pinmux_ok"])))
        duration = max(e.t_us for e in events) + 50
        return Capture(
            board=self.board,
            scenario=self.scenario,
            duration_us=duration,
            events=events,
        )
