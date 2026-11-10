# Models that look designed

Generated builds fail the same way: sharp grey boxes, parts floating near each other, one flat colour,
a label doing the job the shape should. A model passes when a stranger can name it from its silhouette
at the player's camera, on a phone, with no label.

## Order of work

1. **Brief, three lines.** What it is for, how big it is next to a 5-stud avatar, and the two or three
   features that make it recognisable (a stall is a striped canopy over a counter; a lamp post is a
   tall thin pole with a hanging lantern).
2. **Primary masses first.** Three to six big shapes at deliberate ratios (a tree: trunk one third,
   crown two thirds, crown twice as wide as it is tall is a different tree). Look at the front, side
   and three-quarter silhouette before adding anything. If it doesn't read now, detail won't fix it.
3. **Seat parts into each other.** Every part overlaps or touches its neighbour by 0.1-0.3 studs.
   Posts go into the ground and into the roof. Nothing floats, nothing z-fights (offset coplanar faces
   by 0.02).
4. **Soften.** Rounded slabs, tapered posts and blobs from the Build kit below; raw `Block` parts only
   for things that are truly boxes. Chunky reads better than thin: nothing thinner than 0.4 studs.
5. **Secondary, then tertiary.** Thickness, braces, trims, an awning edge; then a few readable props.
   Stop at three levels. Small high-frequency detail shimmers on phones.
6. **Three or four colours per asset** from the game's palette: one dominant, one secondary, one
   accent, with materials chosen per region (wood, fabric, metal), not per part.
7. **Families, not random.** Repeated assets vary in a few set ways (three crown shapes, two heights,
   a seeded lean), never by uniformly randomising every dimension.
8. **Moving parts.** Set the pivot and check the whole range of motion for clipping, not only the
   rest pose.
9. **Collision is separate.** Decoration has CanCollide, CanQuery and CanTouch off; one simple
   invisible collider per walkable thing. Everything static is Anchored, including SpawnLocations and
   hidden supports: check every BasePart, not only the ones your factory made.

A flat roof floating over four poles with crates scattered around fails steps 2, 3 and 7.

## Accept it from captures

`studio shot` the asset from the front, the three-quarter and the player's height in the game's
lighting, plus the phone view. Fix volume, proportion and joins before bloom or particles. Then check
it in the real scene: part count with all its instances, streaming, and frame time on the device
simulator. Keep the builder code and any asset licence with the project. Uploading, spending and
publishing are never part of proving a model.

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
