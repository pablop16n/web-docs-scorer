---
description: Set up development environment
allowed-tools: Read, Bash
---

# Setup Development Environment

Install web-docs-scorer in development mode with all tools.

---

## Quick Setup

```bash
# Install package with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

---

## Full Workflow

### 1. Create Virtual Environment (Optional)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 2. Install Package

```bash
pip install -e ".[dev]"
```

Installs:
- Main dependencies: docopt, pandas, joblib, zstandard, scipy, numpy
- Dev tools: pre-commit, black, ruff, mypy, pytest

### 3. Setup Pre-commit Hooks

```bash
pre-commit install
```

Hooks run automatically on `git commit`.

### 4. Verify Installation

```bash
# Check import works
python -c "from docscorer import DocumentScorer; print('OK')"

# Check dev tools
black --version
ruff --version
mypy --version
pytest --version
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `pip install` fails | Upgrade pip: `pip install --upgrade pip` |
| scipy/numpy version conflict | Use Python 3.10+ |
| pre-commit not found | `pip install pre-commit` |

---

## Project Structure After Setup

```
web-docs-scorer/
|-- src/docscorer/     # Main package
|-- tests/             # Test files
|-- pyproject.toml     # Project config
|-- CLAUDE.md          # Claude Code instructions
+-- .claude/           # Claude commands (this folder)
```
