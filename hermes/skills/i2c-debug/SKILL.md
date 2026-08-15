---
name: i2c-debug
description: Debug I2C NACK, wrong 7-bit address, and missing pull-ups
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [i2c, embedded, bringup-bench]
    category: embedded
---

# I2C Debug

## When to Use

NACK on address, WHO_AM_I never returns, or scan finds a different address than the driver.

## Procedure

1. `bringup trace` — look for START, ADDR, ACK/NACK, STOP.
2. `bringup run "i2c nack opt3001" --execute`
3. Compare firmware 7-bit addr vs ADDR pin / datasheet.
4. Confirm 4.7k pull-ups on SCL/SDA and that I2C clock is ungated.

## Pitfalls

- 8-bit vs 7-bit address (0x88 write is 0x44 << 1).
- Clock stretching timeouts mistaken for NACK.

## Reference

See `references/addr.md`.
