"""bkit: tested Blender helpers for stylised 3D (props, characters, look-dev, animation, export).

Import inside Blender after putting the folder that CONTAINS bkit on sys.path:
    import sys; sys.path.insert(0, "/path/to/roblox-gamesmith/blender")
    import bkit
(`blender-pc run` does this for you.) Manual: references/blender-kit.md in this repo.
"""
import importlib

__version__ = "0.1.0"
_MODULES = ("compat", "palettes", "scene", "lighting", "materials", "modelling", "character",
            "animation", "render", "export", "assets", "detail")
for _m in _MODULES:
    globals()[_m] = importlib.import_module(f".{_m}", __name__)


def finish(code=0):
    """End a headless script without Blender's teardown (some 5.x builds crash while freeing
    meshes on exit). Call it last, after every file is written."""
    import os
    import sys
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)
