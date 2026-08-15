# Flaky Finder 🔍

Static AST analysis tool to diagnose flaky test root causes in Python test suites.

## Features
- Detects hardcoded `time.sleep()` calls (`FLK001`)
- Detects unseeded `random` module calls (`FLK002`)
- Detects global state mutations like `os.environ` (`FLK003`)
- Native CLI and Pytest plugin support (`pytest --check-flaky`)
- Suppression via `# flaky: ignore` comments

## Quickstart
```bash
pip install -e .
flaky-finder tests/