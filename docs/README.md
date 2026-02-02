# Web Docs Scorer - Documentation

> Navigation hub for project documentation.

## Quick Links

| Document | Description |
|----------|-------------|
| [CLAUDE.md](../CLAUDE.md) | Build commands, architecture overview |
| [README.md](../README.md) | Algorithm documentation, usage examples |

## Documentation Structure

```
docs/
|-- README.md                    # This file (navigation hub)
|-- documentation_standards.md   # Documentation conventions
|-- principles.md                # Development principles (DRY, KISS, YAGNI)
|-- project/
|   |-- requirements.md          # Functional requirements
|   |-- architecture.md          # System architecture
|   +-- tech_stack.md            # Technology decisions
+-- reference/
    |-- README.md                # Reference hub
    |-- adrs/                    # Architecture Decision Records
    |-- guides/                  # Project guides
    |-- manuals/                 # Package manuals
    +-- research/                # Research documents
```

## Project Documents

| Document | Purpose |
|----------|---------|
| [Requirements](project/requirements.md) | What the system does |
| [Architecture](project/architecture.md) | How the system is structured |
| [Tech Stack](project/tech_stack.md) | Technology choices and rationale |

## Development Standards

| Document | Purpose |
|----------|---------|
| [Documentation Standards](documentation_standards.md) | How to write docs |
| [Principles](principles.md) | DRY, KISS, YAGNI, SOLID |

## Reference Documentation

| Document | Purpose |
|----------|---------|
| [Reference Hub](reference/README.md) | ADRs, Guides, Manuals index |
| [ADR-001: Compression](reference/adrs/adr-001-compression-library.md) | Zstandard selection |
| [ADR-002: CLI](reference/adrs/adr-002-cli-library.md) | docopt selection |

## External Resources

- [HPLT Project](https://hplt-project.org) - Source of training data
- [Prompsit Language Engineering](http://www.prompsit.com) - Development team
- [GitHub Repository](https://github.com/pablop16n/web-docs-scorer/) - Source code
