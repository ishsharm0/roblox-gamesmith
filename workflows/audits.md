# Audits: security, performance, monetization, code

Run the relevant audit before every publish, and after any change in its area. Each item is checked
by looking (a grep, a scenario, a capture), not by memory. Write the result, with evidence and
anything skipped, into the project's NOTES.md.

## Security (any remote, data, or inserted asset changed)

Find every entry point first:

```bash
studio luau - <<'EOF'
local out = {}
for _, d in game:GetDescendants() do
	if d:IsA("RemoteEvent") or d:IsA("RemoteFunction") or d:IsA("UnreliableRemoteEvent") then
		table.insert(out, d:GetFullName())
	end
end
return table.concat(out, "\n")
EOF
grep -rn "OnServerEvent\|OnServerInvoke" src/
```

- [ ] Every handler checks type -> range -> ownership/state -> rate before acting (`references/security.md`).
- [ ] No handler trusts a price, reward, damage, position or time from the client.
- [ ] No `RemoteFunction` is invoked on a client.
- [ ] Progress is checked in order (no skipping checkpoints/levels); a scenario fires garbage and
      out-of-order requests and the state doesn't change.
- [ ] Currency and items change only through their one server module, with reasons logged.
- [ ] Nothing secret is in ReplicatedStorage, Workspace or client code.
- [ ] Every inserted asset audited for scripts (`require(` with numbers, `getfenv`, `loadstring`,
      hidden scripts); unread scripts deleted.
- [ ] Player text shown to others is filtered.

## Performance (any world, effect or per-frame code changed)

- [ ] MicroProfiler during the busiest moment: no frame over 16 ms on a phone-class target.
- [ ] A 10-minute bot session: memory flat (`Stats:GetTotalMemoryUsageMb()` sampled).
- [ ] Part count, unique meshes and textures noted; scenery anchored with collisions/touch/query off.
- [ ] No per-frame replicated property writes on scenery; client-side animation for decoration.
- [ ] Per-object connections replaced by one loop where there are many objects.
- [ ] Streaming considered for big maps.
- [ ] Particles and transparent parts limited in the busiest view.

## Monetization (before any product goes live)

- [ ] The core loop is fun and the first session retains without spending (`references/game-design.md`).
- [ ] Every product listed with price, what it gives, and why it isn't pay-to-win.
- [ ] `ProcessReceipt` idempotent by `PurchaseId`; tested: failed save, duplicate receipt,
      player left mid-grant (`references/receipts.md`).
- [ ] Game passes granted at join and immediately after purchase.
- [ ] Paid random items: odds shown and regional policy checked, or not shipped.
- [ ] No prompts during core play; no misleading buttons; no pressure on children.
- [ ] Economy events logged (sources and sinks).
- [ ] No Robux spent and no product created without the owner's explicit go-ahead.

## Code (before merging a change)

- [ ] `rbxgame check` passes: Selene zero warnings, StyLua clean, Lune tests pass.
- [ ] The change has a scenario or test that would fail without it.
- [ ] Server authority intact: the client still only requests.
- [ ] Every new `:Connect` has an owner that disconnects it; every new loop yields.
- [ ] Every yield is followed by a re-check of what might have changed (player left, phase changed).
- [ ] Config values live in `shared/Config`, not inline.
- [ ] Names say what things are; comments say why, not what.
- [ ] No dead code, no debug prints left in, no commented-out blocks.
- [ ] UI changes went through `rbxgame tour` on desktop and phone.
