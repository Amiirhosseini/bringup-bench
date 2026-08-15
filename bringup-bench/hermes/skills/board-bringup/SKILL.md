---
name: board-bringup
description: Diagnose MCU first-power faults from bus traces and clocks
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [embedded, bring-up, mcu, rack, bringup-bench]
    category: embedded
    requires_toolsets: [terminal]
---

# Board Bring-up

## When to Use

First power on a new MCU board: peripherals silent, WHO_AM_I wrong, clocks gated,
or "it works on the eval kit."

## Procedure

1. Capture and diagnose:
   ```bash
   bringup --scenario first-power health
   bringup --scenario first-power trace
   bringup clocks
   ```
2. Plan before changing firmware:
   ```bash
   bringup plan "why does I2C NACK and SPI WHO_AM_I read 0x00"
   ```
3. Work findings in order: clocks → address/mode → pinmux → UART fixture.
4. Emit reviewable stubs:
   ```bash
   bringup stubs --out generated/
   ```
5. Re-run `bringup --scenario clean health` after fixes.

## Pitfalls

- Flashing generated C without reviewing RCC and AF registers.
- Treating UART framing errors as a bad cable when baud differs from the fixture.
- Sharing SPI CS and EXTI on the same pin.

## Verification

`clean` scenario: zero critical findings; I2C ACK; SPI WHO_AM_I = 0x6A.
