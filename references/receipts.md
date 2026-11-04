# Durable developer-product grants

Use `templates/project/src/server/ReceiptGrant.luau`. It stages the reward and PurchaseId in ONE
session-locked profile, and acknowledges only when that PurchaseId appears in `LastSavedData`.
An unsaved in-memory receipt prevents a duplicate grant but does not justify PurchaseGranted.
A failed save returns NotProcessedYet on every retry until durable confirmation exists.

Configure one ProcessReceipt callback. Resolve ProductId in server-owned configuration, find the
player's active ProfileStore profile, call ReceiptGrant.Grant with the PurchaseId and a function
that modifies only the supplied profile-data table, and map true to PurchaseGranted and false to
NotProcessedYet. Unknown products and absent/inactive profiles return NotProcessedYet.

The callback must not yield, send remotes, grant transient world objects, or write other stores.
For temporary effects, persist an entitlement/token first and consume it through a separate
idempotent system. Reward and receipt in separate keys cannot form an atomic transaction.
Keep leaderstats/UI as mirrors; update them after grant processing. Do not prune durable receipt
IDs arbitrarily: monitor serialized profile size and design an archive/reconciliation policy before
it reaches the store limit.

Test storage failure, retry before persistence, retry after persistence, duplicate concurrent
callbacks, lost session, unknown ProductId and partial callback failure. The Lily Pad Leap receipt
scenario covers failed saves, memory-only retries, durable confirmation, deduplication and rollback.
This is a reusable primitive, not an enabled shop; use real product IDs only after the product plan
has been approved.

Primary sources reviewed 2026-11-03:
- https://create.roblox.com/docs/reference/engine/classes/MarketplaceService#ProcessReceipt
- https://madstudioroblox.github.io/ProfileStore/devproducts/
- https://madstudioroblox.github.io/ProfileStore/api/
