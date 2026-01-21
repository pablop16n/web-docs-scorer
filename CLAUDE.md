# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **SCOPE:** Entry point with project overview and navigation ONLY. Contains project summary, documentation rules, and links to detailed docs. DO NOT add: scoring formulas (-> README.md), architecture details (-> architecture.md), principles (-> principles.md), technical specs (-> tech_stack.md).

## Critical Rules for AI Agents

**Read this table BEFORE starting any work.**

| Rule | When to Apply | Details |
|------|---------------|---------|
| **Search MCP Ref First** | Before proposing changes | Always search `mcp__Ref__ref_search_documentation` for official solutions (pandas, scipy, numpy) |
| **English Only** | All project content | Code, docs, variables - everything in English. Chat communication in Russian |
| **Read README First** | Before folder work | ALWAYS read README.md in folder before creating/editing files |
| **No Unicode in Python** | Writing Python code | Use ASCII only in Python scripts (user preference) |

## Navigation

**DAG Structure:** CLAUDE.md -> docs/README.md -> topic docs. Read SCOPE tag first in each doc.

## Project Overview

Web Docs Scorer (WDS) - Python library that scores monolingual web-crawled documents on quality (0-1 scale). Analyzes textual indicators to detect issues like excessive URLs, punctuation problems, repetitions, and non-linguistic content.

## Documentation

All project documentation accessible through **[docs/README.md](docs/README.md)** - central navigation hub.

**Quick links:**

| Document | Description |
|----------|-------------|
| [docs/README.md](docs/README.md) | Documentation navigation hub |
| [docs/project/architecture.md](docs/project/architecture.md) | System architecture, components, directory structure |
| [docs/project/requirements.md](docs/project/requirements.md) | Functional/non-functional requirements |
| [docs/project/tech_stack.md](docs/project/tech_stack.md) | Technology choices and rationale |
| [docs/principles.md](docs/principles.md) | Development principles (KISS, DRY, YAGNI) |
| [docs/reference/README.md](docs/reference/README.md) | ADRs, Guides, Manuals |
| [README.md](README.md) | Algorithm documentation, scoring formulas, usage examples |

## Project Highlights

**Unique to this project** (not generic Python patterns):

- **Statistical scoring without ML** - Uses ratios and compression, no neural networks or GPU required
- **Language adaptation via cross-multiplication** - Spanish as reference, other languages adapted from medians
- **10 subscores with weighted geometric penalty** - Amplifies worst scores using custom exponents (alpha=2.9, beta=3.0)
- **Zstandard compression for informativeness** - Detects random text and hashes via compression ratio
- **WALS fallback chain** - Unknown languages fall back to same family/script, then averages

**See [README.md](README.md) for detailed algorithm documentation and [docs/project/architecture.md](docs/project/architecture.md) for system design.**

## Technology Stack

**Core:** Python 3.10+ | pandas | scipy >= 1.14 | numpy >= 2 | zstandard | joblib | docopt

**Dev:** pytest | black | ruff | mypy | pre-commit

See [docs/project/tech_stack.md](docs/project/tech_stack.md) for complete technology stack and rationale.

## Commands

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Code quality
black src/                      # Format
ruff check --fix src/           # Lint
mypy src/                       # Type check
pre-commit run --all-files      # All checks

# Tests
pytest
```

## Maintenance

**Update trigger:** After changing project navigation (new/renamed docs), updating critical rules for agents, or modifying entry points.

**Verification:**
- Quick links resolve to existing files
- Critical rules align with current requirements
- Commands match pyproject.toml

**Last Updated:** 2026-01-21
