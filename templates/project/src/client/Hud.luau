--!strict
-- Every screen, built with UiKit: Title, the play HUD (score, combo, time, lives, charge meter, grade popups) and
-- Results (stars, score, best, Play again, Menu), driven by the player's attributes (Net.luau). Phone-safe at 844x390.
-- A new game keeps the screens' skeleton and replaces the meter and the labels.
local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local Config = require(ReplicatedStorage.Shared.Config)
local Net = require(ReplicatedStorage.Shared.Net)
local Rules = require(ReplicatedStorage.Shared.Rules)
local Kit = require(script.Parent.UiKit)

local T = Kit.Theme
local make = Kit.make
local player = Players.LocalPlayer

export type Hooks = {
	charge: () -> number?, -- the meter while the player holds, nil otherwise (Input.charge)
	onStar: (index: number) -> (), -- a result star lands (for its sound)
}

local Hud = {}

local gradeLabel: TextLabel? = nil
local hintLabel: TextLabel? = nil
local frozenAmount = 0
local frozenUntil = 0
local gradeTicket = 0

local function num(name: string): number
	return (player:GetAttribute(name) :: number?) or 0
end

local function commas(n: number): string
	local reversed = (tostring(math.floor(n)):reverse():gsub("(%d%d%d)", "%1,")):reverse()
	return if reversed:sub(1, 1) == "," then reversed:sub(2) else reversed
end

local function watch(name: string, fn: () -> ())
	player:GetAttributeChangedSignal(name):Connect(fn)
	fn()
end

-- With a gamepad the first button must already be selected, or A has nothing to press.
local function focus(button: GuiObject?)
	if button and UserInputService:GetLastInputType().Name:find("Gamepad") then
		GuiService.SelectedObject = button
	else
		GuiService.SelectedObject = nil
	end
end

local function intent(name: string)
	return function()
		Net.Action:FireServer(name)
	end
end

function Hud.start(hooks: Hooks)
	local _, root = Kit.screen(player:WaitForChild("PlayerGui") :: PlayerGui, "Hud", 10)

	------------------------------------------------------------------ Title
	local titleFace = Kit.panel(root, { Name = "Title", Size = UDim2.fromOffset(520, 350) })
	local title = titleFace.Parent :: Frame
	title.Visible = false
	Kit.text(titleFace, {
		Name = "Name",
		Text = string.upper(Config.Name),
		display = true,
		TextSize = 76,
		Size = UDim2.new(1, 0, 0, 96),
		Position = UDim2.fromOffset(0, 24),
		TextWrapped = false,
	})
	Kit.text(titleFace, {
		Name = "Tagline",
		Text = Config.Tagline,
		TextSize = 24,
		TextColor3 = T.InkSoft,
		Size = UDim2.new(1, -60, 0, 64),
		Position = UDim2.new(0.5, 0, 0, 122),
		AnchorPoint = Vector2.new(0.5, 0),
	})
	local titleBest = Kit.text(titleFace, {
		Name = "Best",
		Text = "",
		TextSize = 26,
		Size = UDim2.new(1, -60, 0, 32),
		Position = UDim2.new(0.5, 0, 0, 180),
		AnchorPoint = Vector2.new(0.5, 0),
	})
	local playButton = Kit.button(titleFace, {
		Name = "Play",
		text = "Play",
		style = "primary",
		Size = UDim2.fromOffset(260, 68),
		Position = UDim2.new(0.5, 0, 1, -44),
		AnchorPoint = Vector2.new(0.5, 1),
		onActivated = intent(Net.Intent.Start),
	})

	------------------------------------------------------------------ Play HUD
	local playing = make("Frame", {
		Name = "Playing",
		Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1,
		Visible = false,
		Parent = root,
	})
	local _, scoreValue = Kit.pill(playing, {
		Name = "Score",
		icon = "star",
		text = "0",
		Position = UDim2.fromOffset(20, 12),
	})
	local comboPill, comboValue = Kit.pill(playing, {
		Name = "Combo",
		text = "x1",
		color = T.Sun,
		height = 40,
		TextSize = 22,
		Position = UDim2.fromOffset(20, 68),
	})
	local timePill, timeValue = Kit.pill(playing, {
		Name = "Time",
		icon = "clock",
		text = tostring(Config.RoundSeconds),
		Position = UDim2.new(0.5, 0, 0, 12),
		AnchorPoint = Vector2.new(0.5, 0),
	})
	local livesBox = make("Frame", {
		Name = "Lives",
		AnchorPoint = Vector2.new(1, 0),
		Position = UDim2.new(1, -20, 0, 12),
		Size = UDim2.fromOffset(Config.Lives * 40 + 24, 48),
		BackgroundColor3 = T.Cream,
		Parent = playing,
	}, {
		Kit.corner(24),
		Kit.stroke(T.Ink, T.Stroke),
		make("UIListLayout", {
			FillDirection = Enum.FillDirection.Horizontal,
			HorizontalAlignment = Enum.HorizontalAlignment.Center,
			VerticalAlignment = Enum.VerticalAlignment.Center,
			Padding = UDim.new(0, 4),
			SortOrder = Enum.SortOrder.LayoutOrder,
		}),
	})
	local hearts: { Frame } = {}
	for i = 1, Config.Lives do
		local heart = Kit.icon(livesBox, "heart", T.Coral, 32)
		heart.LayoutOrder = i
		hearts[i] = heart
	end

	-- the charge meter: a track, the sweet zone (GOOD wide, PERFECT narrow), a fill and a marker
	local meter = make("Frame", {
		Name = "Meter",
		AnchorPoint = Vector2.new(0.5, 1),
		Position = UDim2.new(0.5, 0, 1, -28),
		Size = UDim2.fromOffset(600, 44),
		BackgroundColor3 = T.Ink,
		Parent = playing,
	}, { Kit.corner(22), Kit.stroke(T.Cream, T.Stroke) })
	local bar = make("Frame", {
		Name = "Bar",
		Position = UDim2.fromOffset(8, 8),
		Size = UDim2.new(1, -16, 1, -16),
		BackgroundColor3 = T.InkSoft,
		ClipsDescendants = true,
		Parent = meter,
	}, { Kit.corner(14) })
	local function zoneFrame(name: string, color: Color3, z: number): Frame
		return make("Frame", {
			Name = name,
			AnchorPoint = Vector2.new(0.5, 0),
			Size = UDim2.fromScale(0.2, 1),
			BackgroundColor3 = color,
			BorderSizePixel = 0,
			ZIndex = z,
			Parent = bar,
		})
	end
	local goodZone = zoneFrame("Good", Config.color("Good"), 2)
	local perfectZone = zoneFrame("Perfect", Config.color("Perfect"), 3)
	local fill = make("Frame", {
		Name = "Fill",
		Size = UDim2.fromScale(0, 1),
		BackgroundColor3 = T.Cream,
		BackgroundTransparency = 0.45,
		BorderSizePixel = 0,
		ZIndex = 4,
		Parent = bar,
	})
	local marker = make("Frame", {
		Name = "Marker",
		AnchorPoint = Vector2.new(0.5, 0.5),
		Size = UDim2.new(0, 8, 1, 10),
		Position = UDim2.fromScale(0, 0.5),
		BackgroundColor3 = T.Cream,
		Visible = false,
		ZIndex = 5,
		Parent = bar,
	}, { Kit.corner(4), Kit.stroke(T.Ink, 2) })
	local hint = Kit.text(playing, {
		Name = "Hint",
		Text = "Hold anywhere, let go in the gold",
		TextSize = 24,
		TextColor3 = T.Cream,
		outline = 3,
		Size = UDim2.fromOffset(600, 34),
		Position = UDim2.new(0.5, 0, 1, -82),
		AnchorPoint = Vector2.new(0.5, 1),
		TextWrapped = false,
	})
	hintLabel = hint
	local grade = Kit.text(playing, {
		Name = "Grade",
		display = true,
		TextSize = 52,
		outline = 4,
		TextTransparency = 1,
		Size = UDim2.fromOffset(640, 84),
		Position = UDim2.fromScale(0.5, 0.4),
		AnchorPoint = Vector2.new(0.5, 0.5),
		TextWrapped = false,
	})
	gradeLabel = grade
	local gradeStroke = grade:FindFirstChildOfClass("UIStroke") :: UIStroke
	gradeStroke.Transparency = 1

	------------------------------------------------------------------ Results
	local resFace = Kit.panel(root, { Name = "Results", Size = UDim2.fromOffset(560, 430) })
	local results = resFace.Parent :: Frame
	results.Visible = false
	Kit.text(resFace, {
		Name = "Heading",
		Text = "Round over",
		display = true,
		TextSize = 44,
		Size = UDim2.new(1, 0, 0, 56),
		Position = UDim2.fromOffset(0, 22),
		TextWrapped = false,
	})
	local starRow = make("Frame", {
		Name = "Stars",
		BackgroundTransparency = 1,
		Size = UDim2.fromOffset(330, 84),
		Position = UDim2.new(0.5, 0, 0, 84),
		AnchorPoint = Vector2.new(0.5, 0),
		Parent = resFace,
	}, {
		make("UIListLayout", {
			FillDirection = Enum.FillDirection.Horizontal,
			HorizontalAlignment = Enum.HorizontalAlignment.Center,
			VerticalAlignment = Enum.VerticalAlignment.Center,
			Padding = UDim.new(0, 12),
			SortOrder = Enum.SortOrder.LayoutOrder,
		}),
	})
	local stars: { TextLabel } = {}
	for i = 1, 3 do
		stars[i] = Kit.text(starRow, {
			Name = "Star" .. i,
			Text = "★",
			display = true,
			TextSize = 76,
			TextColor3 = T.Muted,
			outline = 3,
			Size = UDim2.fromOffset(90, 84),
			TextWrapped = false,
			LayoutOrder = i,
		})
	end
	local resultScore = Kit.text(resFace, {
		Name = "Score",
		display = true,
		TextSize = 60,
		Size = UDim2.new(1, -40, 0, 70),
		Position = UDim2.new(0.5, 0, 0, 178),
		AnchorPoint = Vector2.new(0.5, 0),
		TextWrapped = false,
	})
	local resultBest = Kit.text(resFace, {
		Name = "Best",
		TextSize = 28,
		TextColor3 = T.InkSoft,
		Size = UDim2.new(1, -40, 0, 36),
		Position = UDim2.new(0.5, 0, 0, 252),
		AnchorPoint = Vector2.new(0.5, 0),
	})
	local againButton = Kit.button(resFace, {
		Name = "Again",
		text = "Play again",
		style = "primary",
		Size = UDim2.fromOffset(260, 66),
		Position = UDim2.new(0.5, -10, 1, -40),
		AnchorPoint = Vector2.new(1, 1),
		onActivated = intent(Net.Intent.Start),
	})
	Kit.button(resFace, {
		Name = "Menu",
		text = "Menu",
		style = "secondary",
		Size = UDim2.fromOffset(200, 66),
		Position = UDim2.new(0.5, 10, 1, -40),
		AnchorPoint = Vector2.new(0, 1),
		onActivated = intent(Net.Intent.Menu),
	})

	------------------------------------------------------------------ state -> screens
	local shown = ""
	local screenId = 0 -- bumps on every phase change, so a late star callback cannot paint a newer screen
	local function refreshPhase()
		local phase = player:GetAttribute("Phase")
		if phase == shown or type(phase) ~= "string" then
			return
		end
		shown = phase
		screenId += 1
		local mine = screenId
		title.Visible = false
		playing.Visible = false
		results.Visible = false
		if phase == Net.Phase.Title then
			titleBest.Text = if num("Best") > 0 then "Best " .. commas(num("Best")) else "Ready when you are"
			Kit.pop(title, true)
			focus(playButton)
		elseif phase == Net.Phase.Play then
			playing.Visible = true
			hint.Visible = true
			focus(nil)
		elseif phase == Net.Phase.Results then
			local score, best = num("Score"), num("Best")
			resultScore.Text = commas(score)
			resultBest.Text = if score > 0 and score >= best then "New best!" else "Best " .. commas(best)
			for _, star in stars do
				star.TextColor3 = T.Muted
			end
			for i = 1, math.min(3, num("Stars")) do
				task.delay(0.5 + 0.4 * i, function()
					if mine ~= screenId then
						return
					end
					stars[i].TextColor3 = T.Sun
					Kit.punch(stars[i], 1.7)
					hooks.onStar(i)
				end)
			end
			Kit.pop(results, true)
			focus(againButton)
		end
	end
	watch("Phase", refreshPhase)

	local lastScore, lastLives = 0, Config.Lives
	watch("Score", function()
		local score = num("Score")
		scoreValue.Text = commas(score)
		if score > lastScore then
			Kit.punch(scoreValue, 1.3)
		end
		lastScore = score
	end)
	watch("Combo", function()
		local combo = num("Combo")
		comboPill.Visible = combo >= 2
		comboValue.Text = string.format("x%g", Rules.multiplier(combo, Config))
		if combo >= 2 then
			Kit.punch(comboValue, 1.25)
		end
	end)
	watch("Lives", function()
		local lives = num("Lives")
		for i, heart in hearts do
			for _, part in heart:GetChildren() do
				(part :: Frame).BackgroundColor3 = if i <= lives then T.Coral else T.Muted
			end
		end
		if lives < lastLives then
			Kit.punch(livesBox, 1.15)
		end
		lastLives = lives
	end)
	watch("TimeLeft", function()
		local left = num("TimeLeft")
		timeValue.Text = tostring(left)
		timePill.BackgroundColor3 = if left <= 10 and left > 0 then T.Coral else T.Cream
	end)
	watch("Best", function()
		if shown == Net.Phase.Title then
			titleBest.Text = if num("Best") > 0 then "Best " .. commas(num("Best")) else "Ready when you are"
		end
	end)

	-- the sweet zone follows the target and narrows with the streak (same Rules the server judges with)
	local function refreshZone()
		local good, perfect = Rules.widths(num("Combo"), Config)
		local zone = num("Zone")
		goodZone.Position = UDim2.fromScale(zone, 0)
		goodZone.Size = UDim2.fromScale(good * 2, 1)
		perfectZone.Position = UDim2.fromScale(zone, 0)
		perfectZone.Size = UDim2.fromScale(perfect * 2, 1)
	end
	watch("Zone", refreshZone)
	watch("Combo", refreshZone)

	RunService.RenderStepped:Connect(function()
		if not playing.Visible then
			return
		end
		local value = hooks.charge()
		if value == nil and os.clock() < frozenUntil then
			value = frozenAmount -- hold the release on the meter for a moment so the player sees where it landed
		end
		fill.Size = UDim2.fromScale(value or 0, 1)
		marker.Visible = value ~= nil
		marker.Position = UDim2.fromScale(value or 0, 0.5)
	end)
end

-- The player let go at `amount`: keep it on the meter for a moment and drop the how-to hint.
function Hud.released(amount: number)
	frozenAmount = amount
	frozenUntil = os.clock() + 0.4
	if hintLabel then
		hintLabel.Visible = false
	end
end

-- The server's verdict: a popup over the middle of the ring that rises and fades.
function Hud.grade(grade: string, points: number)
	local label = gradeLabel
	if not label then
		return
	end
	gradeTicket += 1
	local mine = gradeTicket
	local stroke = label:FindFirstChildOfClass("UIStroke") :: UIStroke
	label.Text = if points > 0 then ("%s  +%d"):format(grade, points) else grade
	label.TextColor3 =
		Config.color(if grade == "PERFECT" then "Perfect" elseif grade == "GOOD" then "Good" else "Miss")
	label.TextTransparency = 0
	stroke.Transparency = 0
	label.Position = UDim2.fromScale(0.5, 0.42)
	Kit.punch(label, 1.3)
	Kit.tween(label, 0.8, { Position = UDim2.fromScale(0.5, 0.36) })
	task.delay(0.5, function()
		if mine == gradeTicket then
			Kit.tween(label, 0.3, { TextTransparency = 1 })
			Kit.tween(stroke, 0.3, { Transparency = 1 })
		end
	end)
end

return Hud
