# Architecture

Bringup Bench splits **simulation**, **diagnosis**, and **agent planning**.

1. `BoardSim` emits a deterministic clock tree, peripherals, and logic-analyzer events.
2. `diagnose()` compares firmware config vs hardware truth (address, SPI mode, baud, pinmux, RCC gates).
3. `BringupPlanner` turns a natural-language goal into inspectable steps.
4. `generate_stubs()` writes C whoami/init files from **hardware** truth, not the broken driver.

Scenarios: `first-power`, `clock-gate`, `clean`.

Hermes loads skills under `hermes/skills/` or via `bringup install-hermes-skills`. MCP: `bringup mcp`.
