"""Path conventions and builders for yearly ARIS-lite workflows."""

from __future__ import annotations

from pathlib import Path

DEFAULT_BASE_DIR = Path("../data")


def _root(base_dir: str | Path = DEFAULT_BASE_DIR) -> Path:
    return Path(base_dir)


def reference_year(year: int, base_dir: str | Path = DEFAULT_BASE_DIR) -> Path:
    return _root(base_dir) / "reference" / str(year)


def intermediate_year(year: int, base_dir: str | Path = DEFAULT_BASE_DIR) -> Path:
    return _root(base_dir) / "intermediate" / f"{year}.zarr"


def intermediate_snow(year: int, base_dir: str | Path = DEFAULT_BASE_DIR) -> Path:
    return _root(base_dir) / "intermediate" / f"snow_{year}.zarr"


def intermediate_stress(year: int, base_dir: str | Path = DEFAULT_BASE_DIR) -> Path:
    return _root(base_dir) / "intermediate" / f"CSI_{year}.zarr"


def output_year(year: int, base_dir: str | Path = DEFAULT_BASE_DIR) -> Path:
    return _root(base_dir) / "output" / f"{year}.zarr"


def input_taw(base_dir: str | Path = DEFAULT_BASE_DIR) -> Path:
    return _root(base_dir) / "input" / "soil_taw.nc"

