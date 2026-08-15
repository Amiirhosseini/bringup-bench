# Demo walkthrough (no server)

Live page: [amiirhosseini.github.io/bringup-bench](https://amiirhosseini.github.io/bringup-bench/)

Local:

```bash
bringup --scenario first-power health
bringup --scenario first-power trace
bringup plan "fix i2c nack and spi mode"
```

`clean` scenario should report no critical findings.
