# Documentation Standards

> Conventions for writing and maintaining project documentation.

## File Naming

| Type | Convention | Example |
|------|------------|---------|
| Markdown docs | lowercase, hyphens | `tech-stack.md` |
| Python modules | lowercase, underscores | `lang_scorer.py` |
| Configuration | lowercase, underscores | `char_patterns.json` |

## Document Structure

Every document should include:

1. **Title** - H1 header with document name
2. **Description** - One-line summary in blockquote
3. **Content** - Organized with H2/H3 headers
4. **Related Links** - References to related documents

## Markdown Conventions

### Headers

```markdown
# Document Title (H1 - one per document)
## Major Section (H2)
### Subsection (H3)
```

### Tables

Use tables for structured data:

```markdown
| Column A | Column B |
|----------|----------|
| Value 1  | Value 2  |
```

### Code Blocks

Use fenced code blocks with language identifier:

```python
def example():
    return "Hello"
```

## Python Docstrings

Use Google-style docstrings:

```python
def score_document(self, ref_lang: str, document_text: str) -> float:
    """Score a web-crawled document for quality.

    Args:
        ref_lang: ISO 639-3 language code (e.g., "spa", "eng")
        document_text: Document text with segments separated by newlines

    Returns:
        Quality score from 0.0 (low quality) to 1.0 (high quality)

    Example:
        >>> scorer.score_document("spa", "Hola mundo.\\nSegundo parrafo.")
        0.85
    """
```

## Commit Messages

Format: `<type>: <description>`

| Type | Usage |
|------|-------|
| feat | New feature |
| fix | Bug fix |
| docs | Documentation only |
| refactor | Code restructuring |
| test | Adding tests |

## Version Numbers

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking API changes
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

Current version: see `pyproject.toml`
