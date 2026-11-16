"""src package entrypoint."""
from src.svg.svg_generator import CompassRoseSVGGenerator
from src.linear_algebra.array import TwoDimArray
from src.utils.utils import add_arguments_from_signature

__all__ = [
    "add_arguments_from_signature",
    "CompassRoseSVGGenerator",
    "TwoDimArray"
]
