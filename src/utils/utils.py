import argparse
import inspect
import math
import typing
import types


def convert_deg_to_rad(angle: int | float) -> float:
    """Convert an angle in degrees to radians."""
    return angle * math.pi / 180


def _convert_int_or_float(value: str) -> int | float:
    try:
        return int(value)
    except ValueError:
        return float(value)


def add_arguments_from_signature(
    parser: argparse.ArgumentParser,
    func: typing.Callable[..., object],
) -> None:
    """
    Add one command-line option to `parser` for each parameter of `func`.

    The parser is built by reading `func`'s signature, so each parameter only
    has to be declared once, in the function itself:
    - A parameter named `output_dir` becomes the flag `--output-dir`.
    - The type hint (or, failing that, the type of the default value) decides
      how argparse converts the text typed on the command line.
    - Parameters without a default become required flags; parameters with a
      default become optional and keep that default.
    - `bool` parameters become a `--flag` / `--no-flag` pair.
    - `*args` and `**kwargs` are ignored.

    Parameters
    ----------
    parser
        The argparse parser to add the options to. It is modified
        in place.
    func
        The function (or bound method) whose signature is inspected.
        Pass a bound method like `writer.run` so `self` is not included.

    Returns
    -------
    None
        The options are added to `parser` as a side effect.
    """
    # Resolve the type annotations of `func` into real types,
    # e.g. {"length": int}.
    # get_type_hints also handles annotations written as strings.
    hints = typing.get_type_hints(func)

    # signature().parameters is an ordered mapping of name -> Parameter,
    # where each Parameter carries its default, kind and annotation.
    for name, param in inspect.signature(func).parameters.items():
        # *args and **kwargs can't be turned into fixed command-line flags.
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue

        # Parameter.empty is a sentinel meaning "no default was given".
        # (We can't just check for None, since None can be a real default.)
        has_default = param.default is not inspect.Parameter.empty

        # Prefer the explicit type hint. If there isn't one, guess from the
        # default value (e.g. a default of 200 implies int). A default of
        # None tells us nothing, so the type stays unknown in that case.
        param_type = hints.get(name)
        if param_type is None and has_default and param.default is not None:
            param_type = type(param.default)
        if typing.get_origin(param_type) in (typing.Union, types.UnionType):
            param_types = typing.get_args(param_type)
            if len(param_types) == 2 and int in param_types and float in param_types:
                param_type = _convert_int_or_float
            elif type(None) in param_types:
                non_none_types = tuple(
                    arg for arg in param_types if arg is not type(None)
                )
                if len(non_none_types) == 1:
                    param_type = non_none_types[0]

        # Options passed to parser.add_argument below. `dest` makes sure the
        # parsed value is stored under the original parameter name, so that
        # run(**vars(args)) matches the function's argument names.
        kwargs = {"dest": name}

        if param_type is bool:
            # Booleans can't use type=bool, because bool("False") is True.
            # BooleanOptionalAction creates both --name and --no-name.
            kwargs["action"] = argparse.BooleanOptionalAction
            kwargs["default"] = param.default if has_default else False
        else:
            if param_type is not None:
                # argparse calls this on the raw string, e.g. int("200").
                kwargs["type"] = param_type
            if has_default:
                kwargs["default"] = param.default
            else:
                # No default in the function means the user must provide it.
                kwargs["required"] = True
            # Show the default in --help output.
            kwargs["help"] = f"(default: {param.default})" if has_default else None

        # Python names use underscores, but CLI flags conventionally use dashes.
        parser.add_argument(f"--{name.replace('_', '-')}", **kwargs)