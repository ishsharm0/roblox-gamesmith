import unittest
from test_tools import load
from pathlib import Path
import tempfile

class CloudTests(unittest.TestCase):
    def test_model_manifest_is_zero_price_and_has_creator(self):
        cloud=load('rbxcloud')
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'lily.glb';p.write_bytes(b'glTF')
            manifest,mime=cloud.manifest(p,'Lily pad','A stylised pad','178819165',False)
            self.assertEqual(manifest['assetType'],'Model')
            self.assertEqual(manifest['creationContext'],{'creator':{'userId':'178819165'},'expectedPrice':0})
            self.assertEqual(mime,'model/gltf-binary')

    def test_rejects_oversize_and_unsupported_content(self):
        cloud=load('rbxcloud')
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'bad.exe';p.write_bytes(b'bad')
            with self.assertRaises(ValueError): cloud.manifest(p,'Bad','', '1',False)
            p=Path(directory)/'large.glb'
            with p.open('wb') as f:f.truncate(20*1024*1024+1)
            with self.assertRaises(ValueError): cloud.manifest(p,'Bad','', '1',False)

if __name__=='__main__':unittest.main()
