# Bringup Bench

**Agentic MCU board bring-up** — clock trees, I2C/SPI/UART traces, pinmux, and reviewable C driver stubs — with [Hermes Agent](https://hermes-agent.nousresearch.com/) skills and an MCP server.

> **Live demo:** [amiirhosseini.github.io/bringup-bench](https://amiirhosseini.github.io/bringup-bench/)  
> Switch `first-power` / `clock-gate` / `clean`, read analyzer lanes, inspect the agent plan.

New boards fail in the same few ways: wrong 7-bit I2C address, SPI mode leftover from an eval kit, UART baud vs the factory fixture, RCC clock still gated, EXTI sharing a SPI chip-select. Bringup Bench turns those into **ranked findings** and **inspectable plans** you can run offline.

[![Live Demo](https://img.shields.io/badge/demo-live-5ee0a8)](https://amiirhosseini.github.io/bringup-bench/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-green.svg)](pyproject.toml)

## Features

| Area | What you get |
|------|----------------|
| **Board sim** | STM32-class clock tree + OPT3001 (I2C) + LSM6-class IMU (SPI) + console UART |
| **Logic-analyzer events** | START/ADDR/ACK/NACK, SPI WHO_AM_I, UART framing, EXTI edges |
| **Diagnose engine** | Address, CPOL/CPHA, baud, pinmux, gated clocks |
| **Agent planner** | Natural-language goals → steps |
| **C stubs** | Whoami/init from **hardware** truth (review before flash) |
| **Hermes skills** | `board-bringup`, `i2c-debug`, `spi-debug`, `uart-debug`, `clock-tree` |
| **MCP + HTTP API** | For Hermes / other agents / dashboards |

## Quick start

```bash
git clone https://github.com/Amiirhosseini/bringup-bench.git
cd bringup-bench
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

bringup --scenario first-power health
bringup --scenario first-power trace
bringup plan "why does I2C NACK and SPI WHO_AM_I read 0x00"
bringup stubs --out generated/
```

Scenarios: `first-power` (default faults), `clock-gate`, `clean`.

```bash
bringup serve    # http://127.0.0.1:8790/docs
bringup mcp      # Hermes / MCP clients
```

## Hermes

```bash
bringup install-hermes-skills
```

Prompts: `/board-bringup` `/i2c-debug` `/spi-debug` `/uart-debug` `/clock-tree`

## Example findings (`first-power`)

| Severity | Code | Meaning |
|----------|------|---------|
| critical | `i2c.addr_mismatch` | Driver 0x45, ADDR pin → 0x44 |
| critical | `spi.mode_mismatch` | Mode 3 vs device mode 0 |
| warn | `uart.baud_mismatch` | 115200 vs fixture 57600 |
| warn | `gpio.pinmux` | INT1 not on PB4 EXTI |

## Safety

Assist mode plans firmware edits; it does not flash MCUs. Generated C is a starting point — review RCC and alternate functions.

## Layout

```text
bringup-bench/
├── src/bringupbench/   # sim, diagnose, agent, CLI, API
├── firmware/           # example C drivers + host HAL
├── hermes/skills/
├── boards/
├── docs/               # GitHub Pages live demo
└── tests/
```

## License

Apache 2.0 — see [LICENSE](LICENSE).
