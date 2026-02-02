---
description: Run tests and code quality checks
allowed-tools: Read, Bash
---

# Run Tests

Execute tests and code quality checks for web-docs-scorer.

---

## Quick Commands

| Check | Command |
|-------|---------|
| **All checks** | `pre-commit run --all-files` |
| **Tests only** | `pytest` |
| **Format** | `black src/` |
| **Lint** | `ruff check --fix src/` |
| **Types** | `mypy src/` |

---

## Workflow

### 1. Run All Checks (Recommended)

```bash
pre-commit run --all-files
```

Runs: black, ruff, mypy in sequence.

### 2. Run Tests

```bash
pytest
```

For verbose output:
```bash
pytest -v
```

### 3. Individual Checks

**Format code:**
```bash
black src/
```

**Lint with auto-fix:**
```bash
ruff check --fix src/
```

**Type checking:**
```bash
mypy src/
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `pre-commit not found` | `pip install pre-commit && pre-commit install` |
| `black/ruff/mypy not found` | `pip install -e ".[dev]"` |
| Import errors | Reinstall: `pip install -e .` |

---

## Success Criteria

- [ ] All tests pass
- [ ] No black formatting changes
- [ ] No ruff errors
- [ ] No mypy type errors
