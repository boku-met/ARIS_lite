"""`aris calc pheno` command."""

from __future__ import annotations

from argparse import _SubParsersAction

from aris_lite import CROPS
from aris_lite.paths import DEFAULT_BASE_DIR


def add_calc_pheno_parser(subparsers: _SubParsersAction):
    parser = subparsers.add_parser(
        "pheno",
        help="Compute yearly phenology variables.",
        description="Compute yearly crop phenology variables.",
    )
    parser.add_argument(
        "years",
        type=int,
        nargs="*",
        default=[2020, 2021, 2023],
        help="list years to compute",
    )
    parser.add_argument(
        "--crops",
        nargs="+",
        type=str,
        choices=CROPS,
        default=["winter wheat", "spring barley", "maize", "grassland"],
        help="crop names to compute",
    )
    parser.add_argument("--workers", type=int, default=4, help="number of dask workers")
    parser.add_argument(
        "--mem-per-worker",
        type=str,
        default="3Gb",
        help='memory per worker, e.g. "5.67Gb"',
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default=str(DEFAULT_BASE_DIR),
        help="base directory for yearly path conventions (default: ../data)",
    )
    parser.set_defaults(func=run_calc_pheno_cmd)
    return parser


def run_calc_pheno_cmd(args) -> int:
    from aris_lite.phenology import run_calc_pheno

    run_calc_pheno(
        years=args.years,
        crops=args.crops,
        workers=args.workers,
        mem_per_worker=args.mem_per_worker,
        base_dir=args.base_dir,
    )
    return 0
