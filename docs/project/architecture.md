# Architecture

> **SCOPE:** System architecture and component design ONLY. Contains diagrams, components, directory structure. DO NOT add: scoring formulas (-> README.md), technology rationale (-> tech_stack.md), requirements (-> requirements.md).

## High-Level Overview

```
+------------------+     +---------------------+     +------------------+
|                  |     |                     |     |                  |
|  Input Document  +---->+  DocumentScorer     +---->+  WDS Score +     |
|  (text + labels) |     |  (orchestrator)     |     |  Subscores       |
|                  |     |                     |     |                  |
+------------------+     +----------+----------+     +------------------+
                                    |
                                    v
                         +----------+----------+
                         |                     |
                         | ScorerConfiguration |
                         | (language params)   |
                         |                     |
                         +----------+----------+
                                    |
                    +---------------+---------------+
                    |               |               |
              +-----v-----+  +------v------+  +-----v-----+
              |           |  |             |  |           |
              | LangScorer|  | URLScorer   |  |  ...8 more|
              |           |  |             |  |           |
              +-----------+  +-------------+  +-----------+
```

## Component Architecture

### Entry Points

| Component | File | Responsibility |
|-----------|------|----------------|
| **DocumentScorer** | `docscorer.py` | Orchestrate scoring pipeline |
| **ScorerConfiguration** | `configuration.py` | Language-specific parameters |
| **CLI** | `cli.py` | Command-line interface |

### Scorer Pipeline

```
Document Text
     |
     v
+--------------------+
| _extract_features()|  Extract word/punct/number counts per segment
+--------------------+
     |
     v
+--------------------+
| Individual Scorers |  Compute 10 subscores (0-1 each)
+--------------------+
     |
     v
+--------------------+
| _aggregate_scores()|  Combine into basic_score + penalty_score
+--------------------+
     |
     v
WDS_score = basic_score * penalty_score
```

### Scorer Classes

| Scorer | File | Metric |
|--------|------|--------|
| LangScorer | `lang_scorer.py` | Language identification ratio |
| URLScorer | `url_scorer.py` | URL density |
| PunctScorer | `punct_scorer.py` | Punctuation ratio (too much/few) |
| NumsScorer | `numbers_scorer.py` | Numeric character ratio |
| SingularCharsScorer | `singular_chars_scorer.py` | Emojis, separators |
| LongTextScorer | `long_texts_scorer.py` | Long/superlong segments |
| RepeatedScorer | `repeated_scorer.py` | Repeated segments |
| InformativenessScorer | `informativeness_scorer.py` | Compression ratio |
| ShortSegmentsScore | `short_segments_score.py` | Segment length variation |

## Language Adaptation

```
+------------------+     +---------------------+     +------------------+
|                  |     |                     |     |                  |
| Spanish Medians  +---->+ Cross-Multiplication+---->+ Adapted Thresholds|
| (reference)      |     |                     |     | (target language) |
|                  |     |                     |     |                  |
+------------------+     +---------------------+     +------------------+
```

**Fallback chain for unknown languages:**
1. Same WALS family + same script
2. Same script average
3. Global average

## Configuration Files

| File | Purpose |
|------|---------|
| `char_patterns.json` | Unicode ranges for character types |
| `informativeness_config.json` | Compression function groups/weights |
| `medians_language.csv` | Language-specific scoring thresholds |
| `lang_families_script.csv` | WALS family relationships |
| `interpolation_functions/*.pkl` | Pickled interpolation functions |

## Directory Structure

```
src/docscorer/
|-- docscorer.py           # Main entry point
|-- configuration.py       # Language adaptation
|-- cli.py                 # CLI interface
|-- utils.py               # Shared utilities
|-- wds_charts.py          # Visualization
|-- scorers/               # Scorer implementations
|   |-- lang_scorer.py
|   |-- url_scorer.py
|   |-- punct_scorer.py
|   |-- numbers_scorer.py
|   |-- singular_chars_scorer.py
|   |-- long_texts_scorer.py
|   |-- repeated_scorer.py
|   |-- informativeness_scorer.py
|   |-- short_segments_score.py
|   +-- utils.py
+-- configurations/        # Static configuration
    |-- char_patterns.json
    |-- informativeness_config.json
    |-- language_adaption/
    |   |-- medians_language.csv
    |   |-- lang_families_script.csv
    |   +-- extract_ratios.py
    +-- interpolation_functions/
        +-- *.pkl
```

---

**See [README.md](../../README.md) for usage examples and detailed algorithm documentation.**
