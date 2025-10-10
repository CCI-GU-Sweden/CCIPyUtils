#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from argparse import ArgumentParser, Namespace
from typing import Iterable, Tuple, Optional, Any, Literal


class CCIArgParser:
    """
    Build an argparse.ArgumentParser from specs and provide helpers
    to check whether an option was *supplied* on the CLI.

    Spec formats supported (tuple per argument):
      (name, type)                               -> required
      (name, type, required: bool)               -> required / optional
      (name, type, required: bool, default)      -> optional with default (tracked by this class)

    Special handling for bool:
      Creates a --flag / --no-flag pair.
      If 'required' is True, user must choose one.
      If 'required' is False, absence means "unspecified" (no attribute set),
      which you can detect via .has('flag'). Use .get('flag', default) to apply a default.
    """

    def __init__(self, specs: Iterable[Tuple], description: Optional[str] = None):
        self._specs = list(specs)
        self._parser: ArgumentParser = ArgumentParser(description=description)
        self._defaults_map: dict[str, Any] = {}   # only for *optional* args that carry a default
        self._args: Optional[Namespace] = None
        self._build()

    # ---------- public API ----------
    @property
    def parser(self) -> ArgumentParser:
        """Access the underlying ArgumentParser (for help output, etc.)."""
        return self._parser

    def parse(self, argv: Optional[list[str]] = None, on_empty: Literal["help", "error", "ok"] = "help", help_exit_code: int = 0 ) -> Namespace:
        """
        Parse args (default: sys.argv[1:]).
        on_empty:
            - "help": print help and exit with help_exit_code (default 0)
            - "error": show a usage error ("No arguments supplied") and exit(2)
            - "ok": parse an empty argv (only works if all needed args have defaults / are optional)
        """
        if argv is None:
            argv = sys.argv[1:]

        if not argv:
            if on_empty == "help":
                self._parser.print_help()
                self._parser.exit(help_exit_code)
            elif on_empty == "error":
                # argparse-style error (exit code 2)
                self._parser.error("No arguments supplied")
            # else "ok": fall through and parse empty list

        self._args = self._parser.parse_args(argv)
        return self._args


    def has(self, name: str) -> bool:
        """Was this option *supplied* by the user? (True even if value is False/0/'' for bool/ints)"""
        self._ensure_parsed()
        return hasattr(self._args, name)

    def get(self, name: str, default: Any = None) -> Any:
        """
        Get the value if supplied; otherwise:
          - if you provided a default in the spec, return that
          - else return the 'default' parameter here
        """
        self._ensure_parsed()
        if hasattr(self._args, name):
            return getattr(self._args, name)
        return self._defaults_map.get(name, default)

    def as_dict(self, apply_spec_defaults: bool = True) -> dict[str, Any]:
        """Return parsed args as a dict; optionally fill in spec defaults for missing optionals."""
        self._ensure_parsed()
        d = dict(vars(self._args))
        if apply_spec_defaults:
            for k, v in self._defaults_map.items():
                if k not in d:
                    d[k] = v
        return d

    # ---------- internal helpers ----------
    def _build(self) -> None:
        for spec in self._specs:
            if len(spec) < 2:
                raise ValueError(f"Spec needs at least (name, type), got {spec!r}")
            name, typ = spec[0], spec[1]
            if not isinstance(name, str):
                raise TypeError(f"Argument name must be str, got {type(name)!r}")

            required = True
            default: Any = None
            if len(spec) >= 3:
                if not isinstance(spec[2], bool):
                    raise TypeError(f"Third element must be bool (required) in spec {spec!r}")
                required = spec[2]
            if len(spec) >= 4:
                default = spec[3]

            flag = "--" + name.replace("_", "-")

            if typ is bool:
                # Bool: create --flag / --no-flag
                group = self._parser.add_mutually_exclusive_group(required=required)
                group.add_argument(flag,    dest=name, action="store_true",  default=argparse.SUPPRESS,
                                   help=f"Set {name} true")
                group.add_argument(f"--no-{name.replace('_','-')}", dest=name, action="store_false",
                                   default=argparse.SUPPRESS, help=f"Set {name} false")
                # Keep SUPPRESS so we can detect presence. If a default is given in the spec,
                # remember it in our map (do NOT set parser default, to preserve presence check).
                if default is not None and not required:
                    self._defaults_map[name] = bool(default)

            else:
                kwargs = {
                    "type": typ,
                    "help": f"{name} ({getattr(typ, '__name__', str(typ))})"
                }
                if required:
                    kwargs["required"] = True
                    # do NOT set a default for required args
                else:
                    kwargs["required"] = False
                    kwargs["default"] = argparse.SUPPRESS  # so absence => attribute missing
                    if len(spec) >= 4:
                        self._defaults_map[name] = default

                self._parser.add_argument(flag, **kwargs)

    def _ensure_parsed(self) -> None:
        if self._args is None:
            raise RuntimeError("Arguments not parsed yet. Call .parse(...) first.")
