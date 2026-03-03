"""Legacy flat CLI wrappers with deprecation warnings."""

from __future__ import annotations

import sys

from aris_lite.cli.main import main_cli
from aris_lite.deprecation import warn_legacy_cli


def _argv_or_sys(argv: list[str] | None) -> list[str]:
    return list(sys.argv[1:] if argv is None else argv)


def legacy_1go_cli(argv: list[str] | None = None, *, emit_warning: bool = True) -> int:
    if emit_warning:
        warn_legacy_cli("aris-1go", "aris 1go")
    return main_cli(["1go", *_argv_or_sys(argv)])


def legacy_waterbudget_cli(
    argv: list[str] | None = None,
    *,
    emit_warning: bool = True,
) -> int:
    if emit_warning:
        warn_legacy_cli("aris-calc-waterbudget", "aris calc waterbudget")
    return main_cli(["calc", "waterbudget", *_argv_or_sys(argv)])


def legacy_pheno_cli(
    argv: list[str] | None = None,
    *,
    emit_warning: bool = True,
) -> int:
    if emit_warning:
        warn_legacy_cli("aris-calc-pheno", "aris calc pheno")
    return main_cli(["calc", "pheno", *_argv_or_sys(argv)])


def legacy_yield_cli(
    argv: list[str] | None = None,
    *,
    emit_warning: bool = True,
) -> int:
    if emit_warning:
        warn_legacy_cli("aris-calc-yield", "aris calc yield")
    return main_cli(["calc", "yield", *_argv_or_sys(argv)])
