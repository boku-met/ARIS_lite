"""`aris 1go` command."""

from __future__ import annotations

from argparse import _SubParsersAction

from aris_lite import CROPS


def add_1go_parser(subparsers: _SubParsersAction):
    parser = subparsers.add_parser(
        "1go",
        help="Run in-memory ARIS 1go workflow.",
        description=(
            "Compute snow, phenology, soil water, and waterstress in one run. "
            "This command is intended for smaller datasets."
        ),
    )
    parser.add_argument("--workers", type=int, default=6, help="number of dask workers")
    parser.add_argument(
        "--mem-per-worker",
        type=str,
        default="3Gb",
        help='memory per worker, e.g. "5.67Gb"',
    )
    parser.add_argument("crops", nargs="+", type=str, choices=CROPS, help="Crop names")
    parser.add_argument("input", type=str, help="Path to input zarr dataset")
    parser.add_argument("output", type=str, help="Path to output zarr dataset")
    parser.set_defaults(func=run_cmd_1go)
    return parser


def run_cmd_1go(args) -> int:
    import xarray as xr

    from aris_lite import run_1go

    client = None
    if args.workers > 1:
        from dask.distributed import Client, LocalCluster

        client = Client(
            LocalCluster(n_workers=args.workers, memory_limit=args.mem_per_worker)
        )
        print(client.dashboard_link)
    try:
        out_ds = run_1go(
            xr.open_zarr(store=args.input).load().chunk(location=1), crops=args.crops
        )
        out_ds.chunk(location=-1).to_zarr(args.output, mode="w")
    finally:
        if client is not None:
            client.close()
    return 0
