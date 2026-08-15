# Flaky Finder 🔍

Static AST analysis tool to diagnose flaky test root causes in Python test suites.

## 🚀 Features

- **FLK001**: Detects hardcoded `time.sleep()` calls
- **FLK002**: Detects unseeded `random` module usage
- **FLK003**: Detects global state mutations (`os.environ`)
- **Pytest Plugin**: Native integration via `pytest --check-flaky`
- **CI Enforcement**: Block builds with `pytest --check-flaky --flaky-fail`
- **Inline Suppression**: Ignore rules using `# flaky: ignore`

---

## 📦 Installation

Install directly from GitHub:

```bash
pip install git+[https://github.com/SamBeingSam/flaky-finder.git](https://github.com/SamBeingSam/flaky-finder.git)
