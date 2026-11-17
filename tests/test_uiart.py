"""uiart: spec handling, 9-slice maths, post-processing and the Roblox exports (no browser needed)."""
import importlib.machinery
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(name):
    loader = importlib.machinery.SourceFileLoader(name, str(ROOT / "tools" / name))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


uiart = load("uiart")
try:
    import numpy  # noqa: F401
    from PIL import Image
except ImportError:  # the tool runs under uv with these; plain python3 may not have them
    Image = None


def spec(*assets, **extra):
    return uiart.validate({"assets": list(assets), "vars": {"ink": "#2B1D4A", "w": 3}, **extra})


class Spec(unittest.TestCase):
    def test_vars_substitute_whole_values_and_inside_strings(self):
        self.assertEqual(uiart.substitute({"a": "$w", "b": "stroke $ink", "c": ["$ink"]}, {"ink": "#000", "w": 3}),
                         {"a": 3, "b": "stroke #000", "c": ["#000"]})

    def test_rejects_bad_names_types_and_missing_sizes(self):
        with self.assertRaises(ValueError):
            spec({"name": "bad name", "type": "panel", "size": [10, 10]})
        with self.assertRaises(ValueError):
            spec({"name": "a", "type": "photo"})
        with self.assertRaises(ValueError):
            spec({"name": "a", "type": "panel"})
        with self.assertRaises(ValueError):
            spec({"name": "a", "type": "icon"}, {"name": "a", "type": "icon"})

    def test_buttons_expand_to_three_states_with_role_suffixes(self):
        s = spec({"name": "go", "type": "button", "size": [112, 52], "role": "buttonPrimary"})
        jobs = uiart.expand(s, s["assets"][0])
        self.assertEqual([j["name"] for j in jobs], ["go", "go-pressed", "go-disabled"])
        self.assertEqual([j["role"] for j in jobs], ["buttonPrimary", "buttonPrimaryPressed", "buttonPrimaryDisabled"])
        rest, pressed = jobs[0]["meta"], jobs[1]["meta"]
        self.assertEqual(rest["slice"], pressed["slice"], "states share one SliceCenter so they swap cleanly")
        self.assertGreater(pressed["content"][1], rest["content"][1], "pressed face sits lower")
        self.assertLess(rest["slice"][0] + rest["slice"][2], 112)
        self.assertLess(rest["slice"][1] + rest["slice"][3], 52)

    def test_every_template_draws(self):
        for kind in ("panel", "button", "chip", "bar", "ribbon", "badge", "bunting", "pattern", "backdrop"):
            markup, _ = uiart.TEMPLATES[kind]({"layers": [{"kind": "gradient"}, {"kind": "rays"}, {"kind": "bunting"},
                                                          {"kind": "scatter"}, {"kind": "vignette"}]}, 120, 60, None)
            self.assertIn("<svg", markup, kind)
        markup, _ = uiart.t_title({"text": "A<B"})
        self.assertIn("A&lt;B", markup)

    def test_explicit_nine_overrides_the_computed_slice(self):
        s = spec({"name": "p", "type": "panel", "size": [100, 100], "nine": [10, 11, 12, 13]})
        self.assertEqual(uiart.expand(s, s["assets"][0])[0]["meta"]["slice"], [10, 11, 12, 13])


class NineSlice(unittest.TestCase):
    def test_slice_rect_is_image_pixels_after_density_and_margins(self):
        # edges 20,20,20,28 design px at 2x, with 6 px of outline added all round
        self.assertEqual(uiart.slice_rect([20, 20, 20, 28], 2, [6, 6, 6, 6], (396, 396)), [46, 46, 350, 334])

    def test_slice_rect_refuses_an_empty_centre(self):
        with self.assertRaises(ValueError):
            uiart.slice_rect([30, 10, 30, 10], 1, [0, 0, 0, 0], (50, 40))

    @unittest.skipIf(Image is None, "needs Pillow + numpy")
    def test_stretch_keeps_corners_pixel_exact(self):
        img = Image.new("RGBA", (30, 30), (0, 0, 255, 255))
        img.putpixel((0, 0), (255, 0, 0, 255))
        img.putpixel((29, 29), (0, 255, 0, 255))
        out = uiart.nine_stretch(img, [10, 10, 20, 20], (90, 50))
        self.assertEqual(out.size, (90, 50))
        self.assertEqual(out.getpixel((0, 0)), (255, 0, 0, 255))
        self.assertEqual(out.getpixel((89, 49)), (0, 255, 0, 255))


@unittest.skipIf(Image is None, "needs Pillow + numpy")
class Post(unittest.TestCase):
    def dot(self):
        img = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
        for x in range(15, 25):
            for y in range(15, 25):
                img.putpixel((x, y), (255, 80, 160, 255))
        return img

    def test_trim_and_pad_track_margins(self):
        m = [0.0, 0.0, 0.0, 0.0, 1.0]
        out = uiart.apply_post(self.dot(), [{"op": "trim"}, {"op": "pad", "px": 2}], 2, m)
        self.assertEqual(out.size, (18, 18))
        self.assertEqual(m[:4], [-11, -11, -11, -11])

    def test_outline_grows_the_silhouette_in_ink(self):
        m = [0.0, 0.0, 0.0, 0.0, 1.0]
        out = uiart.apply_post(self.dot(), [{"op": "outline", "px": 2, "color": "#2B1D4A"}], 1, m)
        self.assertGreater(out.size[0], 40)
        x = 15 + int(m[0]) - 1
        r, g, b, a = out.getpixel((x, 20 + int(m[1])))
        self.assertEqual((r, g, b), (0x2B, 0x1D, 0x4A))
        self.assertGreater(a, 200)

    def test_alpha_bleed_colours_transparent_pixels_without_changing_alpha(self):
        img = self.dot()
        out = uiart.alpha_bleed(img)
        self.assertEqual(out.getchannel("A").tobytes(), img.getchannel("A").tobytes())
        r, g, b, a = out.getpixel((13, 20))
        self.assertEqual(a, 0)
        self.assertEqual((r, g, b), (255, 80, 160))

    def test_fit_caps_roblox_size_and_scales_margins(self):
        m = [10.0, 10.0, 10.0, 10.0, 1.0]
        out = uiart.fit(Image.new("RGBA", (2048, 512)), 1024, 1024, m)
        self.assertEqual(out.size, (1024, 256))
        self.assertEqual(m, [5.0, 5.0, 5.0, 5.0, 0.5])

    def test_contact_sheet_renders_slices_and_tiles(self):
        with tempfile.TemporaryDirectory() as d:
            Image.new("RGBA", (64, 64), (255, 0, 0, 255)).save(Path(d) / "a.png")
            man = {"assets": [{"name": "a", "file": "a.png", "pixels": [64, 64], "slice": [16, 16, 48, 48]},
                              {"name": "b", "file": "a.png", "pixels": [64, 64], "tile": [32, 32]}]}
            out = uiart.contact_sheet(man, d, Path(d) / "sheet.png")
            self.assertTrue(Path(out).stat().st_size > 0)


class Export(unittest.TestCase):
    manifest = {"assets": [
        {"name": "panel", "size": [192, 192], "slice": [64, 64, 320, 306], "sliceScale": 0.5, "content": [19, 19, 19, 26],
         "role": "panel", "sha256": "aa"},
        {"name": "confetti", "size": [128, 128], "tile": [128, 128], "role": "pattern", "sha256": "bb"},
        {"name": "mascot-cheer", "size": [170, 170], "sha256": "cc"}]}
    ids = {"panel": {"id": 111, "sha256": "aa"}, "mascot-cheer": {"id": 333, "sha256": "cc"}}

    def test_luau_module_has_every_asset_with_typed_values(self):
        text = uiart.luau(self.manifest, self.ids)
        self.assertIn('["panel"] = { image = "rbxassetid://111", size = Vector2.new(192, 192), '
                      'slice = Rect.new(64, 64, 320, 306), sliceScale = 0.5, content = { 19, 19, 19, 26 } }', text)
        self.assertIn('["confetti"] = { image = "", size = Vector2.new(128, 128), tile = Vector2.new(128, 128) }', text)

    def test_theme_art_only_takes_uploaded_roles(self):
        art = uiart.theme_art(self.manifest, self.ids)
        self.assertEqual(list(art), ["panel"])
        uitheme = load("uitheme")
        self.assertIn("slice = Rect.new(64, 64, 320, 306)", uitheme.art_luau(art["panel"]))

    def test_upload_preview_sends_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "panel.png").write_bytes(b"\x89PNG fake")
            man = {"assets": [{"name": "panel", "file": "panel.png", "pixels": [1, 1], "sha256": "new"}]}
            cloud = uiart.load_rbxcloud()
            sent = []
            loader = uiart.load_rbxcloud
            cloud.request = lambda *a, **k: sent.append(a)
            try:
                uiart.load_rbxcloud = lambda: cloud
                uiart.upload(man, d, Path(d) / "ids.json", really=False)
            finally:
                uiart.load_rbxcloud = loader
            self.assertEqual(sent, [])
            self.assertFalse((Path(d) / "ids.json").exists())


if __name__ == "__main__":
    unittest.main()
