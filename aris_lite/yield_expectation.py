#!/usr/bin/env python

"""Stress and yield estimation for ARIS-lite.

This module is the final stage of the ARIS-lite chain:
phenology provides crop activity (`Kc_factor`, `plant_height`), water budget
provides evapotranspiration and soil depletion, and meteorology provides
temperature. From these inputs, stress indicators are derived and translated
into crop-wise yield depression.
"""

__all__ = [
    "main_heat_drought_compound_stress",
    "main_yield",
    "calc_heat_drought_compound_stress",
    "calc_yield",
]

import os
from typing import Iterable
import xarray as xr
import numpy as np


def set_heat_drought_compound_stress_meta(da: xr.DataArray) -> xr.DataArray:
    """
    Set metadata for the crop heat-drought compound stress output.

    Renames the input to ``heat_drought_compound_stress`` and attaches
    descriptive attributes used in exported datasets.

    :param da: DataArray to annotate.
    :type da: xr.DataArray
    :return: Annotated DataArray with metadata.
    :rtype: xr.DataArray
    """
    return da.rename("heat_drought_compound_stress").assign_attrs(
        dict(
            units="",
            long_name="daily crop specific stress index based on maximum "
            "surface air temperature and soil water saturation",
            description="Index of combination of plant growth inhibiting "
            "factors. Used for yield estimation.",
        )
    )


def calc_heat_drought_compound_stress(
    ds: xr.Dataset, threshold_temperature=None
) -> xr.DataArray:
    """
    Calculate crop-specific compound heat-drought stress.

    This stressor approximates daily crop damage pressure from concurrent heat
    and water limitations. Rules are crop-specific and based on the original
    ARIS logic:
    winter cereals and soybean combine water stress with heat exceedance,
    maize/barley/soybean apply a stronger thresholded response, potatoes use
    potato-specific heat thresholds, and grassland follows water stress only.

    The input ``waterstress`` is used when present; otherwise it is derived as
    ``soil_depletion / TAW`` for the top soil layer. Stress values before
    effective crop activity are masked using ``Kc_factor``.

    :param ds: Dataset containing ``max_air_temp`` and ``Kc_factor``, and either
        ``waterstress`` or ``soil_depletion`` with ``TAW``. ``plant_height`` is
        required for irrigated norm potato handling.
    :type ds: xr.Dataset
    :param threshold_temperature: Optional temperature threshold for potato crops
        other than ``norm potato`` and ``irrigated norm potato``.
    :type threshold_temperature: float, optional
    :return: Daily compound stress index for each crop.
    :rtype: xr.DataArray
    """
    if "waterstress" not in ds:
        ds["waterstress"] = (
            ds.soil_depletion.sel(layer="top") * 100 / ds.TAW.sel(layer="top")
        )
    heat_drought_compound_stress = ds.waterstress.where(False)
    for i in range(heat_drought_compound_stress.shape[0]):
        if heat_drought_compound_stress[i].crop == "irrigated norm potato":
            heat_drought_compound_stress[i] = (ds.max_air_temp - 25).where(
                (ds.max_air_temp > 26) & (ds.plant_height > 0)
            )
        if heat_drought_compound_stress[i].crop == "winter wheat":
            heat_drought_compound_stress[i] = xr.where(
                ds.max_air_temp > 26,
                ds.waterstress[i] * (ds.max_air_temp - 25),
                ds.waterstress[i],
            )
        if heat_drought_compound_stress[i].crop in [
            "spring barley",
            "maize",
            "soybean",
        ]:
            heat_drought_compound_stress[i] = xr.where(
                np.logical_and(ds.max_air_temp > 30, ds.waterstress[i] > 33),
                (ds.waterstress[i] * (ds.max_air_temp - 29)) - 33,
                ds.waterstress[i],
            )
        if "potato" in heat_drought_compound_stress[i].crop.item(0):
            if heat_drought_compound_stress[i].crop == "norm potato":
                heat_drought_compound_stress[i] = xr.where(
                    np.logical_and(ds.max_air_temp > 26, ds.waterstress[i] > 33),
                    (ds.waterstress[i] * (ds.max_air_temp - 25)) - 33,
                    ds.waterstress[i],
                )
            else:
                if threshold_temperature is None:
                    raise Exception(
                        'For potatoes, other than "(irrigated) norm potato", you must '
                        "pass the `threshold_temperature`."
                    )
                heat_drought_compound_stress[i] = xr.where(
                    np.logical_and(
                        ds.max_air_temp > threshold_temperature, ds.waterstress[i] > 33
                    ),
                    (
                        ds.waterstress[i]
                        * (ds.max_air_temp - (threshold_temperature - 1))
                    )
                    - 33,
                    ds.waterstress[i],
                )
        if heat_drought_compound_stress[i].crop == "grassland":
            heat_drought_compound_stress[i] = ds.waterstress[i]
        if heat_drought_compound_stress[i].crop in [
            "winter wheat",
            "spring barley",
            "soybean",
        ]:
            heat_drought_compound_stress[i] = heat_drought_compound_stress[i].where(
                ds.time.dt.month >= 3
            )
        if "potato" in heat_drought_compound_stress[i].crop.item(
            0
        ):  # actually 15.4. shouldn't matter
            heat_drought_compound_stress[i] = heat_drought_compound_stress[i].where(
                ds.time.dt.month >= 4
            )
        if heat_drought_compound_stress[i].crop in ["grassland", "maize"]:
            heat_drought_compound_stress[i] = heat_drought_compound_stress[i].where(
                ds.time.dt.month >= 5
            )
    heat_drought_compound_stress = heat_drought_compound_stress.where(
        (ds.Kc_factor > 0.5)[:, ::-1].cumsum("time") != 0
    )
    return heat_drought_compound_stress.rename("heat_drought_compound_stress")


def calc_drought_stress(
    evapotranspiration: xr.DataArray, pot_evapotransp: xr.DataArray
) -> xr.DataArray:
    """
    Compute a daily drought-stress flag from actual vs. potential ET.

    Drought stress is ``True`` where the ratio
    ``sum(evapotranspiration over layer) / pot_evapotransp`` falls below ``0.4``.
    This represents severe water limitation relative to atmospheric demand.

    :param evapotranspiration: Actual evapotranspiration, including ``layer``.
    :type evapotranspiration: xr.DataArray
    :param pot_evapotransp: Potential evapotranspiration.
    :type pot_evapotransp: xr.DataArray
    :return: Boolean drought-stress flag named ``drought_stress``.
    :rtype: xr.DataArray
    """
    return (evapotranspiration.sum("layer") / pot_evapotransp).rename(
        "drought_stress"
    ) < 0.4


def calc_heat_stress(max_air_temp: xr.DataArray) -> xr.DataArray:
    """
    Compute a daily extreme-heat stress flag.

    Heat stress is ``True`` where maximum daily air temperature is at least
    ``32`` degree C.

    :param max_air_temp: Daily maximum air temperature.
    :type max_air_temp: xr.DataArray
    :return: Boolean heat-stress flag named ``heat_stress``.
    :rtype: xr.DataArray
    """
    return max_air_temp.rename("heat_stress") >= 32


def calc_stresses(ds: xr.Dataset) -> xr.DataArray:
    """
    Build the full stress tensor used by yield estimation.

    Combines simple threshold stressors (heat, drought) with the crop-specific
    compound heat-drought stress and stacks them along the ``stressor``
    dimension. This is the direct input expected by ``calc_yield``.

    :param ds: Dataset with meteorological, phenology, and water-balance inputs.
    :type ds: xr.Dataset
    :return: DataArray named ``stresses`` with dimensions including ``stressor``.
    :rtype: xr.DataArray
    """
    return xr.Dataset(
        {
            da.name: da
            for da in [
                calc_heat_stress(ds.max_air_temp),
                calc_drought_stress(ds.evapotranspiration, ds.pot_evapotransp),
                calc_heat_drought_compound_stress(ds),
            ]
        }
    ).to_dataarray(dim="stressor", name="stresses")


def main_heat_drought_compound_stress(years: Iterable[int]):
    """
    Compute and persist yearly compound heat-drought stress datasets.

    For each year, this routine loads intermediate water-balance outputs and
    reference temperature, derives water stress, computes the crop-specific
    compound stress with ``map_blocks``, and writes the result to
    ``../data/intermediate/CSI_<year>.zarr``.

    :param years: List of years to compute combined stress for.
    :type years: Iterable[int]
    """
    # FIXME update with added stressors and rename CSI
    TAW = xr.open_dataarray("../data/input/soil_taw.nc", decode_coords="all")
    for year in years:
        if os.path.isdir(f"../data/intermediate/CSI_{year}.zarr"):
            print(f"! WARNING: CSI_{year}.zarr already exists. Skipping.")
            continue
        print("Calculating stress index for year", year)
        ds = xr.open_zarr(f"../data/intermediate/{year}.zarr", decode_coords="all")
        if not hasattr(TAW, "chunks"):
            TAW = TAW.chunk({k: ds.chunks[k] for k in TAW.dims})
        waterstress = (
            (ds.soil_depletion * 100 / TAW).mean("layer").rename("waterstress")
        )
        max_air_temp = xr.open_zarr(
            f"../data/reference/{year}", decode_coords="all"
        ).max_air_temp.astype("f4")
        data_collection = xr.merge(
            [waterstress, max_air_temp, ds.Kc_factor.astype("f4")]
        )
        csi = set_heat_drought_compound_stress_meta(
            data_collection.map_blocks(
                calc_heat_drought_compound_stress,
                template=data_collection.Kc_factor.astype("f4"),
            )
        )
        csi.drop_encoding().to_zarr(f"../data/intermediate/CSI_{year}.zarr", mode="a-")


def set_yield_meta(da: xr.DataArray) -> xr.DataArray:
    """
    Set metadata for yield depression output.

    Renames the array to ``yield_depression`` and adds standard attributes.

    :param da: DataArray to annotate.
    :type da: xr.DataArray
    :return: Annotated DataArray with metadata.
    :rtype: xr.DataArray
    """
    return da.rename("yield_depression").assign_attrs(
        dict(
            units="%",
            long_name="Yield depression",
            description="The yield depression given a certain combined stress which is "
            "crop specific and bases on water availability and heat above defined "
            "thresholds.",
        )
    )


def calc_yield(
    stress_data: xr.DataArray,
    yield_max: xr.DataArray,
    yield_intercept: xr.DataArray,
    params: xr.DataArray,
    temporal_mask: xr.DataArray = xr.DataArray(True),
    grass_cut_numbers: xr.DataArray = xr.DataArray(0),
) -> xr.DataArray:
    """
    Estimate yield depression from one or multiple stressors.

    The function applies a linear stress-response model where each stressor is
    weighted by a crop-specific parameter, added to an intercept, and scaled by
    maximum attainable yield. The result is expressed as percentage yield loss.

    If a ``time`` dimension exists, stress is first masked by
    ``temporal_mask``, cumulatively aggregated per year, and aligned back to the
    original time coordinate. Optional grass-cut information can be used to
    broadcast management-specific parameters and collapse ``grass1``,
    ``grass2``, and ``grassM`` into a single ``grassland`` class.

    :param stress_data: Stress input with a ``stressor`` dimension.
    :type stress_data: xr.DataArray
    :param yield_max: Maximum attainable yield (same spatial/crop support).
    :type yield_max: xr.DataArray
    :param yield_intercept: Baseline yield term used in the linear model.
    :type yield_intercept: xr.DataArray
    :param params: Stress-response coefficients, typically by ``stressor`` and
        crop (and optionally management class).
    :type params: xr.DataArray
    :param temporal_mask: Boolean mask selecting time steps that contribute to
        cumulative stress.
    :type temporal_mask: xr.DataArray
    :param grass_cut_numbers: Optional grass management descriptor used to align
        and merge grass-specific parameters.
    :type grass_cut_numbers: xr.DataArray
    :return: Yield depression in percent, clipped to ``[0, 100]``.
    :rtype: xr.DataArray
    """
    if "time" in stress_data.dims:
        stress_data = (
            stress_data.where(temporal_mask)
            .resample(time="YE")
            .cumsum("time")
            .reindex(time=stress_data.time)
            .pipe(
                lambda da: (
                    da
                    if stress_data.chunks is None
                    else da.chunk(
                        time=stress_data.chunks[stress_data.dims.index("time")]
                    )
                )
            )
        )
    if grass_cut_numbers is not None:

        def _merge_grasses(da):
            da.loc[{"crop": "grassM"}] = da.sel(crop="grassM").where(
                da.sel(crop="grassM"),
                da.sel(crop="grass2").where(
                    da.sel(crop="grass2"), da.sel(crop="grass1")
                ),
            )
            da = da.drop_sel(crop=["grass1", "grass2"])
            return da.assign_coords(
                crop=[(x if x != "grassM" else "grassland") for x in da.crop.values]
            )

        params = params.broadcast_like(grass_cut_numbers).copy().pipe(_merge_grasses)
    yield_reduction = stress_data * params  # negative
    yield_expectation = yield_intercept + yield_reduction.sum("stressor")
    yield_depression = (100 * (1 - yield_expectation / yield_max)).clip(0, 100)
    return set_yield_meta(
        yield_depression.transpose(*stress_data.isel(stressor=0).dims)
    )


def main_yield(years: Iterable[int]):
    """
    Compute and persist yearly yield outputs for selected years.

    For each year, this routine loads stress inputs, applies ``calc_yield``, and
    stores the result at ``../data/output/<year>.zarr``.

    :param years: List of years to compute yield expectations for.
    :type years: Iterable[int]
    """
    for year in years:
        if os.path.isdir(f"../data/output/{year}.zarr"):
            print(f"! WARNING: {year}.zarr already exists. Skipping.")
            continue
        print("Calculating yield expectation for year", year)
        csi = xr.open_zarr(
            f"../data/intermediate/CSI_{year}.zarr", decode_coords="all"
        ).heat_drought_compound_stress
        yield_expectation = (
            csi.map_blocks(calc_yield, template=csi.isel(time=0).drop_vars("time"))
            .rename("yield_expectation")
            .assign_attrs(
                dict(
                    unit="t/ha",
                    long_name="Expected yield in tonnes per hectare",
                    description="The expected yield given a certain combined stress "
                    "which is crop specific and bases on water availability and heat "
                    "above defined thresholds.",
                )
            )
        )
        yield_expectation.drop_encoding().to_zarr(
            f"../data/output/{year}.zarr", mode="a-"
        )


def main_cli():
    """
    Command-line interface for computing stress indices and/or yield expectations.

    Parses command-line arguments to determine which computations to perform and
    for which years. Initializes a Dask cluster for parallel processing, handles
    missing data, and manages workflow for stress and yield calculations.

    Usage:
        aris-calc-yield [-m MODE] [years ...] [--workers N]
        [--mem-per-worker SIZE]

    :return: None
    """
    import argparse

    parser = argparse.ArgumentParser(description="computes stress and/or yield")
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
    args = parser.parse_args()
    args.years = sorted(args.years)

    if args.mode == "auto":
        if all(
            os.path.isdir(f"../data/intermediate/CSI_{year}.zarr")
            for year in args.years
        ):
            print(
                "Stress index is present, assuming you want to have the yield "
                "expectations computed."
            )
            args.mode = "yield"
        else:
            print(
                "Stress index is missing for year(s):",
                ", ".join(
                    [
                        str(year)
                        for year in args.years
                        if not os.path.isdir(f"../data/intermediate/CSI_{year}.zarr")
                    ]
                )
                + ".",
                "Computing these first before estimating the yield.",
            )
            args.mode = "both"

    from dask.distributed import LocalCluster, Client

    print("Starting dask")
    client = Client(
        LocalCluster(
            n_workers=args.workers, memory_limit=args.mem_per_worker, death_timeout=30
        )
    )
    print("... access the dashboard at", client.dashboard_link)

    try:
        if args.mode in ["stress", "both"]:
            main_heat_drought_compound_stress(args.years)
        main_yield(args.years)
    except (FileNotFoundError,) as err:
        if str(err).startswith("Unable to find group"):
            print(
                "\n! ERROR: data missing. Verify that the necessary data are "
                "available.\n"
            )
            raise
    finally:
        client.close()
        print("Closed dask client\n")

    print(f"Sucessfully computed {args.mode} related variables!\n")


if __name__ == "__main__":
    main_cli()
