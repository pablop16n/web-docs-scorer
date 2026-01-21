# ADR-001: Compression Library Selection

**Status:** Accepted
**Date:** 2026-01-21
**Decision Makers:** Prompsit Language Engineering Team

## Context

Web Docs Scorer uses compression to calculate the **informativeness_score** - a metric that detects repetitive content and random/hashed text by analyzing compression ratios. The compression library choice directly impacts:

1. **Scoring accuracy** - compression ratio determines informativeness detection
2. **Performance** - compression speed affects document processing time
3. **Dependencies** - library must be pip-installable with no system dependencies

## Decision

**Use Zstandard (zstd)** via the `zstandard` Python package for document compression.

## Rationale

| Factor | Zstandard | gzip | lz4 | bzip2 |
|--------|-----------|------|-----|-------|
| **Compression ratio** | High | Medium | Low | Highest |
| **Speed** | Fast | Medium | Fastest | Slow |
| **Balance** | Best ratio/speed | Acceptable | Speed-focused | Ratio-focused |
| **Python package** | zstandard | built-in | python-lz4 | built-in |

Key reasons for Zstandard:

1. **Best compression/speed balance** - Higher ratio than gzip, faster than bzip2
2. **Dictionary support** - Can be tuned for specific content types
3. **Consistent behavior** - Deterministic output across platforms
4. **Active development** - Facebook-backed, regular updates

## Alternatives Considered

### gzip (rejected)
- **Pros:** Built into Python, widely used
- **Cons:** Lower compression ratio affects informativeness accuracy

### lz4 (rejected)
- **Pros:** Fastest compression
- **Cons:** Too low compression ratio - can't distinguish repetitive from random content

### bzip2 (rejected)
- **Pros:** Highest compression ratio
- **Cons:** Too slow for batch document processing

## Consequences

**Positive:**
- Accurate informativeness scoring via high compression ratios
- Fast document processing (< 100ms per document)
- Single pip dependency (`zstandard`)

**Negative:**
- External dependency (not built-in like gzip)
- Requires users to install zstandard package

## Implementation

```python
# src/docscorer/scorers/informativeness_scorer.py
import zstandard as zstd

compression_ratio = 1 - (compressed_weight / raw_weight) * 100
```

## References

- [Zstandard documentation](https://python-zstandard.readthedocs.io/)
- [Compression benchmark](https://github.com/facebook/zstd#benchmarks)
