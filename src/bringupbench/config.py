"""Configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentConfig(BaseModel):
    mode: Literal["assist", "autopilot"] = "assist"
    max_plan_steps: int = 10


class AppConfig(BaseModel):
    board: str = "nucleo-f411-devkit"
    scenario: str = "first-power"
    agent: AgentConfig = Field(default_factory=AgentConfig)
    api_host: str = "127.0.0.1"
    api_port: int = 8790
    boards_dir: Path = Path("boards")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BRINGUP_", extra="ignore")
    board: str | None = None
    scenario: str | None = None
    api_host: str | None = None
    api_port: int | None = None


def load_config() -> AppConfig:
    settings = Settings()
    cfg = AppConfig()
    if settings.board:
        cfg.board = settings.board
    if settings.scenario:
        cfg.scenario = settings.scenario
    if settings.api_host:
        cfg.api_host = settings.api_host
    if settings.api_port:
        cfg.api_port = settings.api_port
    return cfg
