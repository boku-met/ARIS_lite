#!/usr/bin/env python

"""Stress and yield estimation for ARIS-lite.

This module is the final stage of the ARIS-lite chain:
phenology provides crop activity (`Kc_factor`, `plant_height`), water budget
provides evapotranspiration and soil depletion, and meteorology provides
temperature. From these inputs, stress indicators are derived and translated
into crop-wise yield depression.
"""

__all__ = [
    "run_calc_stresses",
    "run_calc_yield",
    "main_heat_drought_compound_stress",
    "main_yield",
    "main_cli",
    "calc_stresses",
    "calc_heat_drought_compound_stress",
    "calc_yield",
]

from pathlib import Path
from typing import Iterable
import xarray as xr
import numpy as np

from aris_lite.deprecation import warn_legacy_python_api
from aris_lite.paths import (
    DEFAULT_BASE_DIR,
    input_taw,
    intermediate_stress,
    intermediate_year,
    output_year,
    reference_year,
)


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


def run_calc_stresses(
    years: Iterable[int],
    base_dir: str = str(DEFAULT_BASE_DIR),
):
    """
    Compute and persist yearly heat-drought compound stress datasets.

    The output store path follows ``intermediate/CSI_<year>.zarr`` under
    ``base_dir``.
    """
    taw = xr.open_dataarray(str(input_taw(base_dir=base_dir)), decode_coords="all")
    for year in years:
        stress_store = intermediate_stress(year, base_dir=base_dir)
        yearly_intermediate = intermediate_year(year, base_dir=base_dir)
        yearly_reference = reference_year(year, base_dir=base_dir)

        if stress_store.exists():
            print(f"! WARNING: {stress_store} already exists. Skipping.")
            continue
        print("Calculating stress index for year", year)
        ds = xr.open_zarr(str(yearly_intermediate), decode_coords="all")
        if not hasattr(taw, "chunks"):
            taw = taw.chunk({k: ds.chunks[k] for k in taw.dims})
        waterstress = (
            (ds.soil_depletion * 100 / taw).sel(layer="top").rename("waterstress")
        )
        max_air_temp = xr.open_zarr(
            str(yearly_reference), decode_coords="all"
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
        csi.drop_encoding().to_zarr(str(stress_store), mode="a-")


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


def _open_dataarray(path: str) -> xr.DataArray:
    path_obj = Path(path)
    if path_obj.is_dir() or path_obj.suffix == ".zarr":
        opened = xr.open_zarr(str(path_obj), decode_coords="all")
    else:
        try:
            return xr.open_dataarray(str(path_obj), decode_coords="all")
        except ValueError:
            opened = xr.open_dataset(str(path_obj), decode_coords="all")
    if isinstance(opened, xr.DataArray):
        return opened
    if len(opened.data_vars) == 1:
        return opened[next(iter(opened.data_vars))]
    raise ValueError(
        f"Could not infer a single DataArray from '{path_obj}'. "
        "Provide a path containing exactly one data variable."
    )


def _validate_yield_paths(
    *,
    mode: str,
    yield_max_path: str | None,
    yield_intercept_path: str | None,
    yield_params_path: str | None,
):
    if mode not in {"yield", "both"}:
        return
    missing = [
        flag
        for flag, value in [
            ("--yield-max", yield_max_path),
            ("--yield-intercept", yield_intercept_path),
            ("--yield-params", yield_params_path),
        ]
        if not value
    ]
    if missing:
        raise ValueError(
            "Yield mode requires explicit parameter paths. Missing flags: "
            + ", ".join(missing)
        )


def run_yield_depression(
    years: Iterable[int],
    *,
    yield_max_path: str,
    yield_intercept_path: str,
    yield_params_path: str,
    temporal_mask_path: str | None = None,
    grass_cut_numbers_path: str | None = None,
    base_dir: str = str(DEFAULT_BASE_DIR),
):
    """Compute and persist yearly yield_depression from stored stress inputs."""
    yield_max = _open_dataarray(yield_max_path)
    yield_intercept = _open_dataarray(yield_intercept_path)
    params = _open_dataarray(yield_params_path)
    temporal_mask = (
        _open_dataarray(temporal_mask_path)
        if temporal_mask_path is not None
        else xr.DataArray(True)
    )
    grass_cut_numbers = (
        _open_dataarray(grass_cut_numbers_path)
        if grass_cut_numbers_path is not None
        else None
    )

    for year in years:
        yearly_output = output_year(year, base_dir=base_dir)
        yearly_stress = intermediate_stress(year, base_dir=base_dir)

        if yearly_output.exists():
            print(f"! WARNING: {yearly_output} already exists. Skipping.")
            continue
        print("Calculating yield depression for year", year)
        csi = xr.open_zarr(
            str(yearly_stress), decode_coords="all"
        ).heat_drought_compound_stress
        stress_data = (
            csi
            if "stressor" in csi.dims
            else csi.expand_dims(stressor=["heat_drought_compound_stress"])
        )
        yield_depression = calc_yield(
            stress_data=stress_data,
            yield_max=yield_max,
            yield_intercept=yield_intercept,
            params=params,
            temporal_mask=temporal_mask,
            grass_cut_numbers=grass_cut_numbers,
        )
        yield_depression.to_dataset(name=yield_depression.name).drop_encoding().to_zarr(
            str(yearly_output),
            mode="a-",
        )


def run_calc_yield(
    years: Iterable[int],
    mode: str = "auto",
    workers: int = 4,
    mem_per_worker: str = "1Gb",
    base_dir: str = str(DEFAULT_BASE_DIR),
    yield_max_path: str | None = None,
    yield_intercept_path: str | None = None,
    yield_params_path: str | None = None,
    temporal_mask_path: str | None = None,
    grass_cut_numbers_path: str | None = None,
):
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
    years = sorted(years)
    mode = mode.lower()

    if mode == "auto":
        if all(
            intermediate_stress(year, base_dir=base_dir).exists()
            for year in years
        ):
            print(
                "Stress index is present, assuming you want to have the yield "
                "depression computed."
            )
            mode = "yield"
        else:
            print(
                "Stress index is missing for year(s):",
                ", ".join(
                    [
                        str(year)
                        for year in years
                        if not intermediate_stress(year, base_dir=base_dir).exists()
                    ]
                )
                + ". Computing these first before estimating yield depression.",
            )
            mode = "both"

    _validate_yield_paths(
        mode=mode,
        yield_max_path=yield_max_path,
        yield_intercept_path=yield_intercept_path,
        yield_params_path=yield_params_path,
    )

    from dask.distributed import LocalCluster, Client

    print(f"Starting dask ({workers} CPUs, each {mem_per_worker} RAM)")
    client = Client(
        LocalCluster(
            n_workers=workers, memory_limit=mem_per_worker, death_timeout=30
        )
    )
    print("... access the dashboard at", client.dashboard_link)

    try:
        if mode in {"stress", "both"}:
            run_calc_stresses(years=years, base_dir=base_dir)
        if mode in {"yield", "both"}:
            run_yield_depression(
                years=years,
                yield_max_path=str(yield_max_path),
                yield_intercept_path=str(yield_intercept_path),
                yield_params_path=str(yield_params_path),
                temporal_mask_path=temporal_mask_path,
                grass_cut_numbers_path=grass_cut_numbers_path,
                base_dir=base_dir,
            )
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

    print(f"Successfully computed {mode} related variables!\n")


def main_heat_drought_compound_stress(
    years: Iterable[int],
    base_dir: str = str(DEFAULT_BASE_DIR),
):
    """Legacy alias for :func:`run_calc_stresses`."""
    warn_legacy_python_api(
        "aris_lite.yield_expectation.main_heat_drought_compound_stress",
        "aris_lite.yield_expectation.run_calc_stresses",
    )
    run_calc_stresses(years=years, base_dir=base_dir)


def main_yield(
    years: Iterable[int],
    *,
    yield_max_path: str | None = None,
    yield_intercept_path: str | None = None,
    yield_params_path: str | None = None,
    temporal_mask_path: str | None = None,
    grass_cut_numbers_path: str | None = None,
    base_dir: str = str(DEFAULT_BASE_DIR),
):
    """Legacy alias for :func:`run_yield_depression`."""
    warn_legacy_python_api(
        "aris_lite.yield_expectation.main_yield",
        "aris_lite.yield_expectation.run_calc_yield",
    )
    _validate_yield_paths(
        mode="yield",
        yield_max_path=yield_max_path,
        yield_intercept_path=yield_intercept_path,
        yield_params_path=yield_params_path,
    )
    run_yield_depression(
        years=years,
        yield_max_path=str(yield_max_path),
        yield_intercept_path=str(yield_intercept_path),
        yield_params_path=str(yield_params_path),
        temporal_mask_path=temporal_mask_path,
        grass_cut_numbers_path=grass_cut_numbers_path,
        base_dir=base_dir,
    )


def main_cli(argv: list[str] | None = None) -> int:
    """Legacy CLI alias for `aris-calc-yield`; use `aris calc yield`."""
    warn_legacy_python_api(
        "aris_lite.yield_expectation.main_cli",
        "aris_lite.cli.main:main_cli",
    )
    from aris_lite.cli.legacy_wrappers import legacy_yield_cli

    return legacy_yield_cli(argv=argv, emit_warning=False)


if __name__ == "__main__":
    raise SystemExit(main_cli())
