# The player journey: five hard requirements for every game

The owner's standing requirements (November 2026). A game is not done until each one passes its check.
They apply to the design (CONCEPT.md), the build, and every review capture.
They are the levers for Roblox's key signals (key-signals.md has the mapping and the scorecard).

## 1. Progression that is rewarding: always something to work toward

- **The next goal is always on screen**, with a bar that is already at least 20% full when the player
  first sees it (goal gradient). Examples: "Next bat: 120 / 150 candy", "Book: 9 / 24", "Rebirth 2: 64%".
- **Three horizons at once:** a goal for the next 30 seconds (this round's haul), the next 5 minutes
  (an upgrade or unlock), and the next days (a collection, a rebirth tier, a rare mutation).
- **Every session ends with visible gain:** a number that went up and stays up. A failed attempt still
  pays something (fun-and-juice.md: fail forward).
- **Unlocks change how you play**, not only a number: a new verb, dash, tool, lawn or route.
- Check: in a 10-minute bot or human run, record when each unlock happened. There must be a new goal
  reached at least every 2-3 minutes in the first 15 minutes, and the HUD must show the next goal in
  every capture.

## 2. No unnecessary downtime

- Spawn into action: first input possible within 3 seconds of loading, no lobby walk.
- Lobbies and intermissions are play, not waiting: a mini-activity, a practice target, a shop open
  in-place, or a countdown under 10 seconds.
- Respawn and retry under 2 seconds. No death screen longer than 1.5 seconds.
- Menus open in place over the game, one tap deep, closable by tapping outside. Never a menu to reach
  the main action.
- Walking only when the walk is fun or short (under 5 seconds between activities); otherwise
  teleport pads, dashes or a vehicle.
- Long loads are hidden: stream assets, show the world while it builds.
- Check: in a recorded first session, list every stretch of 5+ seconds where the player cannot act
  or has nothing new to see. Each must be removed or justified in writing.

## 3. Readable without a tutorial: first 30 seconds, then 5 minutes, then 30 minutes

- **0-30 s:** the world itself shows what to do (a glowing target, a highlighted object, others doing
  it). One prompt at most, as a diegetic hint (a hand animating the gesture, an arrow on the thing),
  gone after the first success. The first reward lands before 30 s.
- **30 s - 5 min:** one new idea every 60-90 s, each taught by a situation, not text (a locked door
  next to the key; a target just out of reach until the first upgrade). The first purchase or unlock
  is affordable by minute 2.
- **5-30 min:** the deeper systems open (collection, social stake, rebirth) at the moment the player
  has a reason to care. Show locked things early so the player knows they exist.
- Write the first 30 seconds second by second, the first 5 minutes minute by minute, and minute 30 in
  CONCEPT.md, then compare against captures.
- Check: give a person (or, if none, a fresh model with no design docs) only the first-30-seconds
  capture and ask "what do you do in this game?". It must be answerable in one sentence.

## 4. Social: reasons to interact, compete or play together

- At least two of: something you can do TO another player (steal, shove, tag, sabotage, outbid);
  something you do WITH them (carry, build, rescue, combo, trade); something you show OFF (rare items
  visible on the avatar or plot, a podium, a leaderboard with faces); something you WATCH (a big
  moment others see happen, with a crowd reaction).
- Friends get a bonus for playing together (party multiplier, shared goal, a co-op-only unlock).
- Bots fill empty seats with the same rules so the social stake exists in a quiet server.
- Celebrate other players' moments too: server-wide toasts for rare finds, a spotlight camera beat.
- Check: in a capture of a full round, count interactions between players; there must be several per
  minute and at least one moment where a player's outcome depended on another player.

## 5. Every important action feels satisfying

- List the game's important actions (the core verb, the hit, the pickup, the purchase, the unlock,
  the rare find, the win). Each gets: an anticipation (80-120 ms for heavy actions), an impact
  (hit-stop, shake by trauma, a flash, particles), a sound with 2-3 layers and random pitch, a
  follow-through (squash, wobble, debris that stays), and a number or label that pops.
- The rarer or bigger the moment, the louder: the best outcome is the loudest thing in the game
  (slow motion, a sting, confetti, the camera).
- UI actions too: buttons press into their lip, counters tick up with a rising pitch, rewards fly to
  their counter. Numbers in fun-and-juice.md and visual-craft.md section 3.
- Check: a table in the handoff listing each important action with its visual, animation and audio
  feedback, and a capture or film of each. Any row with a blank cell is not done.

## Where this sits in the workflow

Concept: CONCEPT.md answers all five in writing (concept-gate.md). Build: implement them in the first
slices, not as polish. Review: every capture sheet and handoff reports the five checks with evidence.
A game that is clean and working but fails any check is not finished.

## From the YouTube study (November 2026)

Techniques taken from 21 studied talks and devlogs on Roblox design, retention, loops, UI, monetisation and fun.

- Requirement 2 check: for every product in the shop, name the pain it relieves; delete the ones without.
- Requirement 3 check: two locked things are visible with counts before minute 3.
- Requirement 4 check: a veteran's flex item is visible within 10 s of spawn.
- Requirement 1 check: a benchmark event exists by minute 30 and upgrades raise its score.

## From the YouTube study, batch 2 (November 2026)

From 48 further talks and devlogs (69 studied in total).

- Requirement 1 check: record a fresh player's first three loops; each names a next desire.
- Season check: any big update ships economy reset, new mechanic within 5 minutes, new reward system, new builds, endgame, QoL.
- Older-player check: every screen readable on a phone at arm's length; trading and revive exist before 18+ marketing.
