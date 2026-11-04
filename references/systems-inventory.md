# Inventory, items and trading

Items are data first, models second. The server holds the truth in the player's profile; the client
renders a copy.

## Data model

```lua
-- shared/Items.luau: the catalogue (what can exist)
return table.freeze({
	sword_basic = { name = "Twig Sword", kind = "weapon", rarity = "common", stack = 1, damage = 8 },
	potion_heal = { name = "Dew Tonic", kind = "consumable", rarity = "common", stack = 20, heal = 40 },
	pet_frog = { name = "Leaf Frog", kind = "pet", rarity = "rare", stack = 1, boost = 1.1 },
})

-- profile.Data.inventory: what this player has
-- stackables by id:  stacks = { potion_heal = 7 }
-- uniques by uid:    uniques = { ["a1b2"] = { id = "pet_frog", level = 3, locked = false } }
```

- Catalogue entries are keyed by stable string ids; never by display name or array index.
- Unique items get a `HttpService:GenerateGUID(false)` uid at creation; they can then carry state
  (level, enchantments) and be traded individually.
- Cap inventory size (and stack sizes) and enforce it on every grant.

## Server API (the only way items change)

```lua
Inventory.grant(player, id, count, reason)   -> boolean
Inventory.take(player, id, count, reason)    -> boolean   -- false if they don't have it
Inventory.equip(player, uid)                 -> boolean
Inventory.snapshot(player)                   -> table      -- for the client
```

Every call validates the id against the catalogue, checks capacity, logs the reason, and publishes a
fresh snapshot (or a delta) to that player.

## Client

- Receives the snapshot on join and deltas after; renders a grid (`UIGridLayout`) of item cards.
- Equip, use, sell and drop are requests (`Inventory:FireServer("Equip", uid)`); the client never
  edits its copy before the server answers, except for a pressed state on the button.
- Item art: a `ViewportFrame` with the model (cache them) or a pre-rendered icon image.

## Equipping

- Tools: clone from `ServerStorage` into the character on the server; the client handles animation.
- Cosmetics: attach accessories or welded models on the server so everyone sees them.
- Re-apply equipped items on `CharacterAdded`.

## Trading

1. A requests trade with B (rate-limited, both in the same server, both willing).
2. Both add offers; every change resets both "ready" flags.
3. Both confirm. The server, in one step: re-checks that both still own every offered item, removes
   from both, adds to both, saves both profiles, logs the trade with a trade id.
4. If any check fails, nothing moves.

Never apply half a trade. While a trade is open, lock those items against selling or dropping. Show a
final summary screen with item values both sides can read; scams thrive on fast-changing offers.

## Drops and rarity

- Drop tables on the server: `{ {id, weight}, ... }`, rolled with a server `Random`.
- Show rarity with colour and a sound on drop. Paid random items must disclose odds and follow
  regional rules (`monetization.md`).
- Pity timers for rare drops keep long grinds from feeling hopeless.

## Persistence

Save stacks and uniques in the profile (`data.md`). Migrations handle renamed or removed catalogue
ids (convert or refund, never crash). Validate on load: unknown ids are logged and dropped.
