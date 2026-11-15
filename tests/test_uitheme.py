"""The committed Luau tokens must reproduce the preview source, including font weights."""
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
loader = importlib.machinery.SourceFileLoader("uitheme", str(ROOT / "tools/uitheme"))
spec = importlib.util.spec_from_loader(loader.name, loader)
uitheme = importlib.util.module_from_spec(spec)
loader.exec_module(uitheme)


class ThemeExport(unittest.TestCase):
    def setUp(self):
        self.themes = json.loads((ROOT / "templates/project/ui-themes.json").read_text())

    def test_committed_tokens_are_reproducible(self):
        path = ROOT / "templates/project/src/shared/Themes.luau"
        self.assertTrue(path.exists(), "generate the public template tokens")
        self.assertEqual(uitheme.luau(self.themes), path.read_text())

    def test_display_and_button_weights_match_preview(self):
        royal = next(t for t in self.themes if t["name"] == "Royal")
        text = uitheme.luau([royal])
        self.assertIn('GrenzeGotisch.json", Enum.FontWeight.ExtraBold)', text)
        self.assertIn('Nunito.json", Enum.FontWeight.Bold)', text)
        toybox = uitheme.luau([self.themes[0]])
        self.assertIn('button = Font.new("rbxasset://fonts/families/FredokaOne.json", Enum.FontWeight.Regular)', toybox)

    def test_starter_fonts_resolve_to_supported_content(self):
        text = uitheme.luau(self.themes)
        self.assertNotIn("families/Bungee.json", text)
        self.assertNotIn("families/TitanOne.json", text)
        self.assertIn('Font.new("rbxassetid://12187370000"', text)

    def test_royal_exports_native_display_metric_correction(self):
        royal = next(t for t in self.themes if t["name"] == "Royal")
        text = uitheme.luau([royal])
        self.assertIn("displayScale = 1.5", text)
        self.assertIn("buttonScale = 1", text)
