# ADR-002: CLI Library Selection

**Status:** Accepted
**Date:** 2026-01-21
**Decision Makers:** Prompsit Language Engineering Team

## Context

Web Docs Scorer provides a command-line interface for batch document processing. The CLI library choice affects:

1. **Developer experience** - ease of defining arguments
2. **User experience** - help output quality
3. **Codebase size** - amount of boilerplate needed

## Decision

**Use docopt** for command-line argument parsing.

## Rationale

| Factor | docopt | argparse | click |
|--------|--------|----------|-------|
| **Boilerplate** | Zero | High | Medium |
| **Documentation** | Docstring IS the spec | Separate from code | Decorators |
| **Dependencies** | 1 (docopt) | Built-in | 1 (click) |
| **Learning curve** | Minimal | Medium | Medium |

Key reasons for docopt:

1. **Docstring-driven** - CLI spec lives in module docstring, self-documenting
2. **Zero boilerplate** - No argument parser setup, just parse the docstring
3. **Minimal code** - ~10 lines vs 30+ for argparse
4. **Readable spec** - POSIX-style usage string humans can understand

## Alternatives Considered

### argparse (rejected)
- **Pros:** Built-in, no dependencies
- **Cons:** Verbose, requires significant boilerplate for simple CLIs

### click (rejected)
- **Pros:** Powerful, good for complex CLIs
- **Cons:** Decorator-heavy, overkill for simple interface

## Consequences

**Positive:**
- CLI specification is human-readable documentation
- Minimal code in `cli.py`
- Easy to extend with new arguments

**Negative:**
- External dependency
- Less flexibility for complex argument validation

## Implementation

```python
# src/docscorer/cli.py
"""Web Docs Scorer CLI.

Usage:
    docscorer <input> [--output=<file>] [--lang=<code>]
    docscorer -h | --help

Options:
    -h --help        Show this help
    --output=<file>  Output file path
    --lang=<code>    Language code [default: spa]
"""
from docopt import docopt

args = docopt(__doc__)
```

## References

- [docopt documentation](http://docopt.org/)
- [docopt Python package](https://github.com/docopt/docopt)
