"""HTTP API."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from bringupbench.agent.planner import BringupPlanner, ToolExecutor
from bringupbench.config import AppConfig, load_config
from bringupbench.models import AgentAction
from bringupbench.sim.board import BoardSim, SCENARIOS


class PlanRequest(BaseModel):
    goal: str
    scenario: str | None = None


class ActionRequest(BaseModel):
    name: str
    args: dict = Field(default_factory=dict)
    scenario: str | None = None


def create_app(config: AppConfig | None = None) -> FastAPI:
    cfg = config or load_config()
    app = FastAPI(
        title="Bringup Bench",
        description="Agentic MCU board bring-up API",
        version="0.1.0",
    )
    planner = BringupPlanner(cfg)
    executor = ToolExecutor(cfg)

    def _maybe_scenario(scenario: str | None) -> None:
        if scenario:
            executor.sim = BoardSim(board=cfg.board, scenario=scenario)

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok", "board": cfg.board}

    @app.get("/v1/scenarios")
    def scenarios() -> dict[str, str]:
        return {k: v["label"] for k, v in SCENARIOS.items()}

    @app.get("/v1/snapshot")
    def snapshot(scenario: str | None = None) -> dict:
        _maybe_scenario(scenario)
        return executor.snapshot().model_dump(mode="json")

    @app.post("/v1/plan")
    def plan(req: PlanRequest) -> dict:
        _maybe_scenario(req.scenario)
        snap = executor.snapshot()
        return planner.plan(req.goal, snap).model_dump(mode="json")

    @app.post("/v1/actions")
    def actions(req: ActionRequest) -> dict:
        _maybe_scenario(req.scenario)
        result = executor.execute(AgentAction(name=req.name, args=req.args))
        return {"result": result}

    return app
