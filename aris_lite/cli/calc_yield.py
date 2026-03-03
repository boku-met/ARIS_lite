"""`aris calc yield` command."""

from __future__ import annotations

from argparse import _SubParsersAction

from aris_lite.paths import DEFAULT_BASE_DIR


def add_calc_yield_parser(subparsers: _SubParsersAction):
    parser = subparsers.add_parser(
        "yield",
        help="Compute yearly stresses and/or yield depression.",
        description="Compute yearly heat-drought stress and/or yield depression.",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        choices=["stress", "yield", "both", "auto"],
        default="auto",
        help="choose whether to compute stress, yield, or both",
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
        default="1Gb",
        help='memory per worker, e.g. "5.67Gb"',
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default=str(DEFAULT_BASE_DIR),
        help="base directory for yearly path conventions (default: ../data)",
    )
    parser.add_argument(
        "--yield-max",
        type=str,
        default=None,
        help="path to yield_max DataArray (required if mode includes yield)",
    )
    parser.add_argument(
        "--yield-intercept",
        type=str,
        default=None,
        help="path to yield_intercept DataArray (required if mode includes yield)",
    )
    parser.add_argument(
        "--yield-params",
        type=str,
        default=None,
        help="path to params DataArray (required if mode includes yield)",
    )
    parser.add_argument(
        "--temporal-mask",
        type=str,
        default=None,
        help="optional path to temporal_mask DataArray",
    )
    parser.add_argument(
        "--grass-cut-numbers",
        type=str,
        default=None,
        help="optional path to grass_cut_numbers DataArray",
    )
    parser.set_defaults(func=run_calc_yield_cmd)
    return parser


def run_calc_yield_cmd(args) -> int:
    from aris_lite.yield_expectation import run_calc_yield

    run_calc_yield(
        years=args.years,
        mode=args.mode,
        workers=args.workers,
        mem_per_worker=args.mem_per_worker,
        base_dir=args.base_dir,
        yield_max_path=args.yield_max,
        yield_intercept_path=args.yield_intercept,
        yield_params_path=args.yield_params,
        temporal_mask_path=args.temporal_mask,
        grass_cut_numbers_path=args.grass_cut_numbers,
    )
    return 0
