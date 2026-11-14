"""CC0 downloads, verified cache and pack import. No third-party Python dependencies.

Poly Haven API users should credit 'Powered by Poly Haven' when surfacing its live catalogue.
Downloads themselves are CC0. A sidecar records source URL, licence and SHA256 for each file.
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import time
import urllib.parse
import urllib.request
import zipfile

USER_AGENT = 'bkit/0.1 (CC0 stylised Blender asset kit)'
SOURCES = {'polyhaven': 'https://polyhaven.com/license',
           'ambientcg': 'https://docs.ambientcg.com/license/',
           'kenney': 'https://kenney.nl/support',
           'quaternius': 'https://quaternius.com/faq.html',
           'kaykit': 'https://kaylousberg.itch.io/'}

def _json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': USER_AGENT}), timeout=45) as r:
        return json.load(r)

def _hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def _record(path, source, name, page, url, dependencies=()):
    path = Path(path)
    record = dict(source=source, name=name, license='CC0-1.0', license_url=SOURCES[source],
                  page=page, download=url, sha256=_hash(path), bytes=path.stat().st_size,
                  retrieved_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                  dependencies={p.relative_to(path.parent).as_posix(): _hash(p) for p in dependencies})
    path.with_suffix(path.suffix + '.license.json').write_text(json.dumps(record, indent=2), encoding='utf8')

def _dependency_path(root, relative):
    """Provider include paths are relative to the model, never outside its cache directory."""
    root = Path(root).resolve()
    p = PurePosixPath(relative.replace('\\', '/'))
    if not p.parts or p.is_absolute() or '..' in p.parts or ':' in str(p):
        raise ValueError('unsafe dependency path: ' + relative)
    target = root.joinpath(*p.parts)
    if not target.resolve().is_relative_to(root) or any(
            root.joinpath(*p.parts[:i]).is_symlink() for i in range(1, len(p.parts)+1)):
        raise ValueError('dependency path contains a symlink: ' + relative)
    return target

def _cached(path, require_dependencies=False):
    path = Path(path)
    try:
        r = json.loads(path.with_suffix(path.suffix + '.license.json').read_text())
        if not path.is_file() or r['sha256'] != _hash(path) or r['license'] != 'CC0-1.0':
            return False
        if require_dependencies and 'dependencies' not in r:
            return False  # Refresh model caches made before dependency downloads were supported.
        for relative, digest in r.get('dependencies', {}).items():
            dep = _dependency_path(path.parent, relative)
            meta = json.loads(dep.with_suffix(dep.suffix + '.license.json').read_text())
            if _hash(dep) != digest or meta['sha256'] != digest or meta['license'] != 'CC0-1.0':
                return False
        return True
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return False

def _download(url, path, md5=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.part')
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': USER_AGENT}), timeout=90) as r, open(tmp, 'wb') as f:
            shutil.copyfileobj(r, f)
        if md5 and hashlib.md5(tmp.read_bytes()).hexdigest() != md5:
            raise ValueError('provider checksum mismatch')
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)

def fetch(name, source='polyhaven', kind='hdri', resolution='1k', format=None, cache=None, channel=None):
    """Fetch exact asset ID; return a hash-verified cached Path. Poly Haven kind='textures'
    selects channel='Diffuse' by default; pass exact API channels such as 'Rough' or 'nor_gl'.
    kind='models' defaults to BLEND and downloads its include files at the required relative
    paths, with licence sidecars. ambientCG selects a resolution-format ZIP (e.g. 1K-JPG).
    Ambiguous/missing variants raise ValueError; no arbitrary URL downloads or licence guessing."""
    if source not in ('polyhaven', 'ambientcg'):
        raise ValueError('fetch supports polyhaven or ambientcg')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', name):
        raise ValueError('name must be an exact asset ID, without paths')
    for value in (resolution, format, channel):
        if value is not None and not re.fullmatch(r'[A-Za-z0-9_-]+', value):
            raise ValueError('resolution, format and channel must not contain paths')
    root = (Path(cache or os.environ.get('BKIT_CACHE', Path.home() / '.cache/bkit')) / source / name).resolve()
    if source == 'polyhaven':
        if kind not in ('hdri', 'textures', 'models'):
            raise ValueError('Poly Haven kind must be hdri, textures or models')
        fmt = (format or ('hdr' if kind == 'hdri' else 'blend' if kind == 'models' else 'jpg')).lower()
        resolution = resolution.lower()
        channel = channel or 'Diffuse'
        filename = f'{name}_{channel}_{resolution}.{fmt}' if kind == 'textures' else f'{name}_{resolution}.{fmt}'
        path = root / filename
        if _cached(path, require_dependencies=kind == 'models'):
            return path
        tree = _json('https://api.polyhaven.com/files/' + name)
        key = 'hdri' if kind == 'hdri' else fmt if kind == 'models' else channel
        try:
            record = tree[key][resolution][fmt]
        except KeyError:
            raise ValueError(f'variant {kind}/{resolution}/{fmt} unavailable; top-level keys: {list(tree)}') from None
        # Validate every path before any writes, including when reusing an extraction/cache tree.
        includes = [(_dependency_path(root, relative), data)
                    for relative, data in record.get('include', {}).items()]
        if any(dep == path or dep == path.with_suffix(path.suffix + '.license.json') for dep, _ in includes):
            raise ValueError('dependency conflicts with model path')
        page = 'https://polyhaven.com/a/' + name
        for dep, data in includes:
            if not _cached(dep):
                _download(data['url'], dep, data.get('md5'))
                _record(dep, source, name, page, data['url'])
        _download(record['url'], path, record.get('md5'))
        _record(path, source, name, page, record['url'], [dep for dep, _ in includes])
    else:
        fmt = (format or 'JPG').upper()
        variant = resolution.upper() + '-' + fmt
        path = root / f'{name}_{variant}.zip'
        if _cached(path):
            return path
        tree = _json('https://ambientcg.com/api/v2/full_json?' + urllib.parse.urlencode({'id':name,'include':'downloadData'}))
        asset = next((a for a in tree['foundAssets'] if a['assetId'].lower() == name.lower()), None)
        if asset is None:
            raise ValueError(f'ambientCG exact ID {name} not found')
        choices = [d for folder in asset.get('downloadFolders', {}).values()
                   for cat in folder['downloadFiletypeCategories'].values() for d in cat['downloads']]
        record = next((d for d in choices if d['attribute'] == variant), None)
        if not record:
            raise ValueError(f'variant {variant} unavailable: {[d["attribute"] for d in choices]}')
        url = record.get('downloadLink') or record['fullDownloadPath']
        _download(url, path)
        _record(path, source, name, 'https://ambientcg.com/a/' + name, url)
    return path

def unpack(archive, destination, max_bytes=1024**3):
    """Extract a ZIP after validating all members (no traversal, symlinks or zip bombs).
    Return extracted file Paths; keep the download's licence sidecar beside the archive."""
    destination = Path(destination).resolve()
    with zipfile.ZipFile(archive) as z:
        total = 0
        for info in z.infolist():
            p = PurePosixPath(info.filename.replace('\\', '/'))
            total += info.file_size
            if p.is_absolute() or '..' in p.parts or ':' in str(p) or stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError('unsafe archive member: ' + info.filename)
            target = destination.joinpath(*p.parts)
            if not target.resolve().is_relative_to(destination) or any(
                    destination.joinpath(*p.parts[:i]).is_symlink() for i in range(1, len(p.parts)+1)):
                raise ValueError('archive destination contains a symlink: ' + info.filename)
            if total > max_bytes:
                raise ValueError('archive exceeds extraction budget')
        z.extractall(destination)
        return [destination / i.filename for i in z.infolist() if not i.is_dir()]

def import_pack(path, source, license_url, height=5.0, name=None):
    """Import a local CC0 GLB/glTF/FBX/OBJ/BLEND file or ZIP, normalize height/base origin.
    Caller supplies approved source + per-pack CC0 licence URL. Returns one parent Empty whose
    children preserve their hierarchy (including armatures). ZIP imports first supported model;
    unpack explicitly to choose among variants. No scripts from .blend files are executed."""
    if source not in SOURCES or not license_url.startswith('https://'):
        raise ValueError('provide an approved CC0 source and its per-pack HTTPS licence URL')
    import bpy
    from mathutils import Matrix
    from ._util import bounds, link
    path = Path(path).resolve()
    if path.suffix.lower() == '.zip':
        files = unpack(path, path.with_suffix(''))
        models = sorted([p for p in files if p.suffix.lower() in ('.glb','.gltf','.fbx','.obj','.blend')], key=lambda p: (p.suffix != '.glb', str(p)))
        if not models:
            raise ValueError('pack contains no supported model')
        path = models[0]
    before = set(bpy.data.objects)
    ext = path.suffix.lower()
    if ext in ('.glb','.gltf'):
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif ext == '.fbx':
        bpy.ops.import_scene.fbx(filepath=str(path))
    elif ext == '.obj':
        bpy.ops.wm.obj_import(filepath=str(path))
    elif ext == '.blend':
        with bpy.data.libraries.load(str(path), link=False) as (src, dst):
            dst.objects = src.objects
        for ob in dst.objects:
            if ob:
                link(ob)
    else:
        raise ValueError('unsupported pack format: ' + ext)
    imported = set(bpy.data.objects) - before
    if not imported:
        raise ValueError('file imported no objects')
    bpy.context.view_layer.update()
    lo, hi = bounds(imported, precise=True)
    if hi.z - lo.z < 1e-8:
        raise ValueError('model has zero height')
    root = link(bpy.data.objects.new(name or path.stem, None))
    roots = [o for o in imported if o.parent not in imported]
    for ob in roots:
        mw = ob.matrix_world.copy()
        ob.parent = root
        ob.matrix_world = mw
    factor = height / (hi.z - lo.z)
    root.matrix_world = Matrix.Scale(factor, 4) @ Matrix.Translation((-((lo.x+hi.x)/2), -((lo.y+hi.y)/2), -lo.z))
    root['bkit_license'] = json.dumps(dict(source=source, license='CC0-1.0', license_url=license_url))
    return root
