#!/usr/bin/env python

from importlib.metadata import version

from docscorer.docscorer import DocumentScorer
from docscorer.configuration import ScorerConfiguration

name = "docscorer"
__version__ = version(name)

__all__ = ["DocumentScorer", "ScorerConfiguration"]
