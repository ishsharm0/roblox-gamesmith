import pathlib
import subprocess
import sys
import tempfile
import unittest

TOOL = pathlib.Path(__file__).resolve().parents[1] / "tools" / "rbxgame"

class CommandHelpTests(unittest.TestCase):
    def test_new_help_has_no_side_effects(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, str(TOOL), "new", "--help"], cwd=folder, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(pathlib.Path(folder).iterdir()), [], "help created a project")
            self.assertIn("rbxgame new", result.stdout)
