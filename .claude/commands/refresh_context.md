---
description: Restore project context after memory loss or compression
allowed-tools: Read
---

# Context Refresh (web-docs-scorer)

> **Scope:** Reload minimal project context for agents.

## Project Overview

Web Docs Scorer (WDS) - Python library for scoring monolingual web-crawled documents on quality (0-1 scale).

---

## 1) Core Files to Read

- [ ] `CLAUDE.md` - project rules, build commands, architecture overview
- [ ] `pyproject.toml` - dependencies and dev tools config
- [ ] `src/docscorer/docscorer.py` - main `DocumentScorer` class
- [ ] `src/docscorer/configuration.py` - `ScorerConfiguration` with language adaptation

---

## 2) Architecture Summary

```
src/docscorer/
|-- docscorer.py           # Entry point: DocumentScorer.score_document()
|-- configuration.py       # ScorerConfiguration - language-specific params
|-- cli.py                 # CLI via docopt
|-- utils.py               # Helper functions
|-- wds_charts.py          # Visualization
|-- scorers/               # Modular scorer classes
|   |-- lang_scorer.py         # Language identification ratio
|   |-- url_scorer.py          # URL density
|   |-- punct_scorer.py        # Punctuation ratio
|   |-- numbers_scorer.py      # Numeric char ratio
|   |-- singular_chars_scorer.py  # Emojis, separators
|   |-- long_texts_scorer.py   # Long segment detection
|   |-- repeated_scorer.py     # Repeated segments
|   |-- informativeness_scorer.py  # Zstandard compression
|   |-- short_segments_score.py    # Segment length variation
|   +-- utils.py               # Scorer utilities
+-- configurations/        # Config files
    |-- char_patterns.json         # Unicode ranges
    |-- informativeness_config.json
    +-- language_adaption/         # Language-specific thresholds
```

---

## 3) Scoring Pipeline

1. Extract features from document segments (word/punct/number counts)
2. Compute 10 individual subscores via specialized scorers
3. Calculate `basic_score = language_score * 0.8 + n_long_segments_score * 0.1 + great_segment_score * 0.1`
4. Calculate `penalty_score` using weighted geometric average
5. Final `WDS_score = basic_score * penalty_score`

---

## 4) Output After Refresh

Respond with:
1. Status: "Context refreshed."
2. Project: web-docs-scorer - document quality scoring library
3. Key entry point: `DocumentScorer.score_document()`
4. Dev commands: pytest, black, ruff, mypy, pre-commit
