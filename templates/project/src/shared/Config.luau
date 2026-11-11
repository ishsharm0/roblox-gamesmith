--!strict
-- Every tunable of the starter game in one place, so balancing never means hunting through scripts.
-- A new game keeps this file and replaces the numbers: the palette first, then the verb's timing and
-- the score and star thresholds. Rules.luau and Game.luau read it; nothing else hard-codes a number.
local Config = {
	Name = "Pop",
	Tagline = "Hold to charge. Let go in the gold.",

	-- round
	RoundSeconds = 45,
	Lives = 3,
	TargetCount = 8, -- orbs in the ring
	ActInterval = 0.12, -- the server ignores a second Act sooner than this (seconds)
	HoldSlack = 0.3, -- tolerated network jitter when checking that a release took long enough to charge

	-- the verb: hold to charge a meter 0 -> 1 in ChargeSeconds, then it swings back down
	ChargeSeconds = 1.4,
	ZoneMin = 0.3, -- the sweet zone's centre is drawn from [ZoneMin, ZoneMax]
	ZoneMax = 0.85,
	GoodHalfWidth = 0.12, -- |release - zone| within this is GOOD
	PerfectHalfWidth = 0.045, -- within this is PERFECT
	ShrinkPerCombo = 0.04, -- every hit in a row narrows both zones by this fraction...
	MinZoneScale = 0.6, -- ...down to this share of their width

	-- score
	Points = { PERFECT = 100, GOOD = 50 },
	ComboStep = 0.25, -- each hit in a row adds this to the multiplier...
	MaxMultiplier = 3, -- ...up to this
	StarScores = { 1500, 6000 }, -- finishing earns 1 star; each score reached adds one

	-- look: RGB triples, so Lune can load this file; Config.color turns one into a Color3
	Palette = {
		Floor = { 72, 92, 132 },
		FloorRim = { 86, 214, 204 },
		Backdrop = { 88, 96, 160 },
		Orb = { 255, 200, 70 },
		OrbIdle = { 120, 150, 190 },
		Perfect = { 255, 200, 70 },
		Good = { 86, 214, 204 },
		Miss = { 255, 122, 132 },
	},
}

function Config.color(name: string): Color3
	local rgb = (Config.Palette :: { [string]: { number } })[name]
	return Color3.fromRGB(rgb[1], rgb[2], rgb[3])
end

return Config
