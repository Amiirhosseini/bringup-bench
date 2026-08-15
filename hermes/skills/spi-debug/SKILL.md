---
name: spi-debug
description: Debug SPI CPOL/CPHA mismatch and gated SCK
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [spi, embedded, bringup-bench]
    category: embedded
---

# SPI Debug

## When to Use

WHO_AM_I reads 0x00/0xFF, SCK stays low while CS is asserted, or data is bit-shifted.

## Procedure

1. Confirm RCC SPI clock enabled (`bringup --scenario clock-gate health`).
2. Match mode to datasheet (this IMU: mode 0, idle low, sample rising).
3. Check CS is GPIO AF, not left as EXTI.

## Pitfalls

- Mode 3 vs mode 0 is a common STM32 SPL leftover.
- Reading MISO on the wrong edge looks like a "dead" sensor.
