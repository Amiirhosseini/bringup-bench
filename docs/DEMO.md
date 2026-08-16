# Interactive live demo

Open **https://amiirhosseini.github.io/bringup-bench/**

The page is a real simulator (JavaScript), not a screenshot.

Try this path:

1. Preset **first-power** — I2C NACK, SPI WHO_AM_I = 0x00, UART framing.
2. Set firmware I2C address to **0x44**. Finding `i2c.addr_mismatch` disappears; I2C lane ACKs.
3. Set SPI mode to **mode 0**. IMU WHO_AM_I becomes 0x6A.
4. Set UART baud to **57600**. Framing error clears.
5. Check **INT1 mapped to PB4 EXTI**.
6. Press **Run probe** — console should read PASS.

Then load **clock-gate**, enable **SPI1 clock**, probe again.

All of that runs in the browser. Clone the repo only if you want the Python CLI / Hermes skills.
