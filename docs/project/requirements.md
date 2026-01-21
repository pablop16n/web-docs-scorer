# Requirements

> **SCOPE:** Functional and non-functional requirements ONLY. For implementation details, see [architecture.md](architecture.md). For usage examples, see [README.md](../../README.md).

## Purpose

Score monolingual web-crawled documents on quality (0-1 scale) to filter datasets for NLP training.

## Functional Requirements

### FR-1: Document Scoring

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Score documents from 0.0 (low quality) to 1.0 (high quality) | Must |
| FR-1.2 | Return detailed subscores explaining the final score | Must |
| FR-1.3 | Support raw_score mode (final score only) | Should |

### FR-2: Language Support

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Support any language with ISO 639-3 code | Must |
| FR-2.2 | Adapt scoring thresholds per language | Must |
| FR-2.3 | Fall back to language family when language unknown | Should |
| FR-2.4 | Fall back to script average when family unknown | Should |

### FR-3: Quality Indicators

| ID | Indicator | What it Detects |
|----|-----------|-----------------|
| FR-3.1 | Language ratio | Mixed-language content |
| FR-3.2 | URL density | Link farms, navigation pages |
| FR-3.3 | Punctuation ratio | SEO lists, code dumps |
| FR-3.4 | Numbers ratio | Tables, catalogs |
| FR-3.5 | Singular chars | Emojis, separators |
| FR-3.6 | Long segments | Quality paragraph presence |
| FR-3.7 | Repeated segments | Boilerplate, headers/footers |
| FR-3.8 | Informativeness | Random text, hashes |
| FR-3.9 | Short segments | Menu fragments, tags |

### FR-4: Input Format

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Accept document text with `\n` segment separators | Must |
| FR-4.2 | Accept per-segment language labels | Must |
| FR-4.3 | Accept document-level language and script | Must |

## Non-Functional Requirements

### NFR-1: Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1.1 | Process single document | < 100ms |
| NFR-1.2 | Memory per document | < 50MB |
| NFR-1.3 | No GPU required | CPU-only |

### NFR-2: Compatibility

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-2.1 | Python version | >= 3.10 |
| NFR-2.2 | OS support | Linux, Windows, macOS |
| NFR-2.3 | Installation method | pip install |

### NFR-3: Quality

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-3.1 | Type safety | mypy strict mode |
| NFR-3.2 | Code style | black + ruff |
| NFR-3.3 | Test coverage | pytest |

## Out of Scope

- Semantic/thematic analysis
- Web crawling or document fetching
- GUI or web interface
- Real-time streaming processing
- Language identification (expects pre-labeled input)

## Data Sources

Training data for threshold calibration:
- **HPLT v1.2** - High-Performance Language Technologies dataset
- **Spanish** as reference language for all adaptations
