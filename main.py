"""
Compass rose SVG generator main entrypoint.

Receives function parameters as flags in the terminal (see
CompassRoseSVGGenerator.run() for full details on each parameter).

Example for calling this function from the terminal:
    python main.py --rose-radius 200 (etc. for other params)
"""
import argparse

from src import (
    add_arguments_from_signature,
    CompassRoseSVGGenerator
)


def main():
    writer = CompassRoseSVGGenerator()

    parser = argparse.ArgumentParser(
        description="Generate SVGs from a template."
    )
    add_arguments_from_signature(parser, writer.run)
    args = parser.parse_args()

    writer.run(**vars(args))


if __name__ == "__main__":
    main()
