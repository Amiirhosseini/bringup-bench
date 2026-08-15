# I2C 7-bit addresses in this sim

| Device | ADDR pin | 7-bit | Write byte |
|--------|----------|-------|------------|
| OPT3001 | GND | 0x44 | 0x88 |
| OPT3001 | VDD | 0x45 | 0x8A |

A NACK on `0x45 WRITE` with a GND-strapped part is an address bug, not a dead chip.
