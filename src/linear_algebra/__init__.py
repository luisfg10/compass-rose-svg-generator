"""
Entrypoint for the Linear Algebra utility module of the project.

This module is intended to be minimalistic and contain only the
necessary abstractions to support the compass rose SVG generation,
but some of the operations can naturally be reused for other purposes.
"""
from src.linear_algebra.array import Array

__all__ = [
    "Array"
]