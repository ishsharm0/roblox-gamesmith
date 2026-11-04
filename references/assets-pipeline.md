# Assets Pipeline

Where models, textures and materials come from, how to make them fit Roblox, and how to bring them in safely. Headless Blender tooling for your Mac is in `blender-pipeline.md`; look and palette in `art-direction.md`; audio in `audio.md`.

## The 5 rules that matter most

1. **Built or licensed, never generated (by default).** Sources in order: built in Studio, made in Blender, CC0 kits, vetted Creator Store assets. Roblox's `generate_*` MCP tools and any AI art are off unless the user opts in by name.
2. **Scale to the character.** A default character is ~5 studs tall; 1 stud is about 0.28 m in Roblox's physics/avatar scale. Check every import against a character before keeping it.
3. **Respect the mesh budget.** Max 20,000 triangles per mesh; most props should be 200-3,000. Reuse the same mesh (same MeshId and TextureID) so the renderer can instance it.
4. **Audit and restyle everything external.** Strip scripts, check licences, recolour to the palette, unify materials and texel density.
5. **Keep a manifest.** `assets/CREDITS.md` (source, author, licence, URL per asset) and the source files (`.blend`, textures) in the repo. Uploads and anything touching the user's Roblox account wait for their yes.

---

## 1. Built in Studio

Best for greybox, architecture, stylised low-poly, anything that changes often.

- **Parts**: `Part` (Block, Ball, Cylinder, Wedge, CornerWedge). Snap to a 1 or 0.5 stud grid for architecture; rotate in 15-degree steps.
- **CSG**: `BasePart:UnionAsync`, `SubtractAsync`, `IntersectAsync` (plugin/edit context) for arches, windows, rounded shapes. Set `UsePartColor = true` to recolour, `CollisionFidelity = Box` or `Hull` for decor. Too many operations in one union produce heavy meshes; prefer a few simple unions.
- **Terrain** for ground, cliffs, water (see `art-direction.md`).
- **MaterialVariants** to give built geometry a consistent stylised surface.
- Build procedurally with `execute_luau` (in chunks) for repeated structures: fences, stairs, rows of houses with variation.
- **Packages** (`PackageLink`, right-click > Convert to Package) for assets reused across places; edits propagate.

## 2. Blender

Use for organic shapes, hero props, characters, anything where parts look blocky.

### Modelling for Roblox

| Spec | Value |
|---|---|
| Triangles per mesh | max 20,000 (importer auto-simplifies above that, often badly). Props 200-3,000, hero objects 5,000-15,000 |
| Units | Easiest: treat 1 Blender unit as 1 stud and keep a 5-unit-tall character reference in the scene |
| Transforms | Apply rotation and scale (Ctrl+A) before export; origin where the object should pivot (usually bottom centre) |
| Geometry | Watertight, no n-gons (quads/tris), no zero-thickness faces, normals pointing out |
| UVs | One UV set, all inside 0-1; overlapping allowed |
| Materials | One material per mesh object (Roblox applies one texture set per MeshPart); split by material into separate objects |
| Pieces | Split large environment pieces into chunks so streaming and culling work (and stay under 2,048 studs per axis) |

### Textures and PBR

| Map | Format | Notes |
|---|---|---|
| Colour (albedo) | RGB (alpha only if using transparency) | No baked lighting for PBR; baked AO is OK for stylised |
| Normal | RGB, **OpenGL tangent space** | DirectX normals look inverted; flip green if needed |
| Roughness | Greyscale 8-bit | |
| Metalness | Greyscale 8-bit | Pure 0 or 1 for most materials |

Resolution budget: ~256 px for a 2-3 stud prop, 512 for ~4-10 studs, 1024 (practical max) for ~10-20 studs or hero assets. Formats `.png`, `.jpg`, `.tga`, `.bmp`. https://create.roblox.com/docs/en-us/art/modeling/texture-specifications

Apply PBR with a `SurfaceAppearance` under the `MeshPart`, or as a `MaterialVariant` for tiling surfaces. Stylised alternative: no textures at all, vertex-colour-like flat materials via part `Color` and `SmoothPlastic`.

### Rigging (R15 characters, creatures, animated props)

- Bones with scale 1 and rotation 0 at rest; root bone at origin; no influence on the root bone; max 4 bone influences per vertex; disable "Add Leaf Bones" on export. https://create.roblox.com/docs/en-us/art/modeling/specifications
- R15 humanoids follow Roblox's body part naming and cage requirements; start from Roblox's official Blender rig/templates rather than from scratch, and check in Studio's Avatar Setup tool.
- Non-humanoid animated models: skinned mesh + `AnimationController` + `Animator`; one animation per FBX export.

### Export

- **glTF/GLB**: simplest; no extra scaling configuration needed. Good default for static props.
- **FBX**: Path Mode = Copy with Embed Textures; Apply Scalings = "FBX Unit Scale" with other scales at 1.0 (or Scale 0.01 if objects arrive 100x too big); disable Add Leaf Bones; Bake Animation only when exporting an animation. https://create.roblox.com/docs/en-us/art/modeling/export-requirements
- Whatever the format, confirm size in the 3D Importer preview against the character before inserting.

### Blender on your Mac

- Default: headless Blender via `tools/blender/` (`Blender -b --python ...`) as documented in `blender-pipeline.md`, so no window pops up in front of the user.
- If `ahujasid/blender-mcp` is installed, it drives a running, visible Blender and offers Poly Haven, Sketchfab and Hyper3D integrations. Use it only when the user is happy for Blender to be open; Poly Haven downloads are CC0, Sketchfab models need a licence check per model, and Hyper3D is AI generation (off unless the user opts in).

## 3. Importing into Roblox

| Route | When |
|---|---|
| Studio 3D Importer (File > Import 3D: FBX, glTF/GLB, OBJ) | Interactive; preview, scale check, rig/animation import, creates MeshParts with textures |
| `insert_asset` / `studio call insert_asset` | Assets already uploaded to the user's inventory or the Creator Store |
| Open Cloud Assets API (`POST https://apis.roblox.com/assets/v1/assets`, API key with asset write scope) | Batch/automated uploads of models, meshes, images, audio; returns an operation to poll for the asset id |
| `studio import <file.rbxm>` | Models already saved as `.rbxm` (world chunks, prefabs) |

Uploading creates assets on the user's account, can trigger moderation, and counts against upload limits: get the user's go-ahead first.

After import:

- `CollisionFidelity`: `Box` for small decor, `Hull` for simple solids, `Default`/`PreciseConvexDecomposition` only where players touch detailed shapes.
- `RenderFidelity = Automatic` (LOD at distance).
- `CanTouch`/`CanQuery` off for decoration; anchor statics.
- Set `DoubleSided` only where needed (leaves, cloth).
- For distant landmarks under streaming, `Model.LevelOfDetail = StreamingMesh` gives a low-cost imposter.

## 4. Creator Store

- Free assets on the Creator Store may be used in your Roblox experiences; some assets are paid. Assets are licensed for use on Roblox, not for export to other engines or merchandise.
- Quality bar: verified or reputable creators, consistent style with your kit, sensible triangle counts, no scripts for decorative items.
- Safety: follow the audit in `studio-mcp.md` section 5 (quarantine, scan for `require(<id>)`, `getfenv`, `loadstring`, obfuscation, hidden scripts; strip scripts). "Anti-lag", "free admin" and "fire/sound" models are the classic backdoor carriers.
- Restyle: rescale to the character, recolour to the palette, replace mismatched materials. A free model left in its original style is the most common reason a game looks cheap.

## 5. CC0 and open sources

| Source | What | Licence notes |
|---|---|---|
| Kenney (kenney.nl) | Low-poly kits, UI packs, icons, audio | CC0: no attribution required (credit appreciated) |
| Quaternius (quaternius.com) | Stylised low-poly characters, nature, buildings, often rigged/animated | CC0 |
| KayKit (Kay Lousberg) | Stylised dungeon/city/character kits | CC0 |
| Poly Haven (polyhaven.com) | PBR textures, HDRIs, realistic models | CC0 |
| ambientCG (ambientcg.com) | PBR textures | CC0 |
| Sketchfab | Everything | Per model: CC0 fine; CC-BY needs visible attribution (in-game credits board + description); NC/ND licences are not suitable for a monetised game |

Rules:

- Avoid "free for personal use", editorial, ripped-from-games, or unclear-licence packs.
- Keep `assets/CREDITS.md`: asset, author, source URL, licence, date, where used.
- Mixing kits from different artists breaks style; prefer one or two kits and fill gaps in Blender with matching proportions and palette.
- Convert CC0 textures to Roblox specs (OpenGL normals, 1024 max, separate roughness/metalness).

## 6. Performance budgets

| Item | Guideline |
|---|---|
| Unique meshes in view | Fewer is better; reuse the same mesh with different colours/rotations |
| Triangles in view (mobile) | Aim for well under ~500k total on screen; keep decor meshes cheap |
| Textures | 1024 only for hero assets; share texture atlases across a kit |
| `SurfaceAppearance` count | Each unique one is a texture set in memory; reuse |
| Transparency | Large transparent/`Glass` areas cost overdraw on mobile |
| Unions | Fine in moderation; each unique union is its own mesh |

Profile with the MicroProfiler and the Developer Console memory tab (`performance.md`).

## Asset checklist

- [ ] Source is built, Blender-made, CC0/licensed, or vetted Creator Store; recorded in `CREDITS.md`
- [ ] No AI-generated meshes/textures unless the user opted in
- [ ] Scale checked against a 5-stud character
- [ ] Under 20k tris per mesh; props in budget; one material per mesh
- [ ] PBR maps to spec (OpenGL normals); texel density consistent
- [ ] Collision and render fidelity set; decor anchored with `CanTouch`/`CanQuery` off
- [ ] Scripts stripped from imported models; audited if kept
- [ ] Recoloured/restyled to the art direction
- [ ] User approved any upload to their account

---

## CHANGELOG

- 2026-11-03: New file.
