#!/usr/bin/env python
from importlib.metadata import version

name="docscorer"
__version__ = version(name)

from .docscorer import DocumentScorer