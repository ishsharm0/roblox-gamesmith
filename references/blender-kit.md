# bkit: tested stylised Blender kit

This kit makes authored geometry with Python; it does not generate AI images or meshes.
One unit is one stud, Z is up, front is -Y. Primitives use centre locations; props/buildings
use base locations. Rotations in convenience functions are degrees; generic animation.key uses
Blender's native radians. Colours are sRGB hex, palette.name, or RGB tuples; shader conversion is internal.

## Run on the remote renderer

Blender never runs on the local Mac. The separately configured `blender-pc` launcher uses SSH to run
one headless job at a time. Leave Studio and processes belonging to others alone.

```sh
blender-pc info
blender-pc run blender/examples/06_cannon.py --out output/cannon --timeout 180
blender-pc run blender/tests/integration.py --in blender/tests --out output/checks --timeout 180
```

The launcher copies bkit next to the script and inserts its parent into sys.path before execution.
Set BKIT_DIR to the package directory when using a different checkout. Without that launcher, copy
the whole bkit folder alongside your script and add the script's directory to sys.path before import.
The first argument after `--` inside Blender is the output directory; the second is the copied input
directory (from `--in`). Script options follow those two arguments. Always end with `bkit.finish()`
after saving files. It flushes streams and exits without Blender teardown. An exception before finish
must be investigated; a partial output folder does not establish successful completion.

Use fresh output folders. Verify expected file counts, PNG dimensions and the check JSON. The launcher
has been observed returning partial files after interrupted transfers: retrieve missing files from the
same job rather than launching a duplicate render. The local launcher was given SCP keepalives and now
fails on copy errors. Those machine-specific SSH settings belong outside this public repository.

Iteration: 960×960; one remote job at a time; keep each frame below about three minutes. Use EEVEE for
layout and most toy shots. GPU Cycles is useful for glass, translucent film/shadow catchers and final
material checks. Set the aspect ratio BEFORE calling add_camera/aim. Pass only the subject to camera,
lighting and cyclorama; including the backdrop in bounds gives huge lights and distant framing.

## Working conventions

- Start with scene.new_scene(); it clears all objects and associated data in the current file.
- Build three or four readable masses, overlapping at joins; then add secondary details.
- Use rounded_box by default. The default bevel is 7% of the smallest dimension, three segments,
  followed by FACE_AREA weighted normals at weight 50. Use segments1–2 for a game mesh budget.
- Use a single palette per asset. Built-ins: toybox, meadow, candy, fortress, sunset, arctic, roblox,
  product. tree's palette must define leaf, pine, grass and bark (meadow does).
- Material constructors return Materials and reuse identical names. Modelling mat accepts a Material
  or colour spec. assign(root, material) affects descendant meshes.
- Character returns .rig, .parts, .mouth and .objects. Pass hero.rig to camera/lighting/export and
  hero to pose/animation helpers. Body parts stay rigidly bone-parented. This is a presentation rig,
  not a skinned Marketplace avatar. Five-stud rest height, 1.35×1.1×1 head, 2×1×2 torso, 1×1×2 limbs.
- Export coloring is deliberate: atlas_from_materials mutates meshes, applies modifiers, maps each
  face into a swatch and creates ONE material + UV set. Its white Col attribute modulates the texture;
  duplicating the swatch colour in Col darkens GLB. join=False preserves separate rigged pieces.
- The atlas flattens material BASE COLOURS. It does not bake grain, roughness variations, emission,
  glass or procedural PBR detail. vertex_gradient modulates exported Col; no texture baking is implied.
- FBX/OBJ automatically save generated image buffers beside the export. Keep OBJ/MTL and copied PNGs
  together. GLB embeds supported maps. Reports check evaluated geometry against 20k tris/mesh, one
  material, and one UV set inside 0–1; strict export refuses violations. Reports are not Studio approval.
- Asset fetch uses exact IDs and CC0 providers, cache hashes and licence sidecars. Poly Haven textures
  default to Diffuse; channel='Rough' or 'nor_gl' selects others. Model include files are fetched too.
  Cache defaults to ~/.cache/bkit or BKIT_CACHE. import_pack requires approved source + actual per-pack
  CC0 licence URL. ZIP picks the first supported model; unpack and choose a file for explicit variants.
  Preserve licence sidecars. Never use pack scripts or claim an unknown licence is CC0.

## Level of detail: cute, not cheap (read before modelling anything)

A first gallery made from smooth boxes, plain cylinders and cones was rejected as "very low quality and
low detail: there's a happy medium between cute low poly and just bad". The medium is this:

- **Build the material, don't colour it.** A wall is courses of separate bricks in running bond; a door
  is planks with iron straps and studs; a roof is rows of overlapping tiles; a path is individual
  stones; a wheel has a tyre, a rim, a hub and spokes. One smooth box with a brick colour reads as
  placeholder at any resolution. `bkit.detail.Batch` puts thousands of small solids in one mesh with
  one bevel, so this costs seconds, not hours.
- **Gaps and tints do the work.** Leave 2 to 4% of the piece size between pieces over a darker core
  ("mortar"), bevel every piece (about 10% of its smallest side, 2 segments), push some pieces out by a
  few percent, and pick each piece's colour from three or four tints within about 7% of the base.
- **Three sizes of form on every asset**: the big masses (towers, walls), medium parts (window frames,
  sills, corbels, caps, plinth course), small parts (studs, knobs, ring handles, finials, flowers).
  An asset with only the first size is a blockout.
- **Organic things get one skin.** Overlap spheres for the masses, voxel-remesh (voxel about 2% of the
  size), smooth 20+ iterations: no seams where the head meets the body. Eyes are black with a white
  glint; the glint is what makes it alive.
- **Colour.** `new_scene()` uses the 'neutral' view: authored colours come out as written. The 'toy'
  (AgX) view greys saturated yellows and creams; use it only for realistic or high-contrast scenes.
  Keep stone warm and light (#F6EAD4), accents saturated (roof #FF5545, duck #FFD21F), a white-ish
  world at 0.7 for fill, a warm key, a white rim, and a backdrop in the complementary hue.
- **Frame it.** `add_camera(subject, margin=0.68)` when the subject sits on a wide base: the automatic
  fit is by bounding sphere and leaves the subject small. Render a wide shot and at least one close-up
  at a low angle (elevation 10 to 15); the close-up is where missing detail shows.
- **Budget.** The detailed fortress set is about 265k triangles: right for stills and film. For Roblox,
  build the same thing with `seg=1` bevels, fewer courses and no hidden faces, then check
  `tri_count` per mesh against 20k (export.report does it).

`bkit.detail` (complete example: `blender/examples/09_fortress_detail.py`):

| Call | Makes |
|---|---|
| `Batch(mats)` then `.box(size, loc, rz, mi, rx, ry)`, `.arc(r0, r1, a0, a1, z0, z1, mi)`, `.prism(pts, z0, z1, mi)`, `.bricks(length, height, thick, origin, rz, ch, bl)`, `.obj(name, bevel, seg)` | Any surface made of pieces: one mesh, one bevel. `mi` is the index into `mats` (use `tints()`) |
| `tints(kind, color)` / `shade(hex, factor)` | Four materials around one colour / a lighter or darker hex |
| `wall(length, height, thick, loc, rot, crenels)` | Brick wall with plinth course, cap and capped merlons |
| `tower(radius, height, loc, flag)` | Round tower of curved bricks, framed windows with sills, corbels, tiled cone roof, finial, flag |
| `gate(width, height, loc)` | Voussoir arch with keystone and jambs, planked door, iron straps with studs, ring handle |
| `house(width, depth, height, loc)` | Plaster and timber-frame house on a stone course, tiled gable roof, brick chimney, lit windows |
| `shingle_cone(R, h, tiers, mats)` / `gable_tiles(width, depth, rise, z)` | Roof tiles for round and pitched roofs |
| `duck(size, loc, facing)` | Rubber duck with one smooth skin |
| `cannon(loc, aim, s)` | Lathed barrel with a brass band on a wooden carriage with spoked wheels |
| `base_disc(R, thick)` / `cobbles(path)` | Plank board with a felt mat / a stone path |

To build something that is not in the table (a ship, a market stall, a robot), write it the same way:
masses first, then replace every surface with pieces through a `Batch`, then the small parts, then
look at a close-up render and add what a real one would have.

## Visual review before delivery

Open every PNG. Check the silhouette at thumbnail size, then inspect highlights, contact shadows,
bevels and noise at full size. A script that exits without error can still make a black frame.

1. Name the object from front, side and three-quarter views. Correct primary proportions first.
2. Check ground contact and joints in every pose, not just the rest frame. Raised arms must stay
   connected; walk feet must neither penetrate nor hover. Keep clearance at sampled and in-between frames.
3. Check all frame edges, including portrait/landscape, camera moves, tall flags and shadow extents.
4. Reject pink textures, unintended black materials, clipped highlights, large noisy shadow patches,
   floating parts, sharp raw boxes, visible plane edges and distracting backdrop shadows.
5. meter = render.measure(path, crop=.65) is a central crop, not a segmentation mask. For these studio
   products mean about 0.4–0.6 and near-zero white clipping worked. Moonlight is intentionally darker.
   Do not force an emissive ball, black rubber or night scene to the same mean.
6. If a cyclorama blocks a rear light, move the lamp inside the sweep or use a large ground plane.
   For low-angle ground-only shots use size 1000; a small plane exposes its distant edge.
7. Check exported material appearance after re-import. Validate triangle count after bevels and join.
   Procedural shader details are not promised by GLB/FBX. Use the technical model sheet for topology.

## Calibration verified on the renderer

Blender **5.3.0**, build 02f0899d78e3 (2026-11-10), Windows, NVIDIA GTX 1050 Ti 4 GB,
Cycles **OptiX**. Blender4.2–5.2 compatibility guards are implemented but those versions were not run.
All images were opened for review; the galleries are external artifacts, not checked into Git.

The shared product setup is AgX/Punchy, exposure 0, gamma 1; 960×960; 70 mm camera, margin 1.3;
matte backdrop #BCB6AB; studio_soft at strength 1. Avoid arbitrary exposure boosts to hide bad lighting.
The materials study uses the same #D68C55 ball (silver #D6DEE6 for metal/glass) on a graphite plinth.
The lighting study uses the same yellow duck, blue box and chrome ball, camera 32°/23°, margin 1.28.

### Material values and measured central brightness

Defaults below are shader inputs, not guessed ranges. Other unspecified Principled inputs retain
Blender defaults. Brushed metal uses anisotropy 0.6; fabric is a smooth cloth shader, not a fibre weave.
Wood grain 0.12 is render-only. Emission is 4.0; car-paint coat roughness 0.03; glass IOR 1.45.

| Material | Roughness | Metallic | Coat | Sheen | Transmission | EEVEE mean | White clip% |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| toy_plastic | 0.32 | 0 | 0.0 | 0 | 0 | 0.429 | 0.0 |
| clay | 0.75 | 0 | 0 | 0.25 | 0 | 0.43 | 0.0 |
| rubber | 0.48 | 0 | 0.15 | 0 | 0 | 0.429 | 0.0 |
| painted_wood | 0.55 | 0 | 0 | 0 | 0 | 0.424 | 0.0 |
| metal_brushed | 0.32 | 1.0 | 0 | 0 | 0 | 0.438 | 0.0 |
| chrome | 0.06 | 1.0 | 0 | 0 | 0 | 0.412 | 0.0 |
| glass | 0.02 | 0 | 0 | 0 | 1.0 | 0.459 | 0.0 |
| emissive | 0.5 | 0 | 0 | 0 | 0 | 0.568 | 0.0 |
| car_paint | 0.38 | 0.55 | 1.0 | 0 | 0 | 0.416 | 0.0 |
| fabric | 0.92 | 0 | 0 | 0.7 | 0 | 0.43 | 0.0 |

### Lighting defaults and measured output

Each area light uses energy=level×π×distance²; distance and emitter size scale with subject radius.
This is a nominal calibration convention, not a promise of exact physical irradiance from a large
area emitter. SUN energy is level directly. Engine gain=1 for both engines. Rigs use camera-relative
azimuth; new_scene should precede switching rigs, otherwise the lamps accumulate.

| Rig | Authored light levels | World strength | EEVEE mean / white clip% | Cycles mean / white clip% |
| --- | --- | ---: | --- | --- |
| studio_soft | key:3.2, fill:0.9, rim:2.6 | 0.25 | 0.483 / 0.0 | 0.496 / 0.0 |
| toy_bright | key:3.2, fill:1.2, rim:2.0 | 0.55 | 0.531 / 0.0 | 0.528 / 0.0 |
| hero_rim | key:2.4, rim_l:6.0, rim_r:6.0, top:0.6 | 0.15 | 0.465 / 0.01 | 0.509 / 0.06 |
| sunny_outdoor | sun:3.6 | 0.75 | 0.507 / 0.0 | 0.505 / 0.0 |
| night_moon | moon:2.0, fill:0.8 | 0.3 | 0.255 / 0.0 | 0.293 / 0.0 |

The former rear moon SUN was blocked by the cyclorama and produced 100% black clipping. Final moon
is at−35°azimuth/40°elevation with a frontal blue fill; black clipping is below 1% in the fixed study.
For hero_rim the long rear emitters may cast a broad shadow on a nearby sweep; use a dark background
or position the sweep farther away for a pure product silhouette.

### Quality and time budget

| Preset | EEVEE samples | Cycles max samples | Ray trace / GI | Shadow rays / steps |
| --- | ---: | ---: | --- | --- |
| draft |16|24|off/off|1/4|
| fast |24|48|on/on|1/6|
| good |64|96|on/on|2/8|
| hero |128|256|on/on|3/12|

Cycles sampling has a 120-second time limit; setup, shader compilation and denoising are additional.
A cold GPU cache can be much slower than a warm render. One long ten-scene Cycles process stalled
on its last material; completed PNGs were recovered and the last material was retried in a fresh job.
Prefer fresh short Cycles jobs with launcher timeout 180. Do not leave a stalled job running or start
a duplicate. EEVEE good material frames measured 3.5–8.7s, hero cannon 12.8s, fortress 14.8s at 960².
Full-HD two-frame sequences measured about 4.0–4.4s/frame with EEVEE fast. Cycles rigs measured 20–132s
per 960²frame including cold setup. The transparent Cycles glass/shadow test measured 23s at 48samples.

Geometry budgets, actual imported packs and function coverage are recorded in the verification
section below. Do not infer game-ready triangle budgets from a beauty render; the rounded duck is
about 6.6ktriangles and needs simplification for repeated mobile-game props.

## API (one-line use per function)

Defaults are shown so small scripts can be copied directly. All operations below run inside Blender.

## bkit

| Function and key arguments | Purpose | Returns / effects |
| --- | --- | --- |
| `finish(code=0)` | Flush output and exit a headless Blender process without normal teardown. | Does not return; exits headless process after flushing stdout/stderr. |

## bkit.scene

Call new_scene once at the start. It deletes the current file contents. Set the output aspect before framing a camera. azimuth 0 faces the model front (-Y); 90 is +X. lens is millimetres; margin greater than 1 adds breathing room.

| Function and key arguments | Purpose | Returns / effects |
| --- | --- | --- |
| `clear()` | Remove every object and data-block from the current file in place. (read_factory_settings from inside a script crashes some 5.x builds, so this is used instead.) | None; clears current file. |
| `new_scene(units='studs', look='toy', engine='EEVEE', fps=30, resolution=(960, 960))` | Start clean: remove everything, set units, colour look, engine, fps and resolution. units: 'studs' (1 BU = 1 Roblox stud; character ~5 tall) or 'metric' (1 BU = 1 m). look: 'toy' \| 'neutral' \| 'product' \| 'flat' (see set_look). engine: 'EEVEE' \| 'CYCLES'. | Scene. |
| `set_look(preset='toy', scene=None, exposure=None)` | Set a named colour-management preset and optional exposure. | (selected view_transform, selected look). |
| `world_color(color='#B8BCC4', strength=0.4)` | Uniform world colour: soft ambient fill and plain background. | World. |
| `world_gradient(top='#9CC9F0', bottom='#F2E8D5', strength=0.8, horizon=0.0)` | Sky-to-ground gradient world (cheap outdoor ambient; bottom colour bounces up). | World. |
| `world_sky(sun_elevation=35.0, sun_rotation=30.0, strength=0.35, sun_disc=False)` | Physical sky texture (Nishita / multiple scattering). | World. |
| `world_hdri(path=None, strength=1.0, rotation=0.0, background=None, background_strength=1.0)` | Load an equirectangular HDRI; omitted path fetches/caches Poly Haven studio_small_08. | World. |
| `cyclorama(width=None, depth=None, height=None, radius=None, color='#D9D4CC', subject=None, roughness=0.9, name='Cyclorama')` | Seamless studio backdrop: a floor that curves up into a back wall (no visible horizon). | Mesh Object. |
| `ground(size=40.0, color='#C8C2B6', z=0.0, name='Ground', roughness=0.95)` | A flat square ground plane at height z. | Mesh Object. |
| `shadow_catcher(size=40.0, z=0.0)` | Invisible ground that only keeps shadows, over a transparent film (Cycles only; EEVEE renders it as a plain ground). | Mesh Object. |
| `add_camera(subject=None, azimuth=30.0, elevation=20.0, lens=70.0, margin=1.12, target=None, distance=None, name='Camera', ortho=False, set_active=True)` | Add a camera aimed at `subject` (objects) or `target` (point), framing it automatically. azimuth: 0 = front (-Y), 90 = right side, 180 = back; elevation: degrees above horizon. lens (mm, 36 mm sensor): 35-50 environments, 70-100 products/characters (less distortion). margin: 1.0 = touching the frame edges; 1.1-1.25 normal. | Camera Object. |
| `aim(cam, subject=None, azimuth=30.0, elevation=20.0, margin=1.12, target=None, distance=None, ortho=False)` | Re-place an existing camera around subject/target (same arguments as add_camera). | Same Camera Object. |
| `dof(cam, focus=None, fstop=2.8)` | Enable camera depth of field using an object, point, or numeric focus distance. | Same Camera Object. |

## bkit.lighting

A rig is sized to its subject and aligned relative to the camera. level is irradiance at the target, not raw light watts. Rigs return a dict which lighting.scale can adjust.

| Function and key arguments | Purpose | Returns / effects |
| --- | --- | --- |
| `add_light(kind='AREA', level=3.0, color='#FFFFFF', target=(0, 0, 0), azimuth=-45, elevation=40, distance=5.0, size=1.0, name='Light', size_y=None)` | Add one light aimed at `target`. level = irradiance at the target (sun strength units, 3-4 is a bright key); azimuth/elevation in world degrees (0 = from the front, -Y). | Light Object. |
| `rig(name='studio_soft', subject=None, camera=None, strength=1.0, world=True, warmth=0.0)` | Light `subject` (objects; default everything) with a named rig, relative to `camera` (default scene camera; azimuth 0 = from the camera). strength scales every light (1.0 = calibrated). world=False keeps your own world. warmth -1..1 tints key warmer (+) or cooler (-). | Dict {role: light Object}. |
| `scale(lights, factor)` | Multiply the energy of every light in a rig dict (brighten/darken the whole rig). | None; changes light energies in place. |
| `practical(location, color='#FFB066', level=2.0, radius=0.1, reach=2.0, name='Practical')` | A small warm point light in the scene (lantern, window, campfire). level is irradiance at distance `reach`. | Point-light Object. |

## bkit.materials

Colour specs are #RRGGBB, palette.colour, or sRGB tuples. Material constructors reuse material names by default. Procedural grain is render-only unless baked; use a colour atlas for a game mesh. atlas_from_materials changes meshes in place; keep join=False for separately rigged parts.

| Function and key arguments | Purpose | Returns / effects |
| --- | --- | --- |
| `principled(name, color='#BBBBBB', reuse=True, **params)` | A plain Principled BSDF material. params: metallic, roughness, specular, coat, coat_roughness, subsurface, sheen, sheen_roughness, transmission, anisotropic, ior, alpha, emission (strength), emission_color. | Material. |
| `bsdf(mat)` | The Principled BSDF node of a material (found by type, not by name). | Principled BSDF Node. |
| `toy_plastic(color='toybox.red', name=None)` | Glossy injection-moulded plastic (LEGO, toy figures). | Material. |
| `clay(color='#C9B8A6', name=None)` | Matte clay/plasticine: soft highlight, faint sheen. | Material. |
| `rubber(color='toybox.yellow', name=None)` | Bath-toy rubber/vinyl: satin, slightly softer than plastic. | Material. |
| `painted_wood(color='fortress.wood', name=None, grain=0.12)` | Painted or stained wood with a faint procedural grain (render only; exports as flat colour). grain 0 = no grain, 0.1-0.2 = subtle. | Material. |
| `metal_brushed(color='#B8BCC2', name=None)` | Brushed steel/aluminium: metallic, anisotropic streaks along the object's X axis. | Material. |
| `chrome(color='#E6E8EB', name=None)` | Mirror chrome. | Material. |
| `glass(color='#DDEFF5', name=None)` | Clear glass (tint with color). | Material. |
| `emissive(color='toybox.yellow', strength=4.0, name=None)` | Self-lit surface (lamps, screens, magic). strength 2-6 glows under AgX; >8 blows out to white. | Material. |
| `car_paint(color='toybox.red', name=None)` | Metallic paint under a mirror clearcoat (cars, hero props). | Material. |
| `fabric(color='toybox.blue', name=None)` | Cloth/felt: very rough with sheen at grazing angles (flags, cushions, clothes). | Material. |
| `matte(color='#BDB7AE', name=None, roughness=0.95)` | Plain matte surface (backdrops, ground, tables). | Material. |
| `make(kind, color, name=None)` | Material by kind name: make('toy_plastic', 'toybox.red'). | Material. |
| `assign(objs, mat, slot=0)` | Give each mesh object `mat` (replacing material slot `slot`, adding it if missing). | Material. |
| `palette_image(colors, name='bkit_atlas', cell=8, path=None)` | Build a square atlas image of flat colour swatches (sRGB tuples/specs), `cell` px each. | (Image, uv_of(index) callable). |
| `atlas_from_materials(objs, name='Atlas', join=True, image_path=None, roughness=0.6)` | Replace per-face flat material colours with a swatch atlas and UVs; optionally join meshes. | Single Object or list of Objects, depending on input/join. |
| `vertex_gradient(objs, bottom=0.72, top=1.08, attr='Col')` | Darken the bottom and lighten the top of each object's 'Col' vertex colours (cheap baked ambient occlusion, the Kenney/Synty trick). | None; changes Col vertex colours. |

## bkit.modelling

Units are studs; Z up, front -Y. Primitive location is its centre. Prop/building location is its ground/base centre. mat accepts a Material or a colour spec. Rotation helpers and primitive rotation tuples use degrees. Bevel/WeightedNormal modifiers stay live until applied or joined.

| Function and key arguments | Purpose | Returns / effects |
| --- | --- | --- |
| `bevel(obj, width=0.05, segments=3, angle=BEVEL_ANGLE, weighted=True, profile=0.5)` | Add a Bevel (+ WeightedNormal) modifier stack to any mesh object and smooth-shade it. width in scene units (rule of thumb: 4-8% of the smallest dimension; 0.05-0.1 on a 1-stud box); segments: 1 = chamfer (Roblox budget), 2 = default prop, 3 = hero. | Mesh Object; operation helpers return the same Object. |
| `rounded_box(size=(1, 1, 1), radius=None, segments=3, location=(0, 0, 0), mat=None, name='Box', rotation=(0, 0, 0))` | Box with rounded edges. size (x, y, z); radius default 7% of the smallest side. | Mesh Object; operation helpers return the same Object. |
| `cylinder(radius=0.5, depth=1.0, verts=32, bevel_width=None, segments=3, location=(0, 0, 0), mat=None, name='Cylinder', rotation=(0, 0, 0), radius_top=None)` | Upright cylinder (or tapered, with radius_top) with rounded rims. verts 24-48 smooth, 6-10 for low-poly. | Mesh Object; operation helpers return the same Object. |
| `sphere(radius=0.5, segments=32, rings=16, location=(0, 0, 0), mat=None, name='Sphere', scale=(1, 1, 1), smooth=True, rotation=(0, 0, 0))` | UV sphere, smooth-shaded (smooth=False for faceted). scale squashes it into an ellipsoid. | Mesh Object; operation helpers return the same Object. |
| `ico(radius=0.5, subdivisions=2, location=(0, 0, 0), mat=None, name='Ico', scale=(1, 1, 1), jitter=0.0, seed=0, flat=True, flatten_bottom=None)` | Icosphere, optionally jittered (seeded) and faceted: the building block of low-poly rocks, bushes and tree crowns. flatten_bottom: z (local) below which vertices are pressed flat. | Mesh Object; operation helpers return the same Object. |
| `capsule(radius=0.3, length=1.0, segments=24, location=(0, 0, 0), mat=None, name='Capsule', rotation=(0, 0, 0))` | Pill shape along Z: total height = length (including the round ends). | Mesh Object; operation helpers return the same Object. |
| `torus(major=0.5, minor=0.12, major_segments=32, minor_segments=12, location=(0, 0, 0), mat=None, name='Torus', rotation=(0, 0, 0))` | Ring/donut around the Z axis. | Mesh Object; operation helpers return the same Object. |
| `lathe(profile, segments=32, location=(0, 0, 0), mat=None, name='Lathe', closed=False, smooth_angle=35.0, rotation=(0, 0, 0))` | Spin a profile around Z. profile: [(radius, z), ...] from bottom to top; points with radius 0 close the ends. closed=True joins last point to first (a ring section, e.g. a torus). | Mesh Object; operation helpers return the same Object. |
| `extrude(profile, depth=0.2, location=(0, 0, 0), mat=None, name='Extrude', bevel_width=None, segments=2, rotation=(0, 0, 0))` | Extrude a 2D outline drawn in the front (X, Z) plane by `depth` along Y, centred on y = 0. profile: [(x, z), ...] counter-clockwise, not repeating the first point. | Mesh Object; operation helpers return the same Object. |
| `arch_profile(width=1.0, height=1.5, segments=10)` | Outline for a door/window with a round top: [(x, z)], base at z = 0. | List of (x, z) outline points. |
| `apply_modifiers(obj)` | Bake an object's modifiers into its mesh (keeps weighted normals). | Mesh Object; operation helpers return the same Object. |
| `join(objs, name='Joined', origin='base')` | Apply modifiers and join objects into one mesh (materials kept as slots). origin: 'base' (bottom centre, for props that stand on the ground), 'center', or None (keep first's). | Mesh Object; operation helpers return the same Object. |
| `set_origin(obj, where='base')` | Move the object's origin to its bounding-box 'base' (bottom centre) or 'center' without moving the geometry in the world. | Mesh Object; operation helpers return the same Object. |
| `place(obj, location=None, rotation=None, scale=None)` | Set location / rotation (degrees) / scale in one call. | Mesh Object; operation helpers return the same Object. |
| `tri_count(obj)` | Triangles in the evaluated (modifiers applied) mesh. | Integer evaluated triangle count. |
| `tree(kind='round', height=4.0, seed=1, location=(0, 0, 0), palette='meadow', lean=None)` | Low-poly faceted tree, `height` tall. kind: 'round' (broadleaf, 2-3 crown blobs), 'pine' (stacked cones), 'tall' (narrow poplar). seed varies shape within the family. ~300-900 tris. | Mesh Object; operation helpers return the same Object. |
| `rock(size=1.0, seed=1, location=(0, 0, 0), color='meadow.stone', chunky=True)` | Faceted boulder about `size` across, sitting flat on the ground. chunky=True merges nearly coplanar facets into bigger planes (the stylised look). ~60-150 tris. | Mesh Object; operation helpers return the same Object. |
| `bush(size=1.2, seed=1, location=(0, 0, 0), color='meadow.leaf', flowers=0)` | Low-poly bush of 3-5 faceted blobs, `size` across. flowers: number of small accent dots. | Mesh Object; operation helpers return the same Object. |
| `cloud(size=3.0, seed=1, location=(0, 0, 8), color='#F4F6FA')` | Puffy smooth cloud of 5-7 overlapping spheres with a flat underside, `size` long. | Mesh Object; operation helpers return the same Object. |
| `grass_tuft(height=0.6, blades=7, seed=1, location=(0, 0, 0), color='meadow.grass')` | A tuft of tapered, outward-curving blades (3-sided, flat-shaded). ~15 tris per blade. | Mesh Object; operation helpers return the same Object. |
| `crate(size=1.0, location=(0, 0, 0), wood='fortress.wood', frame=None, segments=2)` | Wooden crate with a bevelled frame on every edge and a diagonal brace on each side. ~2k tris (segments=1 for ~1k). | Mesh Object; operation helpers return the same Object. |
| `barrel(height=1.2, location=(0, 0, 0), wood='fortress.wood', hoops='#4A4A52', staves=14)` | Bulging wooden barrel with three metal hoops. | Mesh Object; operation helpers return the same Object. |
| `coin(radius=0.5, location=(0, 0, 0.5), color='#F2C14E', upright=True)` | Chunky collectible coin: raised rim, inset face, centre boss. | Mesh Object; operation helpers return the same Object. |
| `rubber_duck(size=1.0, location=(0, 0, 0), color='toybox.yellow', beak='toybox.orange', facing=0.0)` | Classic rubber duck, `size` long, sitting on z = location.z, facing -Y rotated by `facing` degrees. | Mesh Object; operation helpers return the same Object. |
| `wall(length=6.0, height=3.0, thickness=0.9, crenels=True, location=(0, 0, 0), rotation=0.0, stone='fortress.stone', trim='fortress.stone_dark')` | Castle wall segment along X, base centred at location. crenels: merlons along the top. | Mesh Object; operation helpers return the same Object. |
| `tower(radius=1.4, height=5.0, roof='cone', location=(0, 0, 0), stone='fortress.stone', roof_color='fortress.roof', trim='fortress.stone_dark', windows=2, flag=None)` | Round tower. roof: 'cone' (overhanging pointed roof), 'crenel' (battlements), None. windows: arched slits on the front half. flag: colour spec for a pennant on the roof tip. | Mesh Object; operation helpers return the same Object. |
| `flag(height=3.0, location=(0, 0, 0), color='fortress.banner', pole='fortress.stone_dark', wave=0.12)` | Flag on a pole with a gentle wave in the cloth, base at location. | Mesh Object; operation helpers return the same Object. |
| `gate(width=2.4, height=3.2, location=(0, 0, 0), wood='fortress.wood', frame='fortress.stone_dark')` | Arched wooden gate set in a stone frame; front faces -Y. | Mesh Object; operation helpers return the same Object. |
| `roof_gable(width=3.0, depth=3.0, height=1.5, overhang=0.25, location=(0, 0, 0), color='fortress.roof')` | Pitched roof: a prism along Y with eaves overhanging by `overhang`. | Mesh Object; operation helpers return the same Object. |
| `house(width=3.0, depth=3.0, height=2.6, location=(0, 0, 0), walls='#EDE3D0', roof='fortress.roof', trim='fortress.wood', door='fortress.banner', rotation=0.0)` | Small toy house: plastered walls, wooden corner posts, gable roof, door and windows. | Mesh Object; operation helpers return the same Object. |

| `blocky_character(**kwargs)` | Build the block figure through character.blocky_character. | Character dataclass. |

## bkit.character

Each part is rigidly bone-parented. This authoring rig is suitable for Blender/glTF animation; it is not a skinned Roblox avatar. Character has .rig, .parts, .mouth, .objects, .pose(name, **rotations), and .reset(). Parts/bones: head, torso, left_arm, right_arm, left_leg, right_leg; root is the floor pivot. POSES: idle, wave, run, cheer. Alias: blocky_character = r6. Image/blank faces have mouth=None.

| Function and key arguments | Purpose | Returns / effects |
| --- | --- | --- |
| `bone_parent(obj, rig, bone)` | Rigid-parent an object to a bone without changing its world transform. | Same mesh Object. |
| `r6(name='Character', location=(0, 0, 0), skin='#F5CD79', shirt='#377AC8', pants='#34445C', face='simple', face_color='#20232A', scale=1.0)` | Build a grounded five-stud six-part figure with a rigid bone rig and optional shape/image face. | Character dataclass. |
| `reset(character)` | Reset bone transforms to rest; does not clear animation or move the rig object. | Same Character/rig. |
| `pose(character, name='idle', rotations=None, **overrides)` | Reset and apply idle/wave/run/cheer or explicit local bone Euler rotations in degrees. | Same Character/rig. |

## bkit.animation

All start/end/frame values are frames; mouth_flap samples are (seconds, openness) pairs. key uses native Blender values (rotation radians), while key_rotation uses degrees. Easing names: linear, constant, smooth/bezier, ease_in, ease_out, ease_in_out, overshoot, anticipation. Easing belongs to the outgoing segment of the keyed frame. Aliases: set_easing=easing, location=key_location, rotation=key_rotation, scale=key_scale. Camera moves expect parentless cameras.

| Function and key arguments | Purpose | Returns / effects |
| --- | --- | --- |
| `easing(obj, kind='smooth', frame=None, data_path=None)` | Set interpolation on active-action keys, optionally one frame/property. 'overshoot' is a BACK ease-out; 'anticipation' is a BACK ease-in. | Same animated Object. |
| `key(obj, data_path, frame, value=None, easing='smooth', index=-1)` | Set an RNA property and insert a key. | Same animated Object. |
| `key_location(obj, frame, value, easing='smooth')` | Key an object or pose-bone location in scene units. | Same animated Object. |
| `key_rotation(obj, frame, degrees, easing='smooth')` | Key an object or pose-bone XYZ Euler rotation in degrees. | Same animated Object. |
| `key_scale(obj, frame, value, easing='smooth')` | Key an object or pose-bone scale using a scalar or XYZ tuple. | Same animated Object. |
| `key_pose(character, frame, easing='smooth')` | Key all pose-bone locations, rotations and scales at their current values. | Same Character/rig. |
| `squash_stretch(obj, start=1, end=16, amount=0.2, easing='smooth')` | Anticipation, stretch and settle about the object's origin; approximate volume conserved. | Same animated Object. |
| `orbit(camera, target=(0, 0, 0), radius=10, start=1, end=121, azimuth=(0, 360), elevation=15, steps=32, easing='linear')` | Orbit a camera around a fixed target; key location and continuous Euler orientation. | Same animated Object. |
| `dolly(camera, from_location, to_location, start=1, end=48, target=None, easing='smooth')` | Move a camera between two positions, optionally keeping a target in view. | Same animated Object. |
| `push_in(camera, target=(0, 0, 0), start=1, end=48, amount=0.25, easing='smooth')` | Move ``amount`` of the current distance toward a fixed target (0 < amount < 1). | Same animated Object. |
| `walk(character, start=1, end=25, stride=32, arm_swing=24, bounce=0.025, steps=24, loop=True)` | Key an in-place cyclic R6 walk with alternating limbs, floor clearance, and optional bob. | Same Character/rig. |
| `idle(character, start=1, end=97, amount=2, steps=16, loop=True)` | Key a cyclic breathing, head drift, and relaxed arm idle. | Same Character/rig. |
| `talk(character, start=1, end=49, amount=12, beats=3)` | Key small presenting arm gestures and head nods; animate the mouth separately. | Same Character/rig. |
| `mouth_flap(character, samples, start=1, fps=None, strength=3.5, easing='linear')` | Key shape-mouth openness from increasing (seconds, openness_0_to_1) samples. | Same Character/mouth. |

## bkit.render

Still and animation write PNG files. Turntable rotates the subject around its base with fixed lighting; use the returned path list for delivery. Renderer helpers can change scene settings; use explicit engine, quality and resolution in scripts.

| Function and key arguments | Purpose | Returns / effects |
| --- | --- | --- |
| `quality(preset='good', scene=None)` | Apply a quality preset ('draft' \| 'fast' \| 'good' \| 'hero') to EEVEE and Cycles settings. | Scene. |
| `still(path, resolution=None, engine=None, quality=None, transparent=None, camera=None)` | Render the current frame to a PNG at `path`. resolution e.g. (960, 960); engine 'EEVEE' \| 'CYCLES' \| None (keep); quality 'draft' \| 'fast' \| 'good' \| 'hero' \| None (keep). | Dict {path, seconds}. |
| `animation(out_dir, orientation='vertical', engine='EEVEE', quality='fast', frames=None, prefix='frame_', resolution=None, percentage=100)` | Render an inclusive frame range as a numbered PNG sequence. | Dict {dir, frames, seconds_per_frame}. |
| `load_pixels(path)` | PNG -> float32 array (h, w, 4), rows bottom-up (Blender order), display-referred values. | NumPy float32 (height,width,4), rows bottom-up. |
| `save_pixels(px, path)` | float RGBA array (rows bottom-up) -> 8-bit PNG. | Output path. |
| `measure(path, crop=1.0)` | Exposure check of a rendered PNG. crop < 1 measures only the centre fraction (the subject). | Dict {mean,p5,p95,clip_white,clip_black,saturation}. |
| `contact_sheet(paths, out, cols=None, tile=None, labels=None, title=None, bg=(0.93, 0.92, 0.9), gap=8)` | Tile images into one PNG. paths: list of PNGs; cols: tiles per row (default ~square); tile: (w, h) per tile (default first image size, max 480 wide); labels: one string per tile (A-Z 0-9 and - . / : % ( ) + = _ ,); title: a line across the top. | Output path. |
| `turntable(subject, out_dir, angles=8, elevation=18.0, lens=70.0, resolution=(480, 480), sheet=True, engine=None, quality=None, margin=1.15)` | Spin the subject (not the camera, so the lighting stays put) and render `angles` stills plus a contact sheet out_dir/turntable.png. | PNG path list; contact-sheet path last when enabled. |
| `model_sheet(subject, path, tile=(480, 480), engine=None, quality='fast', title=None, wire=True)` | Render beauty views, silhouette, and optional wireframe into one labelled PNG. | Output path. |
| `outline(objs, thickness=None, color='#1E1E24', method='hull')` | Add a hull outline (remove before export) or render-time Freestyle lines. | Material, or None for Freestyle. |

## bkit.export

Reports inspect evaluated meshes against the mesh import budget: at most 20,000 triangles, one material, one UV set within 0..1. This does not certify Marketplace avatars. Strict FBX/OBJ rejects failed reports. GLB includes descendants and can include rigid bone-parented animation.

| Function and key arguments | Purpose | Returns / effects |
| --- | --- | --- |
| `report(objects, path=None)` | Inspect evaluated meshes for the Roblox mesh import budget and optional JSON report. | Report dict: ok + per-mesh budget/issues. |
| `glb(objects, path, animation=True)` | Export selected objects and descendants to a GLB, optionally including animation. | Written pathlib.Path. |
| `roblox(objects, path, format='FBX', strict=True, animation=False)` | Export FBX or OBJ with a mesh-budget report; strict mode rejects failing meshes. | Report dict; file + .report.json written. |
| `fbx(objects, path, strict=True, animation=False)` | Roblox FBX with report (Copy/embed textures, unit scaling, no leaf bones). | Report dict; file + .report.json written. |
| `obj(objects, path, strict=True)` | Roblox static OBJ with report and accompanying MTL/images. | Report dict; OBJ/MTL/textures + report written. |

## bkit.assets

Downloads use explicit registered asset IDs and cache entries. External packs require caller-supplied approved source and CC0 licence metadata; fetch/import is not an arbitrary-URL downloader.

| Function and key arguments | Purpose | Returns / effects |
| --- | --- | --- |
| `fetch(name, source='polyhaven', kind='hdri', resolution='1k', format=None, cache=None, channel=None)` | Fetch a registered asset ID and return the cached local file. | Cached pathlib.Path. |
| `unpack(archive, destination, max_bytes=1024 ** 3)` | Extract a ZIP after validating all members (no traversal, symlinks or zip bombs). | List of extracted pathlib.Path values. |
| `import_pack(path, source, license_url, height=5.0, name=None)` | Import an approved local CC0 model pack, preserve hierarchy, and normalize height/base origin. | Parent Empty object, preserving child hierarchy. |

## bkit.palettes



| Function and key arguments | Purpose | Returns / effects |
| --- | --- | --- |
| `get(name)` | Return the palette dict {colour_name: hex} called `name` (see PALETTES). | Dict {colour_name: #RRGGBB}. |
| `names()` | Names of all palettes. | Sorted palette-name list. |
| `colors(name)` | ['palette.colour', ...] specs for every colour in a palette, in order. | List of palette.colour specs in palette order. |

## bkit.compat

These are low-level version guards used by the other modules; prefer higher-level helpers when possible.

| Function and key arguments | Purpose | Returns / effects |
| --- | --- | --- |
| `engine_id(kind='EEVEE')` | Return the render-engine identifier for kind 'EEVEE', 'CYCLES' or 'WORKBENCH'. | Render-engine identifier string. |
| `set_engine(scene=None, kind='EEVEE', gpu=True)` | Switch the scene to 'EEVEE', 'CYCLES' or 'WORKBENCH'. | Chosen engine identifier. |
| `enable_gpu(scene=None)` | Point Cycles at the GPU. | GPU backend name, or CPU. |
| `smooth_by_angle(obj, angle=30.0)` | Smooth-shade a mesh object but keep edges sharper than `angle` degrees sharp. 4.1+: Mesh.shade_smooth + set_sharp_from_angle. | None; changes mesh shading. |
| `shade_smooth(obj)` | Smooth-shade every face (no sharp edges). | None; changes mesh shading. |
| `shade_flat(obj)` | Flat-shade every face (faceted low-poly look). | None; changes mesh shading. |
| `compositor(scene=None)` | Return the scene's compositor node tree, creating it if needed. 5.x: a CompositorNodeTree assigned to scene.compositing_node_group (with an Image output socket). 4.x: scene.use_nodes + scene.node_tree. | Compositor NodeTree. |
| `compositor_io(scene=None)` | Return (tree, render_layers_node, output_input_socket). | (tree, render_layers_node, output_input_socket). |
| `fcurves(id_data)` | All F-curves of an object's (or armature's) active action, on any version. 5.x actions are layered: curves live in a channelbag per slot; 4.x: action.fcurves. | List of active-action FCurve values. |
| `set_enum(owner, prop, *candidates)` | Set owner.prop to the first candidate value Blender accepts (enum names differ by version and OCIO config). | Accepted enum value, or None. |
| `socket(node, *names)` | First input socket of `node` matching any of `names` (Principled names changed in 4.0). | First matching input socket, or None. |
| `material_nodes(mat)` | Turn on nodes for a material (always on in 5.x) and return its node tree. | Material NodeTree. |
| `world_nodes(world)` | Same as material_nodes for a World. | World NodeTree. |
| `set_blend_transparent(mat, refraction=False)` | Make a material render transparency in EEVEE (blended, or ray-traced refraction for glass). | None; changes material settings. |

## bkit._util

Internal shared module; useful for bounds/colour/vector operations when building additional helpers.

| Function and key arguments | Purpose | Returns / effects |
| --- | --- | --- |
| `srgb_to_linear(c)` | Convert one sRGB channel to linear. | Linear float channel. |
| `srgb(spec)` | Parse a colour spec to sRGB floats (r, g, b) in 0-1. | sRGB (r,g,b) tuple. |
| `rgb(spec)` | Colour spec -> linear RGB tuple (what shader sockets want). | Linear (r,g,b) tuple. |
| `rgba(spec, alpha=1.0)` | Colour spec -> linear RGBA tuple. | Linear (r,g,b,a) tuple. |
| `mix(a, b, t)` | Blend two colour specs in sRGB space; returns sRGB floats usable as a spec. | sRGB tuple usable as a colour spec. |
| `shade(spec, factor)` | Darken (factor < 1) or lighten (factor > 1, towards white) a colour; returns sRGB floats. | sRGB tuple usable as a colour spec. |
| `link(obj, collection=None)` | Link an object into `collection` (default: the scene collection). | Same Object. |
| `as_list(objs)` | Normalize None, an Object, or an iterable into an Object list. | List of Objects. |
| `descendants(obj)` | obj plus all its children, recursively. | Root + recursive children list. |
| `mesh_objects(objs=None)` | Mesh objects among objs (and their children); default: all visible meshes in the scene. | Unique mesh Object list. |
| `bounds(objs=None, precise=False)` | World-space bounds; precise=True evaluates vertices for exact floor contact. | (world-space min Vector, max Vector). |
| `center_radius(objs=None)` | (centre Vector, bounding-sphere radius) of objs. | (center Vector, bounding-sphere radius). |
| `select(objs, active=None)` | Deselect everything, select objs, make `active` (default first) the active object. | None; updates active/selected Objects. |
| `look_at(obj, target)` | Rotate obj (camera/light) so its -Z axis points at target (a Vector or tuple). | None; changes object rotation. |
| `spherical(center, radius, azimuth, elevation)` | Point at `radius` from center. azimuth 0 = in front (-Y, Blender Front view), 90 = right (+X); elevation in degrees above the horizon. | World-space Vector. |


## Verification and remaining limits

Verified in real headless Blender 5.3.0, not a bpy mock:

- Scene reset, colour looks, gradient/sky/HDRI worlds, transparent Cycles shadow catcher, depth of
  field, Blender 5 compositor I/O, soft bevels/weighted normals and all procedural prop constructors.
- Ten requested material balls in EEVEE and Cycles; matte background shader also exercised.
  Five lighting rigs on one fixed subject in both engines. Material/lighting PNGs opened at full size.
- Four character poses with actual shoulder-surface contact and head/arm BVH collision guards.
  All 25default gait frames checked using evaluated vertices; eight phases rendered to a contact sheet.
  Slotted F-curves, loop boundaries, cycles modifiers, idle/talk, mouth-flap timestamps and scale,
  squash/stretch, BACK anticipation/overshoot, orbit/dolly/push-in and RGBA image-face node/UV setup.
- Off-centre targets, square/portrait/landscape camera fits and switching orthographic/perspective.
  Technical model sheet front/side/three-quarter/back/top/silhouette/wire, four-view turntable,
  hull and Freestyle outlines, real 1080×1920 and 1920×1080 two-frame PNG sequences.
- GLB static export/import; animated GLB parsed for channels and re-imported for active curves.
  FBX and OBJ exported and re-imported, one-material UV mesh checks, invalid UV rejection,
  excessive triangles and multiple UV sets rejected. Independent atlases and generated images
  without image_path export with real texture files, not an empty MTL or missing FBX image.
- Real downloads/cache integrity: Poly Haven studio_small_08 HDRI, brick_wall_001 Diffuse,
  wooden_crate_01 BLEND and its four dependencies; ambientCG Wood049 1K-JPG ZIP. SHA256 sidecars,
  provider checksums where supplied, dependency repair, traversal and existing-symlink rejection.
- Real CC0 pack import and 3-stud normalization: KayKit Furniture Bits armchair in glTF and OBJ,
  plus Poly Haven wooden_crate_01 in BLEND. Materials/textures rendered and opened, all bases at 0.

Sources: [Poly Haven licence](https://polyhaven.com/license),
[Poly Haven API](https://github.com/Poly-Haven/Public-API),
[ambientCG licence](https://docs.ambientcg.com/license/),
[KayKit Furniture Bits CC0 licence](https://github.com/KayKit-Game-Assets/KayKit-Furniture-Bits-1.0/blob/main/addons/kaykit_furniture_bits/Assets/LICENSE.txt).
Downloaded assets and per-file licence logs stay with the external gallery/cache, outside this repository.

### Evaluated default helper budgets

Measured after modifiers, seed 1, base at 0 for props. height is nominal for a tree family: actual
bounds differ across round/pine/tall silhouettes. Radius/height ratios remain deliberate and seeded.

| Helper | Triangles | Actual dimensions (x,y,z) |
| --- | ---: | --- |
| tree_round | 264 | 3.5448, 2.5057, 3.6281 |
| tree_pine | 108 | 2.2989, 2.3416, 3.8999 |
| tree_tall | 104 | 1.5587, 1.5969, 4.8199 |
| rock | 66 | 0.9945, 1.0219, 0.5222 |
| cloud | 2200 | 3.1913, 1.3229, 1.1079 |
| bush | 320 | 1.1905, 1.1912, 1.0484 |
| grass | 84 | 0.537, 0.4835, 0.5634 |
| crate | 1836 | 1.026, 1.026, 1.0 |
| barrel | 1544 | 0.9264, 0.9264, 1.2 |
| coin | 960 | 1.0, 0.14, 1.0 |
| duck | 6568 | 0.88, 1.2301, 1.06 |
| wall | 756 | 6.04, 1.06, 3.54 |
| tower | 1550 | 3.752, 3.752, 8.08 |
| gate | 584 | 3.0, 1.26, 3.5 |
| flag | 620 | 1.6821, 0.24, 3.2 |
| house | 1408 | 3.6, 3.6, 4.1493 |
| roof | 172 | 3.5, 3.5, 1.6574 |
| capsule | 528 | 0.6, 0.6, 1.0 |
| torus | 768 | 1.24, 1.24, 0.24 |

### Explicitly untested

- Blender versions other than 5.3.0, other operating systems/GPUs, CUDA/HIP/Metal/oneAPI fallback
  rendering, and CPU image rendering. Engine/device selection itself is asserted where applicable.
- Actual Roblox Studio import, Open Cloud upload, Roblox animation playback, Marketplace avatar
  certification, skinning/retargeting and bone influence budgets. No Studio processes were touched.
- FBX pack normalization from a third-party rigged pack (the FBX operator round trip is tested),
  unexercised asset IDs/resolutions/formats and bulk Kenney/Quaternius pack imports.
- Long films, audio/video encoding, long camera-move playback, facial lip sync quality, visually
  reviewed idle/talk clips, arbitrary custom poses and collisions outside the four guarded poses.
  These helpers have curve/geometry assertions; this is not a claim of cinematic motion review.
- Cycles outlines, nondefault light types in beauty shots (POINT/SPOT constructors were exercised),
  draft and Cycles hero image quality. Quality setting assignment is tested; rendered presets were
  EEVEE fast/good/hero and Cycles fast/good.
- Every optional/invalid parameter combination, arbitrary custom palettes, enormous third-party
  archives and every possible malicious archive structure. The tested extraction checks are listed above.

Known artistic limits: the face is deliberately minimal; rigid limbs slide without knee/foot IK;
clouds show overlapping puffs; basic buildings repeat simple masses. Hull outlines can produce
intersection marks; use Freestyle or omit the outline for a clean product shot. Fabric is smooth
rather than woven. Export color atlases intentionally discard procedural PBR details.

## Eight complete executed scripts

These are the same files used for the calibration renders. Run each through blender-pc; no local
Blender is needed. The two engine galleries also accept `-- CYCLES` after launcher options.

### 01_materials.py

```sh
blender-pc run blender/examples/01_materials.py --out output/01_materials --timeout 600
```

```python
"""Ten identical test balls, same studio. blender-pc run this_file --out gallery."""
import json
from pathlib import Path
import sys
import bkit as b

out = Path(sys.argv[sys.argv.index('--')+1])
args = sys.argv[sys.argv.index('--')+3:]
engine = args[0] if args else 'EEVEE'
records, paths = {}, []
for kind in list(b.materials.KINDS)[:10]:
    b.scene.new_scene(engine=engine)
    mat = b.materials.make(kind, '#D68C55' if kind not in ('chrome','metal_brushed','glass') else '#D6DEE6')
    ball = b.modelling.sphere(1, segments=64, rings=32, location=(0,0,1.32), mat=mat)
    base = b.modelling.cylinder(1.05,.28,location=(0,0,.14),mat='product.graphite')
    subject = [ball,base]
    b.scene.add_camera(subject,azimuth=25,elevation=18,margin=1.3)
    b.scene.cyclorama(subject=subject,color='#BCB6AB')
    b.lighting.rig('studio_soft',subject)
    path = out / (kind+'.png')
    records[kind] = b.render.still(str(path),quality='good')
    records[kind].pop('path')
    records[kind].update(b.render.measure(str(path),crop=.65))
    paths.append(str(path))
b.render.contact_sheet(paths,str(out/'materials.png'),cols=5,tile=(320,320),labels=list(records),title=engine+' MATERIALS')
(out/'metrics.json').write_text(json.dumps(records,indent=2))
b.finish()
```

### 02_lighting.py

```sh
blender-pc run blender/examples/02_lighting.py --out output/02_lighting --timeout 600
```

```python
"""Every rig on exactly the same toy subject; optional -- CYCLES."""
import json
from pathlib import Path
import sys
import bkit as b
out=Path(sys.argv[sys.argv.index('--')+1])
args=sys.argv[sys.argv.index('--')+3:]
engine=args[0] if args else 'EEVEE'
records,paths={},[]
for name in b.lighting.RIGS:
    if len(args)>1 and name!=args[1]:
        continue
    b.scene.new_scene(engine=engine)
    duck=b.modelling.rubber_duck(2,location=(-.45,-.25,.5))
    box=b.modelling.rounded_box((2.8,2.4,.5),location=(0,0,.25),mat='toybox.blue')
    ball=b.modelling.sphere(.43,location=(1,.55,.93),mat=b.materials.chrome())
    subject=[duck,box,ball]
    b.scene.add_camera(subject,azimuth=32,elevation=23,margin=1.28)
    b.scene.cyclorama(subject=subject,color='#BCB6AB')
    lights=b.lighting.rig(name,subject)
    path=out/(name+'.png')
    records[name]=b.render.still(str(path),quality='good')
    records[name].pop('path')
    records[name].update(b.render.measure(str(path),crop=.65))
    records[name]['watts']={k:round(v.data.energy,2) for k,v in lights.items()}
    paths.append(str(path))
b.render.contact_sheet(paths,str(out/'lighting.png'),cols=5,tile=(320,320),labels=list(records),title=engine+' LIGHTING')
(out/'metrics.json').write_text(json.dumps(records,indent=2))
b.finish()
```

### 03_helpers.py

```sh
blender-pc run blender/examples/03_helpers.py --out output/03_helpers --timeout 600
```

```python
"""Each procedural helper alone: see the silhouette and joins."""
from pathlib import Path
import sys
import bkit as b
out=Path(sys.argv[sys.argv.index('--')+1])
m=b.modelling
factories={'tree_round':lambda:m.tree(), 'tree_pine':lambda:m.tree('pine'),
           'tree_tall':lambda:m.tree('tall'), 'rock':m.rock,
           'cloud':lambda:m.cloud(location=(0,0,0)), 'bush':lambda:m.bush(flowers=5),
           'grass_tuft':m.grass_tuft,'crate':m.crate,'barrel':m.barrel,
           'coin':m.coin,'rubber_duck':m.rubber_duck, 'wall':m.wall,
           'tower':lambda:m.tower(flag='fortress.banner'), 'gate':m.gate,
           'flag':m.flag,'house':m.house,'roof_gable':m.roof_gable,
           'lathe':lambda:m.lathe([(0,0),(.6,0),(.7,.1),(.5,.7),(.7,1),(0,1)],mat='toybox.blue'),
           'extrude':lambda:m.extrude(m.arch_profile(),mat='toybox.red')}
paths=[]
for name,make in factories.items():
    args=sys.argv[sys.argv.index('--')+3:]
    if args and name not in args:
        continue
    b.scene.new_scene()
    obj=make()
    b.scene.add_camera(obj,azimuth=30,elevation=22,margin=1.3)
    b.scene.cyclorama(subject=obj,color='#BCB6AB')
    b.lighting.rig('studio_soft',obj)
    path=str(out/(name+'.png'))
    b.render.still(path,quality='good')
    paths.append(path)
b.render.contact_sheet(paths,str(out/'helpers.png'),cols=5,tile=(300,300),labels=list(factories),title='PROCEDURAL HELPERS')
b.finish()
```

### 04_poses.py

```sh
blender-pc run blender/examples/04_poses.py --out output/04_poses --timeout 600
```

```python
"""A bone-parented figure in all four named poses."""
from pathlib import Path
import sys
import bkit as b
out=Path(sys.argv[sys.argv.index('--')+1])
paths=[]
for pose in b.character.POSES:
    b.scene.new_scene()
    hero=b.character.blocky_character(shirt='toybox.blue',pants='product.graphite')
    hero.pose(pose)
    b.scene.add_camera(hero.rig,azimuth=18,elevation=10,margin=1.3)
    b.scene.cyclorama(subject=hero.rig,color='#BCB6AB')
    b.lighting.rig('studio_soft',hero.rig)
    path=str(out/(pose+'.png'))
    b.render.still(path,quality='good')
    paths.append(path)
b.render.contact_sheet(paths,str(out/'poses.png'),cols=4,tile=(360,360),labels=list(b.character.POSES),title='RIG POSES')
b.finish()
```

### 05_walk.py

```sh
blender-pc run blender/examples/05_walk.py --out output/05_walk --timeout 600
```

```python
"""Eight walk phases, fixed camera and lighting; exports the animated GLB too."""
from pathlib import Path
import sys
import bkit as b
import bpy
out=Path(sys.argv[sys.argv.index('--')+1])
b.scene.new_scene(resolution=(640,640))
hero=b.character.blocky_character()
b.animation.walk(hero,start=1,end=25)
# A hidden proxy reserves the full motion envelope in a fixed frame.
proxy=b.modelling.rounded_box((4.5,3.5,5.3),location=(0,0,2.6))
cam=b.scene.add_camera(proxy,azimuth=30,elevation=10,margin=1.16)
bpy.data.objects.remove(proxy,do_unlink=True)
b.scene.cyclorama(subject=hero.rig,color='#BCB6AB')
b.lighting.rig('studio_soft',hero.rig)
paths=[]
for frame in range(1,25,3):
    bpy.context.scene.frame_set(frame)
    path=str(out/f'walk_{frame:02d}.png')
    b.render.still(path,quality='good')
    paths.append(path)
b.render.contact_sheet(paths,str(out/'walk.png'),cols=4,tile=(360,360),labels=[str(f) for f in range(1,25,3)],title='WALK - 24 FRAME CYCLE')
b.export.glb(hero.rig,str(out/'walk.glb'))
b.finish()
```

### 06_cannon.py

```sh
blender-pc run blender/examples/06_cannon.py --out output/06_cannon --timeout 600
```

```python
"""Hero product still, assembled only from kit functions."""
from pathlib import Path
import sys
import bkit as b
out=Path(sys.argv[sys.argv.index('--')+1])
b.scene.new_scene()
m=b.modelling
red=b.materials.toy_plastic('toybox.red')
blue=b.materials.toy_plastic('#284D59')
gold=b.materials.metal_brushed('#DDA849')
cream=b.materials.toy_plastic('toybox.cream')
parts=[]
parts.append(m.rounded_box((1.75,2.45,.45),location=(0,.1,.78),mat=blue))
for x in (-.72,.72):
    parts.append(m.extrude([(-1.2,0),(1.2,0),(.8,.9),(-.5,1.2),(-1.1,.9)],depth=.25,
                           location=(x,.12,.85),rotation=(0,0,90),mat=blue))
for x in (-1.15,1.15):
    parts.append(m.cylinder(.76,.26,48,location=(x,.35,.76),rotation=(0,90,0),mat=cream))
    parts.append(m.cylinder(.57,.29,48,location=(x,.35,.76),rotation=(0,90,0),mat=red))
    parts.append(m.cylinder(.21,.34,32,location=(x,.35,.76),rotation=(0,90,0),mat=gold))
profile=[(0,-1.05),(.36,-1.05),(.56,-.85),(.59,-.6),(.48,1.45),(.6,1.48),
         (.61,1.66),(.56,1.75),(.39,1.75),(.36,1.59),(.32,.6),(0,.6)]
parts.append(m.lathe(profile,64,location=(0,0,1.9),rotation=(75,0,0),mat=red))
parts.append(m.sphere(.2,location=(0,1.17,1.65),mat=gold))
for y,z in ((-.1,1.92),(.64,1.73)):
    parts.append(m.torus(.53,.055,location=(0,y,z),rotation=(75,0,0),mat=gold))
for x,y in ((1.7,-1.2),(2.25,-.7),(1.95,-.2)):
    parts.append(m.sphere(.28,location=(x,y,.28),mat=b.materials.metal_brushed('#505C66')))
subject=m.join(parts,'ToyCannon')
b.scene.add_camera(subject,azimuth=34,elevation=18,margin=1.28,lens=80)
b.scene.cyclorama(subject=subject,color='#B8B0A2')
b.lighting.rig('studio_soft',subject)
b.render.still(str(out/'cannon.png'),quality='hero')
b.export.glb(subject,str(out/'cannon.glb'),animation=False)
b.finish()
```

### 07_fortress.py

```sh
blender-pc run blender/examples/07_fortress.py --out output/07_fortress --timeout 600
```

```python
"""Toy block fortress with rubber ducks, on a round wooden table."""
from pathlib import Path
import sys
import math
import bkit as b
out=Path(sys.argv[sys.argv.index('--')+1])
b.scene.new_scene()
m=b.modelling
parts=[]
parts.append(m.cylinder(6.2,.55,96,location=(0,0,1.1),mat=b.materials.painted_wood('#B9956C')))
parts.append(m.cylinder(5.9,.12,96,location=(0,0,.79),mat='fortress.wood'))
for angle in (30,150,270):
    a=math.radians(angle)
    parts.append(m.cylinder(.42,.85,24,location=(3.8*math.cos(a),3.8*math.sin(a),.42),mat='fortress.wood'))
z=1.375
for x in (-3.1,3.1):
    parts.append(m.tower(.78,2.5,location=(x,1.55,z),flag='fortress.banner'))
parts.append(m.wall(6.2,1.8,.65,location=(0,1.55,z)))
for x in (-3.1,3.1):
    parts.append(m.wall(3.3,1.6,.65,location=(x,0,z),rotation=90))
for x in (-2.15,2.15):
    parts.append(m.wall(1.9,1.6,.65,location=(x,-1.65,z)))
parts.append(m.gate(1.9,2.3,location=(0,-1.65,z)))
parts.append(m.house(2.7,2.1,1.8,location=(0,.25,z),door='fortress.banner'))
for size,loc,facing in [(1.2,(-2,-3.5,z),-20),(.9,(.1,-3.7,z),15),(1.05,(3.7,-2.6,z),-35),
                        (.85,(-1.6,0,z),15),(.75,(2,.15,z),-20)]:
    parts.append(m.rubber_duck(size,loc,facing=facing))
for x,y in ((-4.5,.4),(4.45,.2)):
    parts.append(m.bush(.9,location=(x,y,z),flowers=3))
subject=parts
b.scene.add_camera(subject,azimuth=24,elevation=27,lens=75,margin=1.25)
b.scene.cyclorama(subject=subject,color='#B7B0A1')
b.lighting.rig('toy_bright',subject,strength=.9)
b.render.still(str(out/'fortress.png'),quality='hero')
b.finish()
```

### 08_delivery.py

```sh
blender-pc run blender/examples/08_delivery.py --out output/08_delivery --timeout 600
```

```python
"""Model sheet, turntable, outlines, real full-HD PNG sequences and Roblox export reports."""
from pathlib import Path
import sys
import bkit as b
out=Path(sys.argv[sys.argv.index('--')+1])
b.scene.new_scene()
obj=b.modelling.rubber_duck(2)
b.scene.add_camera(obj,azimuth=30,elevation=20,margin=1.3)
b.scene.cyclorama(subject=obj,color='#BCB6AB')
b.lighting.rig('studio_soft',obj)
b.render.model_sheet(obj,str(out/'model_sheet.png'),tile=(320,320),title='DUCK - FORM AND TOPOLOGY')
b.render.turntable(obj,str(out/'turntable'),angles=4,resolution=(320,320),quality='fast')
b.render.outline(obj,method='hull',thickness=.018)
b.render.still(str(out/'outline.png'),resolution=(960,960),quality='good')
# Outline is a render effect; remove before export.
obj.modifiers.remove(obj.modifiers['bkit_outline'])
obj=b.materials.atlas_from_materials(obj,image_path=str(out/'duck_atlas.png'))
b.export.fbx(obj,str(out/'duck.fbx'))
b.export.obj(obj,str(out/'duck.obj'))
b.animation.key_rotation(obj,1,(0,0,0))
b.animation.key_rotation(obj,2,(0,0,5))
for orientation in ('vertical','horizontal'):
    # Refit at the actual aspect ratio before rendering.
    import bpy
    bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y=b.render.RESOLUTIONS[orientation]
    b.scene.aim(bpy.context.scene.camera,obj,azimuth=30,elevation=20,margin=1.3)
    b.render.animation(str(out/orientation),orientation=orientation,frames=(1,2),quality='fast')
b.finish()
```

