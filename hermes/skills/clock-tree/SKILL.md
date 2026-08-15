---
name: clock-tree
description: Inspect MCU clock tree and gated peripheral clocks
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [clock, rcc, embedded, bringup-bench]
    category: embedded
---

# Clock Tree

## When to Use

Peripheral silent after reset, SCK/SCL idle, or timers run at the wrong rate.

## Procedure

```bash
bringup clocks
bringup --scenario clock-gate health
```

Enable gated clocks in RCC before the first transaction. Re-check AHB/APB dividers if baud or SPI MHz is wrong.

## Pitfalls

- Enabling the GPIO port clock but not the I2C/SPI kernel clock.
- PLL lock assumed; HSE not actually oscillating.
