from pathlib import Path
import unittest

from aris_lite.paths import (
    input_taw,
    intermediate_snow,
    intermediate_stress,
    intermediate_year,
    output_year,
    reference_year,
)


class PathBuilderTests(unittest.TestCase):
    def test_default_convention_paths(self):
        self.assertEqual(reference_year(2026), Path("../data/reference/2026"))
        self.assertEqual(
            intermediate_year(2026),
            Path("../data/intermediate/2026.zarr"),
        )
        self.assertEqual(
            intermediate_snow(2026), Path("../data/intermediate/snow_2026.zarr")
        )
        self.assertEqual(
            intermediate_stress(2026), Path("../data/intermediate/CSI_2026.zarr")
        )
        self.assertEqual(output_year(2026), Path("../data/output/2026.zarr"))
        self.assertEqual(input_taw(), Path("../data/input/soil_taw.nc"))

    def test_custom_base_dir(self):
        base = "/tmp/aris_data"
        self.assertEqual(
            reference_year(2030, base), Path("/tmp/aris_data/reference/2030")
        )
        self.assertEqual(
            intermediate_year(2030, base),
            Path("/tmp/aris_data/intermediate/2030.zarr"),
        )


if __name__ == "__main__":
    unittest.main()
