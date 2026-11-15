-- Run in Studio Client context while playing: studio luau scenarios/ui-themes.luau --ctx Client
-- Change ThemePreview's Theme / Screen (HUD, Shop, Result) attributes to capture each sheet state.
local Players = game:GetService("Players")
local source = Players.LocalPlayer.PlayerGui:FindFirstChild("ThemeProof")
	or Players.LocalPlayer.PlayerScripts.Client
local Kit = require(source.UiKit)
local Themes = require(game.ReplicatedStorage.Shared.Themes)
local make = Kit.make
local StarterGui = game:GetService("StarterGui")
StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.All, false)
pcall(function()
	StarterGui:SetCore("TopbarEnabled", false)
end)
local playerGui = Players.LocalPlayer.PlayerGui
for _, gui in playerGui:GetChildren() do
	if gui:IsA("ScreenGui") then
		if gui.Name == "ThemeChecks" then
			gui:Destroy()
		else
			gui.Enabled = false
		end
	end
end
local old = playerGui:FindFirstChild("ThemePreview")
if old then
	old:Destroy()
end

-- Behavioral checks also exercise a live theme change without reconstructing the components.
Kit.reducedMotion = true
local probeGui, probe = Kit.screen(playerGui, "ThemeChecks", 99, Enum.ScreenInsets.None)
Kit.setTheme("Toybox")
local legacy = Kit.Theme
local button = Kit.button(probe, { text = "Buy", Size = UDim2.fromOffset(30, 30) })
local panel = Kit.panel(probe, { title = "Shop" })
local label = Kit.text(probe, { Text = "Readable", TextSize = 10 })
local custom = Kit.panel(probe, { color = Color3.fromRGB(12, 34, 56) })
local switch, setSwitch = Kit.switch(probe, { text = "Sound", value = true })
Kit.setTheme("Royal")
assert(Kit.Theme == legacy, "legacy Theme reference must stay live")
assert(button.Face.BackgroundColor3 == Themes.Royal.color.primary, "existing button must retheme")
assert(panel.ThemeGradient.Color.Keypoints[1].Value == Themes.Royal.color.surfaceTop, "surface gradient top")
assert(label.TextColor3 == Themes.Royal.color.text and label.TextSize == 16, "text roles and floor")
assert(custom.BackgroundColor3 == Color3.fromRGB(12, 34, 56), "explicit colour wins")
task.wait()
assert(button.AbsoluteSize.X >= 48 and button.AbsoluteSize.Y >= 48, "48 px button floor")
assert(switch.Track.BackgroundColor3 == Themes.Royal.color.primary, "switch rethemes")
setSwitch(false)
assert(switch:GetAttribute("On") == false, "switch setter is retained")
Kit.setButton(button, false, "Locked")
assert(not button.Interactable and button.Face.BackgroundColor3 == Themes.Royal.color.muted, "disabled role")
Kit.setTheme("Cozy")
assert(button.Face.BackgroundColor3 == Themes.Cozy.color.muted, "disabled stays disabled on theme change")
Kit.setButton(button, true)
assert(button.Face.BackgroundColor3 == Themes.Cozy.color.primary, "re-enable uses new theme")
local override = Color3.fromRGB(23, 45, 67)
Kit.setTheme("Toybox", { color = { primary = override }, shape = { lip = 0, stroke = 0 } })
assert(button.Face.BackgroundColor3 == override and Kit.Theme.Lip == 0, "partial overrides / zero values")
assert(Themes.Toybox.color.primary ~= override, "generated tokens must not be mutated")
local ok = pcall(function()
	Kit.setTheme("Missing theme")
end)
assert(not ok and Kit.Theme.Lime == override, "unknown theme must fail without changing active tokens")
Kit.setTheme("Bubblegum")
local glyph = Kit.text(probe, { Text = "Text shadow", display = true })
assert(glyph.TextShadow.Mode == Enum.ApplyShadowMode.Text and glyph.TextShadow.Enabled, "native glyph shadow")
local scale = probe:FindFirstChildOfClass("UIScale")
scale.Scale = 1.5
local deadline = os.clock() + 2
repeat
	task.wait()
until button.Face.Lip.Offset.Y.Offset == math.floor(Kit.tokens.shape.lip * 1.5) or os.clock() > deadline
assert(
	button.Face.Lip.Offset.Y.Offset == math.floor(Kit.tokens.shape.lip * 1.5),
	"shadow offsets follow UIScale"
)
Kit.reducedMotion = true
Kit.roll(label, 42)
assert(label.Text == "42", "reduced-motion counter reaches final value")
Kit.setTheme("Royal")
assert(label.Text == "42", "live theme keeps rolled counters")
probeGui:Destroy()
Kit.reducedMotion = false
Kit.setTheme("Toybox")

local gui, root = Kit.screen(playerGui, "ThemePreview", 100, Enum.ScreenInsets.None)
gui:SetAttribute("Theme", "Toybox")
gui:SetAttribute("Screen", "HUD")
local worlds = {
	Toybox = { "7EC8F2", "CDEBFA", "8FD98A", "F5A3B8" },
	["Night Arcade"] = { "1A1147", "5B2A86", "201A3D", "FF3EC8" },
	Cozy = { "BDE3FF", "FFE9F3", "BFEAC2", "FFC2D9" },
	Royal = { "5B6E8C", "B9C4CF", "566B4A", "7D7468" },
}
local function at(x, y)
	return UDim2.fromOffset(x, y)
end
local function text(parent, value, x, y, w, h, size, display, color)
	return Kit.text(parent, {
		Text = value,
		Position = at(x, y),
		Size = at(w, h),
		TextSize = size,
		display = display,
		preserveCase = string.find(value, "Fort 3", 1, true) ~= nil,
		TextColor3 = color,
		TextWrapped = false,
	})
end
local function btn(parent, value, icon, style, x, y, w, h)
	return Kit.button(parent, {
		text = value,
		icon = icon,
		style = style,
		Position = at(x, y),
		Size = at(w, h),
		TextSize = 20,
		iconSize = 24,
	})
end
local function render()
	for _, child in root:GetChildren() do
		if not child:IsA("UIScale") then
			child:Destroy()
		end
	end
	local name = gui:GetAttribute("Theme")
	Kit.setTheme(name)
	local t = Kit.tokens
	local c, s = t.color, t.shape
	local state = gui:GetAttribute("Screen")
	local canvas = make("Frame", {
		Name = "Canvas",
		BackgroundTransparency = 1,
		Size = at(844, 390),
		Position = UDim2.fromScale(0.5, 0.5),
		AnchorPoint = Vector2.new(0.5, 0.5),
		Parent = root,
	})
	local world = worlds[name] or worlds.Toybox
	make("Frame", {
		Size = UDim2.fromScale(1, 1),
		BackgroundColor3 = Color3.new(1, 1, 1),
		BorderSizePixel = 0,
		Parent = canvas,
	}, {
		make("UIGradient", {
			Rotation = 90,
			Color = ColorSequence.new({
				ColorSequenceKeypoint.new(0, Color3.fromHex(world[1])),
				ColorSequenceKeypoint.new(0.58, Color3.fromHex(world[2])),
				ColorSequenceKeypoint.new(1, Color3.fromHex(world[2])),
			}),
		}),
	})
	make("Frame", {
		Position = at(0, 226),
		Size = at(844, 164),
		BackgroundColor3 = Color3.fromHex(world[3]),
		BorderSizePixel = 0,
		Parent = canvas,
	})
	for i, data in { { 253, 70, 96 }, { 329, 110, 140 }, { 447, 60, 80 } } do
		make("Frame", {
			Name = "WorldProp" .. i,
			Position = at(data[1], 304 - data[3]),
			Size = at(data[2], data[3]),
			BackgroundColor3 = Color3.fromHex(world[4]),
			BorderSizePixel = 0,
			Parent = canvas,
		}, { Kit.corner(10) })
	end
	for _, data in { { 68, 39, 120, 34 }, { 523, 78, 160, 40 } } do
		make("Frame", {
			Position = at(data[1], data[2]),
			Size = at(data[3], data[4]),
			BackgroundColor3 = Color3.new(1, 1, 1),
			BackgroundTransparency = 0.5,
			BorderSizePixel = 0,
			Parent = canvas,
		}, { Kit.corner(100) })
	end
	local function hud()
		Kit.pill(
			canvas,
			{ text = "12.4K", icon = "coin", Position = at(16, 12), width = 148, height = 40, TextSize = 20 }
		)
		local progress =
			Kit.pill(canvas, { text = "", Position = at(272, 12), width = 300, height = 46, radius = 16 })
		text(progress, "Fort 3 · 63% down", 0, 0, 300, 28, 17, true)
		local bar = make("Frame", {
			Position = at(14, 31),
			Size = at(272, 9),
			BackgroundColor3 = c.surfaceAlt,
			BorderSizePixel = 0,
			Parent = progress,
		}, { Kit.corner(5) })
		make("Frame", {
			Size = UDim2.fromScale(0.63, 1),
			BackgroundColor3 = c.secondary,
			BorderSizePixel = 0,
			Parent = bar,
		}, { Kit.corner(5) })
		btn(canvas, nil, "pause", "neutral", 780, 10, 48, 48)
		for i, data in
			{
				{ "secondary", "store" },
				{ "accent", "book" },
				{ "neutral", "shield" },
				{ "neutral", "refresh" },
			}
		do
			local b = btn(canvas, nil, data[2], data[1], 776, 76 + (i - 1) * 62, 52, 48)
			if i == 1 then
				make("Frame", {
					Position = UDim2.new(1, -11, 0, -5),
					Size = at(16, 16),
					BackgroundColor3 = c.danger,
					ZIndex = 5,
					Parent = b,
				}, { Kit.corner(8), Kit.stroke(c.outline, 2) })
			end
		end
	end
	if state ~= "Result" then
		hud()
	end
	if state == "HUD" then
		for i, icon in { "circle", "bomb", "fork", "barbell" } do
			btn(
				canvas,
				nil,
				icon,
				if i == 1 then "primary" else "neutral",
				300 + (i - 1) * 64,
				if i == 1 then 314 else 320,
				56,
				52
			)
		end
		Kit.toast(canvas, {
			text = "+150 coins · x1.2",
			Position = at(422, 70),
			AnchorPoint = Vector2.new(0.5, 0),
			Size = at(220, 40),
			TextSize = 18,
		})
	else
		Kit.scrim(canvas)
		if state == "Shop" then
			local face = Kit.panel(canvas, {
				Position = at(132, 44),
				AnchorPoint = Vector2.zero,
				Size = at(580, 318 - s.shadow),
				title = "Toy Shop",
				titleWidth = 210,
			})
			for i, data in
				{
					{ "common", "bolt", "Power", "Lv 3 / 8", "60" },
					{ "rare", "clock", "Reload", "Lv 1 / 8", "240" },
					{ "legendary", "bomb", "Bomb Ball", "Unlock", "5K" },
				}
			do
				Kit.rarityCard(face, {
					Position = at(28 + (i - 1) * 178, 76),
					Size = at(162, 206),
					rarity = data[1],
					icon = data[2],
					text = data[3],
					subtitle = data[4],
					price = data[5],
					enabled = i ~= 3,
				})
			end
			local close = btn(canvas, nil, "close", "danger", 682, 30, 48, 48)
			close.ZIndex = 4
		else
			local result = Kit.panel(canvas, {
				Position = at(60, 52),
				AnchorPoint = Vector2.zero,
				Size = at(400, 306 - s.shadow),
				title = if s.title == "plain" then nil else "Collapse!",
				titleColor = c.accent,
				titleWidth = 220,
				titlePosition = at(362, -22),
			})
			for i = 1, 3 do
				local star = text(
					result,
					"★",
					96 + (i - 1) * 66,
					if i == 2 then 40 else 50,
					54,
					64,
					54,
					false,
					c.accent
				)
				star.TextTransparency = if i == 3 then 0.72 else 0
			end
			text(result, "+180 coins!", 0, 124, 400, 40, 30, true)
			text(result, "Top toys: Mo · Last hit: you", 0, 166, 400, 26, 16, false, c.textSoft)
			btn(result, "Home", "home", "neutral", 24, 306 - s.shadow - 72 - s.lip, 120, 52)
			btn(result, "Next fort", "play", "primary", 160, 306 - s.shadow - 72 - s.lip, 216, 52)
			local settings = Kit.panel(
				canvas,
				{ Position = at(500, 52), AnchorPoint = Vector2.zero, Size = at(290, 306 - s.shadow) }
			)
			local heading = text(settings, "Settings", 22, 18, 240, 34, 24, true)
			heading.TextXAlignment = Enum.TextXAlignment.Left
			Kit.switch(settings, {
				text = "Sound",
				value = true,
				Position = at(22, 60),
				Size = at(246, 48),
				compact = true,
				TextSize = 18,
			})
			Kit.switch(settings, {
				text = "Reduced motion",
				Position = at(22, 112),
				Size = at(246, 48),
				compact = true,
				TextSize = 18,
			})
			btn(settings, "Reset progress", nil, "danger", 22, 306 - s.shadow - 68 - s.lip, 246, 48)
		end
	end
	gui:SetAttribute("Ready", name .. "/" .. state)
	task.delay(0.1, function()
		if not canvas.Parent then
			return
		end
		local shadows = 0
		for _, item in canvas:GetDescendants() do
			if item:IsA("TextLabel") then
				assert(item.TextSize >= 16, "text floor: " .. item:GetFullName())
			end
			if item:IsA("GuiButton") then
				assert(item.AbsoluteSize.X >= 48 and item.AbsoluteSize.Y >= 48, "target floor")
				local p, v = item.AbsolutePosition - canvas.AbsolutePosition, item.AbsoluteSize
				assert(
					p.X >= -1 and p.Y >= -1 and p.X + v.X <= 845 and p.Y + v.Y <= 391,
					"action outside reference screen"
				)
			end
			if item:IsA("UIShadow") and item.Enabled then
				shadows += 1
			end
		end
		assert(shadows <= 100, "shadow budget")
		gui:SetAttribute("Audit", name .. "/" .. state)
	end)
end
gui:GetAttributeChangedSignal("Theme"):Connect(render)
gui:GetAttributeChangedSignal("Screen"):Connect(render)
render()
return "Theme preview ready; behavioral checks passed"
