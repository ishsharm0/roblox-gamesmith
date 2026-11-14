# Visual craft: what makes 3D, motion and UI look expensive and feel alive

Researched November 2026. [verified: URL] was read at the source; [memory] is a working default to
check by eye. Before any art, UI or video graphics, write a one-page style bible with section 5's
procedure (three keywords, palette with one sacred colour, shape rule, lighting recipe, motion rule,
one signature motif that appears in world, UI and video) and hold every asset to it.

## 0. Why our output reads "generic / cheap / needs creativity" (diagnosis, [memory])

1. Every element is the same size class: no big/medium/small hierarchy, so the eye has nowhere to rest and nowhere to land.
2. Colour is chosen per object, not per frame: saturated everything, no value plan, no dominant hue, no colour script.
3. Light is a neutral studio light on every scene: no time of day, no warm/cool split, no atmosphere, no depth planes.
4. Motion is uniform: one easing (usually Quad/Back), everything moves at once, nothing anticipates, nothing settles, nothing idles.
5. UI is the default kit shape (rounded rectangle, flat fill, centred modal): competent but has no motif, so it could belong to any game.
6. No signature: nothing a player could draw from memory (Splatoon's ink, Persona's red ransom-note, Balatro's wobble, Monument Valley's isometric pastel).
The cure is not "more effects": it is a written style bible (section 5) that fixes one dominant hue, one shape motif, one material, one light, one motion personality, and applies them to every asset, screen and video.

---------------------------------------------------------------------

## 1. STYLISED 3D THAT LOOKS EXPENSIVE

### 1.1 Shape language

- Big/medium/small: split every design into shapes of three clearly different sizes so that no two shapes compete; each tier must be clearly different from the next. The same split is often called 70/30 or 80/20. [verified: https://mayabeginner.readthedocs.io/en/latest/Design/L3_DesignPrinicplesPrimer.html (search summary)]
- Concentrate detail in small clusters at focal spots, next to big areas with little detail ("rest areas"); the rule nests (small shapes inside big shapes follow it too). [verified: same source + https://coda.io/@hankyu/character-design/research-brainstorming-design-concepts-3 (search summary)]
- Group objects in threes with varied big/medium/small arrangement, then overlap other elements loosely so the grouping is not obvious. [verified: https://steveyang.readthedocs.io/Modeling/123/ (search summary)]
- Working numbers [memory]: tier sizes about 1 : 1/3 : 1/9 (each tier ~3x smaller than the one above). Area budget per asset: 60-70% rest (large, plain, low-frequency), 20-30% medium (frames, bands, caps), <=10% small (studs, rivets, flowers) and that 10% sits in 1-2 clusters, near the top or the "face" of the object, never spread evenly.
- Shape psychology [memory]: circle = friendly/safe/collectable; square = stable/structure/home; triangle = danger/speed/enemy. Assign per role and keep it: player, pickups and NPC friends round; buildings and platforms square with soft corners; hazards and enemies with points.
- Straight against curve [memory]: each silhouette should alternate straight runs with curves (a straight wall under a bulging roof, a curved belly over straight legs). A WoW-style diorama breakdown frames its shape language as balancing curved and sharp lines. [verified: https://80.lv/articles/004adk-crafting-a-wow-inspired-diorama-part-1 (search summary)]
- Silhouette [memory]: fill black, view at 64 px: the object must be nameable, have 3+ distinct bumps/notches, have no tangents (edges that just touch), and have at least one hole of negative space for anything larger than a person (arch, window, gap between legs).
- Exaggeration [memory]: push the defining proportion 20-50% beyond real. Toy logic: heads 1.3-1.6x (earlier file), hands and feet 1.3-1.5x, doors 0.8x height but 1.2x width, handles/knobs/wheels 1.5x, thin parts (poles, rails, legs) >= 1.5x real thickness. Make the top or the bottom deliberately heavier: wider tops read cheeky (mushroom, Toad), wider bottoms read sturdy (castle, Goomba).
- Hand-made "wonky" offsets [memory]: rotate each repeated piece 1-4 deg (random sign), scale-jitter +-3-6%, position-jitter 1-3% of its size, lean verticals 2-5 deg as a group; taper boxes 5-10% (top narrower). Keep the ground contact flat and the main silhouette readable: wonky details, planted base.
- A Blender 2D-look artist puts a Lattice on the whole scene so perspective is slightly off and feels hand-made, and makes the scene narrower and more vertical with it. [verified: https://80.lv/articles/shapes-and-colors-creating-scenes-with-a-2d-effect-in-blender/]
- Chamfer by material [memory] (as % of smallest dimension; earlier kit default 10%): hard metal 2-4% sharp, painted wood 5-8%, stone 8-12% rounded and irregular, toy plastic / vinyl 12-25% ("inflated"). The rounder the bevel, the softer and younger the read.
- Inflatable / vinyl reads come from no sharp edges at all and soft volumes; Fall Guys' look came from a lead artist and a UI artist who collect vinyl toys and like simple shapes, aimed at padded vinyl or plastic toy blocks, objects that look inflatable like crash mats or giant rubber hammers, and big primary colours of TV knockout shows. [verified: https://m.tonight.co.za/technology/gaming/fall-guys-developers-talk-crunch-level-design-and-lore-c2c129f6-ddaa-43cf-81c3-bed3974e2ed6 and https://www.pressreader.com/australia/edge/20200910/283553748016109 (search summaries)]
- Diorama scale logic: Link's Awakening (2019) imagined Link as a small figurine in a miniature world and balanced rich detail against that scale, avoiding excess detail. [verified: https://www.zeldadungeon.net/links-awakening-graphics-director-sheds-light-on-the-remakes-diorama-inspired-visuals/] So: detail density is set by the "real" size of the toy, not the world it depicts: a toy castle has toy-sized bricks (fewer, bigger), not real-sized ones.

Rules (shape):
- S1 Every asset: 1 big mass, 2-4 medium parts, 1-2 clusters of small parts. Measure area: rest >= 60%.
- S2 Silhouette test at 64 px black fill: nameable, >= 3 bumps, no tangents.
- S3 Role shapes: friendly = round (corner radius >= 25% of size), structure = square with 8-12% bevel, danger = triangles/points.
- S4 Jitter repeated pieces: rot +-1-4 deg, scale +-3-6%, pos +-1-3%; never jitter the footprint.
- S5 Push one proportion per asset 20-50% past real; thin parts >= 1.5x.
- S6 Pick one shape-softness level per project and apply it to every asset (all 4% chamfers or all 20%), never mixed.

### 1.2 Colour: value first, then hue, then saturation budget

- Value plan [memory]: design in greyscale first. 3-4 value groups per frame (light, mid-light, mid-dark, dark), one of them dominant (>= 50% of frame). The subject sits in the group that contrasts most with its surroundings; aim for >= 30 points of L* (CIELAB) between subject and its immediate background, and keep the strongest light/dark contrast of the whole frame at the focal point.
- Colour shares: dominant 60%, secondary 30%, accent 10%. [verified: https://uxplanet.org/the-60-30-10-rule-a-simple-way-to-creating-catchy-user-interfaces-e9e2cf957213 (search summary)]
- Saturation budget [memory]: only 10-15% of the frame at full chroma, and that is the focal point (player, reward, interactive). Background and large surfaces at 30-60% of the subject's chroma. Each depth plane further away: +10-15% blend toward the sky/fog colour and -10% contrast (aerial perspective).
- Restraint as identity: Persona 5 used no sub-colours other than in HP/MP elements in order to keep its red distinctive, and used central lines to draw the gaze [verified: https://mechanicsofmagic.com/2022/04/23/visual-design-of-games-persona-5/ (search summary of Atlus CEDEC 2017 notes)]; its theme colours are red, black and white, and the selected item gets a splash of blue that contrasts with them. [verified: same URL]
- Warm light / cool shadow is the safe default for a lighting scheme that has to work everywhere; shadows are where you are free to vary hue. [verified: https://ben304.blogspot.com/2021/07/ and https://www.proko.com/course-lesson/light-vs-shadow-painting-techniques (search summaries)] A warm key against a cool background isolates a character. [verified: https://www.indepthcine.com/videos/colour-palette (search summary)]
- Hue-shifted ramps (stop using plain darker/lighter of one hue) [memory]: from a base colour, shadow = hue rotated 15-30 deg toward blue/violet, saturation +10-20%, value -25-35%; highlight = hue rotated 10-20 deg toward yellow, saturation -10-20%, value +15-20%. Example red: highlight #FF9A66, base #E8503F, shadow #9C2E55. Example green: highlight #D9F26B, base #67C23A, shadow #1F7A5C. Never shade toward black or grey.
- Neutrals are tinted [memory]: no pure greys; tint every "grey" 5-10% toward the scene's ambient hue (cool scene #8C95A8 not #909090; warm scene #A39A8C).
- Pixar practice: colour scripts are small sequential images of each scene's palette that guide lighting, environment and character artists [verified: https://www.slashfilm.com/cool-stuff-lou-romanos-color-script-for-pixars-up (search summary)]; a Toy Story lighting supervisor desaturated the lighting of a prison sequence to make it bleak. [verified: https://digital.copcomm.com/i/14320/19 (search summary)]
- Monument Valley printed every screen of the game and pasted them on a wall to see the game as a colour script, changing palettes from there; colour was applied directly through shaders rather than a lighting system; each level has a new palette. [verified: https://www.creativebloq.com/computer-arts/making-monument-valley-71412213 and https://killscreen.com/monument-valley-elegance (search summaries)] Isometric art uses about three tones per object, one per visible face. [verified: same search] Rule [memory]: top face 100% value, left face ~80%, right face ~60% of the colour's value, hue-shifted per the ramp above.
- Gradient ramps on surfaces [memory]: every large surface gets a gentle gradient (vertical: 5-12% lighter at top; or toward the light), because flat fills read as placeholder. Earlier kit already does vertex-colour bottom x0.7; extend to: walls lighter toward the top, ground darker toward the frame edges, water darker with depth.

Colour script for a game or a video [memory]: one row of thumbnails, one per level/scene. Give each a dominant hue family and a temperature; adjacent entries must differ in temperature or value key; the climax gets the highest saturation and contrast; rest beats are desaturated and lighter. Write it as a table before building anything:
| Beat | Dominant hue | Key (light/mid/dark) | Temperature | Accent | Max saturation |
| Tutorial | sky blue | light | warm sun | yellow | 70% |
| Mid levels | green | mid | neutral | red | 80% |
| Boss/climax | violet | dark | cold + warm practicals | orange | 100% |
| Reward/ending | gold | light | warm | white | 85% |

Rules (colour):
- C1 Greyscale check: the frame must read with colour removed; subject vs neighbour >= 30 L*.
- C2 60/30/10 hue shares; full chroma only on <= 15% of pixels, all of it at the focal point.
- C3 Ramps hue-shift: shadow +15-30 deg toward blue, highlight +10-20 deg toward yellow.
- C4 No pure grey, no #000, no #FFF on surfaces; tint neutrals 5-10% toward ambient.
- C5 Each level/scene has one dominant hue; neighbours differ in temperature or key.
- C6 One sacred colour per project that only the player/reward uses (Persona's red rule).

### 1.3 Materials: toy, vinyl, clay, felt, diorama (new presets; plastic/clay/metal basics are in blender-3d.md)

Principled BSDF 4.x/5.x input names; all [memory] unless tagged.
| Look | Base | Roughness | Coat (weight/rough) | Subsurface | Sheen | Notes |
|---|---|---|---|---|---|---|
| Soft vinyl toy (Fall Guys, designer toys) | palette colour, value 0.35-0.85 | 0.45-0.55 | 0.2 / 0.3 | weight 0.1-0.2, radius scale 0.02-0.05 x object size | 0.1 | 15-25% bevels, no texture detail, maybe a tiny seam line |
| Glossy ABS brick (Lego-like) | saturated, jitter +-2% value per brick | 0.18-0.28 | 0 | 0.03 | 0 | real scale 8 mm stud pitch, 9.6 mm brick, 3.2 mm plate; rotation jitter 0.2-0.5 deg; tiny 0.1-0.2 mm bevel; fingerprints/scratches via roughness noise 0.05 |
| Painted wood toy | paint colour | 0.55-0.7 | 0 | 0 | 0 | edge wear: raw wood #D9B38C on convex edges (Pointiness or AO mask, 5-15% coverage); grain noise stretched 1:8, bump 0.03-0.05 |
| Felt / plush | 10-15% desaturated | 1.0 | 0 | 0.05 | weight 0.6-1.0, rough 0.3-0.5 | micro noise bump 0.02; stitch lines as small cylinders |
| Squeaky rubber (duck, ball) | saturated | 0.35 | 0.5 / 0.05 | 0.1 | 0 | one sharp coat highlight sells "rubber" |
| Candy / jelly | saturated, lighter | 0.15-0.25 | 1.0 / 0.05 | weight 0.6-0.8, large radius | 0 | or Transmission 0.6-0.9, IOR 1.4; needs a bright backlight |
| Glazed ceramic | pastel | 0.5 | 1.0 / 0.02 | 0 | 0 | crisp reflections over a matte body |
| Clay (stop-motion) | slightly desaturated | 0.8-0.9 | 0 | 0.05 | 0.2 | add fingerprint/tool noise bump 0.02-0.04 and boil (noise seed change every 2 frames) |
| Diorama water | depth gradient teal #2EC4B6 -> #1B6F86 | 0.05 | 0 | 0 | 0 | foam ring where objects meet water (distance mask, 3-6% of object size), slight transmission |

- Material choice is an art-direction decision, not a finish: Astro Bot Rescue Mission's art director found material choice especially critical when dressing each level; platforms were rebuilt at high quality to be reused from all angles like connectable toy blocks. [verified: https://blog.playstation.com/2019/01/24/astro-bot-rescue-mission-inside-the-art-and-animation-of-japan-studios-ps-vr-hit/ (search summary)]
- Link's Awakening's characters and objects look made of plastic or clay inside a diorama. [verified: https://www.gameinformer.com/preview/2019/06/12/why-the-art-style-does-it-justice (search summary)]
- One project = one material family [memory]: a toy game is "painted wood + ABS", a pond game is "clay + glazed ceramic + water", a science reel is "glass + matte paper". Mixing realistic PBR (scanned bark) into a toy set is the most common cheapener.
- Roblox mapping [memory]: SmoothPlastic + vertex colours for ABS/vinyl; Wood/WoodPlanks MaterialVariants for wood toys; Fabric for felt; Glass + transparency 0.3 for jelly (weak); SurfaceAppearance with roughness map for hero props. Emissive masks are live for worlds, and emissive textures for avatar items come late 2026. [verified: https://devforum.roblox.com/t/creator-roadmap-2026-spring-update/4625473 and https://devforum.roblox.com/t/rdc26-what-we-announced/4865880]

Rules (materials):
- M1 One material family per project, written in the style bible; no scanned/realistic textures inside a toy set.
- M2 Every material has one "tell": coat glint (rubber), edge wear (wood), sheen (felt), SSS glow (vinyl/candy), fingerprints (clay).
- M3 Detail lives in geometry and roughness variation, not in colour noise.

### 1.4 Lighting recipes that make stylised renders pop

Ratios are in stops: key:fill 2:1 = 1 stop (cheerful), 4:1 = 2 stops (drama), 8:1 = 3 stops (noir). Kid-friendly stylised: 2:1 to 3:1. [memory]
- 80.lv Medieval Market (stylised, UE5): warm low-intensity directional key, slightly bluish HDRI skylight, sky sphere, rim light, many small point/spot practicals, exponential fog at light density with bluish tint plus volumetric fog, shadow filter sharpness 0.16, contact shadow length 0.06, subtle grading with toe and white-clip tweaks. [verified: https://80.lv/articles/medieval-market-a-detailed-guide-on-stylized-environment-art-in-unreal-engine] That is the stylised recipe in one line: warm key, cool sky, cool fog, rim, practicals.
- The 2D-look Blender artist adds lights only to build gradients and shapes, and uses negative lights to paint artificial shadows. [verified: https://80.lv/articles/shapes-and-colors-creating-scenes-with-a-2d-effect-in-blender/]
- Colour bounce [memory]: EEVEE without raytracing has weak GI; fake it: an area light under/near the subject facing up, coloured like the ground (grass -> #7BC86C, sand -> #E8C88A), 10-20% of key energy, no shadows. A second bounce from any big coloured wall at 5-10%.

Five recipes (Blender units: 1 BU = 1 stud; view transform per blender-kit: 'neutral' for palette fidelity) [memory]:
| Recipe | Key | Fill / sky | Rim | Atmosphere | Use |
|---|---|---|---|---|---|
| R1 Sunny diorama | Sun, strength 3-4, angle 2-4 deg, elevation 35-50 deg, 30-60 deg off the camera axis toward the back, #FFE2BF | world #A8CCFF at 0.6-1.0 (cool fill = blue shadows) | the sun itself at 3/4 back gives rim; add area rim #FFFFFF 1x key if subject merges | none, or mist pass 15-25% at far depth | toy-siege, daytime levels, thumbnails |
| R2 Golden hour | Sun 4-6, elevation 8-15 deg, #FFB070 | world #5F7FBF at 0.3-0.5 | strong: sun behind subject 120-160 deg from camera | world volume density 0.002-0.01, anisotropy 0.5-0.7 (god rays) | emotional beats, end cards |
| R3 Overcast pastel / cosy | no sun (or 0.5); big area 5x subject size overhead, #FFF4E6 | world #F2EEE6 at 1.0 | soft area rim #FFE9F0 at 0.5x | low mist, morning haze in pale teal | pond game, calm reels |
| R4 Night + practicals | moon Sun 0.2-0.4 #9FB6FF | world #1B2340 at 0.1-0.2 | moon as rim | volume 0.01-0.03 for halos; emissive windows/lanterns 5-10 with warm #FFB55E point lights (radius 0.1-0.3) | spooky/cosy night, fireflies |
| R5 Gradient studio hero | area key 45/45 deg (earlier file) | coloured backdrop in the subject's complementary hue, gradient lighter behind the subject | coloured rim (accent hue) 1-1.5x key | none | product shots, model sheets, thumbnails |
- Depth and volume [memory]: volumetrics only help when there is a light to scatter: put a light behind or beside the haze. Mist pass: start just behind the subject, depth 3-5x subject distance, mix sky colour at 20-40%. Three depth planes (foreground, subject, background) must each differ by >= 1 value step.
- Shadow colour check [memory]: sample a shadow on a white surface: in R1 it should be blue-violet (#8A93C8-ish), never neutral grey. If grey, the world/sky fill is too weak or uncoloured.

Rules (light):
- L1 Pick one recipe per scene from the bible; never the default neutral studio for a world shot.
- L2 Key:fill 2:1-3:1 for stylised kid-friendly; warm key, cool fill; shadows must sample blue-violet.
- L3 Always a rim or backlight on the hero subject (1-1.5x key) so it separates from the background.
- L4 Fake bounce with a ground-coloured up-light at 10-20% of key.
- L5 Volumetrics only with a light behind the haze; density 0.002-0.03.

### 1.5 Composition and camera

- Lenses (full-frame 36 mm sensor) [memory]: 18-28 mm establishing / dynamic (big foreground, exaggerated depth, fun for toys seen low); 35-50 mm neutral gameplay; 85-135 mm character, product and miniature (compresses depth, flattens, sells "tabletop"); 200 mm+ for flat graphic stacks.
- Orthographic isometric [memory, computed]: Blender camera rotation X 54.736 deg, Z 45 deg (true isometric); classic "2:1 pixel" dimetric: X 60 deg (camera 30 deg above horizon), Z 45 deg. Monument Valley-style: ortho, flat per-face shading (1.2).
- Diorama read: high angle 30-45 deg down, telephoto 85-135 mm, a visible base/plinth or world edge, shallow depth of field. Link's Awakening's team wanted the miniature-diorama feel and added tilt-shift to emphasise it. [verified: https://nintendoeverything.com/aonuma-on-how-the-art-style-came-to-be-for-zelda-links-awakening-on-switch/ (search summary)] Diorama photographs are usually taken from a high angle, and blur simulates the shallow DOF of close-up photography. [verified: https://en.wikipedia.com/wiki/Diorama_effect (search summary)]
- Tilt-shift maths [memory, computed]: depth of field relative to the subject scales with scene size at fixed framing and lens. If your scene is s times larger than the miniature it should look like, divide the f-stop by s. Example: a castle 60 BU wide that should read as a 30 cm toy (s = 200): to imitate f/2.8 at toy scale use f/0.014. Blender may clamp tiny f-stops: then scale the whole scene down (0.005) for the render, or blur in post with the Z pass. A real-scale Blender scene shows almost no blur at realistic f-stops. [verified: https://blenderartists.org/t/depth-of-field-and-f-stops/698119 (search summary)]
- three.js tilt-shift (pmndrs postprocessing `TiltShift`): defaults offset 0, rotation 0, focusArea 0.4, feather 0.3, kernelSize MEDIUM. [verified: https://react-postprocessing.docs.pmnd.rs/effects/tilt-shift] For a toy look use focusArea 0.25-0.35, feather 0.15-0.25, and raise saturation +10-20% and contrast +10% (the classic fake-miniature recipe boosts saturation and contrast [verified: https://help.shapediver.com/doc/tilt-shift (search summary)]).
- Thirds and focus [memory]: subject on a thirds intersection; horizon on a third line, never the middle unless the shot is a symmetrical hero; 9:16 video: subject's eyes/top at y ~ 600-700 of 1920 (upper third), because the bottom 420 px is covered by UI.
- Leading lines [memory]: paths, rails, rows of bricks, rivers point into the subject; rotate the camera 10-25 deg so the main lines are diagonals, not parallel to frame edges.
- Foreground framing [memory]: a dark (-1 stop), out-of-focus foreground element covers 10-25% of one or two frame edges (leaf, wall corner, toy block). It creates depth and says "we are looking into a world".
- Camera height [memory]: low (lens at 0.3-0.5 of subject height, looking slightly up) makes toys heroic; eye level is neutral; 30-45 deg down is the board-game/diorama read.
- Layout match: the Medieval Market artist built the whole scene around one primary camera matching the concept art. [verified: 80.lv medieval market URL above] Rule: choose the camera first, then model only what it sees in detail.

Rules (camera):
- K1 Lock the hero camera before modelling; detail only what it sees.
- K2 Lens by intent: 24 dynamic, 50 neutral, 85-135 miniature/product.
- K3 Diorama = 30-45 deg down + 85-135 mm + shallow DOF + visible world edge.
- K4 Three depth planes with a dark blurred foreground on 10-25% of one edge.
- K5 9:16: subject in the upper third, nothing important below y 1500.

### 1.6 Render finishing (post chain, in this order)

| Step | Blender (5.x compositor) | three.js (pmndrs postprocessing) | Value [memory] |
|---|---|---|---|
| AO | render AO / `view_layer.eevee.ambient_occlusion_distance` (renamed in 5.0, see blender-3d.md) | N8AO / SSAO | distance ~0.1-0.2 x subject size, subtle |
| Bloom/glare | Glare node, Bloom or Fog Glow | `Bloom` (mipmapBlur) | threshold 0.8-1.0 so only emissives and speculars glow; strength low (glow radius 1-3% of frame) |
| Grade | Color Balance (lift/gamma/gain), Hue Correct | `HueSaturation`, `BrightnessContrast`, LUT | lift shadows toward blue (+0.01-0.03 B), gain toward warm; saturation +5-15% |
| Vignette | Ellipse Mask + Blur + Mix multiply | `Vignette` | 15-30% darkening, starts at 55-65% of radius |
| Grain | noise texture overlay | `Noise` (premultiply) | 2-4% luminance, 1-1.5 px grain; kills banding in gradients |
| Chromatic aberration | Lens Distortion dispersion | `ChromaticAberration` | 0-0.5 px; skip on toy looks |
- The 2D-look artist's compositor: dilate/erode nodes for a painted base, a Prewitt filter for outlines, several dilate/erode passes masked by hand, Glare for light streaks, film grain on top, viewport curves for contrast and colour; "Masking is really the key." [verified: https://80.lv/articles/shapes-and-colors-creating-scenes-with-a-2d-effect-in-blender/]
- Medieval Market finished with subtle grading plus toe and white-clip changes for contrast. [verified: 80.lv medieval market URL]
- 2026 trend that suits renders: grain, paper fibres, dust and soft light artefacts layered quietly over clean compositions. [verified: https://blog.videobolt.net/post/top-motion-graphics-trends-2026]

Rules (finish):
- F1 Always finish: AO, restrained bloom (threshold >= 0.8), grade (cool shadows/warm highlights), vignette 15-30%, grain 2-4%.
- F2 Never ship the raw render of a scene; never let bloom touch non-emissive surfaces.
- F3 Match the grade across all shots of one video/game (save it as a preset).

### 1.7 What to steal from each reference look

| Reference | Steal this | Tag |
|---|---|---|
| Link's Awakening (2019) | figurine-in-diorama scale, detail limited to toy scale, tilt-shift blur, plastic/clay sheen | [verified: zeldadungeon, nintendoeverything, gameinformer URLs above] |
| Super Mario Bros. Wonder | animation exists to communicate the character's state; joints increased to 12 and animation count more than doubled; expressions joints can't make are model swaps; enemies greet each other, sleep, look fed-up when stuck; SFX retimed to the animation, not the button | [verified: https://www.nintendo.com/sg/interview/aqmx/02.html] |
| Astro Bot | material choice per level is the art direction; toy-block reusable platforms; simple look so players know where to go | [verified: PlayStation Blog search summaries above] |
| Fall Guys | vinyl-toy simplicity, inflatable/padded game-show props, primary colours, floppy jelly physics | [verified: tonight.co.za, Edge search summaries above] |
| Monument Valley | ortho isometric, ~3 tones per object (one per face), colour in shader not lights, whole-game colour script on a wall, new palette per level | [verified: creativebloq/killscreen search summaries above] |
| Persona 5 | one sacred colour (red) and nothing else competes; contrast colour only for selection | [verified: mechanicsofmagic URL above] |
| Pixar | colour script before lighting; desaturate to change mood | [verified: slashfilm, CGW search summaries above] |
| Hades | scenery must never obscure combat readability; an early colour script of the whole game | [verified: https://lr.us.psf.lt/r/NintendoSwitch/comments/ixri6b/we_are_supergiant_games_creators_of_hades_pyre/g68ec1o and https://mcvuk.com/business-news/behind-the-art-of-hades-we-value-artistic-integrity-and-excellence-in-artistic-craft-at-supergiant-however-were-first-and-foremost-a-game-design-lead-team/ (search summaries)]; thick ink linework, saturated rim light on characters [memory] |
| Supercell | readability and polish are stated hiring criteria; custom chunky display type (Supercell-Magic, built from You Blockhead) | [verified: https://www.fontsinuse.com/uses/66357/clash-royale-mobile-game and Supercell job pages (search summary)]; oversized heads/hands, top-down warm sun, saturated green/blue [memory] |
| Medieval Market (80.lv) | modular kit on a 50 cm grid (150/300/600 cm parts), warm key + bluish sky + bluish fog + rim | [verified: 80.lv URL above] |
| Polygon Runway | isometric rooms from a handful of reusable materials (ground, wall, metal, accent), Cycles with area lights and volumetric fog | [verified: https://hq-raydata-co.pages.dev/vault/06-reference/2026-04-29-polygon-runway-2026-blender5-beginner/ (low-quality secondary page)] |
| Ian Hubert | "lazy" photo-cards and simple geometry sold by fog, light and bloom; atmosphere hides missing detail | [memory] |
| Grant Abbitt | flat-colour low poly from a palette texture, simple sun + sky; shape and colour do the work | [memory] |
| Lego renders | true scale, telephoto macro (60-100 mm), f/4-8 at real scale, per-brick micro-jitter and roughness smudges | [memory] |

---------------------------------------------------------------------

## 2. ANIMATION THAT FEELS ALIVE

### 2.1 Timing units (30 fps)
1 frame = 33 ms. 2 f = 67 ms, 3 f = 100 ms, 4 f = 133 ms, 6 f = 200 ms, 9 f = 300 ms, 12 f = 400 ms, 15 f = 500 ms, 24 f = 800 ms, 30 f = 1 s. [memory, computed]
Classic charts are in 24 fps frames ("frame" = 1/24 s in Williams and Goldberg) [verified: https://animation.monmouth.edu/instruct/?p=351 (search summary)]: multiply by 1.25 for 30 fps.

| Action | 30 fps frames | ms | Tag |
|---|---|---|---|
| UI tap response (visual) | 0-2 | <= 67 | [memory] |
| Button press down / release | 2 / 4-5 | 60 / 150 | earlier game-ui.md |
| Blink (close, hold, open) | 2 + 1 + 3 | ~200 | [memory] |
| Hit-stop / impact freeze | 2-5 | 60-170 | [memory] |
| UI pop-in with overshoot | 8-12 | 270-400 | [memory] |
| Anticipation (UI / character jump) | 3-5 / 6-12 | 100-170 / 200-400 | [memory] |
| Settle after overshoot | 6-10 | 200-330 | [memory] |
| Hold on a key pose | 8-15 | 270-500 | [memory] |
| Walk step (brisk, natural) | 15 (12 @24) | 500 | [verified: https://idearocketanimation.com/27285-animate-a-walk-cycle/ (search summary)] |
| Run step | 5-8 (4-6 @24) | 170-270 | [verified: same] |
| Normal gait per step range | 10-20 | 333-667 | [verified: https://education.siggraph.org/static/HyperGraph/animation/character_animation/walking/learning_to_walk.htm (search summary)] |
| Camera push-in | 90-180 | 3-6 s | [memory] |

### 2.2 Easing library (copy these exact values)

| Name | cubic-bezier | GSAP | Roblox TweenInfo | Use | Tag |
|---|---|---|---|---|---|
| M3 standard | (0.2, 0, 0, 1) | power2.out-ish | Quart Out | default UI move | [verified: https://docs.rs/crate/bevy_material_ui/latest/source/src/tokens.rs] |
| M3 emphasized decelerate | (0.05, 0.7, 0.1, 1) | expo.out-ish | Exponential Out | hero entries, panels arriving | [verified: same] |
| M3 emphasized accelerate | (0.3, 0, 0.8, 0.15) | power3.in | Cubic In | exits | [verified: same] |
| M3 standard accelerate / decelerate | (0.3, 0, 1, 1) / (0, 0, 0, 1) | | | | [verified: same] |
| easeOutCubic | (0.33, 1, 0.68, 1) | power2.out | Cubic Out | small moves | [memory: easings.net] |
| easeOutQuart | (0.25, 1, 0.5, 1) | power3.out | Quart Out | slides | [memory] |
| easeOutExpo | (0.16, 1, 0.3, 1) | expo.out | Exponential Out | big confident reveals (Apple-style) | [memory] |
| easeInOutCubic | (0.65, 0, 0.35, 1) | power2.inOut | Cubic InOut | camera moves, position A->B | [memory] |
| easeInOutSine | (0.37, 0, 0.63, 1) | sine.inOut | Sine InOut | loops: bob, breathe, float | [memory] |
| easeOutBack | (0.34, 1.56, 0.64, 1) | back.out(1.7) | Back Out | pops, overshoot ~10% | [memory] |
| easeInBack | (0.36, 0, 0.66, -0.56) | back.in(1.7) | Back In | anticipation-then-exit | [memory] |
- M3 duration tokens: short1-4 = 50/100/150/200 ms; medium1-4 = 250/300/350/400; long1-4 = 450/500/550/600; extra-long1-4 = 700/800/900/1000. [verified: tokens.rs URL above] Use: micro 50-150, small component 200-300, panel/screen 350-500, celebratory 600-1000.
- Apple's spring: `spring(response: 0.5, dampingFraction: 0.825)` is the default; response = approximate duration in seconds; dampingFraction = fraction of critical damping. [verified: https://developer.apple.com/documentation/swiftui/animation/spring(response:dampingfraction:blendduration:).md] Presets `smooth` (no bounce), `snappy` (small bounce), `bouncy` (more bounce) exist; exact values are not listed on Apple's page. [verified: https://developer.apple.com/documentation/swiftui/animation.md]
- Damping ratio -> overshoot of a step (underdamped spring: overshoot = exp(-z*pi/sqrt(1-z^2))) [memory, computed]: z 0.825 -> 1%; 0.7 -> 4.6%; 0.6 -> 9.5%; 0.5 -> 16%; 0.4 -> 25%; 0.3 -> 37%. Pick: UI panels 0.75-0.85, buttons and cards 0.6-0.7, cartoon pops and jelly 0.35-0.5.
- Penner Back with s = 1.70158 overshoots ~10%. [memory]
- Roblox: TweenService EasingStyle Linear, Sine, Back, Quad, Quart, Quint, Bounce, Elastic, Exponential, Circular, Cubic; directions In, Out, InOut. [memory] There is no native spring: write a 10-line critically-damped/underdamped spring in RenderStepped for anything interruptible (drag, hover, follow), and use TweenService for fire-and-forget.

Spring in Luau (semi-implicit Euler, stable at 60 fps) [memory]:
```lua
-- x: position, v: velocity, target, f: frequency in Hz (2-6), z: damping ratio (0.3-1)
local function stepSpring(x, v, target, f, z, dt)
	local w = 2 * math.pi * f
	v += (-2 * z * w * v - w * w * (x - target)) * dt
	x += v * dt
	return x, v
end
```

### 2.3 The 12 principles as numbers

| Principle | Code rule [memory unless tagged] |
|---|---|
| Squash & stretch | preserve volume: scaleY = s, scaleX = scaleZ = 1/sqrt(s). UI pop 0.92-1.08; character landing squash 0.75-0.85 for 2-4 f; takeoff stretch 1.15-1.3 along velocity for 2-3 f; jelly/vinyl characters up to 0.65/1.4. Velocity stretch: s = 1 + min(0.3, k*speed) along the velocity axis. The Roblox guide: squash the whole body before a jump, stretch on takeoff. [verified: https://devforum.roblox.com/t/jespones-guide-to-animations/225752] |
| Anticipation | move 5-20% of the travel in the opposite direction first: UI 80-150 ms at 3-8%; character 6-12 f at 10-20%; big attack 12-20 f. Mario Wonder: Mario now does an action before entering a pipe. [verified: Nintendo Ask the Developer URL above] |
| Staging | one thing moves at a time when it matters: freeze or dim (to 50%) everything else for the key beat; camera frames the action. |
| Straight-ahead vs pose-to-pose | keyframes = pose-to-pose (block goals first, then in-betweens) [verified: Jespone URL]; physics/procedural = straight-ahead. Combine: key poses + spring between them. |
| Follow-through & overlap | children lag parents 2-4 f (67-133 ms) per hierarchy level, amplitude x0.7 per level; let hair/cape/ears/antenna/tail keep moving 6-12 f after the body stops; do it on everything except the root and don't make it floppy. [verified: Jespone URL for the rule; numbers memory]. Avoid "twinning" (all parts keyed on the same frames). [verified: same] |
| Slow in / slow out | nothing linear except constant mechanical loops; ease every position and rotation. |
| Arcs | limbs and thrown objects travel on arcs [verified: Jespone URL]; UI flights on a quadratic bezier with the control point offset perpendicular by 15-40% of distance; rotate along velocity (atan2) for flying objects. |
| Secondary action | add one supporting motion per primary (hand to chin while thinking [verified: Jespone URL]; tail wag while walking; coins jingling). |
| Timing | fewer frames = faster [verified: Jespone URL]; contrast is the point: fast action (4-6 f) next to long holds (12-20 f). |
| Exaggeration | push poses 1.2-1.5x past reference; rotations of spine/head 1.3x. |
| Solid drawing (3D: posing) | no twins in pose (left/right limbs never mirror), weight over the support foot, line of action as one C or S curve. |
| Appeal | asymmetric poses, clear silhouette per pose; confident character = open chest, head level. [verified: Jespone URL] |

Balatro's "juice" (the reason its UI feels alive): a decaying sine on scale and rotation added on top of the base transform. From the game's Lua (engine/moveable.lua) [memory: recalled from the source, verify before quoting]:
```lua
-- juice_up(amount = 0.4, rot_amt = +-0.6*amount), lasts 0.4 s
scale = amount * sin(50.8 * t) * ((t_end - now) / (t_end - t_start))^3
rot   = rot_amt * sin(40.8 * t) * ((t_end - now) / (t_end - t_start))^2
```
i.e. an ~8 Hz scale wobble and ~6.5 Hz rotation wobble that die out in 0.4 s. Apply it to every element that changes value (counter, card, button) on the frame it changes. Port to Luau with RenderStepped; amount 0.1-0.4 for UI. A Godot port of Balatro's hover lerps toward scale ~1.05 with a decaying rotation. [verified: https://godotshaders.com/shader/balatro-card-hover/ (search summary)]

### 2.4 Secondary motion: idle, breathing, blinking

- Nothing in a scene should be perfectly still for more than ~2 s [memory]: idle loops on characters, props and UI focal elements; desynchronise loops (random phase and +-10-20% random period per instance) or the world looks mechanical.
- Idle bob for pickups/floating things [memory]: y = A sin(2 pi t / T + phase), A = 3-6% of object height, T = 1.6-2.4 s, Sine InOut; plus slow spin 30-60 deg/s or a +-8 deg sway; a ground shadow that shrinks 10% at the top of the bob.
- Breathing [memory]: chest/torso scale Y 1.00-1.02 (Roblox blocky: UpperTorso offset 0.02-0.05 stud) on a 3-4 s cycle (adults 12-20 breaths/min); shoulders rise 1-2% on the inhale; head follows 2-3 f later.
- Blink: humans average ~14 blinks/min looking straight ahead, 10-15/min in other reviews, 3-4/min while reading. [verified: https://pmc.ncbi.nlm.nih.gov/articles/PMC2817301 and search summary] Duration: clinical 10-80 ms for the closure phase; popular figures 100-400 ms. [verified: search summary of PMC/UCL sources] Animation rule [memory]: interval random 2-6 s (mean ~4 s); close 2 f, hold 1 f, open 3-4 f; 15-20% chance of a double blink; always blink at the start of a head turn; never blink during a "surprise" take.
- Eyes lead, head follows, body follows [memory]: eyes move first (saccade 2-3 f, no easing), head starts 2-4 f later, torso 2-4 f after the head.
- Weight shifts in long idles [memory]: every 4-8 s shift hips 2-4% sideways over 15-20 f and settle; 1 in 3 idles add a small gesture (look around, scratch, stretch).
- Mario Wonder's world feels alive because enemies have off-duty behaviours (Goombas greeting each other, sleeping, fed-up when stuck). [verified: Nintendo URL above] Give every NPC/creature 2-3 idle "moods" that trigger at random and on proximity.

### 2.5 Camera animation

- Trauma shake (Squirrel Eiserloh's GDC 2016 model): trauma 0-1, shake = trauma^2, Perlin noise per axis; reference constants from Bevy's example: TRAUMA_EXPONENT 2.0, MAX_ANGLE 10 deg ("somewhat high but still reasonable"), MAX_TRANSLATION 20 px ("low enough not to be distracting"), TRAUMA_DECAY_PER_SECOND 0.5 (full trauma lasts 2 s), NOISE_SPEED 20, TRAUMA_PER_PRESS 0.4; noise sampled at t, t+100, t+200 for rotation/x/y. [verified: https://bevy.org/examples/camera/2d-screen-shake/] A Godot camera kit defaults to a gentler 1.5 deg and 12 px at full shake. [verified: https://www.strayspark.studio/docs/godot-camera-system/noise-and-shake (search summary)]
- Game numbers [memory]: small hit trauma +0.15-0.25, big impact +0.4-0.6, explosion +0.8; decay 1.0-1.5/s for snappy mobile; max roll 2-4 deg on phones (10 deg is too much on a small screen); translation 0.3-0.8 stud in 3D. Respect a "reduce motion" setting by scaling to 25%.
- Handheld feel for video [memory]: rotation 0.15-0.4 deg and translation 0.2-0.5% of frame width, 2 octaves of noise at 0.3-1.0 Hz; on 3D renders apply it to the camera, not as 2D post. Too much reads as amateur.
- Push-in [memory]: 5-12% scale (or dolly 10-25% of distance, earlier file) over 3-6 s, Sine InOut; starts at a beat, never constant across the whole video.
- Parallax [memory]: layer speed proportional to 1/depth: foreground 1.4-1.6x, subject 1.0x, background 0.3-0.5x, sky 0.05-0.1x. 3-5 layers minimum for 2.5D.
- Whip pan [memory]: 6-10 f, speed peaks in the middle (InOut Expo), directional blur 40-80 px at 1080 or shutter 360 deg; cut to the next shot inside the blurriest frame.
- Speed ramp [memory]: 100% -> 20-30% over 6-10 f into the key moment, hold slow 0.5-1.0 s, back to 100-120% over 4-6 f; Expo InOut on the time curve.
- Orbit for hero turntables in reels [memory]: 10-20 deg/s (a 360 in 18-36 s is premium-slow; 8-12 s reads "product spin").
- Dolly zoom [memory]: keep d * tan(fov/2) constant; 2-3 s, used once per video maximum.

### 2.6 Procedural walk/run (for Blender bpy or Luau)

Phase p = 2 pi t / T, T = one full cycle (2 steps). Walk T = 30 f (1.0 s) at 30 fps, brisk; slow 36-40 f; run T = 12-16 f; cartoon/toddle walk 20-24 f. [verified for step timings above; T derived]
| Channel | Walk | Run | Tag |
|---|---|---|---|
| Leg swing (hip pitch) | +-20-30 deg, left sin(p), right sin(p+pi) | +-40-60 deg | [memory] |
| Knee bend | 0-40 deg, peak during swing | 0-90 deg | [memory] |
| Foot lift | H = 5-10% leg length on swing half only: max(0, sin(p)) | 20-30% | [memory] |
| Body bob (2x step frequency) | 2-4% of height, lowest just after contact, highest at passing: z = B cos(2p) | 4-8%, airborne 30-40% of cycle | [memory] |
| Hip sway (side) | 2-4% of height at cycle frequency | 1-2% | [memory] |
| Hip yaw / shoulder counter-yaw | +-5-8 deg / +-4-6 deg opposite | +-8-12 / +-8-10 | [memory] |
| Arm swing | +-20-30 deg opposite to the same-side leg, lagging 2-3 f | +-45-70 deg, elbows 70-90 deg bent | [memory] |
| Head | counter-bob 50% so it stays steadier than the body; lags torso 2 f | same | [memory] |
| Forward lean | 0-5 deg | 10-15 deg | [memory] |
- Feet must plant: during stance, foot world position is fixed (IK or computed from body speed: stride L = speed * T / 2). Sliding feet are the #1 tell of cheap procedural walks [memory].
- Contact accent: at foot contact, 1-2 f squash 0.95 on blocky characters, and a soft step sound on that frame [memory]. A Roblox animator's advice: legs accelerate and decelerate; a landing foot decelerates on impact, then kicks back with explosive acceleration. [verified: https://devforum.roblox.com/t/making-animations-feel-more-natural-and-human/2736367]
- David Rosen (Overgrowth, GDC 2014 Animation Bootcamp): fluid interactive animation from very few key frames plus simple procedural techniques. [verified: https://gdcvault.com/play/1020049/Animation-Bootcamp-An-Indie-Approach (search summary)] Practical version [memory]: 2-4 key poses per cycle (contact, passing), blend between them by phase, drive cycle speed by actual ground speed, add bob/lean/arm lag procedurally, and use springs for landing compression.

### 2.7 Motion-graphics conventions (video)

- Kurzgesagt: research-heavy script, then on average ~200 illustrated panels in Illustrator per video, animated in After Effects (now trying Cinema 4D); vector, pixel and infographic styles with recurring characters. [verified: https://kurzgesagt.org/youtube/ and https://rosetta.to/u/kurzgesagt/how-to-make-a-kurzgesagt-video-in-1200-hours (search summaries)] Motion signatures [memory]: nothing is ever fully still (ambient drift, particles, slow parallax), objects enter with scale pops and overshoot, elements arrive in staggered cascades (2-3 f apart), lines draw on, soft gradients + subtle grain, camera drifts slowly through layered depth.
- Vox [memory]: paper/cut-out textures, highlighter swipes on key phrases, 2.5D parallax of photo cut-outs with drop shadows, map zooms, typewriter stamps.
- Apple keynote graphics [memory]: one idea per frame; huge type on black or white; entries by blur-to-sharp (from 20 px blur, opacity 0, y +20-40 px) or mask-wipe over 600-900 ms on easeOutExpo; long holds (2-4 s); numbers as heroes; products rotate slowly under a soft top light; no bounce.
- School of Motion craft [memory]: shape the speed graph, not just the value graph: entries are mostly ease-out (fast start, long settle); offset layers 1-3 f so nothing starts on the same frame; "overlap and offset" is the cure for robotic motion; a motion should anticipate, act, overshoot, settle.
- Rhythm [memory]: cut and key on the beat of the music or the narration's stressed syllables; hold every text until it is read (~3 words/s) plus 0.5 s.

### 2.8 Roblox character animation: good vs stiff

- Stiff = everything keyed on the same frames, linear easing, no hip motion, arms swinging like pendulums, no holds, no overlap. Alive = offsets, easing, hips leading, arcs, holds, secondary motion. [verified in spirit: Jespone guide URL; specifics memory]
- Easing is the main lever and Moon Animator offers more easing styles than the default editor; timing is set by keyframe spacing; use video reference for timing. [verified: https://devforum.roblox.com/t/jespones-guide-to-animations/225752 and https://devforum.roblox.com/t/making-animations-feel-more-natural-and-human/2736367] One animator found Moon's easing alone did little for human motion: spacing keyframes matters more. [verified: search summary of https://devforum.roblox.com/t/seeking-advice-on-making-more-smoother-animations/1011283]
- R15 tricks for blocky rigs [memory]: (1) sell weight with LowerTorso height: drop 0.1-0.3 stud on landings and contacts; (2) UpperTorso twist +-10-15 deg against the hips on every action; (3) head lags the torso 2 f and overshoots 5%; (4) hands and feet arc, never straight lines; (5) offset left/right limbs by 1-3 f; (6) keep the HumanoidRootPart for travel only, animate from LowerTorso; (7) for comedic storytime, step the timing on 2s or 3s (Stepped interpolation) [earlier file]; (8) one strong silhouette pose per beat, held 8-15 f.
- New rig fidelity: R15 platform avatars now support articulated fingers, a refined torso with clavicles, and ball-of-foot joints; Animation Graphs are in Studio Beta for transitions and blends with a Character Controller library. [verified: https://devforum.roblox.com/t/creator-roadmap-2026-spring-update/4625473] New default movement with motion matching and root motion is planned for early 2027; Animation Graph state-machine nodes mid 2027. [verified: https://devforum.roblox.com/t/rdc26-what-we-announced/4865880] Use the fingers (fists, points, open hands) and clavicles (shrugs) where available: they are the cheapest expressiveness win.
- Priorities [memory]: Core < Idle < Movement < Action (Action2-4 in newer API); play emotes as Action; layer an additive "breathing" idle at low weight.
- Faces (dynamic heads): animation is driven by FaceControls; each pose is a named property. [verified: https://create.roblox.com/docs/art/characters/facial-animation] Pose names include LeftEyeClosed, RightEyeClosed, EyesLookLeft/Right/Up/Down, LeftEyeUpperLidRaiser, LeftInnerBrowRaiser, LeftOuterBrowRaiser, LeftBrowLowerer, LeftCheekRaiser, LeftCheekPuff, LeftLipCornerPuller, LeftLipCornerDown, LeftLipStretcher, LeftDimpler, LeftNoseWrinkler, LeftUpperLipRaiser, LeftLowerLipDepressor, JawDrop, JawLeft, JawRight, LipsTogether, LipPresser, FlatPucker, ChinRaiser, UpperLipSuck, LowerLipSuck, MouthLeft, MouthRight, TongueOut (Right* mirrors exist). [verified: https://create.roblox.com/docs/avatar/dynamic-heads/facs-poses-reference.md]
  Expression recipes (0-1 weights) [memory]: blink = both EyeClosed 0->1 in 2 f, hold 1 f, ->0 in 3 f. Smile = LipCornerPuller 0.7 + CheekRaiser 0.4 (+ Dimpler 0.2). Big grin = + JawDrop 0.25. Surprise = Inner+OuterBrowRaiser 0.8 + EyeUpperLidRaiser 0.6 + JawDrop 0.4, arrive in 3 f with 10% overshoot. Anger = BrowLowerer 0.8 + LipPresser 0.5 + NoseWrinkler 0.3. Sad = InnerBrowRaiser 0.7 + LipCornerDown 0.6 + gaze down 0.4. Lip flap for TTS: JawDrop 0.2-0.6 driven by audio amplitude (RMS over 50 ms windows), LipsTogether pulses on b/m/p if you have phonemes. Always pair a face change with a head tilt 5-10 deg.
- Classic (decal) faces: swap decals on the expression beat and on blinks (2-3 decal frames: open, half, closed) [memory].

Rules (animation, summary in the final list).

---------------------------------------------------------------------

## 3. GAME UI PLAYERS CALL BEAUTIFUL (and want to touch)

### 3.1 What the loved UIs actually do (steal list)

| Game | What makes it loved | Steal | Tag |
|---|---|---|---|
| Persona 5 | the UI is treated as "graphical entertainment", not information layout; typography inspired by the ransom-note Sex Pistols covers; red/black/white only, blue splash for selection; central lines steer the eye; the director says it was "impossible to read at first" and was tuned until legible | one sacred colour; tilted, cut-paper type; selection in a contrast colour; every menu has a character pose | [verified: https://www.thestar.com.my/tech/tech-news/2024/10/20/exuberant-video-game-menus-designed-with-da-vinci-in-mind and mechanicsofmagic URL] ; panel tilts of -5 to -15 deg, jagged starburst shapes, animated transitions between every menu [memory] |
| Splatoon 3 | a UI designer built a custom typeface because no font suited the countdown numerals; it spread to web, ads and merch; type mixes liquid softness with sporty weight; coloured shading instead of realistic shadows; a two-person UI team | a custom (or customised) numeral style; the UI motif is the game's verb (ink); colour shading | [verified: https://www.nintendo.co.jp/jobs/keyword/18.html and Nintendo UI Crunch summary (search summaries)]; splat masks, sticker/zine collage, team colours re-tint the UI per match [memory] |
| Balatro | every value change wobbles (decaying sine), every scored card plays a rising note (C D E F G), chips blue / mult red, CRT scanlines and vignette, score-scaled screen shake | juice on change; pitch ladders; colour = meaning; texture overlay | [verified: https://blakecrosley.com/guides/design/balatro (author's illustrative CSS, not the game's code)] + source maths in 2.3 [memory] |
| Pokemon TCG Pocket | built around "recreating the physical feel of a card" plus digital-only expressions; swipe to tear the pack; rare packs crack with light shining out before the reveal; cards rotate under the finger; "immersive" rares animate inside the card; players later demanded skippable repeats | a physical gesture as the reward trigger; reveal rarity before the item; touch-tilt cards; let repeats skip | [verified: https://corporate.pokemon.co.jp/en/topics/detail/t-28/ , https://gamewith.net/pokemon-tcg-pocket/49002 , https://www.itmedia.co.jp/mobile/spv/2411/06/news118_2.html , https://jamtest.dexerto.com/pokemon/pokemon-tcg-pocket-desperately-needs-one-key-qol-feature-3005478 (search summaries)] |
| Clash Royale / Supercell | custom chunky display face (Supercell-Magic from You Blockhead); readability and polish are hiring criteria | a heavy rounded display face with outline; chest bounce -> glow by rarity -> cards fly out and flip with "x12" counts, tap-to-continue rhythm | [verified: fontsinuse URL above; job listings (search summary)]; choreography [memory] |
| Brawl Stars | logo kept skull/colours; home screen dense with clearly tappable buttons (a critique says too many for new users) | skewed/italic buttons, starburst behind rewards, heavy outlined type; but limit home-screen buttons | [verified: https://supercell.com/en/games/brawlstars/blog/news/brawl-stars-logo-is-changing/ and https://ixd.prattsi.org/2025/02/design-critique-brawl-stars/ (search summaries)]; styling [memory] |
| Genshin Impact | wish reveal: the meteor's colour (blue/purple/gold) announces rarity before the item; elegant serif-ish titles, cream panels, gold hairlines | colour-coded anticipation; thin gold rules for "premium" | [memory] |
| Hades | boon choices themed per god (colour, ornament, portrait, voice line); big painted portraits; readable over chaos | theme the reward frame by its source | [memory] |
| Zelda TOTK | minimal HUD that fades out in calm play; one glowing Zonai green-teal motif across tools, menus and world; glyph patterns on dark slate | UI motif = world motif; HUD that gets out of the way | [memory] |
| Marvel Snap | card reveal impact scales with power; 3D parallax "flare" on card art; the Snap button pulses; cube stakes animate | scale feedback intensity with stakes | [verified: https://gdcvault.com/play/1029024/Designing-MARVEL-SNAP exists; specifics memory] |
| Fall Guys | the UI artist's vinyl toys shaped the characters themselves; UI and world share one toy language | let the UI artist set the world's shape language, or vice versa | [verified: tonight.co.za search summary above]; pastel pink/purple, slanted rounded type, confetti, crowns [memory] |
| Top Roblox 2025-26 | see game-ui.md; common: currency pills, side stacks, rarity colours, Back-ease pops | (already covered) | |

### 3.2 Giving a UI kit an identity (instead of generic rounded rectangles)

Write these six decisions into the style bible; apply them to every button, panel, badge, toast and loading screen [memory]:
1. Signature silhouette: one shape that replaces the plain rounded rectangle: e.g. alphabet block (square with deep bevel and embossed letter), lily pad (circle with a notch), ticket stub (notched sides), parallelogram skewed 6-10 deg, speech bubble, stitched patch, specimen tag with a punched hole. Roblox now has per-corner radii (TopLeftRadius etc. as UDim), so asymmetric shapes like leaves (two opposite corners round, two sharp), tabs and one-sided callouts need no images. [verified: https://devforum.roblox.com/t/full-release-new-ui-capabilities-shadows-individual-corners/4636263 (via forum JSON)]
2. One angle: all headers/ribbons rotated -2 to -4 deg (energetic) or perfectly level (calm). Never mixed.
3. One texture at 5-15% opacity on panels: wood grain, felt, paper fibre, halftone dots, ink grain. Texture is what separates "designed" from "default".
4. One ornament family: stitches, rivets, splats, stars, sparkles, tape corners, tick marks. Used on max 1-2 elements per screen.
5. A mascot: appears in empty states, loading, tutorials, results (reacts: happy on win, flops on fail). Monument Valley/Duolingo logic: a character carries the tone better than any colour [memory].
6. A sound family matched to the material (wood clacks, water plinks, glass tings), see 3.6.
"Cover the logo" test [memory]: hide the game name; if a screenshot of the shop could be from any other Roblox simulator, the motif is too weak: push silhouette or texture until it could not.
Ban list [memory]: flat fill + 12 px radius + centred title + X button as the only design; system/Arial fonts; emoji as icons; more than 2 fonts; gradients that change hue by more than 30 deg on a button; drop shadows on text without an outline; glassmorphism on a toy game.

### 3.3 Roblox UI tech that changed in 2026 (use it; most kits predate it)

- UIShadow (full release, June 2026): 2D drop shadow with BlurRadius, Color, Transparency, Offset, Spread, Enabled. [verified: https://devforum.roblox.com/t/full-release-new-ui-capabilities-shadows-individual-corners/4636263]
- Upgraded UIShadow (full release, Nov 2026): `Mode = Text` casts the shadow from the glyph outlines of TextLabel/TextButton/TextBox (several text shadows allowed, and a text shadow can stack with a shape shadow); `Inset = true` draws the shadow inside the element (pressed/recessed states; positive Spread grows inward); `ShowBehindParent = false` knocks out the shadow under the element (for glass/transparent panels); a child UIGradient tints the shadow (multi-tone glows, auras). Spread/Inset/ShowBehindParent do nothing in Text mode. Keep <= 100 UIShadows on screen. [verified: https://devforum.roblox.com/t/full-release-upgraded-uishadow-capabilities/4934553]
- Per-corner radius on UICorner: TopLeftRadius, TopRightRadius, BottomLeftRadius, BottomRightRadius; CornerRadius sets all four. [verified: 4636263 URL]
- Multiple UIStrokes and UIGradients can be combined with shadows. [verified: 4636263 URL]
- UIShadow.BlurRadius is a UDim whose Offset is reported not to scale with UIScale (open bug). [verified: thread title https://devforum.roblox.com/t/uishadow-blurradius-offset-does-not-get-scaled-by-uiscale/4888407] Rule: multiply blur/offset pixel values by your current UIScale yourself.
- UI Styling (StyleSheets, StyleRules, StyleLinks, StyleDerives, tokens, themes; Style Editor) fully released; StyleQuery (conditional styles by parent size or device/user settings) fully released May 2026. [verified: https://devforum.roblox.com/t/full-release-ui-styling-is-officially-released/4275082 and https://devforum.roblox.com/t/weekly-recap-may-11-to-may-15-2026/4638298] Put the bible's palette, radii, strokes and fonts in one StyleSheet as tokens so every screen inherits the identity.
- Coming late 2026: UI blur, text shadows (already shipped via UIShadow), improved gradients, animated image containers and sprite-sheet import. [verified: RDC26 URL above]

Recipes with these [memory; property names verified above]:
- Chunky toy button: face Frame (UIGradient 90 deg, lighter top) + UIStroke 3 ink + UIShadow A (hard lip): Offset (0, 6), BlurRadius 0, Spread 0, Color = shade colour, Transparency 0 + UIShadow B (soft drop): Offset (0, 12), BlurRadius 14, Color ink, Transparency 0.75. Replaces the old 3-frame lip stack from game-ui.md.
- Pressed state: disable shadow A, move face +5 px, add UIShadow Inset = true, Offset (0, 4), BlurRadius 6, Color ink, Transparency 0.55. 60 ms down, 150 ms up.
- Chunky 3D title text: UIStroke 3-4 ink + UIShadow Mode Text, Offset (0, 5), BlurRadius 0, Color ink (extruded look) + optional second text shadow BlurRadius 18, Color accent, Transparency 0.35 (glow) on reward titles only.
- Reward glow: UIShadow on the item frame, Spread 6-10, BlurRadius 24-32, Color gold, Transparency 0.2, child UIGradient gold->white; pulse Transparency 0.2<->0.45 at 1.2 s Sine.
- Glass panel (only for calm/sci-fi bibles): BackgroundTransparency 0.35, knockout UIShadow (ShowBehindParent false) BlurRadius 20 Transparency 0.6, hairline UIStroke white 1 px at 0.6.

### 3.4 Reward choreography (ms; first time full length, repeats <= 1.2 s, always skippable on tap after the first)

Chest / egg / pack open [memory; structure follows PTCGP and Genshin verified above]:
| t (ms) | Step |
|---|---|
| 0 | scrim to 0.5 black over 200; UI chrome slides away 200 |
| 0-350 | container drops in from above, Back Out; on landing squash 0.85/1.15 for 80, settle 150 |
| 550-1500 | anticipation: wobble +-6 deg at ~8 Hz in 2-3 bursts with shrinking gaps (400, 300, 200 ms), scale heartbeat 1->1.06; rarity-coloured light leaks from seams (colour = rarity, before the item is seen); rising whoosh, pitch up 3-5 semitones |
| on tap / 1500 | hit-stop 60; white flash 0.8->0 over 100; 20-40 particles; radial rays (rotate 20 deg/s); lid flies off on an arc |
| +150 | item rises 0.2 -> 1.15 in 300 (Back Out), settles to 1.0 in 150; glow + rays behind; rarity sting (longer and more layered the rarer) |
| +450 | name pops word by word 50 ms apart; rarity banner slides in 250 |
| +700 | count "x12" punches 1 -> 1.3 -> 1 in 200; stats roll up 500-800 |
| +1100 | Collect button fades in (delay prevents an accidental skip of the best moment) |

Coin fly-to-counter [verified pieces + memory]:
- Spawn min(amount, 10) icons [verified cap of 10: https://sstyles93.github.io/blogs/mmgs_bezier]; burst outward 40-80 px over 150-250 ms (Quad Out), pause 50-100 ms. Burst-then-zoom is the CoinZoom pattern. [verified: https://github.com/leonard4/CoinZoom (search summary)]
- Fly each on a quadratic bezier with the control point randomly scattered above the start [verified: MarbleMaze URL], EaseInOutCubic [verified: same] (or Quart Out over ~0.5 s as in GDQuest [verified: https://school.gdquest.com/courses/learn_2d_gamedev_godot_4/tower_defense_upgrades/collecting_coins (search summary)]); duration 450-700 ms, stagger 30-60 ms, scale 1 -> 0.6 near the target.
- The counter starts counting when the FIRST icon lands and tweens over 1 s [verified: MarbleMaze URL]; each landing punches the counter icon 1 -> 1.2 -> 1 in 120 ms and plays a tick whose pitch rises 1 semitone per coin (cap +12) [memory]; sparkle at the counter on the last one.

Level-up [memory]: bar fills to 100% (600, InOut Cubic) -> hold 100 -> flash -> "LEVEL UP" scales 2.5 -> 1 with rotation -10 -> 0 deg in 350 (Back Out) + camera/UI shake trauma 0.3 + confetti 1.5 s -> level number flips (old slides up, new rises with 10% overshoot) -> unlocked rewards cascade 80 ms apart -> Continue after 600. Total ~2.5 s.
Results stars: see game-ui.md (250 ms stagger, 2.2 -> 1 scale, rising pitch).

Rules of reward design [memory]: (1) anticipation length scales with rarity; (2) colour announces rarity before the item; (3) the player's own gesture triggers the reveal (tap, swipe, hold) when possible; (4) one big beat per reward, not ten small ones; (5) repeats get faster, never slower; (6) the number change itself is animated, never just replaced.

### 3.5 Buttons and micro-interactions (adds to game-ui.md states)

[memory]:
- Primary CTA idle "breath": scale 1.00 <-> 1.04 every 1.2 s (Sine InOut), only on the ONE button you want pressed; plus a shine sweep: a white diagonal band 20% of width, transparency 0.65, crossing in 600 ms every 3-4 s.
- Notification dot: bounce 1 -> 1.25 -> 1 every 4 s; never more than 2 dots on screen.
- Card hover/selection: lift -12 px and scale 1.05 in 150 ms; selected -24 px and 1.08 (Balatro-style values from the guide [verified: blakecrosley URL]); tilt toward the pointer up to 6-8 deg on touch-drag.
- Denied action: shake x +-6 px, 3 cycles in 300 ms, red flash on the price, low "bonk" sound.
- Long-press: radial fill ring 400-600 ms, haptic/sound at completion.
- Toggle: knob travel 180 ms with 10% overshoot; track colour cross-fades 120 ms.
- Value change anywhere: juice it (2.3 Balatro wobble, amount 0.15-0.3) and colour-flash the delta (+green / -red) for 400 ms.
- Scroll lists: items enter with 30-50 ms stagger, 12-20 px rise, 200 ms; never more than ~8 staggered at once (cap total at 400 ms).
- Panel open: Back Out 0.88 -> 1 over 280 ms (game-ui.md), content cascades in 60 ms after the frame lands; close is faster (180 ms, In).

### 3.6 Sound pairing

- Every interactive event gets a sound; jump SFX in Mario Wonder varies with how the player jumps, and pipe SFX were retimed to the animation instead of the button press. [verified: Nintendo Ask the Developer URL] Rule: fire sounds on the contact/impact frame of the animation.
- Pitch ladders: Balatro plays a rising note per scored card (C, D, E, F, G) with a separate "ka-ching" layer for multipliers and a bass drop + flash on thresholds. [verified: blakecrosley URL] Use a major pentatonic ladder (C D E G A C') for streaks so any sequence sounds pleasant [memory].
- Randomise pitch +-3-5% and volume +-1.5 dB on repeated sounds (taps, coins, footsteps) to avoid the machine-gun effect [memory].
- Loudness hierarchy [memory]: UI taps -18 to -14 dBFS, confirms -14 to -10, rewards -10 to -6, music bed under VO -20 to -16.
- Sound family matches the bible's material: wood (clack, knock), water (plink, bloop), glass/lab (ting, soft synth blip), paper (swish, stamp) [memory].
- Latency: sound within 50 ms of the visual [memory].

### 3.7 Typography

- Fonts are identity: Sakurai uses Splatoon 3 among his examples of how changing fonts and colours of even a settings menu changes how players perceive a game. [verified: https://gonintendo.com/contents/20898-masahiro-sakurai-stresses-the-importance-of-fonts-and-menu-design-in-latest-dev]
- Roblox pairings by personality (Enum.Font names verified in game-ui.md) [memory]:
| Personality | Display (titles, numbers, buttons) | Body | Accent (sparingly) |
|---|---|---|---|
| Toy / slapstick | LuckiestGuy | BuilderSans ExtraBold | none |
| Cosy / hand-made | FredokaOne | Nunito (Bold/ExtraBold via Font.new weight) | PatrickHand or Kalam for journal labels >= 20 px |
| Arcade / action | Bangers or DenkOne | BuilderSans Bold | none |
| Sci-fi clean | Michroma (short titles only) | TitilliumWeb or Jura | RobotoMono for numbers |
| Storybook / fantasy | Merriweather (bold) | Nunito | AmaticSC for decorative single words |
- Numbers that count must not jitter: right-align them in a fixed-width label, or use a monospace (RobotoMono) for live counters [memory].
- Display text treatment [memory]: stroke 8-12% of font size (UIStroke), hard text shadow offset 6-10% of size downward (UIShadow Mode Text, BlurRadius 0), vertical gradient on the fill (top 15% lighter); rotate headline -3 to -6 deg in energetic bibles.
- Google Fonts for video (OFL) by personality [memory]: chunky toy "Lilita One", "Luckiest Guy", "Titan One"; cosy "Fredoka", "Baloo 2", "Nunito"; editorial "Fraunces", "Bricolage Grotesque", "Instrument Serif"; tech "Space Grotesk", "Sora", "JetBrains Mono", "IBM Plex Mono".

### 3.8 Layout grid (phone landscape; adds to game-ui.md HUD map)

[memory]: reference 844x390; 12 columns, 16 px margins, 8 px gutters; spacing scale 4, 8, 12, 16, 24, 32, 48 only; panel widths snap to 6, 8 or 10 columns; panels 60-85% of screen height; one primary action per screen bottom-centre or bottom-right of the panel; tap targets >= 48 with >= 8 apart; thumbs' corners clear in play. Asymmetry beats centring: put the hero visual (3D item in a ViewportFrame) left 5 columns and info right 7, rather than centring everything.

### 3.9 Colour system for UI

[memory]:
- Roles: ink (outline/text), paper (panel face), brand (1 hue), reward (gold), danger (coral/red), info (aqua), disabled (desaturated, 0.5 transparency). Use the 60/30/10 split per screen: paper 60, brand 30, reward/danger accents 10.
- States: hover +8% lightness, pressed -12% lightness + inset shadow, disabled -70% saturation.
- Rarity ramp increases hue, value and saturation together, and adds motion tiers: common static grey -> uncommon green static -> rare blue with shine sweep -> epic purple with particles -> legendary gold with rays + particles -> mythic animated hue cycle. Motion tier matters more than colour.
- One colour means one thing everywhere (Roblox's own guide: unaffordable price always red, grey for unusable [verified in game-ui.md]).

### 3.10 Iconography

[memory]: one style only: filled two-tone with the same ink outline as the UI (3 px at 48 px), light from top-left (lighter top half), 4 px padding inside a 48 grid, silhouette readable at 24 px; reward icons tilted 10-15 deg and slightly oversized (they "pop" out of their frame by 10-20%); never emoji, never mixed line + filled; for in-game items render the real 3D model (ViewportFrame or pre-rendered PNG from Blender with the R5 studio recipe) so icons match the world.

### 3.11 Diegetic / themed UI ideas per genre

[memory]:
- Toy siege: buttons are alphabet blocks; the power meter is a tape measure or a wind-up key; stars are wooden star stickers; level map is a playroom rug with a drawn road; results board is a chalkboard; pause is a toy-box lid.
- Cosy pond: buttons are lily pads with a notch; every tap emits a ripple ring (scale 0.6 -> 1.6, transparency 0.4 -> 1, 450 ms); the collection book is a field journal with tape corners and pressed specimens; the hint pointer is a dragonfly; currency is a smooth pebble.
- Science reel: labels are specimen tags; numbers sit inside measuring brackets; transitions use an aperture/iris; progress is a test-tube filling.

Rules (UI, summary in the final list).

---------------------------------------------------------------------

## 5. CREATIVE DIRECTION METHOD: a style bible in one hour

Professional pattern: pillars first, then research and shared moodboards, then concepts, then an art bible of rules with examples, then discipline style guides, then per-level plans. [verified: https://sites.google.com/view/demetrius-leal/art-bible-art-plans-and-style-guides (The Callisto Protocol)] A bible is the single source of truth for every asset and must cover palette, lighting, shape language, proportions and detail density; retrofitting a style mid-project is one of the costliest mistakes. [verified: https://www.juegostudio.com/blog/art-direction-in-games and https://www.ixiegaming.com/?p=35038 (search summaries)] Monument Valley and Hades both made a whole-game colour script early. [verified: 1.2 and 1.7 sources]

### 5.1 Procedure a code-writing model can run [memory: synthesis]
1. Brief (5 min): write the player/viewer, platform, the one feeling ("the giggle when a tower falls"), and 3 games/films the audience already loves.
2. Moodboard (15 min): 12 real references (no AI images): 4 for world/shape, 4 for material/surface, 4 for light/colour. Plus 3 "anti" references (what we must not look like). For each write one line: "steal X". Sources: the studies in 1.7/3.1, Game UI Database, 80.lv, ArtStation, film stills, real toys/products.
3. Three keywords (5 min): one for FORM (chunky, round, angular, spindly), one for MATERIAL (painted wood, clay, glass, paper), one for MOOD (slapstick, gentle, precise). Plus one anti-keyword. If a keyword could describe any game ("fun", "colourful", "clean"), replace it.
4. Translate every keyword into rules on 8 channels (15 min): shape, colour (hex, 60/30/10, sacred colour), material, light recipe, camera, motion personality (easing, overshoot %, damping ratio, timing), UI identity (silhouette, angle, texture, ornament, mascot), sound family, typography. Every rule has a number.
5. Signature motif (5 min): one thing a player could draw from memory, that appears in world, UI and video (ink splat, alphabet block, ripple, specimen tag).
6. Style frames (the proof, by the agent): one hero render (world + character + light), one UI screen (the shop or results), one 3-second motion test (the core verb + its reward). Render, then look.
7. Stress test (10 min): (a) greyscale: reads? (b) 64 px thumbnail: subject findable in 1 s? (c) silhouette of the hero asset nameable? (d) cover the logo: could this be another game? (e) phone at arm's length: smallest text readable? (f) colour-blind (deuteranopia) check on rarity/state colours; (g) 10-second test with the sound off: does motion alone say what happened? Fix and re-render.
8. Lock: one page, below; every later asset is checked against it; changes are edits to the page, not ad-hoc.

Template (copy for each new project):
```
TITLE / one-line feeling
KEYWORDS: form / material / mood ; ANTI: ...
PALETTE: hex + role + share (60/30/10), sacred colour, shadow tint, neutrals
TYPE: display / body / accent (Roblox Enum + Google equivalent), sizes, stroke, rotation
SHAPE: role shapes, chamfer %, exaggeration, jitter, detail budget
MATERIALS: family + Principled numbers
LIGHT: recipe (key/fill/rim colours, strengths, angles), atmosphere, post chain
CAMERA: lenses, angles, DOF
MOTION: easing names, overshoot %, damping, anticipation frames, idle loops, shake budget
UI IDENTITY: silhouette, angle, texture, ornament, mascot, button recipe
SOUND: family, pitch ladder
SIGNATURE MOTIF: where it appears (world / UI / video)
NEVER: 5 bans
```

### 5.2 Style bible A: TOY SIEGE (toy-siege physics game, Roblox) [memory: design]
- Feeling: "knocking over your little brother's block castle, and the room cheering". Keywords: CHUNKY / PAINTED WOOD + RUBBER / SLAPSTICK. Anti: war, realism, grime.
- Palette: playroom cream #F6EAD4 (world + panels, 60%); ink navy #1E2A4A (outlines, text); block red #E8503F, block blue #2F7DE1, block green #4CB963, raw wood #D9A86C (structures, 30%); SACRED duck yellow #FFD21F (ducks and duck rewards only); coin gold #FFB81F / shade #D68C1E; TNT orange #FF6A2B; glass #A8E6F0 at 0.4; shadow tint #6C6FB0; highlight #FFF6E0; window sky #A8CCFF. Themes keep the system and swap the dominant: Picnic Park dominant grass #8ED16B, Moon Castle dominant night #1B2340 with practical-lit blocks.
- Type: Roblox LuckiestGuy (titles, numbers, buttons, ALL CAPS) + BuilderSans ExtraBold (body); video Lilita One + Nunito 800. Display stroke 10% of size in ink, hard text shadow (UIShadow Mode Text) offset 8% down; headers rotated -3 deg.
- Shape: everything is a toy-store toy: blocks with 8% chamfer (wood) or 20% (rubber/foam), cylinders and arches from a child's block set; cannons with oversized 1.5x wheels; ducks round; jitter rot +-2 deg on stacked blocks; detail 10% (wood grain, painted letters on block faces, nail heads). Role shapes: fortress square, ducks/coins round, TNT and spikes triangular.
- Materials: painted wood (roughness 0.6, edge wear to raw wood on 10% of edges), ABS for cannons (0.25), squeaky rubber ducks (coat 0.5), felt rug floor.
- Light: R1 sunny diorama through a playroom window: sun #FFE2BF strength 3.5, elevation 40 deg, 45 deg off camera toward the back; world #A8CCFF 0.7; ground bounce rug colour 15%; window light shafts with volume density 0.005. Post: AO, bloom threshold 0.9, vignette 20%, grain 2%. Trailer: low 24 mm hero on the cannon, 100 mm diorama with tilt-shift on the fortress.
- Motion: slapstick: anticipation 6-8 f before every shot (cannon recoils back 10%), overshoot 15-25% (spring z 0.45), squash 0.8 on landings, hit-stop 3 f on big hits, COLLAPSE = 30% slow-mo for 1 s + trauma 0.6 + confetti; UI juice amount 0.3 on every coin/score change; panels Back Out 300 ms.
- UI identity: buttons are alphabet blocks (square, deep 8 px hard lip via UIShadow BlurRadius 0, embossed icon/letter, per-corner radius 10%); ribbons are rows of letter blocks spelling the title (W-I-N); stars are wooden star stickers; power meter = tape measure; texture: wood grain at 8% on panels; ornament: painted dots; mascot: the rubber duck (cheers, faints on fail).
- Sound: wood clacks, block tumbles, rubber squeaks, toy drum and kazoo stings; coin ladder in C major pentatonic.
- SIGNATURE MOTIF: alphabet blocks + rubber duck (world, UI buttons, logo, thumbnails).
- NEVER: metal grime, realistic explosions, thin UI type, grey shadows, a button without a lip.

### 5.3 Style bible B: LILY PAD (cosy pond collecting game, Roblox) [memory: design]
- Feeling: "a quiet misty morning by a pond, finding something new under every pad". Keywords: ROUND / CLAY + GLAZED CERAMIC + WATER / GENTLE. Anti: neon, sharp, frantic.
- Palette: morning cream #FFF4E6 (panels, 60% of UI); pond teal #2EC4B6 -> deep #1B6F86 (world dominant); lily green #7CC36B / shade #3E8E5A / highlight #CBEA8A; petal pink #F7A8C4 / shade #D9668F; ink #24405A (soft teal-navy, never black); reward butter #FFD873; mist #DDEFEF; SACRED dragonfly violet #6C7BF2 (rare finds only); shadow tint #7A8FB8.
- Type: Roblox FredokaOne (titles, numbers) + Nunito ExtraBold (body) + PatrickHand for journal notes only (>= 20 px); video Fredoka 600 + Nunito 800 + Caveat for notes. Stroke 6% in ink (softer than Toy Siege), no hard text shadow (soft one: BlurRadius 6, transparency 0.7).
- Shape: round everything: corner radius >= 30% of size; pads are circles with a 30-40 deg notch; creatures are one-skin clay blobs with big glinting eyes; only hazards (reeds, pike, herons) get points; wonky clay jitter +-3%; detail clusters on pads (dew drops, flowers).
- Materials: clay creatures (roughness 0.85, fingerprint bump 0.02), glazed ceramic shells/pebbles (coat 1.0), stylised water (depth gradient, foam rings, roughness 0.05), soft felt-like moss (sheen 0.6).
- Light: R3 overcast morning: big soft overhead area #FFF4E6, world #F2EEE6 1.0, rim #FFE9F0 0.5x, low mist in pale teal (volume 0.003); evening levels R2 golden hour at 12 deg. Post: bloom on dew and fireflies only, vignette 15%, grain 2%, slight warm grade.
- Motion: gentle: Sine/Quart easings, overshoot <= 5% (z 0.75-0.8), idle bobs T 2.4-3.2 s, frog hop: anticipation 5 f, squash 0.85, stretch 1.15, land ripple; NO screen shake (replace with a ripple ring); panel pops 350 ms Quart Out; collection reveals slow (anticipation 800 ms, colour glow by rarity).
- UI identity: lily-pad buttons (circle with notch, or leaf shape with TopLeft/BottomRight radius 50% and the other two 10%); every tap emits a ripple ring (scale 0.6 -> 1.6, transparency 0.4 -> 1, 450 ms); collection book = field journal with tape corners and pressed specimens; texture: watercolour paper at 6%; ornament: dew drops; mascot: a small frog that sits on the edge of panels; hint pointer = dragonfly.
- Sound: water plinks, bloops, soft marimba ladder (pentatonic), wind chimes for rare finds, frogs croak on fail.
- SIGNATURE MOTIF: the ripple ring (world hops, UI taps, transitions, logo).
- NEVER: black outlines, red alarms, shake, hard edges on friendly things, more than one popup at a time.

### 5.4 Style bible C: TINY LAB (science reel series, three.js/HyperFrames + Blender stills) [memory: design]
- Feeling: "a museum specimen drawer opened in the dark, one glowing fact at a time". Keywords: PRECISE / GLASS + PAPER ON VELVET / CURIOUS. Anti: stock footage clutter, cartoon bounce, AI imagery.
- Palette: velvet black #121014 (60%); specimen paper #F2EDE3 (cards, tags); ink #1A1A1A (text on paper); lumen cyan #45D9F5 (light, leader lines, glows; 30% of accents); SACRED signal orange #FF7A2F (the one key number per episode); soft violet #8C7CF0 (secondary data); warm grey #8A847B (muted labels). Captions white #FFFFFF on velvet with 8 px #121014 stroke.
- Type (Google Fonts): headlines Instrument Serif (italic for the key word), captions Inter Tight 800 at 72-80 px, numbers/labels IBM Plex Mono 600 (tabular). Sizes: hero number 220, headline 120, caption 76, label 44.
- Shape: no rounded-rectangle cards: specimen tags (rectangle 2:1, 6 px radius, punched hole + thin string line to the object), corner brackets (4 L-shapes, 6 px stroke, 40 px arms) to frame the subject, tick-mark rulers for scale; circles only for focus rings.
- Materials (3D): frosted glass (transmission 0.9, roughness 0.25), matte paper, brushed metal pins, black velvet backdrop (sheen 0.8, base #121014).
- Light: macro specimen: overhead area key 30 deg in front, 2x subject size, #FFF3E6; cyan rim #45D9F5 at 1.5x key from behind; backdrop falls to black; dust motes in the key beam (volume 0.01); 100 mm lens, shallow DOF (tilt-shift maths in 1.5). Post: bloom threshold 0.85 on cyan only, vignette 30%, grain 3%, cool shadows.
- Motion: precise and calm: entries easeOutExpo 500-700 ms, exits 250 ms emphasized-accelerate; leader lines draw 400 ms then labels; numbers count up 1 s from 60%; camera push-in 5% over 4 s per beat, orbit 12 deg/s; one "eureka" punch per episode (the orange number 1 -> 1.12 -> 1 with a glass ting); no other bounce; transitions: rack focus 15 f or aperture iris 12 f.
- Layout: subject in brackets in the upper-middle (y 400-1100), caption at y 1250-1450, tag/label lanes left and right inside x 72-936; top progress bar 8 px cyan with chapter ticks.
- Sound: soft synth blips, glass tings, low drone bed, paper slides for tags.
- SIGNATURE MOTIF: the specimen tag + corner brackets (open: specimen framed in brackets; end card: the tag with the takeaway).
- NEVER: emoji, stock "whoosh" on every cut, more than one accent per frame plus orange, captions over the subject, AI-generated footage.

---------------------------------------------------------------------

## RULES FOR 3D (ordered by impact)
1. Write the style bible first; every asset uses its palette, material family, chamfer level and light recipe.
2. Lock the hero camera before modelling; model detail only where it sees.
3. Big/medium/small on every asset: >= 60% rest area, <= 10% small detail in 1-2 clusters at the focal point.
4. Check value in greyscale: 3-4 value groups, subject vs neighbour >= 30 L*.
5. Full saturation on <= 15% of the frame, all of it on the focal subject; background at 30-60% of subject chroma.
6. Warm key, cool fill; shadows on white must sample blue-violet, never neutral grey.
7. Always rim or backlight the hero (1-1.5x key) so it separates from the background.
8. Key:fill 2:1-3:1 for stylised; pick R1-R5 per scene, never a neutral studio light for a world shot.
9. Hue-shift ramps: shadows rotate 15-30 deg toward blue and +10-20% saturation; highlights 10-20 deg toward yellow.
10. No pure black, white or grey on surfaces; tint neutrals 5-10% toward the ambient hue.
11. Every large surface gets a gradient (5-12% lighter toward the light/top).
12. One material family per project; give each material one tell (coat glint, edge wear, sheen, SSS glow).
13. One chamfer level per project (2-4% hard, 5-12% wood/stone, 12-25% toy/vinyl), applied to everything.
14. Push one proportion per asset 20-50% past real; thin parts >= 1.5x real thickness.
15. Jitter repeated pieces (rot +-1-4 deg, scale +-3-6%, pos +-1-3%); keep the footprint flat.
16. Role shapes: friendly round, structural square, dangerous pointed; never break it.
17. Silhouette test at 64 px black fill: nameable, >= 3 bumps, no tangents, a hole of negative space on big things.
18. Three depth planes with >= 1 value step between them; dark blurred foreground on 10-25% of one edge.
19. Atmosphere: mist 20-40% sky colour toward the back; volumetrics only with a light behind the haze.
20. Fake GI with a ground-coloured up-light at 10-20% of key in EEVEE.
21. Diorama read = 30-45 deg down + 85-135 mm + shallow DOF + visible world edge; divide f-stop by the scene-to-miniature scale.
22. Lens by intent: 24 mm dynamic/heroic low, 50 mm neutral, 85-135 mm miniature/product.
23. 9:16: subject in the upper third; nothing important below y 1500.
24. Finish every render: AO, bloom threshold >= 0.8, cool-shadow/warm-highlight grade, vignette 15-30%, grain 2-4%.
25. Make a colour script table before a multi-level game or multi-scene video; neighbours differ in temperature or key.
26. Reserve one sacred colour for the player/reward; nothing else uses it.
27. Detail density follows the toy's real size, not the depicted world's size.
28. Render a wide shot and a low close-up; judge both before calling it done.

## RULES FOR ANIMATION/MOTION (ordered by impact)
1. Never move two things on the same frame: offset parts 1-3 frames, children 2-4 frames behind parents (amplitude x0.7 per level).
2. Nothing linear except constant mechanical loops; use the easing table (M3 standard (0.2,0,0,1), expo-out (0.16,1,0.3,1), back-out (0.34,1.56,0.64,1)).
3. Anticipate every significant action: 5-20% of the travel backwards, 3-5 f for UI, 6-12 f for characters.
4. Overshoot and settle: UI 3-8%, characters 5-15%, cartoon 20-30%; choose by spring damping (0.8 = 1%, 0.6 = 9.5%, 0.45 = 21%).
5. Contrast timing: fast actions (4-6 f) next to holds (8-15 f); hold every key pose long enough to read.
6. Squash and stretch with volume preserved (sx = 1/sqrt(sy)); landing 0.8 for 2-4 f, takeoff 1.2 along velocity.
7. Move on arcs: limbs and flying objects follow curves; rotate flying objects along velocity.
8. Nothing static for more than 2 s: idle bob (3-6% height, 1.6-2.4 s), breathing (1-2%, 3-4 s), randomised phase per instance.
9. Blink every 2-6 s at random (close 2 f, hold 1, open 3-4), 15-20% double blinks, always at the start of a head turn.
10. Eyes lead, head follows 2-4 f later, body 2-4 f after the head.
11. Juice every value change with a decaying sine wobble (Balatro: ~8 Hz scale, ~6.5 Hz rotation, 0.4 s, cubic decay).
12. Sound fires on the animation's contact frame, not on the input.
13. Camera shake = trauma^2 x Perlin; phones max 2-4 deg roll; decay 1-1.5/s; scale to 25% with reduced motion.
14. Hit-stop 2-5 frames on impacts that matter; slow-mo (20-30%) only for the one biggest moment.
15. Procedural walks: plant feet (no sliding), body bob at 2x step frequency, arms opposite legs lagging 2-3 f, hips yaw +-5-8 deg.
16. Walk 15 f per step at 30 fps (brisk), run 5-8 f; drive cycle speed from real ground speed.
17. Roblox R15: animate from LowerTorso (drop 0.1-0.3 stud on contacts), twist UpperTorso +-10-15 deg, offset limbs, never key the root for poses.
18. Use the new R15 fingers and clavicles for hand shapes and shrugs; pair every facial change with a 5-10 deg head tilt.
19. Faces via FaceControls: smile = LipCornerPuller 0.7 + CheekRaiser 0.4; surprise = brow raisers 0.8 + upper lid 0.6 + JawDrop 0.4 in 3 f.
20. Give every creature/NPC 2-3 off-duty idle moods triggered at random and on proximity (Mario Wonder's Goombas).
21. Video entries ease-out (fast start, long settle) 400-700 ms; exits 30-40% shorter with ease-in.
22. Stagger lists and words 30-60 ms; cap a cascade at ~400-600 ms total.
23. Push-ins 5-12% over 3-6 s on beats, never one constant zoom; parallax speed proportional to 1/depth.
24. Count numbers up from ~60-70% of the value over 0.8-1.2 s, land with a 3-5% punch and a tick.
25. Hold every caption for reading time (~3 words/s) + 0.5 s; cut and key on beats or stressed syllables.
26. One transition family per series; whip pans 6-10 f with the cut inside the blur.
27. Motion personality comes from the bible: slapstick (z 0.45, big squash), gentle (z 0.8, no shake), precise (expo-out, no bounce).

## RULES FOR UI (ordered by impact)
1. Give the kit a signature silhouette (block, lily pad, tag, ticket, skewed panel) instead of the plain rounded rectangle; use per-corner radii.
2. One sacred colour for the one thing you want pressed or wanted (reward/primary), 60/30/10 per screen.
3. Use the 2026 Roblox primitives: UIShadow hard lip (BlurRadius 0, Offset 0,6) + soft drop (Offset 0,12, Blur 14, T 0.75); Inset shadow for pressed; Mode Text for chunky titles.
4. Put palette, radii, strokes, fonts in one StyleSheet with tokens; no per-screen styling.
5. Every value change is animated: wobble (amount 0.15-0.3), colour-flash the delta 400 ms, never a silent swap.
6. Rewards: anticipation scales with rarity, colour reveals rarity before the item, the player's gesture triggers the reveal, one big beat, repeats faster and skippable.
7. Coins fly in arcs (<= 10 icons, 30-60 ms stagger, 450-700 ms InOutCubic); the counter starts on the first landing and rises over ~1 s with a rising-pitch tick.
8. Every interactive element has pressed, disabled and denied states with sound; press 60 ms down, 150 ms up.
9. Exactly one primary CTA per screen; only it breathes (1.04 scale, 1.2 s) and gets a shine sweep every 3-4 s.
10. Two fonts maximum, chosen by the bible's personality; display text gets a stroke of 8-12% of size plus a hard shadow 6-10% down.
11. Live counters never jitter: fixed-width right-aligned labels or a mono font.
12. Add one texture at 5-15% opacity to panels (wood, paper, felt, grain).
13. One ornament family, on at most 1-2 elements per screen.
14. A mascot reacts in empty states, loading, tutorial and results.
15. Sound family matches the material; randomise pitch +-3-5%; pentatonic pitch ladders for streaks.
16. Panels open Back Out 0.88 -> 1 in 280 ms, content cascades 60 ms later; close faster (180 ms).
17. Rarity = hue + value + saturation + motion tier (static, shine, particles, rays, hue cycle).
18. Icons: one style (filled two-tone + UI stroke, light top-left), readable at 24 px, rewards tilted 10-15 deg; in-game items rendered from the real 3D model.
19. Grid: 844x390 reference, 12 columns, 16 margins, 8 gutters, spacing only from 4/8/12/16/24/32/48.
20. Asymmetric layouts: hero visual left 5 columns, info right 7; panels 60-85% of screen height.
21. Keep <= 100 UIShadows on screen and scale shadow pixel values by UIScale yourself.
22. Theme the frame by the reward's source (Hades' per-god boons): colour, ornament, portrait, sound.
23. Diegetic first: express meters and buttons as objects from the game's world (tape measure, lily pad, test tube).
24. HUD gets out of the way in calm play (fade to 40% after 4 s idle, back on input) except currency and the primary action.
25. Legibility beats style: if a stylised screen is hard to read, tune until it reads (Persona 5's lesson), text never below 16 px on phone.
26. Pass the cover-the-logo test: a screenshot must be identifiable as this game without its name.
27. Ban list: flat fill + default radius + centred title + X as the whole design, system fonts, emoji icons, > 2 fonts, glassmorphism on a toy game.

