-- Pure-rule tests: run by `rbxgame check` (Lune, no Studio). Put game rules in src/shared and test them here.
local Config = require("../src/shared/Config")
assert(type(Config) == "table", "Config must return a table")
print("PASS: config loads")
