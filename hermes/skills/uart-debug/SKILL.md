---
name: uart-debug
description: Debug UART framing errors and fixture baud mismatch
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [uart, embedded, bringup-bench]
    category: embedded
---

# UART Debug

## When to Use

Factory fixture or console shows framing errors, garbage, or one-way traffic.

## Procedure

1. `bringup trace` — look for `FRAMING_ERROR`.
2. Match USART_BRR to the fixture (this board: 57600 8N1), not the debug dongle default 115200.
3. Confirm TX/RX not swapped on the harness.

## Pitfalls

- APB clock change without recomputing BRR.
- Assuming 115200 because the eval kit used it.
