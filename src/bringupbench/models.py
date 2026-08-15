"""Domain models for boards, buses, traces, and agent plans."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class BusKind(str, Enum):
    I2C = "i2c"
    SPI = "spi"
    UART = "uart"
    GPIO = "gpio"
    CLOCK = "clock"


class ClockNode(BaseModel):
    name: str
    source: str
    hz: int
    gated: bool = False
    enabled: bool = True
    consumers: list[str] = Field(default_factory=list)


class Peripheral(BaseModel):
    name: str
    kind: BusKind
    instance: str
    address: int | None = None
    pins: dict[str, str] = Field(default_factory=dict)
    clock: str
    firmware_config: dict[str, Any] = Field(default_factory=dict)
    hardware_config: dict[str, Any] = Field(default_factory=dict)
    present: bool = True
    notes: str = ""


class TraceEvent(BaseModel):
    t_us: int
    bus: BusKind
    channel: str
    kind: str
    detail: str
    ack: bool | None = None
    byte: int | None = None
    level: int | None = None


class Capture(BaseModel):
    board: str
    scenario: str
    duration_us: int
    events: list[TraceEvent]
    captured_at: datetime = Field(default_factory=utcnow)


class Finding(BaseModel):
    severity: Literal["info", "warn", "critical"]
    code: str
    title: str
    detail: str
    resource: str
    suggested_action: str | None = None
    evidence: list[str] = Field(default_factory=list)


class BoardSnapshot(BaseModel):
    board: str
    mcu: str
    scenario: str
    clocks: list[ClockNode]
    peripherals: list[Peripheral]
    capture: Capture
    findings: list[Finding] = Field(default_factory=list)
    collected_at: datetime = Field(default_factory=utcnow)


class AgentAction(BaseModel):
    name: str
    args: dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = False
    rationale: str = ""


class AgentPlan(BaseModel):
    goal: str
    steps: list[AgentAction]
    risks: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)
