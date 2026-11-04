-- Human-model bot: plays several full runs with the real controls and a person's errors, then reports
-- failures per stage and the beats that fail most (failures / tries). Method: references/mechanics-and-fun.md.
--
-- The game's client exposes a BindableFunction `BotHook` under the player:
--   BotHook:Invoke("busy")          -> true while the player can't act (mid-air, animating, input locked)
--   BotHook:Invoke("act", amount)   -> performs the core verb with amount 0..1 (charge, power, timing)
-- and the server publishes these player attributes: Phase ("Run" while playing, "Results" at the end),
-- Stage, Progress (index of the last beat cleared in this stage), Fails (count of failures).
-- Fill in the GAME-SPECIFIC functions below; leave the harness alone. Run against a tested game through an
-- adapter: precise and casual profiles finished every run; failures during automatic movement are
-- reported separately as "<stage>.<progress> auto".
--
-- Usage (runs in the background; MCP calls time out after ~5 minutes):
--   studio play
--   echo 'local p=game.Players.LocalPlayer p:SetAttribute("BotProfile","casual") p:SetAttribute("BotRuns",4)' | studio luau - --ctx Client
--   studio luau scenarios/human-bot.luau --ctx Client
--   echo 'return game.Players.LocalPlayer:GetAttribute("BotReport")' | studio luau - --ctx Client   (poll until BotDone)
local p = game.Players.LocalPlayer
local hook = p:WaitForChild("BotHook")
local action = game.ReplicatedStorage:WaitForChild("Action") -- your request remote

------------------------------------------------------------------ GAME-SPECIFIC
-- The next objective's position, or nil if there is none right now.
local function target(): Vector3?
	return nil -- e.g. workspace.Map.Course[("Pad_%d_%02d"):format(stage, progress + 1)].PrimaryPart.Position
end
-- The perfect input for a target at horizontal distance d, and how visible the guide is in this stage
-- ("full" | "arc" | "half" | "none"; more guide = less judgement error).
local function ideal(d: number, _stage: number): (number, string)
	return math.clamp(d / 30, 0, 1), "none"
end
-- Wait here for hazards a person would wait for (a platform under water, a closing door, a telegraphed
-- attack). Skipping this makes a precise bot's retries sync with a hazard timer and fail forever.
local function waitForSafe(_stage: number) end
-- Start or restart a run from whatever screen is showing.
local function startRun()
	local phase = p:GetAttribute("Phase")
	if phase == "Results" then
		action:FireServer("Restart")
	elseif phase ~= "Run" then
		action:FireServer("Begin")
	end
end
------------------------------------------------------------------ HARNESS

local PROFILES = { -- timing error (s), judgement error (fraction of distance) by guide level, reaction (s)
	precise = { timing = 0, judge = { full = 0, arc = 0, half = 0, none = 0 }, react = 0.1 }, -- must finish every run
	careful = { timing = 0.035, judge = { full = 0.015, arc = 0.04, half = 0.06, none = 0.08 }, react = 0.25 },
	casual = { timing = 0.06, judge = { full = 0.03, arc = 0.07, half = 0.1, none = 0.13 }, react = 0.4 },
	new = { timing = 0.09, judge = { full = 0.05, arc = 0.1, half = 0.14, none = 0.18 }, react = 0.55 },
}
local INPUT_SECONDS = 0.85 -- how long the input takes to sweep 0 -> 1 (converts timing error to amount)
local name = p:GetAttribute("BotProfile") or "casual"
local prof = PROFILES[name]
local runs = p:GetAttribute("BotRuns") or 4
local rng = Random.new(p:GetAttribute("BotSeed") or 7) -- fixed seed: before/after comparisons are fair
local function gauss(sd: number): number
	return sd * math.sqrt(-2 * math.log(1 - rng:NextNumber())) * math.cos(2 * math.pi * rng:NextNumber())
end
local function attr(n: string): number
	return p:GetAttribute(n) or 0
end

local report, spots = {}, {} -- spots["stage.progress"] = { tries, fails }
p:SetAttribute("BotDone", false)
p:SetAttribute("BotReport", name .. " | started")
task.spawn(function()
	for run = 1, runs do
		local t = os.clock()
		while p:GetAttribute("Phase") ~= "Run" and os.clock() - t < 20 do
			startRun()
			task.wait(1)
		end
		local t0, acts, fails = os.clock(), 0, {}
		local lastFails = attr("Fails")
		while p:GetAttribute("Phase") == "Run" and acts < 150 do
			local wb = os.clock()
			while hook:Invoke("busy") and os.clock() - wb < 4 do
				task.wait(0.05)
			end
			local stage, progress = attr("Stage"), attr("Progress")
			if attr("Fails") > lastFails then -- failed during automatic movement (a bounce, a conveyor), not an input
				local key = ("%d.%d auto"):format(stage, progress)
				spots[key] = spots[key] or { 0, 0 }
				spots[key][1] += 1
				spots[key][2] += 1
				fails[stage] = (fails[stage] or 0) + 1
				lastFails = attr("Fails")
			end
			waitForSafe(stage)
			task.wait(prof.react * 0.5) -- a person looks before acting
			local goal = target()
			local root = p.Character and p.Character:FindFirstChild("HumanoidRootPart") :: BasePart?
			-- standing on the "next" objective means the server hasn't counted this landing yet: wait for it
			local wt = os.clock()
			while
				goal
				and root
				and os.clock() - wt < 0.8
				and Vector3.new(goal.X - root.Position.X, 0, goal.Z - root.Position.Z).Magnitude < 2.5
			do
				task.wait(0.05)
				goal = target()
			end
			if not (goal and root) then
				task.wait(0.2)
				continue
			end
			local d = Vector3.new(goal.X - root.Position.X, 0, goal.Z - root.Position.Z).Magnitude
			local _, guide = ideal(d, stage)
			local judged = ideal(d * (1 + gauss(prof.judge[guide] or prof.judge.none)), stage)
			local amount = judged + gauss(prof.timing / INPUT_SECONDS)
			local key = ("%d.%d"):format(stage, progress)
			local spot = spots[key] or { 0, 0 }
			spots[key] = spot
			spot[1] += 1
			hook:Invoke("act", math.clamp(amount, 0, 1))
			acts += 1
			-- wait for the outcome itself, never a fixed delay: reading the world before a respawn
			-- settles makes the bot blame the game for its own stale input
			local w = os.clock()
			while os.clock() - w < 4 do
				if attr("Fails") > lastFails or attr("Progress") ~= progress or attr("Stage") ~= stage then
					break
				end
				if os.clock() - w > 1.5 and not hook:Invoke("busy") then
					break
				end
				task.wait()
			end
			if attr("Fails") > lastFails then
				fails[stage] = (fails[stage] or 0) + 1
				spot[2] += 1
				task.wait(0.6) -- the respawn settles
			end
			lastFails = attr("Fails")
		end
		local perStage = {}
		for s = 1, math.max(#fails, attr("Stage")) do
			perStage[s] = tostring(fails[s] or 0)
		end
		table.insert(
			report,
			("run %d: %s %.0fs acts=%d fails/stage=%s score=%s"):format(
				run,
				tostring(p:GetAttribute("Phase")),
				os.clock() - t0,
				acts,
				table.concat(perStage, ","),
				tostring(p:GetAttribute("Score"))
			)
		)
		p:SetAttribute("BotReport", name .. " | " .. table.concat(report, " | "))
		task.wait(2)
	end
	local list = {}
	for k, v in spots do
		if v[2] > 0 then
			table.insert(list, { k, v })
		end
	end
	table.sort(list, function(a, b) -- by rate: a stage's first beat is retried after every later failure
		return a[2][2] / a[2][1] > b[2][2] / b[2][1]
	end)
	local top = {}
	for i = 1, math.min(10, #list) do
		local k, v = list[i][1], list[i][2]
		top[i] = ("%s %d/%d (%.0f%%)"):format(k, v[2], v[1], 100 * v[2] / v[1])
	end
	p:SetAttribute(
		"BotReport",
		name .. " | " .. table.concat(report, " | ") .. " | worst beats: " .. table.concat(top, ", ")
	)
	p:SetAttribute("BotDone", true)
end)
return "started " .. name .. " x" .. runs
