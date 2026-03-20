"""`aris calc waterbudget` command."""

from __future__ import annotations

from argparse import _SubParsersAction

from aris_lite.paths import DEFAULT_BASE_DIR


def add_calc_waterbudget_parser(subparsers: _SubParsersAction):
    parser = subparsers.add_parser(
        "waterbudget",
        help="Compute yearly snow/soil water budget.",
        description="Compute either snow or soil-water part of yearly water budget.",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        choices=["snow", "soil", "auto"],
        default="auto",
        help="choose which part of the water budget to compute",
    )
    parser.add_argument(
        "years",
        type=int,
        nargs="*",
        default=[2020, 2021, 2023],
        help="list years to compute",
    )
    parser.add_argument("--workers", type=int, default=4, help="number of dask workers")
    parser.add_argument(
        "--mem-per-worker",
        type=str,
        default="2Gb",
        help='memory per worker, e.g. "5.67Gb"',
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default=str(DEFAULT_BASE_DIR),
        help="base directory for yearly path conventions (default: ../data)",
    )
    parser.set_defaults(func=run_calc_waterbudget_cmd)
    return parser


def run_calc_waterbudget_cmd(args) -> int:
    from aris_lite.water_budget import run_calc_waterbudget

    run_calc_waterbudget(
        years=args.years,
        mode=args.mode,
        workers=args.workers,
        mem_per_worker=args.mem_per_worker,
        base_dir=args.base_dir,
    )
    return 0
