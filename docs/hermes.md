# Hermes

```bash
pip install -e .
bringup install-hermes-skills
bringup mcp
```

Skills: `/board-bringup` `/i2c-debug` `/spi-debug` `/uart-debug` `/clock-tree`

Or in `~/.hermes/config.yaml`:

```yaml
skills:
  external_dirs:
    - /path/to/bringup-bench/hermes/skills
```
