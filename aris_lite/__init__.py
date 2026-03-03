"""Implementation of the ARIS-lite model package."""

__version__ = "0.3.0"

from collections.abc import Iterable
from typing import TYPE_CHECKING, Literal

from aris_lite.deprecation import warn_legacy_python_api

if TYPE_CHECKING:
    import xarray as xr

CROPS = [
    "winter wheat",
    "spring barley",
    "maize",
    "soybean",
    "norm potato",
    "grassland",
]

type T_crop_names = Literal[
    "winter wheat",
    "spring barley",
    "maize",
    "soybean",
    "norm potato",
    "grassland",
]


def run_1go(
    ds: "xr.Dataset",
    crops: Iterable[T_crop_names],
) -> "xr.Dataset":
    """
    Run the in-memory 1go ARIS-lite workflow on a single dataset.

    This routine computes snow, phenology, soil-water outputs, and top-layer
    waterstress. It intentionally does not compute yield outputs.
    """
    import xarray as xr

    from aris_lite.phenology import compute_phenology_variables
    from aris_lite.water_budget import calc_snow, calc_soil_water

    def _load_resample_apply(input_ds, func, *args, **kwargs):
        return (
            input_ds.load()
            .resample(time="YE")
            .map(func, args=args, **kwargs)
            .assign_coords(time=("time", input_ds.time.data))
        )

    out = xr.merge(
        [
            ds,
            calc_snow(
                ds.assign(
                    initial_snowcover=xr.zeros_like(ds.precipitation.isel(time=0))
                )
            ).persist(),
        ]
    )
    out = xr.merge(
        [
            out,
            (
                xr.coding.calendar_ops.convert_calendar(  # pyright: ignore[reportAttributeAccessIssue]
                    out.air_temperature.where(~(out.snowcover > 0)), "gregorian"
                ).pipe(
                    _load_resample_apply,
                    compute_phenology_variables,
                    crops,
                )
            ).persist(),
        ]
    )
    out = xr.merge(
        [
            out,
            out.map_blocks(
                _load_resample_apply,
                args=(calc_soil_water,),
                template=xr.Dataset(
                    {
                        var: xr.zeros_like(out.Kc_factor.broadcast_like(out.TAW))
                        .transpose(*out.Kc_factor.dims, ...)
                        .chunk(out.chunks)
                        for var in ["evapotranspiration", "evapo_ETC", "soil_depletion"]
                    }
                ),
            )
            .chunk(out.chunks)
            .persist(),
        ]
    )
    out = out.assign(
        waterstress=(out.soil_depletion * 100 / out.TAW)
        .sel(layer="top")
        .persist()
    )
    return out.map(lambda da: da.astype("float32") if da.dtype.kind == "f" else da)


def aris_1go(
    ds: "xr.Dataset",
    crops: Iterable[T_crop_names],
) -> "xr.Dataset":
    """Legacy alias for :func:`run_1go`."""
    warn_legacy_python_api("aris_lite.aris_1go", "aris_lite.run_1go")
    return run_1go(ds=ds, crops=crops)


def main_cli(argv: list[str] | None = None) -> int:
    """Legacy CLI alias for `aris-1go`; use `aris 1go`."""
    warn_legacy_python_api("aris_lite.main_cli", "aris_lite.cli.main:main_cli")
    from aris_lite.cli.legacy_wrappers import legacy_1go_cli

    return legacy_1go_cli(argv=argv, emit_warning=False)


def cli(argv: list[str] | None = None) -> int:
    """Legacy CLI alias for `aris-1go`; use `aris 1go`."""
    warn_legacy_python_api("aris_lite.cli", "aris_lite.cli.main:main_cli")
    from aris_lite.cli.legacy_wrappers import legacy_1go_cli

    return legacy_1go_cli(argv=argv, emit_warning=False)


def extract_point_data(ds, locations):
    """
    Extract data for specific point locations from a dataset.

    For each location provided, selects the nearest grid point in the dataset and
    concatenates the results along a new 'location' dimension.
    """
    import xarray as xr

    return (
        xr.concat(
            [
                ds.sel({**loc}, method="nearest").assign_coords(location=name)
                for name, loc in locations.iterrows()
            ],
            "location",
        )
        .chunk(location=-1)
        .transpose("time", ...)
    )


__all__ = [
    "CROPS",
    "T_crop_names",
    "run_1go",
    "aris_1go",
    "main_cli",
    "cli",
    "extract_point_data",
]
