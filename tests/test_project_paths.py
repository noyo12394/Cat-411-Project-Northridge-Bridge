from pathlib import Path
import tempfile
import unittest

from project_paths import get_project_root, build_paths


class ProjectPathsTests(unittest.TestCase):
    def test_get_project_root_finds_repo_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            (root / "README.md").write_text("test\n")
            nested = root / "a" / "b"
            nested.mkdir(parents=True)
            self.assertEqual(get_project_root(nested).resolve(), root.resolve())

    def test_build_paths_creates_expected_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            (root / "README.md").write_text("test\n")
            paths = build_paths(root)
            self.assertTrue(paths["PROCESSED_DIR"].exists())
            self.assertTrue(paths["CHANGE_DETECTION_DIR"].exists())
            self.assertTrue(paths["FIGURES_DIR"].exists())


if __name__ == "__main__":
    unittest.main()
