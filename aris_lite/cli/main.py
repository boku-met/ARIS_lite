"""Canonical `aris` CLI tree."""

from __future__ import annotations

from argparse import ArgumentParser

from aris_lite.cli.calc_pheno import add_calc_pheno_parser
from aris_lite.cli.calc_waterbudget import add_calc_waterbudget_parser
from aris_lite.cli.calc_yield import add_calc_yield_parser
from aris_lite.cli.cmd_1go import add_1go_parser


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="aris",
        description="ARIS-lite canonical CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_1go_parser(subparsers)

    calc_parser = subparsers.add_parser(
        "calc",
        help="Yearly staged calculations.",
        description="Run staged yearly calculations.",
    )
    calc_subparsers = calc_parser.add_subparsers(dest="calc_command", required=True)
    add_calc_waterbudget_parser(calc_subparsers)
    add_calc_pheno_parser(calc_subparsers)
    add_calc_yield_parser(calc_subparsers)

    return parser


def main_cli(argv: list[str] | None = None) -> int:
    """Entry point for the canonical `aris` CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)

