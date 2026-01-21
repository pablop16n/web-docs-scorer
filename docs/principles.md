# Development Principles

> Core principles guiding the design and implementation of Web Docs Scorer.

## Design Philosophy

Web Docs Scorer is designed to be:

1. **Lightweight** - No heavy ML models, uses compression and statistics
2. **Language-agnostic** - Works with any language via adaptation
3. **Surface-level** - Analyzes structure, not semantics
4. **Transparent** - Subscores explain the final score

## Core Principles

### KISS (Keep It Simple, Stupid)

> Prefer simple solutions over complex ones.

**Applied in WDS:**
- Simple ratios (punctuation/alphabetic characters) instead of ML models
- Linear interpolation for scoring thresholds
- Zstandard compression as informativeness proxy

### YAGNI (You Aren't Gonna Need It)

> Don't add functionality until it's needed.

**Applied in WDS:**
- No semantic analysis (not needed for quality detection)
- No deep learning (statistical methods sufficient)
- No web interface (library-only design)

### DRY (Don't Repeat Yourself)

> Every piece of knowledge should have a single source of truth.

**Applied in WDS:**
- Language adaptation via cross-multiplication from Spanish reference
- Shared `_extract_features()` for all scorers
- Configuration loaded once in `ScorerConfiguration`

### Single Responsibility Principle

> A class should have only one reason to change.

**Applied in WDS:**
- Each scorer handles exactly one metric (URL, punctuation, numbers...)
- `DocumentScorer` orchestrates, doesn't calculate
- `ScorerConfiguration` handles only language adaptation

## Anti-Patterns to Avoid

| Anti-Pattern | Why Bad | WDS Approach |
|--------------|---------|--------------|
| **Premature optimization** | Adds complexity without proof | Profile first, optimize proven bottlenecks |
| **Magic numbers** | Unclear meaning | Named constants in configuration |
| **God class** | Hard to test/maintain | Small, focused scorer classes |
| **Deep nesting** | Hard to read | Early returns, flat structure |

## Code Quality

### Type Hints

All public functions must have type hints:

```python
def score_document(
    self,
    ref_lang: str,
    ref_script: str,
    lang_segments: list[str],
    document_text: str,
    doc_id: str,
    raw_score: bool = False
) -> dict[str, Any] | float:
```

### Testing

- Unit tests for each scorer
- Integration tests for full pipeline
- Edge cases: empty documents, unknown languages

### Documentation

- Docstrings for public API
- README.md for algorithm explanation
- CLAUDE.md for build commands
