--!strict
-- Server entry: build the arena, then start the systems in order. Net must load first (it creates the remotes).
local ReplicatedStorage = game:GetService("ReplicatedStorage")

require(ReplicatedStorage.Shared.Net)
require(script.Parent.Arena).build()
require(script.Parent.Game).start()
print("[server] start")
