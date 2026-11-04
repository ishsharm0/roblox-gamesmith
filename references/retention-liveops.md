# Retention and Live Ops

Load when designing reasons to return, daily systems, events, social hooks, analytics, or the experience's store page (icon, thumbnails, title, description). Design theory for loops lives in `game-design.md`; first-minute layout in `level-design.md`.

## The 5 rules that matter most

1. **The algorithm now optimises for 28-day retention.** Since June 2026 Recommended For You measures Day 1, Days 2-7 and Days 8-28 separately; play-through rate and first-play bounce rate replaced qualified play-through rate. Short-term spikes without return visits do not carry a game. https://devforum.roblox.com/t/recommended-for-you-algorithm-improvements-that-better-value-long-term-retention/4684575
2. **Win the first session first.** A player who bounces in the first minute never sees your daily rewards. Fix FTUE before adding live-ops systems.
3. **Give a reason to come back tomorrow, and next week.** A daily reward, an unfinished goal, a timer that completes, a friend who is waiting. Make the reason visible at the end of every session.
4. **Play together beats play alone.** Intentional co-play is an explicit discovery signal; build features that are better with connections.
5. **Measure, then change one thing.** Log funnels, economy and progression with `AnalyticsService`; read Creator Analytics; ship changes in small, attributable steps.

---

## 1. What discovery rewards (2026)

Signals are per-user averages over users who joined organically from the Home "Recommended For You" sort. No single signal decides ranking; the algorithm keeps testing the game with new users. https://create.roblox.com/docs/en-us/discovery-faq.md

| Most important | Meaning |
|---|---|
| Play-through rate (PTR) | Of users shown the game who click, how many actually play the first session |
| First-play bounce rate | Users who leave right after joining (first session) |
| Play days per user (Day 2-7, plus Day 8-28 window) | How many of the following days they came back |
| Playtime per user | Total playtime in the window / users |

| Other signals | |
|---|---|
| Intentional co-play days per user | Days played with people they chose to play with |
| Qualified play sessions per user | Sessions that count as real play |
| Spend days per user, Robux spent per user | Spending, measured separately from play |

Practical consequences:

- **Metadata must match the game.** Misleading or mismatched thumbnails, titles, genre tags or gameplay video raise bounce and can reduce exposure. Near-identical copies of other games' visuals/titles get less discoverability; Roblox favours the one that added the unique metadata first.
- **Thumbnails are being personalised and tested against PTR.** Upload several honest thumbnails showing different angles of the game.
- **Spending is measured separately from play.** Aggressive early monetisation that hurts bounce or Day 2-7 return costs more than it earns.
- Check Creator Analytics > Acquisition > Home Recommendations for where the game is weak.

Background: Roblox newsroom, June 2026 https://about.roblox.com/newsroom/2026/06/optimizing-discovery-great-games-reach-millions-players-roblox

---

## 2. Daily rewards and streaks

- Calendar of 7 (and optionally 28-30) days, escalating; day 7 notable, day 28 exclusive cosmetic.
- **Do not wipe the streak on one missed day.** Pause it or allow 1 grace day per week; offer a "streak saver" earned in game. Punishing absence lowers Day 8-28 return.
- Claim UI appears after the first reward of a session, not on join (do not block the FTUE).
- Server time only, UTC day boundaries, stored in the profile.

```lua
-- Server. profile.Data.Daily = { lastDay = 0, streak = 0, graceUsed = false }
local function utcDay(): number
	return os.time() // 86400
end

local REWARDS = { 50, 75, 100, 150, 200, 300, 1000 } -- coins; day 7 is the big one

local function claimDaily(profile): (boolean, number?)
	local d = profile.Data.Daily
	local today = utcDay()
	if d.lastDay == today then
		return false -- already claimed
	end
	local gap = today - d.lastDay
	if gap == 1 then
		d.streak += 1
	elseif gap == 2 and not d.graceUsed then
		d.streak += 1
		d.graceUsed = true -- one forgiven miss per cycle
	else
		d.streak = 1
		d.graceUsed = false
	end
	d.lastDay = today
	local index = ((d.streak - 1) % #REWARDS) + 1
	if index == 1 then d.graceUsed = false end
	local amount = REWARDS[index]
	profile.Data.Coins += amount
	return true, amount
end
```

---

## 3. Quests and goals

- **Daily**: 3 short quests (5-15 minutes total) that steer players through different systems; one free reroll per day.
- **Weekly**: 3-5 larger goals; reward a premium-feeling cosmetic or currency.
- **Long-term**: collection index, achievements, rank/rebirth. Always show the next unfinished milestone in the HUD or on the session-end screen.
- **Timers that complete while away**: crops grow, eggs hatch, factories produce. Cap offline accumulation (e.g. 8-12 h) so returning daily beats returning weekly.
- Quest progress is server-side, driven by the same events your analytics log.

---

## 4. Social hooks

- **Better together**: co-op bonuses when playing with connections (`player:IsFriendsWith(otherUserId)`; Roblox calls friends "connections" in its UI), shared goals, party-size reward multipliers, trading, gifting.
- **Invites**: `SocialService:PromptGameInvite(player)` after the player has had fun (post-first-reward or after a win), with a reward for invited users who play; check `SocialService:CanSendGameInviteAsync(player)` first.
- **Show-off surfaces**: leaderboards near spawn, showcase plots, rare item auras, titles.
- **Groups**: optional group-join reward (`player:IsInGroup(groupId)` on the server); never gate content behind it.
- **Trading**: check `PolicyService:GetPolicyInfoForPlayerAsync(player).IsPaidItemTradingAllowed` before allowing trades of items bought with Robux; log every trade (see `systems-inventory.md`).
- **Chat**: use `TextChatService`. Default chat needs no work; custom chat UIs must move to platform-integrated chat (default from February 2027, required May 2027). https://create.roblox.com/docs/chat/platform-integrated-chat.md

---

## 5. Notifications, events and updates

- **Experience notifications**: `ExperienceNotificationService:PromptOptIn()` shows an opt-in prompt to users 13+ who have not opted in and have not seen it in 30 days; ask after a meaningful moment ("Get notified when your eggs hatch"). Send through the Open Cloud `UserNotification` API with a notification string created in the Creator Dashboard; users receive at most one notification per experience per day. https://create.roblox.com/docs/en-us/production/promotion/experience-notifications
- **Events**: weekend boosts, seasonal zones, limited cosmetics. Time-limited cosmetics are fine; time-limited power is not. Bring popular event items back later in a variant.
- **Cadence** (adjust to team size): weekly small update (fixes, balance, a new item), monthly content drop (new zone, system or event), quarterly big update. Announce in an in-game update board and on the game page.
- **Updates must not reset trust**: never wipe progress; migrate data (see `data.md`).

---

## 6. Analytics

Log on the server with `AnalyticsService` (Log* methods; the old `Fire*` methods are deprecated). https://create.roblox.com/docs/en-us/reference/engine/classes/AnalyticsService.md

| Method | Use | Limits |
|---|---|---|
| `LogOnboardingFunnelStepEvent(player, step, stepName)` | FTUE steps | steps 1-100 |
| `LogFunnelStepEvent(player, funnelName, funnelSessionId, step, stepName)` | Shop, quest, purchase flows | 10 funnels per experience |
| `LogEconomyEvent(player, flowType, currency, amount, endingBalance, transactionType, itemSku)` | Sources and sinks | 5 currencies, 20 transaction types, 100 SKUs; amount > 0 |
| `LogProgressionEvent` / `LogProgressionStart/Complete/FailEvent` | Levels, stages | not in Roblox's default charts yet |
| `LogCustomEvent(player, name, value?)` | Anything else | custom fields only via `AnalyticsCustomFieldKeys`, 8,000 combos |

```lua
local AnalyticsService = game:GetService("AnalyticsService")

-- FTUE
AnalyticsService:LogOnboardingFunnelStepEvent(player, 1, "Spawned")
AnalyticsService:LogOnboardingFunnelStepEvent(player, 2, "FirstCoin")
AnalyticsService:LogOnboardingFunnelStepEvent(player, 3, "FirstUpgrade")

-- Economy: earned 25 coins from a quest
AnalyticsService:LogEconomyEvent(player, Enum.AnalyticsEconomyFlowType.Source, "Coins", 25,
	profile.Data.Coins, Enum.AnalyticsEconomyTransactionType.Gameplay.Name, "DailyQuest")
```

Read in Creator Analytics: retention (D1/D7/D30 cohorts), engagement (session length, sessions per user), monetisation (payer conversion, ARPDAU), acquisition (Home Recommendations signals), funnels and economy dashboards. Rough community benchmarks, not official: D1 20-30% healthy, D7 8-15% strong, D30 3-6% very strong; median session 10-20 minutes in most genres.

Use experiments for big changes (Roblox's experiment tools in the Creator Dashboard, or your own A/B split by `UserId % 2` logged as a custom field), and change one variable per experiment.

---

## 7. Store page

| Asset | Spec | Notes |
|---|---|---|
| Icon | Square, 512x512 | One focal subject, strong silhouette, high contrast, readable at ~150 px; no small text |
| Thumbnails | 16:9, 1920x1080, several | Real in-game captures, composed and lit well; light text overlay allowed but not required |
| Video | Short gameplay | Show the core loop in the first seconds |
| Title | Short, searchable, genre-clear | No emoji spam, no fake update tags, no misleading claims |
| Description | First two lines say what you do and why it is fun | Then features, update notes, social links |
| Genre/tags, maturity | Accurate | Complete the content maturity questionnaire honestly; mislabels hurt bounce and can be actioned |

Icon guidance: https://create.roblox.com/docs/production/promotion/game-icons

**Real captures only.** Thumbnails and icons come from the actual game: stage a scene in Studio (good lighting preset, characters posed, UI hidden), capture at full resolution, then crop, colour-grade and add a title in an image editor. Never use AI-generated art, renders of things not in the game, or other games' assets. With MCP: position the camera with `studio shot out.png --pos x,y,z --look x,y,z`, but the viewport capture resolution is limited, so for final 1920x1080 thumbnails take the shot in Studio at full screen or use a dedicated capture place; ask the user before uploading anything.

---

## Live-ops checklist

- [ ] FTUE funnel logged; first-play bounce known
- [ ] Daily reward with forgiving streak; claim after first reward of session
- [ ] Daily/weekly quests touching different systems
- [ ] At least one feature better with connections; invite prompt after fun
- [ ] Offline progress capped to encourage daily return
- [ ] Economy sources/sinks logged; currencies <= 5
- [ ] Update board in game; regular cadence planned
- [ ] Store page: honest icon/thumbnails from real captures, accurate genre/tags/maturity
- [ ] Notification opt-in asked at a meaningful moment (13+ only)

---

## CHANGELOG

- 2026-11-03: New file. Discovery section reflects the June 2026 RFY change (28-day window, PTR + first-play bounce replace QPTR).
