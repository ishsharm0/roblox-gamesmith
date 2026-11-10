# Procedural models with designed form

Use the game's art direction and actual player camera. Procedural modeling should produce recognizable, intentionally constructed forms, not an assortment of Parts with labels. Read assets-pipeline and performance for import/runtime constraints; verify unfamiliar APIs with rbxdocs. No new API is required by this guide.

## Asset brief and pass order

For each hero or repeated asset, record function, style references, scale against the avatar, silhouette landmarks, proportion ratios, material regions, attachment points, moving pivots and collision behavior. Specify what must read from player height and on a phone. Group dimensions in one config and derive repeated offsets.

1. Block out the primary masses and negative spaces; inspect front/side/three-quarter silhouettes at the intended camera. Correct proportions before surface detail. A thick cylinder with random cubes is not automatically a believable engine, tree or building.
2. Choose construction that suits the form. Parts/wedges are useful for deliberately stylized assemblies; use terrain for landscape volume and a vetted mesh when the silhouette genuinely needs continuous surfaces. Build supports, joints, openings and thickness visibly where the player can see them. Do not replace a visible opening with black paint if the camera exposes the cheat.
3. Use consistent edge treatment and intentional material boundaries. Avoid stretched textures, random reflectance, z-fighting, tiny high-frequency trim and floating contacts. Design repeated assets as a family, varying proportions/pose/details within constraints instead of uniformly randomizing every dimension.
4. Establish pivots and contact clearances before animation. Check the full motion range, not just rest pose. Moving doors need actual clearance; feet should ground, handles should attach, and collision should match the player's expectations.
5. Separate render detail from simple collision geometry. Decorative parts should not create invisible snags or unnecessary physics/query work. Choose Anchored, collision/query/touch settings and ownership deliberately according to existing architecture; don't disable interaction needed by gameplay.

## Concrete construction exercise

For a stylized market stall: primary silhouette is roof canopy over a counter, supported by posts with believable roof attachment; secondary forms are fabric edge, counter thickness, shelves and braces; tertiary forms are a few readable goods/sign details. Keep a clear walkable opening and player-height view of the interaction. Test rain/shadow/lighting shape and camera clearance. A flat roof floating above four poles with randomly scattered crates fails the construction brief. This recipe can be built with Parts without claiming a new model was visually validated.

## Visual and runtime acceptance

Capture neutral-material front/side/three-quarter views, silhouette, final lighting/player-height view, phone view and articulation extremes. A model should read without its label. Fix missing volume, bad proportions and broken joins before bloom or particles. The visual sheet is evidence; a script compiling or number of Parts is not aesthetic validation.

Measure part/mesh/material/texture budgets in the real scene, with repeated instances, streaming and target-device performance. No universal triangle count guarantees quality or speed. Preserve silhouettes when reducing detail; use simpler distant variants when appropriate. Do not hide a performance problem by replacing the hero with a vague primitive. Use pooling/reuse and existing asset tooling where it genuinely helps.

Before acceptance: verify no unintended clipping, collision snags, unanchored decoration or unexpected scripts from imported assets; inspect normal and reduced-motion presentation; check real interaction from touch and desktop cameras. Preserve source geometry/config, asset license and regeneration instructions. Never upload, spend or publish to demonstrate a documentation change. Blender and generated asset tools remain subject to the local skill's authorization rules.

Runtime audit must include every BasePart class, including SpawnLocation and hidden collision/support parts—not just objects made through the prop factory. Explicitly choose anchored versus simulated behavior for each; never assume an instance default matches the intended static construction.

## The Build kit (in every new project: `src/shared/Build.luau`)

Raw sharp boxes are what make generated builds look cheap. `Build` gives rounded-corner slabs
(`roundedBlock`), capsules (`pill`), upright cylinders, `taper`ed trunks/towers/posts, `arch`es, gable
`roof`s with real overhang, seeded organic `blob`s for foliage/clouds/rocks, ring placement (`around`)
and one invisible `collider` per walkable thing. Decorative parts default to no collision/query/touch.

`scenarios/build-examples.luau` builds seven worked assets on a plate in the sky (tree, market stall,
lamp post, bench, stone gate, cloud, rock): `studio luau scenarios/build-examples.luau`, then
`studio shot --pos 14,214,34 --look 14,204,0` and `--pos 52,212,30 --look 52,203,0`. Read one before building a new asset;
each is 3-6 masses at deliberate ratios, seated into each other, with a small palette. Delete
`Workspace.BuildExamples` afterwards. Tested in Studio 2026-11-09 (140 parts; roof orientation fixed after capture).
