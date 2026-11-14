"""Pure-Python tests; no Blender on this machine."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile

SOURCE = Path(__file__).resolve().parents[1] / 'blender/bkit/assets.py'

class Assets(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('bkit_assets', SOURCE)
        self.assets = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.assets)

    def provider_download(self, url, path, md5=None):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(url.encode())

    def test_polyhaven_texture_channels_have_independent_cache_entries(self):
        a = self.assets
        tree = {channel: {'1k': {'jpg': {'url': 'https://example.org/' + channel}}}
                for channel in ('Diffuse', 'Rough')}
        with tempfile.TemporaryDirectory() as td, mock.patch.object(a, '_json', return_value=tree), \
                mock.patch.object(a, '_download', side_effect=self.provider_download) as download:
            diffuse = a.fetch('brick', kind='textures', cache=td)
            rough = a.fetch('brick', kind='textures', channel='Rough', cache=td)
            self.assertNotEqual(diffuse, rough)
            self.assertEqual(diffuse.read_bytes(), b'https://example.org/Diffuse')
            self.assertEqual(rough.read_bytes(), b'https://example.org/Rough')
            self.assertEqual(a.fetch('brick', kind='textures', cache=td), diffuse)
            self.assertEqual(download.call_count, 2)

    def test_polyhaven_model_downloads_and_verifies_dependencies(self):
        a = self.assets
        tree = {'blend': {'1k': {'blend': {
            'url': 'https://example.org/model.blend',
            'include': {'textures/diff.jpg': {'url': 'https://example.org/diff.jpg'}}}}}}
        with tempfile.TemporaryDirectory() as td, mock.patch.object(a, '_json', return_value=tree), \
                mock.patch.object(a, '_download', side_effect=self.provider_download) as download:
            model = a.fetch('crate', kind='models', cache=td)
            texture = model.parent / 'textures/diff.jpg'
            self.assertTrue(texture.exists())
            self.assertTrue(a._cached(texture))
            self.assertTrue(a._cached(model))
            with mock.patch.object(a, '_json', side_effect=AssertionError('cache must work offline')):
                self.assertEqual(a.fetch('crate', kind='models', cache=td), model)
            texture.write_bytes(b'corrupt')
            self.assertFalse(a._cached(model))
            a.fetch('crate', kind='models', cache=td)
            self.assertEqual(texture.read_bytes(), b'https://example.org/diff.jpg')
            self.assertTrue(a._cached(model))

    def test_polyhaven_rejects_dependency_traversal_before_download(self):
        a = self.assets
        tree = {'blend': {'1k': {'blend': {
            'url': 'https://example.org/model.blend',
            'include': {'../escape.jpg': {'url': 'https://example.org/diff.jpg'}}}}}}
        with tempfile.TemporaryDirectory() as td, mock.patch.object(a, '_json', return_value=tree), \
                mock.patch.object(a, '_download', side_effect=self.provider_download) as download:
            with self.assertRaises(ValueError):
                a.fetch('crate', kind='models', cache=td)
            download.assert_not_called()

    def test_fetch_rejects_variant_path_components(self):
        for kwargs in ({'resolution': '../escape'}, {'format': '../jpg'},
                       {'kind': 'textures', 'channel': '../Diffuse'}):
            with self.assertRaises(ValueError), mock.patch.object(self.assets, '_json') as get:
                self.assets.fetch('brick', **kwargs)
            get.assert_not_called()

    def test_polyhaven_rejects_dependency_symlink_before_download(self):
        a = self.assets
        tree = {'blend': {'1k': {'blend': {
            'url': 'https://example.org/model.blend',
            'include': {'textures/diff.jpg': {'url': 'https://example.org/diff.jpg'}}}}}}
        with tempfile.TemporaryDirectory() as td, mock.patch.object(a, '_json', return_value=tree), \
                mock.patch.object(a, '_download', side_effect=self.provider_download) as download:
            root = Path(td) / 'polyhaven/crate'
            root.mkdir(parents=True)
            outside = Path(td) / 'outside'
            outside.mkdir()
            (root / 'textures').symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                a.fetch('crate', kind='models', cache=td)
            download.assert_not_called()
            self.assertEqual(list(outside.iterdir()), [])

    def test_polyhaven_missing_texture_channel_is_explicit(self):
        with tempfile.TemporaryDirectory() as td, mock.patch.object(self.assets, '_json', return_value={}):
            with self.assertRaisesRegex(ValueError, 'variant textures/1k/jpg unavailable'):
                self.assets.fetch('brick', kind='textures', channel='Rough', cache=td)

    def test_extract_rejects_traversal_before_writing(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'pack.zip'
            with zipfile.ZipFile(p, 'w') as z:
                z.writestr('good.obj', 'v 0 0 0')
                z.writestr('../escape.obj', 'bad')
            with self.assertRaises(ValueError):
                self.assets.unpack(p, Path(td) / 'unpacked')
            self.assertFalse((Path(td) / 'escape.obj').exists())

    def test_cache_checks_hash_and_logs_licence(self):
        with tempfile.TemporaryDirectory() as td:
            a = self.assets
            path = Path(td) / 'fixture.hdr'
            path.write_bytes(b'cc0-fixture')
            a._record(path, 'polyhaven', 'fixture', 'https://polyhaven.com/a/fixture',
                      'https://dl.polyhaven.org/fixture.hdr')
            self.assertTrue(a._cached(path))
            self.assertEqual(json.loads(path.with_suffix('.hdr.license.json').read_text())['license'], 'CC0-1.0')
            path.write_bytes(b'corrupt')
            self.assertFalse(a._cached(path))

    def test_unknown_source_and_path_names_rejected(self):
        for name in ('../secret', 'x/y', ''):
            with self.assertRaises(ValueError):
                self.assets.fetch(name, source='polyhaven')
        with self.assertRaises(ValueError):
            self.assets.fetch('thing', source='unknown')

    def test_extract_regular_pack(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'pack.zip'
            with zipfile.ZipFile(p, 'w') as z:
                z.writestr('Models/a.obj', 'v 0 0 0')
            paths = self.assets.unpack(p, Path(td) / 'unpacked')
            self.assertEqual(len(paths), 1)
            self.assertEqual(paths[0].read_text(), 'v 0 0 0')

    def test_extract_rejects_existing_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            outside=root/'outside'
            outside.mkdir()
            dest=root/'dest'
            dest.mkdir()
            (dest/'Models').symlink_to(outside,target_is_directory=True)
            p=root/'pack.zip'
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('Models/escape.obj','bad')
            with self.assertRaises(ValueError):
                self.assets.unpack(p,dest)
            self.assertFalse((outside/'escape.obj').exists())
