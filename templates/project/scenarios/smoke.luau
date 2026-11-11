-- Server scenario (rbxgame test scenarios/smoke.luau): a player joins, starts a round, plays hits and
-- misses through the real Action remote (fired from a throwaway LocalScript, as a client would), and the
-- server's attributes must follow the rules: bad payloads ignored, early releases ignored, score and combo
-- up on hits, lives down on misses, Results after the last life, Play again works. Proves the rules, not the feel.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Shared.Config)

local function waitFor(test: () -> boolean, seconds: number): boolean
	local t0 = os.clock()
	while not test() and os.clock() - t0 < seconds do
		task.wait(0.05)
	end
	return test()
end
local t0 = os.clock()
while #Players:GetPlayers() == 0 and os.clock() - t0 < 10 do
	task.wait(0.2)
end
local p = Players:GetPlayers()[1]
assert(p, "no player joined")
assert(
	waitFor(function()
		return p:GetAttribute("Phase") == "Title"
	end, 20),
	"Phase never reached Title (Phase=" .. tostring(p:GetAttribute("Phase")) .. ")"
)

-- what the client would send, e.g. fire('"Act", 0.5')
local function fire(args: string)
	local s = Instance.new("LocalScript")
	s.Source = ('game.ReplicatedStorage:WaitForChild("Action"):FireServer(%s) script:Destroy()'):format(args)
	s.Parent = p:WaitForChild("PlayerGui")
	task.wait(0.35)
end
local function attr(name: string): number
	return p:GetAttribute(name) :: number
end

-- out of phase: acting or going to the menu from the Title does nothing
fire('"Act", 0.5')
fire('"Menu"')
assert(
	p:GetAttribute("Phase") == "Title" and (p:GetAttribute("Score") or 0) == 0,
	"Title accepted a play intent"
)

local started = os.clock()
fire('"Start"')
assert(p:GetAttribute("Phase") == "Play", "Start did not begin a round")
assert(attr("Lives") == Config.Lives and attr("Score") == 0 and attr("TimeLeft") > 0, "round did not reset")
assert(
	type(p:GetAttribute("Zone")) == "number" and type(p:GetAttribute("Target")) == "number",
	"no target published"
)

-- malformed or implausible Acts are ignored: a full charge with no time to charge (first, while the round is
-- still young), wrong types, NaN, an unknown intent, Menu mid-round
for _, bad in { '"Act", 1', '"Act", "x"', '"Act"', '"Act", 0/0', '"Act", {}', '"Act", true', "123", '"Menu"' } do
	fire(bad)
end
assert(
	attr("Lives") == Config.Lives and attr("Score") == 0 and p:GetAttribute("Phase") == "Play",
	"bad input changed state"
)

-- three exact hits: each waits as long as the meter takes to reach the zone
for i = 1, 3 do
	local zone = attr("Zone")
	local pause = zone * Config.ChargeSeconds + Config.HoldSlack - (os.clock() - started)
	task.wait(math.max(0, pause))
	local before = attr("Score")
	fire(('"Act", %.6f'):format(zone))
	assert(attr("Score") > before, "a hit on the zone did not score (hit " .. i .. ")")
	assert(attr("Combo") == i, "combo did not climb")
	started = os.clock() - 0.35
end
assert(attr("Lives") == Config.Lives, "hits cost a life")

-- three misses end the round: aim at the far side of the zone
local score = attr("Score")
for i = 1, Config.Lives do
	local amount = if attr("Zone") > 0.6 then 0 else 1
	task.wait(amount * Config.ChargeSeconds + 0.1)
	fire(('"Act", %d'):format(amount))
	assert(attr("Combo") == 0, "a miss kept the combo")
	assert(i == Config.Lives or attr("Lives") == Config.Lives - i, "a miss did not cost a life")
end
assert(
	waitFor(function()
		return p:GetAttribute("Phase") == "Results"
	end, 3),
	"round did not end at zero lives"
)
assert(attr("Score") == score and attr("Stars") >= 1 and attr("Stars") <= 3, "results are wrong")
assert(attr("Best") >= score, "best was not recorded")

-- Play again
local stars = attr("Stars")
fire('"Start"')
assert(
	p:GetAttribute("Phase") == "Play" and attr("Score") == 0 and attr("Lives") == Config.Lives,
	"Play again failed"
)
return ("PASS: score=%d best=%d stars=%d, lives and phases follow the rules"):format(
	score,
	attr("Best"),
	stars
)
