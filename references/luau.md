# Luau that holds up in a real game

Luau is Lua 5.1 plus gradual types, string interpolation, compound assignment, `continue`, generalized
iteration and a fast VM. Write it the way the engine wants: typed at the edges, plain in the middle,
and never blocking the frame.

## Every script starts the same way

```lua
--!strict
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage.Shared.Config)
```

- `--!strict` on new modules. Use `--!nonstrict` only where a third-party API fights the checker.
- Get services with `GetService`, never `game.Players` (a renamed or missing service then fails loudly).
- Requires at the top, in order: services, shared modules, local modules. Required modules are
  cached; requiring is cheap after the first time, but cycles deadlock: break a cycle by passing the
  dependency into an `init(deps)` function.

## Types that pay for themselves

```lua
export type Pad = {
	stage: number,
	index: number,
	kind: "pad" | "bounce" | "drift" | "turtle",
	base: BasePart,
}

local function score(quality: number, combo: number): number
	return math.floor((if quality <= 0.4 then 250 else 100) * math.min(4, 1 + combo * 0.25))
end
```

- Type module boundaries (exported functions, remote payloads, saved data). Leave locals to inference.
- Singleton string unions beat enums-as-numbers: the checker catches typos.
- `typeof(x) == "Instance"` / `x:IsA("BasePart")` for runtime checks; types vanish at runtime, so data
  from a client or a DataStore still needs checking (see `security.md`).
- `::` casts silence the checker; each one is a claim you have verified some other way. Prefer a
  real check (`assert(part:IsA("BasePart"))`).

## Idioms

| Instead of | Write | Why |
|---|---|---|
| `x = x + 1` | `x += 1` | shorter; same speed |
| `"Stage " .. n .. "/" .. total` | `` `Stage {n}/{total}` `` | readable; tostring is automatic |
| `a and b or c` | `if a then b else c` | the `and/or` form breaks when `b` is false or nil |
| `for i, v in ipairs(t)` / `pairs(t)` | `for i, v in t` | generalized iteration; arrays still go in order |
| `#t + 1` insertion in hot loops | `table.insert(t, v)` or a tracked count | clearer; same cost |
| manual copy loop | `table.clone(t)` | shallow, fast; deep copies need your own function |
| `wait()`, `spawn()`, `delay()` | `task.wait()`, `task.spawn()`, `task.delay()` | the legacy ones throttle and are deprecated |
| `table.getn`, `unpack` | `#t`, `table.unpack` | 5.1 leftovers |

`table.freeze(t)` makes config and constant tables read-only; a write then errors at the mistake
instead of corrupting state somewhere else.

## Scheduling: never block the frame

- `task.spawn(f)` runs now until the first yield; `task.defer(f)` runs at the end of the current
  resumption cycle (use it to break re-entrancy); `task.delay(t, f)` later.
- Every `while` loop yields. A long unyielding loop freezes the server (and in Studio over MCP it drops
  the connection): build large worlds in chunks with `task.wait()` between them.
- Per-frame work goes on `RunService.Heartbeat` (both sides, after physics), `RenderStepped` / 
  `BindToRenderStep` (client only, before render: cameras and character poses), or `Stepped` (before
  physics: overriding joint transforms). Keep the body short; move heavy work to a throttled loop.
- `os.clock()` for durations (precise, monotonic), `workspace:GetServerTimeNow()` for times both sides
  agree on, `os.time()` / `DateTime` for calendar time (daily rewards).

## Connections and cleanup

Every `:Connect` returns a connection that keeps its function, and everything it closes over, alive.

```lua
local conns = {}
table.insert(conns, part.Touched:Connect(onTouch))
-- later, when the owner goes away:
for _, c in conns do c:Disconnect() end
table.clear(conns)
```

- Per-player connections are disconnected on `PlayerRemoving`; per-character ones die with the
  character if they are on its descendants, but not if they are on something else (a remote, a
  service, a shared part).
- `:Once` for one-shot events. `Instance:Destroy()` disconnects the instance's own events and locks
  `Parent`; set your references to nil too.
- A tiny "janitor" module (a list of connections, instances and cleanup functions with one `clean()`)
  is worth writing once per project; it removes the whole class of leak.

## Errors

- `pcall` / `xpcall` around anything that can fail for reasons outside your code: DataStores,
  HTTP, `MarketplaceService`, `TeleportService`, `require` of an asset. Never around your own logic to
  hide a bug.
- Don't swallow: log with context (`warn(("[Data] load failed for %d: %s"):format(userId, err))`) and
  decide what the player sees.
- `error("message", 2)` blames the caller, which is what you want from a validating function.
- Retries use exponential backoff with a cap and give up loudly; an infinite retry loop on a throttled
  service makes the throttling worse.

## Strings and numbers

- `string.format("%.1f", t)` for times; `("%02d:%05.2f"):format(m, s)` for a race clock.
- Thousands separators: `tostring(n):reverse():gsub("(%d%d%d)", "%1,"):reverse():gsub("^,", "")`.
- Check finiteness of anything that came from outside: `x == x and x ~= math.huge and x ~= -math.huge`
  (NaN is the only value not equal to itself).
- Integers above 2^53 lose precision. Currency totals in the billions are fine; IDs are fine as numbers.
- `utf8` library for player-entered text; `string.len` counts bytes.

## Performance that matters in Luau

- Cache globals and services in locals at the top of hot modules; the VM inlines many builtins already,
  so don't micro-optimise beyond that without a profile.
- Avoid creating tables or closures per frame per object; reuse them.
- `Vector3`, `CFrame` and `Color3` are value types: cheap to make, but math in tight loops is still
  math. Precompute what doesn't change.
- Use the profiler (`references/performance.md`) before believing any rule here.

## Modules

- One module, one job; return a table of functions (or a class-like table with `__index` when there
  really are many instances with state).
- No side effects at require time beyond building constants. Start work from an explicit `Start()` so
  boot order is visible in one place (`Main.server.luau`, `Main.client.luau`).
- Shared code (`ReplicatedStorage.Shared`) must not touch server-only services; anything a client can
  require, an exploiter can read.
