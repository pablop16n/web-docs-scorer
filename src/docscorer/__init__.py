#!/usr/bin/env python

try:
	from importlib.metadata import version, PackageNotFoundError
except Exception:
	# fallback for very old Python versions or environments
	version = None
	PackageNotFoundError = Exception

from docscorer.docscorer import DocumentScorer
from docscorer.configuration import ScorerConfiguration

name = "docscorer"
if version is not None:
	try:
		__version__ = version(name)
	except PackageNotFoundError:
		__version__ = "0.0"
else:
	__version__ = "0.0"

__all__ = ["DocumentScorer", "ScorerConfiguration"]
