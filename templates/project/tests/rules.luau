-- Pure-rule tests: run by `rbxgame check` (Lune, no Studio). Put game rules in src/shared and test them here.
local Config = require("../src/shared/Config")
local Rules = require("../src/shared/Rules")

local function near(a: number, b: number): boolean
	return math.abs(a - b) < 1e-9
end

-- meter: up in ChargeSeconds, then back down, then up again
local C = Config.ChargeSeconds
assert(near(Rules.meter(0, Config), 0))
assert(near(Rules.meter(C / 2, Config), 0.5))
assert(near(Rules.meter(C, Config), 1))
assert(near(Rules.meter(C * 1.5, Config), 0.5), "swings back down")
assert(near(Rules.meter(C * 2, Config), 0))
assert(near(Rules.meter(C * 2.25, Config), 0.25), "and up again")
assert(Rules.meter(-1, Config) == 0 and Rules.meter(0 / 0, Config) == 0, "bad input reads as empty")

-- judge: boundaries are inclusive (binary-exact widths so the edge itself is testable), junk is a miss
local exact = setmetatable({ GoodHalfWidth = 0.25, PerfectHalfWidth = 0.125 }, { __index = Config }) :: any
assert(Rules.judge(0.5, 0.5, 0, exact) == "PERFECT")
assert(Rules.judge(0.625, 0.5, 0, exact) == "PERFECT", "edge of PERFECT counts")
assert(Rules.judge(0.626, 0.5, 0, exact) == "GOOD")
assert(Rules.judge(0.25, 0.5, 0, exact) == "GOOD", "edge of GOOD counts")
assert(Rules.judge(0.249, 0.5, 0, exact) == "MISS")
local z = 0.5
assert(Rules.judge(0 / 0, z, 0, Config) == "MISS", "NaN is a miss")
assert(Rules.judge(5, 0.7, 0, Config) == "MISS", "release is clamped to 1 first")
assert(Rules.judge(5, 1, 0, Config) == "PERFECT", "an over-charge clamps to the top, it does not wrap")
assert(Rules.judge(z + 0.1, z, 0, Config) == "GOOD")
assert(Rules.judge(z + 0.1, z, 20, Config) == "MISS", "the zone narrows after a long streak")
local g0, p0 = Rules.widths(0, Config)
local g20, p20 = Rules.widths(20, Config)
assert(near(g0, Config.GoodHalfWidth) and near(p0, Config.PerfectHalfWidth))
assert(near(g20, Config.GoodHalfWidth * Config.MinZoneScale) and near(p20, Config.PerfectHalfWidth * Config.MinZoneScale))
assert(p20 > 0 and g20 > p20, "never narrower than the floor, GOOD always wider than PERFECT")

-- score: combo multiplier rises by ComboStep and stops at MaxMultiplier
assert(Rules.scoreFor("PERFECT", 0, Config) == Config.Points.PERFECT)
assert(Rules.scoreFor("GOOD", 0, Config) == Config.Points.GOOD)
assert(Rules.scoreFor("MISS", 5, Config) == 0)
assert(Rules.scoreFor("PERFECT", 4, Config) == math.floor(Config.Points.PERFECT * (1 + 4 * Config.ComboStep)))
assert(Rules.scoreFor("PERFECT", 99, Config) == Config.Points.PERFECT * Config.MaxMultiplier, "multiplier is capped")
assert(Rules.scoreFor("PERFECT", -3, Config) == Config.Points.PERFECT, "a negative combo reads as none")
assert(Rules.multiplier(0, Config) == 1)

-- stars: 1 for finishing, +1 per threshold, at the threshold exactly
local s1, s2 = Config.StarScores[1], Config.StarScores[2]
assert(Rules.starsFor(0, Config) == 1)
assert(Rules.starsFor(s1 - 1, Config) == 1)
assert(Rules.starsFor(s1, Config) == 2)
assert(Rules.starsFor(s2 - 1, Config) == 2)
assert(Rules.starsFor(s2, Config) == 3)
assert(Rules.starsFor(1e9, Config) == 3)
assert(Rules.starsFor(0 / 0, Config) == 1, "NaN never earns extra stars")

-- the server's charge check: a release needs about amount * ChargeSeconds of holding
assert(Rules.holdPlausible(0, 0, Config), "a zero release needs no hold")
assert(not Rules.holdPlausible(1, 0.1, Config), "a full charge in 0.1 s is a cheat")
assert(Rules.holdPlausible(1, C, Config))
assert(Rules.holdPlausible(1, C - Config.HoldSlack, Config), "jitter is forgiven")
assert(not Rules.holdPlausible(0.8, 0.2, Config))

-- Lune has no Random; this stand-in has the two methods Rules uses (Roblox's Random has them too)
local function newRandom(seed: number)
	local state = seed
	local self = {}
	function self.NextNumber(_): number
		state = (state * 1103515245 + 12345) % 2147483648
		return state / 2147483648
	end
	function self.NextInteger(_, min: number, max: number): number
		return min + math.floor(self:NextNumber() * (max - min + 1))
	end
	return self
end

-- targets: never repeat the previous orb, always inside the ring and the zone range
local rng = newRandom(5)
local seen = {}
for _ = 1, 400 do
	local previous = rng:NextInteger(0, Config.TargetCount)
	local index, zone = Rules.nextTarget(previous, rng, Config)
	assert(index ~= previous, "no repeat")
	assert(index >= 1 and index <= Config.TargetCount and index == math.floor(index))
	assert(zone >= Config.ZoneMin and zone <= Config.ZoneMax)
	seen[index] = true
end
for i = 1, Config.TargetCount do
	assert(seen[i], "every orb gets picked, including #" .. i)
end

-- balance: simulate players through Rules alone (the 45 s round, 1.4 s sweeps). A precise player
-- must earn every star; a shaky one must still finish with a score worth beating.
local function play(timingSd: number, seed: number): (number, number)
	local r = newRandom(seed)
	local function gauss(sd: number): number
		return sd * math.sqrt(-2 * math.log(1 - r:NextNumber())) * math.cos(2 * math.pi * r:NextNumber())
	end
	local score, combo, lives, clock, previous = 0, 0, Config.Lives, 0, 0
	while clock < Config.RoundSeconds and lives > 0 do
		local index, zone = Rules.nextTarget(previous, r, Config)
		previous = index
		local release = math.clamp(zone + gauss(timingSd), 0, 1)
		clock += release * C + 0.35 -- charge, then a person's look at the next target
		local grade = Rules.judge(release, zone, combo, Config)
		if grade == "MISS" then
			combo, lives = 0, lives - 1
		else
			score += Rules.scoreFor(grade, combo, Config)
			combo += 1
		end
	end
	return score, lives
end
local function average(sd: number): number
	local total = 0
	for seed = 1, 60 do
		total += play(sd, seed)
	end
	return total / 60
end
local precise, newcomer = average(0), average(0.06)
assert(Rules.starsFor(precise, Config) == 3, "a perfect player earns 3 stars, got " .. precise)
assert(Rules.starsFor(newcomer, Config) >= 1 and newcomer > 0, "a shaky player scores, got " .. newcomer)
print(("PASS: rules (precise averages %d, shaky averages %d)"):format(precise, newcomer))
