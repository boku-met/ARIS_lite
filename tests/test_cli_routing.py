import unittest
from unittest.mock import patch

from aris_lite.cli.main import main_cli


class CliRoutingTests(unittest.TestCase):
    def test_routes_1go(self):
        with patch("aris_lite.cli.cmd_1go.run_cmd_1go", return_value=0) as mocked:
            rc = main_cli(["1go", "winter wheat", "input.zarr", "output.zarr"])
        self.assertEqual(rc, 0)
        mocked.assert_called_once()

    def test_routes_calc_waterbudget(self):
        with patch(
            "aris_lite.cli.calc_waterbudget.run_calc_waterbudget_cmd", return_value=0
        ) as mocked:
            rc = main_cli(["calc", "waterbudget"])
        self.assertEqual(rc, 0)
        mocked.assert_called_once()

    def test_routes_calc_pheno(self):
        with patch(
            "aris_lite.cli.calc_pheno.run_calc_pheno_cmd", return_value=0
        ) as mocked:
            rc = main_cli(["calc", "pheno"])
        self.assertEqual(rc, 0)
        mocked.assert_called_once()

    def test_routes_calc_yield(self):
        with patch(
            "aris_lite.cli.calc_yield.run_calc_yield_cmd", return_value=0
        ) as mocked:
            rc = main_cli(["calc", "yield"])
        self.assertEqual(rc, 0)
        mocked.assert_called_once()


if __name__ == "__main__":
    unittest.main()
