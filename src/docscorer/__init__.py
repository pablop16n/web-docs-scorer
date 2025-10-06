#!/usr/bin/env python

from importlib.metadata import version

from docscorer.docscorer import DocumentScorer

name = "docscorer"
__version__ = version(name)

__all__ = ["DocumentScorer"]
