# Art Direction: Making a Roblox Game Look Good

Load when building or reviewing a map, choosing a visual style, setting up Lighting, or when a place "looks like a default baseplate".

## The 5 rules that matter most

1. **Pick one style and enforce it everywhere.** One palette, one material family, one lighting preset, one level of detail. Mixed styles look worse than any single style done consistently.
2. **Light it before you decorate it.** Set `Lighting`, `Atmosphere`, `Sky` and post effects first; a good preset makes primitive blockouts look intentional, and a bad one ruins expensive assets.
3. **Value contrast carries readability.** Paths and interactables must separate from the background in greyscale. Saturate what matters; mute what does not.
4. **Every view needs a landmark and a focal point.** A tall, distinctive silhouette visible from spawn, and light/colour that pulls the eye to the next objective.
5. **No defaults left visible.** No grey `Plastic` baseplate, no 4x4 grid texture, no stock sky with nothing in it, no free-model soup at mismatched scales.

---

## 1. Choose a style

| Style | Lighting | Materials | Palette | Post | Fits |
|---|---|---|---|---|---|
| Stylised low-poly | `LightingStyle.Soft`, sunny | `SmoothPlastic`, flat-shaded meshes, few textures | 5-7 saturated mid-values | Light bloom, +0.1 saturation | Simulators, adventure, obby |
| Bright cartoon ("Adopt Me") | `Soft`, high ambient, soft shadows | `SmoothPlastic`, rounded meshes, subtle gradients | Pastels + one strong accent | Bloom 0.3-0.5, +0.15 saturation | Social/roleplay, pets, kids-first |
| Realistic PBR | `Realistic`, `PrioritizeLightingQuality` on | 2022 materials, `MaterialVariant`, `SurfaceAppearance` | Natural, desaturated, value-driven | Atmosphere haze, mild contrast | Shooters, survival, exploration |
| Neon / sci-fi | `Realistic`, night or interior | Dark `Metal`/`Glass`, `Neon` trim | Near-black + 1-2 emissive hues | Bloom 0.8-1.2, low threshold | Arenas, racing, cyber hubs |
| Horror | `Realistic`, near-zero ambient | Grimy textures, `Concrete`, `Wood`, decals | Desaturated, cold shadows, warm practical lights | Desaturate, contrast up, fog | Horror, escape |

Lighting: `Lighting.Technology` is deprecated, read-only and non-scriptable. Use `LightingStyle` (`Realistic` or `Soft`) and `PrioritizeLightingQuality`. Old mappings: Future = Realistic + priority on; ShadowMap = Soft + priority on; Voxel = Soft + priority off. https://create.roblox.com/docs/en-us/reference/engine/classes/Lighting.md

In a Rojo project, also pin the lighting style under `Lighting.$properties` in `default.project.json` so a rebuild cannot reset it; if `execute_luau` refuses to set a lighting-mode property, setting it there is the fallback.

---

## 2. Lighting properties that matter

| Property | Use |
|---|---|
| `ClockTime`, `GeographicLatitude` | Sun direction. Low sun (ClockTime 7-8 or 16.5-18) gives long shadows and warm light; noon is flat. |
| `Brightness` | Sun/moon strength. 2-3 for day, 0-1 for night. |
| `ExposureCompensation` (-5..5) | Whole-image exposure; +1 doubles. Use small steps (0.1-0.3). |
| `Ambient` | Light in places the sky cannot reach (interiors, under roofs). Keep low (0-60) for depth; raise for cartoon. |
| `OutdoorAmbient` | Sky fill outdoors. Clamped to at least `Ambient`. |
| `EnvironmentDiffuseScale` / `EnvironmentSpecularScale` (0-1) | Sky-driven fill and reflections. Specular 1 makes metal and wet surfaces read; lower `Ambient` when raising diffuse. |
| `ColorShift_Top` / `ColorShift_Bottom` | Tint of sun-lit / away-facing surfaces. Warm top for golden hour. |
| `ShadowSoftness` (default 0.2) | Higher reads softer and more cartoony. |
| `GlobalShadows` | Leave on. |

When an `Atmosphere` exists in Lighting, `FogStart`/`FogEnd`/`FogColor` are ignored.

### Atmosphere, Sky, Clouds

- `Atmosphere`: `Density` (0-1) thickness, `Offset` (horizon haze vs sky), `Color` (in-scatter tint), `Decay` (far colour), `Glare` (0-10, sun halo), `Haze` (0-10, distance murk). Atmosphere is what sells scale: distant objects fade into `Decay`.
- `Sky`: replace the default skybox when the style demands it (cartoon gradient sky, starfield for sci-fi). `SunAngularSize`, `MoonAngularSize`, `StarCount`, `CelestialBodiesShown`.
- `Clouds` (parented to `Workspace.Terrain`): `Cover` (0-1), `Density` (0-1), `Color`. Dynamic clouds only render with terrain present.

### Post effects (in `Lighting`)

| Effect | Typical range | Notes |
|---|---|---|
| `BloomEffect` | Intensity 0.3-1, Size 18-40, Threshold 0.8-2 | Lower threshold = more things glow; keep high for daylight |
| `ColorCorrectionEffect` | Brightness -0.05..0.05, Contrast 0-0.2, Saturation -0.4..0.25, TintColor | Grade, do not repaint; big swings look cheap |
| `SunRaysEffect` | Intensity 0.03-0.15, Spread 0.5-1 | Only reads when the sun is in view |
| `DepthOfFieldEffect` | FarIntensity 0.1-0.3, InFocusRadius 30-60 | Menus, cutscenes, photo modes. Avoid in gameplay; it blurs targets. |
| `ColorGradingEffect` | `TonemapperPreset` | `Retro` imitates pre-2019 Roblox lighting; use only on purpose |

---

## 3. Worked presets

Starting points, not law. Apply in Edit with `execute_luau`, then compare with `screen_capture`.

```lua
-- datamodel_type = "Edit"; wrap in a ChangeHistoryService recording (see studio-mcp.md)
local Lighting = game:GetService("Lighting")

local PRESETS = {
	CartoonDay = {
		lighting = { LightingStyle = Enum.LightingStyle.Soft, PrioritizeLightingQuality = true,
			ClockTime = 14, GeographicLatitude = 35, Brightness = 3, ExposureCompensation = 0.2,
			Ambient = Color3.fromRGB(70, 70, 80), OutdoorAmbient = Color3.fromRGB(140, 140, 150),
			EnvironmentDiffuseScale = 0.6, EnvironmentSpecularScale = 0.3, ShadowSoftness = 0.4 },
		atmosphere = { Density = 0.25, Offset = 0.1, Color = Color3.fromRGB(199, 220, 255),
			Decay = Color3.fromRGB(120, 150, 200), Glare = 0, Haze = 0.5 },
		clouds = { Cover = 0.45, Density = 0.5, Color = Color3.fromRGB(255, 255, 255) },
		bloom = { Intensity = 0.4, Size = 24, Threshold = 1.5 },
		cc = { Brightness = 0.02, Contrast = 0.05, Saturation = 0.15, TintColor = Color3.fromRGB(255, 255, 255) },
		sunRays = { Intensity = 0.05, Spread = 0.6 },
	},
	GoldenHour = {
		lighting = { LightingStyle = Enum.LightingStyle.Realistic, PrioritizeLightingQuality = true,
			ClockTime = 17.6, GeographicLatitude = 40, Brightness = 2.5, ExposureCompensation = 0,
			Ambient = Color3.fromRGB(60, 50, 50), OutdoorAmbient = Color3.fromRGB(150, 120, 110),
			ColorShift_Top = Color3.fromRGB(255, 200, 150), EnvironmentDiffuseScale = 1,
			EnvironmentSpecularScale = 1, ShadowSoftness = 0.25 },
		atmosphere = { Density = 0.35, Offset = 0.25, Color = Color3.fromRGB(255, 200, 160),
			Decay = Color3.fromRGB(130, 90, 90), Glare = 0.6, Haze = 1.8 },
		clouds = { Cover = 0.55, Density = 0.6, Color = Color3.fromRGB(255, 225, 200) },
		bloom = { Intensity = 0.6, Size = 24, Threshold = 1.2 },
		cc = { Brightness = 0, Contrast = 0.1, Saturation = 0.1, TintColor = Color3.fromRGB(255, 240, 225) },
		sunRays = { Intensity = 0.12, Spread = 0.8 },
	},
	Overcast = {
		lighting = { LightingStyle = Enum.LightingStyle.Realistic, PrioritizeLightingQuality = true,
			ClockTime = 13, GeographicLatitude = 50, Brightness = 1.5, ExposureCompensation = -0.2,
			Ambient = Color3.fromRGB(40, 42, 48), OutdoorAmbient = Color3.fromRGB(120, 125, 135),
			EnvironmentDiffuseScale = 1, EnvironmentSpecularScale = 1, ShadowSoftness = 0.8 },
		atmosphere = { Density = 0.45, Offset = 0, Color = Color3.fromRGB(180, 185, 195),
			Decay = Color3.fromRGB(110, 115, 125), Glare = 0, Haze = 2.5 },
		clouds = { Cover = 0.85, Density = 0.8, Color = Color3.fromRGB(200, 200, 205) },
		bloom = { Intensity = 0.3, Size = 24, Threshold = 2 },
		cc = { Brightness = 0, Contrast = 0.1, Saturation = -0.15, TintColor = Color3.fromRGB(245, 248, 255) },
	},
	NeonNight = {
		lighting = { LightingStyle = Enum.LightingStyle.Realistic, PrioritizeLightingQuality = true,
			ClockTime = 0, Brightness = 0.5, ExposureCompensation = 0.3,
			Ambient = Color3.fromRGB(20, 20, 35), OutdoorAmbient = Color3.fromRGB(40, 40, 70),
			EnvironmentDiffuseScale = 0.5, EnvironmentSpecularScale = 1, ShadowSoftness = 0.2 },
		atmosphere = { Density = 0.3, Offset = 0.1, Color = Color3.fromRGB(60, 70, 120),
			Decay = Color3.fromRGB(30, 20, 60), Glare = 0, Haze = 1 },
		bloom = { Intensity = 1, Size = 30, Threshold = 0.8 },
		cc = { Brightness = 0, Contrast = 0.15, Saturation = 0.2, TintColor = Color3.fromRGB(225, 230, 255) },
	},
	Horror = {
		lighting = { LightingStyle = Enum.LightingStyle.Realistic, PrioritizeLightingQuality = true,
			ClockTime = 2, Brightness = 0, ExposureCompensation = -0.3,
			Ambient = Color3.fromRGB(0, 0, 0), OutdoorAmbient = Color3.fromRGB(15, 15, 20),
			EnvironmentDiffuseScale = 0.2, EnvironmentSpecularScale = 0.6, ShadowSoftness = 0.3 },
		atmosphere = { Density = 0.6, Offset = 0, Color = Color3.fromRGB(40, 40, 45),
			Decay = Color3.fromRGB(20, 20, 25), Glare = 0, Haze = 3 },
		bloom = { Intensity = 0.4, Size = 20, Threshold = 1.5 },
		cc = { Brightness = -0.02, Contrast = 0.2, Saturation = -0.4, TintColor = Color3.fromRGB(210, 220, 255) },
	},
}

local function getOrCreate(parent: Instance, className: string): Instance
	return parent:FindFirstChildOfClass(className) or (function()
		local i = Instance.new(className); i.Parent = parent; return i
	end)()
end

local function apply(name: string)
	local p = assert(PRESETS[name], "unknown preset")
	for k, v in p.lighting do (Lighting :: any)[k] = v end
	for k, v in p.atmosphere do (getOrCreate(Lighting, "Atmosphere") :: any)[k] = v end
	local clouds = workspace.Terrain:FindFirstChildOfClass("Clouds")
	if p.clouds then
		clouds = clouds or getOrCreate(workspace.Terrain, "Clouds")
		for k, v in p.clouds do (clouds :: any)[k] = v end
	elseif clouds then
		clouds.Enabled = false
	end
	for k, v in p.bloom do (getOrCreate(Lighting, "BloomEffect") :: any)[k] = v end
	for k, v in p.cc do (getOrCreate(Lighting, "ColorCorrectionEffect") :: any)[k] = v end
	local rays = Lighting:FindFirstChildOfClass("SunRaysEffect")
	if p.sunRays then
		rays = rays or getOrCreate(Lighting, "SunRaysEffect")
		for k, v in p.sunRays do (rays :: any)[k] = v end
	elseif rays then
		rays.Enabled = false
	end
	return `applied {name}`
end

return apply("CartoonDay")
```

Horror extras: `Sky.CelestialBodiesShown = false`, `Sky.StarCount = 0`; give the player a `SpotLight` (Range 40, Angle 45, Brightness 2, `Shadows = true`) on the head or a held tool; place warm `PointLight`s (Range 10-14, Brightness 1, colour 255/180/120) as "safe" pools.

Neon extras: use `Neon` material only on thin trim and signage (under ~5% of visible surface); pair each large neon element with a `PointLight`/`SurfaceLight` of the same hue (Range 12-16, Brightness 1-2) so it actually lights the scene; keep surrounding surfaces dark and slightly reflective (`Metal`, `Glass`, `SmoothPlastic` with `Reflectance` 0.05-0.15 used sparingly).

---

## 4. Materials

- **Built-in materials** (the 2022 set): tile size is controlled per material; mixing more than 5-6 materials in one view looks noisy.
- **`MaterialService` + `MaterialVariant`**: override or add materials with your own PBR maps (`ColorMap`, `NormalMap`, `MetalnessMap`, `RoughnessMap`, `StudsPerTile`, `Pattern` Regular/Organic). Set `MaterialService.<Base>Name` to make a variant the place-wide default for that base material, or set `BasePart.MaterialVariant` per part. This is the cleanest way to give a whole map a coherent stylised look.
- **`SurfaceAppearance`** on a `MeshPart`: per-mesh PBR (`ColorMap`, `NormalMap`, `MetalnessMap`, `RoughnessMap`, `AlphaMode`). Normal maps must be OpenGL tangent-space. Use for hero props and characters. https://create.roblox.com/docs/en-us/art/modeling/texture-specifications
- **Texel density**: keep roughly consistent; 512 px per ~10 studs for props, 1024 for hero objects up to ~20 studs.
- **Cartoon rule of thumb**: `SmoothPlastic` + vertex/part colour + good lighting beats noisy textures.
- `Neon` and `Glass` are expensive in large areas on mobile; use them as accents.

---

## 5. Terrain

- Shape with the Terrain Editor (Generate, Sculpt, Paint) or code: `Terrain:FillBlock`, `FillBall`, `FillCylinder`, `FillWedge`, `ReplaceMaterial`, `WriteVoxels` (4-stud voxels).
- Recolour terrain to the palette: `workspace.Terrain:SetMaterialColor(Enum.Material.Grass, Color3.fromRGB(110, 170, 80))`. Default terrain colours are a strong "unstyled" tell.
- Water: `Terrain.WaterColor`, `WaterTransparency` (0.3-0.6 for readable shallow water), `WaterReflectance` (0.5-1), `WaterWaveSize` (0.05-0.2), `WaterWaveSpeed` (5-15).
- Grass: `Terrain.Decoration = true` animates grass blades on `Grass` material; `Terrain.GrassLength` 0.3-0.7 reads well. Decoration only renders near the camera and on higher graphics levels, so the grass colour still has to work bare.
- Biomes: change ground material and colour at biome borders with a 10-20 stud blend (paint mixed `Grass`/`Mud`/`Sand`), and change atmosphere colour per zone with a client script when the player crosses a boundary.
- Use `MaterialVariant`s on terrain materials (via `MaterialService`) for a stylised ground.

```lua
-- Small island: sand beach, grass top, water ring. Edit datamodel, idempotent per region.
local T = workspace.Terrain
local c = Vector3.new(0, 0, 0)
T:FillCylinder(CFrame.new(c + Vector3.new(0, -6, 0)), 12, 120, Enum.Material.Water)
T:FillCylinder(CFrame.new(c + Vector3.new(0, -2, 0)), 8, 70, Enum.Material.Sand)
T:FillCylinder(CFrame.new(c + Vector3.new(0, 1, 0)), 4, 55, Enum.Material.Grass)
T:FillBall(c + Vector3.new(15, 4, -10), 14, Enum.Material.Grass)
T:SetMaterialColor(Enum.Material.Grass, Color3.fromRGB(118, 176, 82))
T:SetMaterialColor(Enum.Material.Sand, Color3.fromRGB(232, 214, 160))
```

---

## 6. Colour and value

- **60/30/10**: 60% dominant environment colour, 30% secondary, 10% accent reserved for interactables, rewards and UI.
- **Value first**: background masses darker or lighter than the play path by at least ~20% luminance; interactables the highest contrast in view. Test with the greyscale capture (`ColorCorrection.Saturation = -1`).
- **Saturation budget**: saturate small things, mute big things. A fully saturated green field makes coins invisible.
- **Temperature**: warm = safe/reward/goal, cool = neutral/distance, desaturated red/purple = danger. Keep this consistent across zones.
- **Hazards**: one hazard colour language for the whole game (e.g. red-orange glow + stripes for kill parts), never reused for decoration.

Example palettes (hex):

| Style | Palette |
|---|---|
| Cartoon meadow | `#7CC36B` grass, `#F6E7B4` path, `#8AD1F5` water/sky, `#F49A63` roofs, `#FFD23F` accent |
| Pastel social | `#FADADD`, `#C9E4DE`, `#C6DEF1`, `#F7D9C4`, accent `#FF6F91` |
| Sci-fi | `#0D0F1A` base, `#1E2235` panels, `#00E5FF` and `#FF2E88` emissive, `#F5F7FF` text |
| Horror | `#1A1A1C`, `#3A3B3F`, `#5C5A55`, practical light `#FFB570`, danger `#8B1E1E` |

---

## 7. Composition, landmarks, silhouettes

- **Three scales**: landmark (100+ studs, visible everywhere: tower, giant tree, volcano), structures (10-40 studs: buildings, arenas), detail (1-5 studs: crates, plants, lamps). Every screenshot should contain at least two scales.
- **Landmark from spawn**: the first thing a new player sees should include the place they will want to reach.
- **Silhouette test**: a landmark must be recognisable as a black shape against the sky. Avoid flat-topped boxes; add spires, overhangs, asymmetry.
- **Clusters, not grids**: group props in odd-numbered clusters (3, 5, 7) with varied scale (0.8-1.25x) and rotation (any yaw, +/-5 degrees tilt for organic props). Leave negative space between clusters.
- **Leading lines**: paths, fences, rivers and light rows should point at objectives.
- **Framing**: arches, trees and cliffs that frame the next goal from the approach path.
- **Edges**: never show the void. Bound the map with terrain mountains, water, fog walls (Atmosphere) or dense props; place invisible walls only behind something visible.

---

## 8. Readable play spaces

- Walkable surfaces are visibly different from decoration (lighter, smoother, consistent material).
- Collision matches visuals: decoration that looks solid is `CanCollide = true`; foliage the player walks through is `CanCollide = false`. Turn off `CanTouch`/`CanQuery` on pure decoration to cut physics and raycast cost.
- Jumpable gaps and climbable edges have a consistent visual language (trim colour, a lip, a light).
- Interactables pop: accent colour, gentle idle motion (bob or rotate via client tween), a `ProximityPrompt` with a clear `ActionText`, and a `Highlight` on approach (max 31 Highlights render at once).
- Keep UI-safe areas in mind for world text: billboards above 3 studs, `MaxDistance` set.

---

## 9. Lighting for gameplay

- Light the goal brighter and warmer than its surroundings. Players walk toward light.
- Put a light source at every decision point (forks, doors, ladders).
- Darkness is a tool, not a default: if an area is dark, give the player a light or a lit exit.
- Shadow-casting local lights are expensive. Budget: a handful of `Shadows = true` lights in view; everything else `Shadows = false`. `Realistic` style renders many local lights well on capable devices but falls back on low-end.
- `Neon` parts do not light the scene by themselves; add a light if it should.

---

## 10. Avoiding the default look

| Tell | Fix |
|---|---|
| Grey `Baseplate` with grid texture | Delete it; build terrain or a styled floor |
| Default skybox, flat noon light | Apply a preset; pick a ClockTime with angle |
| Mixed free models at random scales | Rescale to a 5-stud character, recolour to palette, unify materials, strip scripts |
| Every part `Plastic`, primary colours | Palette + `SmoothPlastic`/MaterialVariants |
| Uniform rows of identical props | Clusters, varied scale/rotation, mixed prop types |
| Floating objects, gaps at joins | Snap to ground, overlap joins 0.05-0.1 studs, use wedges/corner pieces |
| Huge empty flat areas | Height variation, paths, props, landmarks every 60-100 studs of travel |
| Text-only signage | Iconic shapes, colour coding, world-space arrows |

---

## Beauty pass checklist
- Every zone has its own look (`src/client/Mood.luau`: time of day, air, water, grade). Two zones that
  differ only by a banner colour are one zone. Check it on the play sheet.
- The next target is the most visible thing on screen: a beacon, a glow or value contrast against its
  background, in every zone's lighting.

Run with `screen_capture` from the standard shot list (`studio-mcp.md` section 7).

- [ ] One documented style, palette (hex) and lighting preset
- [ ] `LightingStyle` and `PrioritizeLightingQuality` set deliberately; no reliance on `Technology`
- [ ] Atmosphere present; distant geometry fades into the decay colour
- [ ] Sky and clouds match the mood
- [ ] Bloom/colour correction subtle (no blown highlights, no crushed blacks)
- [ ] Greyscale capture: path, interactables and hazards separate clearly
- [ ] Landmark visible from spawn; focal point lit
- [ ] No default baseplate, grid textures or untouched terrain colours
- [ ] Props clustered with scale/rotation variation; no floating or z-fighting parts
- [ ] Map edges hidden; no visible void
- [ ] Collision matches visuals; decoration has `CanTouch`/`CanQuery` off where possible
- [ ] Local light budget respected; few shadow-casting lights
- [ ] Looks acceptable at low graphics quality (test with Studio's graphics slider or a device)
- [ ] All Creator Store assets audited, scripts stripped, recoloured to palette

---

## CHANGELOG

- 2026-11-03: New file. Lighting guidance uses `LightingStyle`/`PrioritizeLightingQuality` (Technology deprecated and non-scriptable).
