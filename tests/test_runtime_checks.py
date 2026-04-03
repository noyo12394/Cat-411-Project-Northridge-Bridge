import unittest
from unittest.mock import patch

from runtime_checks import ensure_packages, ensure_supported_runtime


class RuntimeChecksTests(unittest.TestCase):
    def test_supported_runtime_passes(self):
        with patch("runtime_checks.sys.platform", "darwin"):
            ensure_supported_runtime()

    def test_browser_runtime_raises_clear_error(self):
        with patch("runtime_checks.sys.platform", "emscripten"):
            with self.assertRaises(RuntimeError) as ctx:
                ensure_supported_runtime()
        self.assertIn("Pyodide", str(ctx.exception))

    def test_missing_package_raises_clear_error(self):
        with patch("runtime_checks.find_spec", side_effect=lambda name: None if name == "fakepkg" else object()):
            with self.assertRaises(ModuleNotFoundError) as ctx:
                ensure_packages(["numpy", "fakepkg"])
        self.assertIn("fakepkg", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
