# Technology Stack

> **SCOPE:** Technology choices and versions ONLY. For architecture decisions rationale, see [ADRs](../reference/adrs/). For system design, see [architecture.md](architecture.md).

## Runtime

| Component | Choice | Version | Rationale |
|-----------|--------|---------|-----------|
| **Language** | Python | >= 3.10 | Type hints, match statements, scientific ecosystem |
| **Package Manager** | pip | latest | Standard, wide compatibility |

## Core Dependencies

| Package | Version | Purpose | Why This Choice |
|---------|---------|---------|-----------------|
| **pandas** | latest | Data manipulation | Fast segment feature extraction |
| **numpy** | >= 2 | Numerical operations | Array operations for scoring |
| **scipy** | >= 1.14 | Statistical functions | Interpolation for thresholds |
| **zstandard** | latest | Compression | Informativeness score calculation |
| **joblib** | latest | Serialization | Load pickled interpolation functions |
| **docopt** | latest | CLI parsing | Simple, declarative argument parsing |

### Why These Dependencies?

**pandas + numpy**: Industry standard for numerical Python. Efficient segment-level feature extraction.

**scipy**: Provides `interp1d` for threshold interpolation curves. No lighter alternative with same functionality.

**zstandard**: Fast compression for informativeness metric. Better compression ratio than gzip, faster than bzip2.

**joblib**: Efficient loading of pickled interpolation functions. Better than raw pickle for numpy arrays.

**docopt**: Minimal CLI library. Generates parser from docstring - zero boilerplate.

## Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| **pytest** | >= 8.0 | Testing framework |
| **black** | >= 24.0 | Code formatting |
| **ruff** | >= 0.5 | Linting + import sorting |
| **mypy** | >= 1.0 | Static type checking |
| **pre-commit** | >= 3.0 | Git hooks management |

### Code Quality Tools Config

**black** (pyproject.toml):
```toml
[tool.black]
line-length = 88
target-version = ["py310"]
```

**ruff** (pyproject.toml):
```toml
[tool.ruff]
line-length = 88
target-version = "py310"
select = ["E", "F", "B", "I"]
fix = true
```

**mypy** (pyproject.toml):
```toml
[tool.mypy]
python_version = "3.10"
ignore_missing_imports = true
strict = true
```

## Design Decisions

### ML-Based Scoring (Rejected)

| Option | Rejected Because |
|--------|------------------|
| Transformer models | Too heavy, requires GPU |
| fastText | Still requires model files |
| Statistical only | **Chosen** - lightweight, no models |

### Architecture Decision Records

For detailed rationale on library choices, see ADRs:

| Decision | ADR | Summary |
|----------|-----|---------|
| Compression library | [ADR-001](../reference/adrs/adr-001-compression-library.md) | Zstandard for best ratio/speed balance |
| CLI library | [ADR-002](../reference/adrs/adr-002-cli-library.md) | docopt for zero-boilerplate parsing |

## File Formats

| Format | Used For | Rationale |
|--------|----------|-----------|
| JSON | Character patterns, config | Human-readable, standard |
| CSV | Language medians, WALS data | Tabular data, easy to update |
| Pickle (.pkl) | Interpolation functions | scipy objects, performance |

## Compatibility Matrix

| Python | numpy | scipy | Status |
|--------|-------|-------|--------|
| 3.10 | >= 2.0 | >= 1.14 | Supported |
| 3.11 | >= 2.0 | >= 1.14 | Supported |
| 3.12 | >= 2.0 | >= 1.14 | Supported |
| < 3.10 | - | - | Not supported |

## Installation

```bash
# Production install
pip install docscorer

# Development install
pip install -e ".[dev]"
```

## No Infrastructure Required

This is a **pure Python library** with no:
- Docker containers
- Database connections
- Web server
- GPU requirements
- Cloud services

All computation runs locally on CPU.
