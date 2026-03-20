import io
from contextlib import redirect_stderr
import unittest
from unittest.mock import patch
import warnings

from aris_lite.cli.legacy_wrappers import (
    legacy_1go_cli,
    legacy_pheno_cli,
    legacy_waterbudget_cli,
    legacy_yield_cli,
)
from aris_lite.deprecation import ArisDeprecationWarning


class LegacyWrapperTests(unittest.TestCase):
    def _assert_wrapper_warns(self, fn, old_name):
        with patch("aris_lite.cli.legacy_wrappers.main_cli", return_value=0):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                stderr = io.StringIO()
                with redirect_stderr(stderr):
                    rc = fn(argv=["--dummy"], emit_warning=True)
        self.assertEqual(rc, 0)
        self.assertIn("WARNING:", stderr.getvalue())
        self.assertIn(old_name, stderr.getvalue())
        self.assertTrue(any(w.category is ArisDeprecationWarning for w in caught))

    def test_legacy_1go_wrapper_warns(self):
        self._assert_wrapper_warns(legacy_1go_cli, "aris-1go")

    def test_legacy_waterbudget_wrapper_warns(self):
        self._assert_wrapper_warns(legacy_waterbudget_cli, "aris-calc-waterbudget")

    def test_legacy_pheno_wrapper_warns(self):
        self._assert_wrapper_warns(legacy_pheno_cli, "aris-calc-pheno")

    def test_legacy_yield_wrapper_warns(self):
        self._assert_wrapper_warns(legacy_yield_cli, "aris-calc-yield")


if __name__ == "__main__":
    unittest.main()

