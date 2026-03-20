import unittest
from unittest.mock import patch
import warnings

import aris_lite
from aris_lite.deprecation import ArisDeprecationWarning


class PythonDeprecationTests(unittest.TestCase):
    def _assert_warns(self, fn, patch_target):
        with patch(patch_target, return_value=0):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                rc = fn([])
        self.assertEqual(rc, 0)
        self.assertTrue(any(w.category is ArisDeprecationWarning for w in caught))

    def test_package_main_cli_warns(self):
        self._assert_warns(
            aris_lite.main_cli,
            "aris_lite.cli.legacy_wrappers.legacy_1go_cli",
        )

    def test_legacy_aris_1go_warns(self):
        with patch("aris_lite.run_1go", return_value="ok"):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                out = aris_lite.aris_1go(ds="dummy", crops=["maize"])
        self.assertEqual(out, "ok")
        self.assertTrue(any(w.category is ArisDeprecationWarning for w in caught))

if __name__ == "__main__":
    unittest.main()
