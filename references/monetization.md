# Monetization that players don't resent

Players pay for games they already enjoy. Money comes after the core loop is fun and the first session
retains. A shop added to a boring game makes a boring game with a shop.

## The products

| Product | What it's for | Notes |
|---|---|---|
| **Game pass** | Permanent perks: 2x coins, VIP area, a trail, an extra slot | One-time; check ownership with `MarketplaceService:UserOwnsGamePassAsync` (cache per session) and on `PromptGamePassPurchaseFinished` |
| **Developer product** | Consumables: coins, revives, skips, boosts | Repeatable; granted in `ProcessReceipt`, which must be idempotent (`receipts.md`) |
| **Subscriptions** | Monthly perks | Check status server-side each session; perks end when it lapses |
| **Private servers** | Play with friends alone | Price in game settings; cheap ones (or free) raise retention |
| **Premium payouts** | Engagement-based income from Premium members | Free money for time played; a Premium-only perk (small) nudges it |
| **Immersive ads / rewarded video** | Where available, opt-in rewards | Follow current Roblox ad policy and age rules |

## Placement that works

- Show the value in play before the price: let the player see the VIP trail on someone else, use a
  boost once free, see the pet they'd get.
- One shop entry point in the HUD, and contextual offers at natural moments (after a failure: "revive
  for 25"; after a win: "double this reward").
- Never interrupt the core loop with a prompt; never put a prompt behind a fake close button.
- Prices in a ladder (small, medium, best value). Roblox players spend in small amounts; the most
  bought products are usually the cheapest.

## Fairness lines

- Skill games: sell cosmetics, convenience and second chances, not score. A paid leaderboard ruins it.
- Competitive games: no damage or health for Robux. Matchmaking that ignores spending is a must.
- Random paid items (loot boxes, gachas) must show odds, and paid random items are restricted in some
  regions; check the current Roblox policy before shipping one, and prefer direct purchases.
- Children make up much of the audience; no pressure tactics (countdown sales on everything, guilt
  messages, "your friends bought this").

## Implementation rules

- Prices and product IDs live in one server config module; the client receives a display list.
- The client calls `PromptProductPurchase` / `PromptGamePassPurchase` (or the server prompts a
  player); either way, only the server grants. A client that claims it bought something is ignored; only `ProcessReceipt` and
  ownership checks count.
- Grant game pass perks both at join (owned) and immediately after purchase (finished event), so
  players don't have to rejoin.
- Log every grant with `PurchaseId`, product and player; use `AnalyticsService:LogEconomyEvent` for
  sources and sinks.
- Test with Studio's test purchases (no Robux spent) and a receipt scenario (`receipts.md`),
  including a failed save and a duplicate receipt.

## Balancing the economy

- Every currency has sources (earning) and sinks (spending). Track both with analytics; inflation
  shows up as unspent balances climbing.
- A paid shortcut should save time a player could also spend; if nobody can reach something without
  paying, it's a paywall.
- Price soft currency so a session's earnings buy something visible: the first purchase within the
  first 10 minutes.

`workflows/audits.md` has the monetization audit; run it before turning on any product.
