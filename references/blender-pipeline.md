# Blender to Roblox

Five rules:
1. Blender runs only when the person wants meshes from it, and then headless only
   (`/Applications/Blender.app/Contents/MacOS/Blender -b --python <script>.py -- args`), never the
   GUI: the person is using their Mac.
2. Every script ends through `rbxblend.finish()` (`os._exit`) after writing its files. Blender 5.0.1
   double-frees mesh data in its exit teardown, and every crash puts a "Blender quit unexpectedly"
   alert on the person's screen. Run one script once and check it exits cleanly before running it in
   a loop. Ask the person before the first Blender run in a session.
3. Parts first. Most stylised Roblox worlds are built from Parts, WedgeParts, cylinders and unions,
   and they need no upload at all. Reach for Blender when a silhouette can't be built from primitives
   (organic trees, rocks, characters, curved props).
4. Author in studs: 1 Blender unit = 1 stud (0.28 m); a character is about 5 studs tall. Origin at the
   base centre; Blender (x, y, z) maps to Roblox (-x, z, y).
5. Keep a mesh under 20,000 triangles (Roblox's import limit for one MeshPart). Props for a phone game
   should be far lower, around 50-1,500.

## Scripts (`tools/blender/`)

| Script | Does |
|---|---|
| `rbxblend.py` | shared helpers: palette material (8x8 swatch texture plus a vertex-colour attribute), bmesh primitives, bounds in studs, limits check, FBX and glTF export with Roblox axes, `finish()` |
| `make_asset.py -- <kind> <out> [--seed N]` | stylised low-poly kinds: tree, pine, bush, rock, crate, barrel, coin, gem, platform, fence |
| `preview.py -- <in> <out.png>` | a turntable contact sheet rendered headless, to judge the asset by eye |
| `to_luau_mesh.py -- <out.luau> <in>` | mesh data as a ModuleScript, for the runtime EditableMesh route |

These were written in the first build session and have not run since the crash-safe exit was added.
Test one with the person's OK before relying on them.

## Getting a mesh into a place

1. **Open Cloud upload (tested).** Use `rbxcloud upload <file.glb> --name "Name"` to preview,
   then add `--upload --wait --out operation.json` for an authorized upload. Key and creator metadata
   are stored privately in `~/.config/roblox/`, outside projects. Read [open-cloud.md](open-cloud.md).
   A parts-built lotus was exported to RBXM, uploaded, approved, read back and imported in Studio.
   GLB/FBX requests use the same Assets API; Blender export remains untested after the earlier crash.
2. **Runtime EditableMesh (no key).** `to_luau_mesh.py` writes the mesh as a ModuleScript; a loader
   builds it at runtime with `AssetService:CreateEditableMesh()` and `CreateMeshPartAsync`. Works in
   Studio (tested in Edit mode); check the current EditableMesh rules for published experiences
   (memory budget, replication) in the docs before shipping with it.
3. **Studio's own importer** (File > Import 3D) is a GUI flow; the person can do it in a minute when
   asked.

Textures: palette swatches survive any route. For PBR, a SurfaceAppearance needs uploaded image ids
(ColorMap, NormalMap, RoughnessMap, MetalnessMap), so it is route 1 only.
