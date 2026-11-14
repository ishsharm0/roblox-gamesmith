# Fun, stickiness and ideas: what the concept gate does not cover

Read after `concept-gate.md` and before designing systems. Researched November 2026 from designer talks,
postmortems, Roblox's own docs and live charts; tags: [V]/[verified] checked at the source, [H]/[memory]
a default to tune by eye. Charts move weekly: re-check with `references/research.md` before committing.

## 0. THE ONE-PARAGRAPH ANSWER (read this if nothing else)

Popular, sticky games are made of four stacked layers, and the two rejected games had only layer 1:
1. Feel: the verb is pleasurable for 30 seconds with no goal (juice, forgiveness, readable cause and effect).
2. A decision or a skill beat that has a visible risk and a visible reward (Sid Meier: a series of interesting decisions).
3. A number or collection that grows across sessions, with a purchase every 20 to 60 seconds early (idle math, Vampire Survivors reward cadence).
4. Other people: a stake (steal, rescue, tether, sabotage, trade, spectate) that produces a filmable clip. Every 2025-26 breakout outside Roblox (Lethal Company, Content Warning, R.E.P.O., Peak, Meccha Chameleon, How to Fish) is a cheap game whose core fun happens BETWEEN friends and whose clips sell it. [verified: https://appmagic.rocks/blog/friendslop-steam-games-2025 ; https://newsletter.gamediscover.co/p/how-peak-sold-45m-copies-in-less]

"Not much to it" = layers 2 to 4 missing. More levels (more layer 1) never fixes that.

---------------------------------------------------------------------

## 5. CREATIVITY METHODS (and a procedure a weaker model can run)

### 5.1 Methods real designers use
- Game jams: constrain by time (48 h) and by theme; the first idea that survives a 10-minute paper prototype beats the best idea never built. Peak itself came out of a short offsite jam with a goal of "commercial game in a short time". [verified: GameDiscoverCo Peak article]
- "Find the toy first" [memory: Nintendo/Miyamoto, Shigeru; Sakurai; also Jenova Chen's flower-field "emotion first"]: before levels or goals, find a thing that is fun to poke with no goal (Mario's jump, Katamari rolling, Peggle's ball bounce). If the toy isn't fun in 30 s on a flat plane, stop.
- Kishotenketsu for levels: teach, vary, twist, conclude (section 1.1). [verified]
- Verb/noun matrices [memory]: list 8 verbs (carry, throw, tow, stack, aim, ride, hide, swap) and 8 nouns/settings (rope, elevator, pizza, moon, glacier, orchestra, post office, aquarium); combine; keep the ones where the verb has a skill beat and the setting suggests a hazard.
- "What is the clip": write the 10-s clip first; build only mechanics that produce it. [verified: clip-first pattern: Content Warning/Peak; Dead Rails twist "must show in a five-second clip" in concept-gate.md]
- Constraint-first design [memory]: lock constraints that cut cost (stock R15 avatar, no custom characters, one small map, <300 physics parts, 4-8 players) THEN ask what the funniest game inside them is. Peak and Meccha Chameleon (2 people, ~$5 price) are constraint-first. [verified: Windows Central]
- Mutation of proven loops: clone the structure, change one verb (Break and Steal an Egg, Steal An Egg treadmill, Fake an Egg). [verified: game-design.md]
- MDA: pick the aesthetic first (section 1.1). [memory]
- Interesting decisions test (Meier). [verified]
- Theory of Fun test: what pattern does the player learn at minute 1, 5, 20? [verified-summary]
- Roblox-specific rule: the verb must work on a phone thumb and a mouse. [game-design.md]

### 5.2 STEP-BY-STEP IDEATION PROCEDURE (weak-model runnable, ~40 min)
Input: nothing. Output: 1 chosen concept with 60-second script.
1. Pick 3 proven hits from section 3/4 whose STAKE you like (e.g. Peak's tether, Steal an Egg's raid, Lethal's quota).
2. For each, write: core verb, shared meter, the stake (what another player can do to/with me), the growing thing. 4 lines.
3. List 8 verbs from the Roblox physics/toolbox you can build in a day (carry, throw, grab, tie, ride, swing, stack, paint, flick, type, time-a-bar, steer).
4. List 8 fantasy settings where something goes wrong funnily (moving company, pizza van, lifeguard, space janitor, museum guard, deep dive, haunted hotel, lighthouse).
5. Generate 25 lines in the format: [fantasy] + [one verb with a skill beat] + [what another player can do to or with me] + [a collectable or number that grows]. At least 10 must change the VERB of a proven stake, not the skin.
6. Kill test (any fail = kill): (a) clip test: 10-s clip, UI off, stranger understands; (b) mutation test: name the proven game + the one verb changed; (c) stake test: another player does something TO/WITH me; (d) the verb has a skill beat (a timing, an aim, a balance); (e) a number/collection grows across sessions; (f) buildable in 1 week with stock avatar and <300 physics parts.
7. Score survivors 0-3 on six axes: Clip, Stake, Skill beat, Growth, Mutation novelty, Cheapness. Add. Max 18.
8. Take top 5. For each, write: first 60 seconds by second; the clip; 3 depth systems (and the minute each first shows); 1-week plan; biggest risk; kill criterion.
9. Pick the one whose biggest risk you can test in 48 h with a greybox and 5 humans. If a risk cannot be tested in 48 h, drop it.
10. Playtest gate from concept-gate.md: 3 of 5 voluntary restarts, 2 of 5 "watch this" moments.

### 5.3 RUN: 25 concepts and scores
Scores: C=clip, S=stake, K=skill beat, G=growth, M=mutation novelty, B=build-cheap (each 0-3). Total /18. My judgement, [heuristic]. "from" names the proven structure.

 1. TETHER CLIMB: mountaineers roped together with a physical rope; stamina bar that injuries damage; whoever falls swings the team. From Peak + Roblox RopeConstraint. C3 S3 K2 G2 M2 B2 = 14.
 2. ANOMALY HOTEL: half the players are guests who secretly move/replace room items between inspections; the other half are night staff who must spot changes; roles swap each round. From Animal Hospital/Sell Fries anomaly + Among Us. C3 S3 K2 G2 M3 B2 = 15.
 3. FRAGILE MOVERS: two to four players carry a priceless item (piano, glass) through a house; value ticks down on bumps; stairs and doors need turn coordination. From R.E.P.O. + carry. C3 S3 K2 G2 M2 B2 = 14.
 4. PINATA PANIC: one random player is the pinata (runs, candy inside grows as they survive); others swing bats with timing bar; each hit sprays candy to everyone. Hunt asymmetry, from Fake an Egg + sumo. C3 S3 K3 G2 M3 B2 = 16.
 5. SHARED TANK DIVER: all divers breathe from one oxygen tank on the boat; salvage loot, greedy divers drain it; boat winch pulls everyone up in 90 s cycles. From Lethal Company quota + Peak shared meter. C2 S3 K2 G2 M3 B2 = 14.
 6. PIZZA LAVA: deliver pizzas across a rising lava level, others can rob your pizza and you can wave a coupon... From Escape Tsunami + steal. C2 S3 K2 G2 M1 B3 = 13. (hazard clone, low novelty)
 7. CRANE CREW: one player drives a crane hook, others stand on the hook platform placing beams; a heist of stacking a tower. From Backseat Rally asymmetric + Peak. C3 S3 K2 G1 M3 B1 = 13 (physics risk).
 8. HUSH HOTEL: sneak room service past a sleeping giant; sprinting makes noise; other players can throw bells to wake it. From DONT SPLASH rule + friendly griefing. C3 S2 K3 G2 M2 B2 = 14.
 9. TYPE-A-SPELL ARENA: duel by typing 3-4 letter words shown on screen; wrong letter backfires; interrupts via collision. From YAPYAP shout. C2 S3 K3 G2 M2 B3 = 15 (mobile typing risk).
10. SLIME KING (.io): eat, grow, split, throw mass to a friend. From .io. C2 S3 K2 G3 M1 B3 = 14.
11. TRAMPOLINE BRAWL: bounce-to-height contest, spikes of height score; knock others with a dive. From Cat Battles. C2 S3 K3 G2 M1 B3 = 14.
12. TAPE NIGHT: film mode with a clip ring buffer; judged views at dawn. From Content Warning. C3 S2 K1 G2 M2 B2 = 12.
13. FISH BANK: fishing with a SHARED group bank; anyone can bet the bank on a boss fish. From How to Fish + Fisch. C2 S3 K2 G3 M2 B2 = 14.
14. PAINT HIDE: sample colour under you and spray to blend; seekers have a scanner. From Meccha Chameleon. C3 S3 K2 G2 M2 B2 = 14.
15. CHICKEN TRAPS OBBY: each round players place one hazard each; the course accumulates; points for finishing when not everyone does. From Ultimate Chicken Horse. C3 S3 K3 G2 M2 B2 = 15.
16. ROPE BOAT: row a boat in sync, one steers, one bails, one navigates by map; capsizes with rogue waves. From Backseat Rally + Peak. C2 S3 K2 G2 M2 B2 = 13.
17. GRAVITY JANITOR: mop a space station with magnet boots; airlock buttons can be pressed by others (friendly griefing). C2 S2 K2 G2 M2 B2 = 12.
18. MERGE MARKET: shared merge board; each friend's merge feeds one machine; ingredients sell at a stall. From merge + Grow a Garden. C1 S2 K1 G3 M2 B3 = 12.
19. LIGHTHOUSE KEEPER: co-op defend by aiming a shared beam (one rotates, one adjusts focus) vs night swarm. From 99 Nights + two-player dependency. C2 S3 K3 G2 M2 B2 = 14.
20. SOUP RELAY: carry a full bowl through a moving crowd, spill rule; passing the bowl to a teammate mid-run. From carry + balance. C3 S2 K3 G2 M2 B3 = 15.
21. ESCAPE ELEVATOR: shared elevator with a button panel; each floor a mini room; others press other floors (griefing), creating the clip of surprise doors. C3 S3 K1 G2 M2 B3 = 14.
22. MOVING DAY RV: a driving RV with duties (steer, fix, shoo raccoons); fix tasks mid-road. From RV There Yet? + Dead Rails. C3 S3 K2 G2 M2 B2 = 14.
23. DOMINO DEMOLITION: build a domino chain with friends, someone triggers early (friendly griefing); chain scores = coins. C3 S3 K2 G2 M1 B2 = 13.
24. KITE FESTIVAL: steer a kite in shared wind and cut others' strings (kite fighting); string upgrades. C3 S3 K3 G3 M3 B2 = 17 (novel verb; physics wind simple).
25. SWAP-SHOP SHOPLIFT: customers vs shopkeepers; keeper has 5 cameras, customers hide items in disguises; items stolen = coins. From Fake an Egg + Animal Hospital. C3 S3 K2 G2 M1 B2 = 13.

Ranking by total (ties broken by cheapness and testability): 
 Kite Festival 17; Pinata Panic 16; Anomaly Hotel 15; Type-a-Spell 15; Chicken Traps Obby 15; Soup Relay 15; then 14s.
Honesty note: I selected the top 5 by total but swapped Type-a-Spell and Chicken Traps Obby for Tether Climb and Fragile Movers because the 14-point ones have more verified comparables (Peak 15.4M, R.E.P.O. 18.5M copies) and Roblox-native physics fit; scoring ignores that. Final five: Kite Festival, Pinata Panic, Anomaly Hotel, Tether Climb, Fragile Movers.

### 5.4 TOP 5 IN DETAIL

#### C-K. KITE FESTIVAL (kite fighting)
Formula: festival-goer + steer a kite in shared wind with a pull/slack skill beat + cut the strings of rival kites and steal their tails + collect string upgrades and a trophy sky of kites.
Why: novel verb with no Roblox clone; fully visible from far away (kites in the sky read in a thumbnail). Related to a real, ancient sport [memory] so no IP issue.
First 60 s: 0-5 s spawn on a hill with a kite already in the air above a wide meadow; 5-10 s drag/hold to pull string (kite climbs or dives), see wind arrows; 10-20 s fly through three wind gusts for coins; 20-30 s a rival kite appears, your string glows where it can cut; 30-45 s first cut: tap at the crossing moment (timing bar of 0.4 s) to slash; their kite spins down with ragdoll tail ribbons; 45-60 s the fallen kite's tail ribbons fall for you to catch; you buy the first stronger string.
Clip: two kites crossing, a string snaps with a slow-mo 0.3x for 0.4 s, the loser's kite tumbles.
Depth: (1) string tiers (strength, length) with 5 levels x costs 1.15^n; (2) tail ribbon collection with colours x 1/20 mutations; (3) wind zones that change every 60 s (hazard cycle readable); (4) tournament bracket every 10 minutes; later team kites. Minute 10: new wind pattern + first rival with shield; minute 20: tournament.
Build plan 1 week: D1 kite physics = a Part with BodyVelocity/LinearVelocity steered by two inputs (pull/slack, tilt) and a visual-only string using Beam between hand and kite; D2 wind field (global direction + gusts, readable via particles and ribbon motion); D3 cut mechanic: raycast segments between rival string points, timing prompt, server-validated; D4 coins/upgrades/DataStore; D5 meadow environment, lighting, sound; D6 matchmaking of 6-10 players, bots; D7 playtest and tune.
Biggest risk: string-cut collision detection across lag. Mitigation: approximate string as a line between hand and kite sampled at 4 points; resolve cuts on server with a 100 ms forgiveness window; the cut is a "contest" where both players have a timing bar so latency matters less.
Kill criterion: fewer than 2 of 5 testers cut a rival within 90 s unprompted.

#### C-P. PINATA PANIC
Formula: party-day + dodge a swarm of bat-wielding kids with a sprint/stamina skill beat + candy you hold bursts out of you on hits for everyone to grab + a candy collection of mutated sweets and a pinata wardrobe.
First 60 s: 0-5 s join a lobby of 8, 10-s countdown; 5-15 s one player becomes the pinata (random, but never the same player twice in a row); 15-25 s the others chase; pinata can dash (3 s cooldown) and jump over low fences; 25-35 s first hit lands, 12 pieces burst, camera shake 0.15 s, hit stop 60 ms; 35-60 s everyone races for candy, pinata hides on a roof where candy count grows 1/s. Round ends at 90 s or when pinata is "broken" (5 hits).
Clip: the burst: 40 candy pieces ragdoll across the lawn and 5 kids dive-tackling the same piece. 
Depth: pinata skins with a different dash (rolling, jump); candy rarity and mutations (rainbow, gold); bats with different timing arcs; birthday cake hazard zones; rounds rotate lawns. Rebirth: "party level" unlocks harder lawns with 2x candy.
Build plan: D1 chase + dash + hit; D2 burst spawn with despawn after 10 s and pickup magnet; D3 round loop and role rotation; D4 progression + DataStore; D5 art and sound; D6 bots as bat kids; D7 tune.
Biggest risk: hunted player feels bad. Mitigation: pinata is the hero: lots of invulnerable frames after hit (0.8 s), it keeps 50% of the candy it carries at round end, and "rescue" kids can block bats.
Kill: pinata players quit mid-round more than 20% of time (record in playtest).

#### C-A. ANOMALY HOTEL
Formula: hotel night shift + inspect a room for what changed with a timed 20-second inspect + guests (other players) secretly rearrange items between inspections + a star rating and room-themes collection.
Inspired by Animal Hospital (358k at its August peak; 1.7B visits) and Sell Fries (cosy by day horror by night), but PvP: the anomaly maker is a human. [verified: game-design.md citing studiokrew & ggrecon]
First 60 s: 0-10 s you are staff, a bell rings, you walk into a hallway lit warm; 10-25 s inspect room 1 (a clipboard shows the "correct" snapshot as 6 icons); 25-40 s you find the clock is wrong; press report, ding +coins; 40-60 s meanwhile as a guest next round you have 15 s to swap a lamp with a vase before the staff come.
Clip: staff member spots the swap at the last second, or a guest hiding inside the wardrobe watching.
Depth: more anomaly types (swap, rotate, missing, extra, colour shift) parametric across modular rooms (concept-gate says this is the cheap way); hotel tier unlocks (lobby decor, themes); rank ladder; "Supervisor" role sees everything. 
Build 1 week: D1 modular room kit with 12 swappable props; D2 snapshot/diff system (server stores each prop's cframe/colour/exists and compares); D3 guest move tool with 15 s and noise rule (carrying makes a sound ring staff can hear); D4 round loop of 8; D5 rewards/themes; D6 lighting/audio; D7 playtest.
Biggest risk: fairness and solvability: guests can hide moves cleverly, staff frustrated. Mitigation: the diff tool is exact and each round caps changes at 3; staff has a "flashlight" scan hint after 20 s.
Kill: <3 of 5 testers say "again".

#### C-T. TETHER CLIMB
Formula: stranded mountaineers + climb with a stamina meter, grab-and-lunge skill beat + tied together by a rope so a fall yanks everyone and a rescue pull saves them + a summit height and rope/gear collection.
First 60 s: 0-5 s start tied to 2 friends or bots at a base camp, snow wind; 5-15 s climb a slope with sprint; stamina bar drains, rest ledges; 15-30 s first rock face with grips, press to grab/lunge; 30-45 s teammate slips, rope tightens, you feel the pull (camera yank 0.2 s) and must hold or let go to cut loose (cutting saves you but loses them); 45-60 s reach a flag, +altitude, +coins.
Clip: three people wobbling on a rope, the one at the end falling and swinging everyone, the "cut the rope?" decision.
Depth: gear (pick, cleats, bag weight like Peak), weather cycle every 90 s, procedural daily mountain seed, ghost helper; tournaments with altitudes.
Build 1 week: D1 climb + stamina; D2 RopeConstraint chain with rope visual (Beam) and a max-length constraint; D3 fall/yank forces tuned; D4 rescue mechanics; D5 procedural route (seed per day) from 6 modular slabs; D6 audio/wind/lighting; D7 test.
Biggest risk: physics stability of ropes with lag and exploits (flying). Mitigation: rope is a simple spring distance rule not a physics rope; server applies velocity impulses; cap speed. Roblox can handle RopeConstraint with network ownership issues [memory]; if unstable, use a "tether line" visual only.
Kill: 2+ of 5 groups don't try to rescue each other.

#### C-F. FRAGILE MOVERS
Formula: moving-day crew + carry/steer a heavy priceless object through a house and out to the truck, balance rule + the object's value ticks down at every bump + saves for upgrades to the truck and crew.
Clip: two players rotating a couch up stairs while a third yells; the grandfather clock topples and value flashes red.
First 60 s: 0-10 s spawn at the truck; 10-25 s grab a lamp together (solo you can only slide it); 25-45 s navigate a corner, collision force flashes the value; 45-60 s load into the truck, +money.
Depth: item tiers; shortcuts; random events (dog runs through, floor wet); truck capacity upgrades.
Build 1 week: grab constraints with soft force, collision damage from relative velocity (as the R.E.P.O. approach), 3 houses.
Biggest risk: Roblox physics jitter with welded players/objects and low-end mobile perf; cap props at ~120 unanchored.
Kill: players do not coordinate within 2 minutes.

---------------------------------------------------------------------

## RULES TO ADD TO THE GAME SKILL (ordered by impact; max 40)

1. Write the 10-second clip before any code; if it cannot be filmed without UI, the concept fails.
2. Every concept must contain a stake: another player can do something TO or WITH me, and it must be reversible or recoverable.
3. Never ship a game with only layer 1 (feel): require a growing number or collection AND another player in the same space.
4. Make the verb need a second player (carry, tether, spot, hunt) rather than merely allow one.
5. Use one shared meter that all hazards feed (stamina, oxygen, quota, rope tension, value-left).
6. First input within 3 s of spawn; first reward in 15 s; first affordable upgrade by 30 s.
7. Every attempt pays something; failed run shows distance to the next purchase.
8. Retry takes under 3 s with no menu.
9. Use a four-act micro-loop (teach, vary, twist, payoff) of 60-90 s; the twist re-uses the same input.
10. Name a decision with no dominant choice at minute 3; if none exists, add a risk/reward fork.
11. Teach a new pattern at minutes 5, 10 and 20 (new tool, hazard or combo).
12. Client-predict all feedback (sound, particles, shake) on input; the server only corrects state.
13. Stack small effects on every impact: sound (3 layers, pitch random 0.92-1.08), particle burst, camera trauma, hit stop, popup number.
14. Use trauma-based camera shake (trauma 0..1, shake = trauma^2, smooth noise, decay about 1.5 per second), never random jitter; add a reduce-shake setting.
15. Hit stop: 40 ms small, 80 ms medium, 120-160 ms finisher; freeze both actors' animations then restore.
16. Add input buffer 120 ms and coyote time 100 ms to any jump or action; add invisible corner correction.
17. Make hitboxes and pickup radii 20-30% bigger than they look; magnet pickups at 6-10 studs.
18. Give heavy actions an 80-120 ms anticipation pose and a 100-200 ms recovery.
19. Leave permanence: debris, paint, corpses persist (cap ~300 parts, despawn 10 s after settling).
20. Make the best outcome the loudest thing in the game; reserve slow-mo and the biggest sound for it.
21. Idle numbers: cost = base * 1.15^owned (1.07 for cheap tiers); multipliers at 25 and 50 owned; first rebirth at 8-12 minutes; each next about 2x longer; cap offline income at 2 hours.
22. Use rolls with earned currency only; if Robux touches the roll, show exact odds before purchase, check PolicyService, update odds for luck boosts, block trading of paid items for restricted users.
23. Add a visible pity counter on rare rolls and a collection book with silhouettes.
24. Show a progress bar to the next goal at 20% or more on arrival; make late steps cheaper (goal gradient).
25. Roguelite rounds: reward tick every 20-30 s, pick 1 of 3 upgrades every 40-60 s, persistent currency that moves a bar every round.
26. Daily ladder 7 days, 1-day grace, reward worth 10-15 minutes of play; never a hard reset to zero.
27. Add a 5-minute in-session ritual (restock, wave, tide) so there is a reason to stay five more.
28. Design for Roblox's signals: PTR + bounce (honest icon, join under 10 s on a low-end phone), play days (daily/event/idle), co-play days (friend-required mechanic), playtime (15-20 minute first session of 3-5 loops).
29. Mutate the VERB of a proven stake; reskins lose (about 8% of format traffic). Name the proven game and the changed verb in CONCEPT.md.
30. Keep every concept constraint-first: stock R15, one small map, 4-10 players, bots fill seats, under 300 live physics parts.
31. Give dead players a job (ghost, spectator helper, camera) so death is not exit.
32. Build one seasonal event per quarter and have the first ready in weeks 3-4; MM2-style events double CCU.
33. Offer friendly griefing tools that are funny not destructive (shove, swap, rope, bell, steal-and-return).
34. Use the proven thumbnails rule: one dominant subject at near-full-frame, saturated colour, readable at 150x150, the clip not the menu, nothing important on the bottom edge; upload 2-5 different 16:9 thumbnails.
35. Judge icon changes by impressions-to-visits over 7 days AND bounce rate; do not trust unsourced CTR claims.
36. Lighting recipe: Technology, Atmosphere (density 0.25-0.4), Bloom (0.3-0.8, high threshold), ColorCorrection (+contrast, +saturation, mood tint), SunRays subtle; add motion (wind, particles, ambience) before adding props.
37. Keep scale consistent (door 7-8 studs, player 5) and one visual style; consistency beats fidelity.
38. Test on a low-end phone; crash on join counts as bounce.
39. Ask the 3-minute playtest questions (restart? "watch this"? one-sentence goal?) with 5 real people; bots only prove completability; if no humans, say so in the handoff.
40. Plan a 2-4 week life: ship the second event before the first ends and a daily/seed variation (Peak's daily mountain) so replays differ.

---------------------------------------------------------------------
## JUICE CHECKLIST WITH NUMBERS (copy into the game skill)

Source tags: [V] verified in this research, [H] heuristic default, tune by eye.

Input and response
 [ ] Visual+audio response within 1 frame (16 ms) and total feedback under 100 ms from input [H; <100 ms from secondary refs].
 [ ] Input buffer 120 ms [V: Godot checklist]. Coyote time 100 ms [V], about 6 frames; Celeste wiki says 5 frames [V-secondary].
 [ ] Jump apex: hold-to-float halves gravity near apex (Celeste) [V]. Corner correction about half a step [V].
 [ ] Walk/run acceleration ramp 0.08-0.12 s; sprint FOV +4 to +8 degrees over 0.15 s [H].

Impact (per hit)
 [ ] Hit stop 0.06 s at 0.05 timescale [V: Godot]; fighting games 8/12/16 frames light/medium/heavy [V: Capcom]; Roblox default 40 / 80 / 120-160 ms [H].
 [ ] Camera trauma: add 0.15 small, 0.35 medium, 0.6 big, 0.9 finisher; shake = trauma^2 (squared or cubed) [V-secondary: Eiserloh model]; decay 1.5/s; max offset 0.4 stud, max roll 1-2 degrees [H]; noise frequency 15-25 Hz [H].
 [ ] Screen shake direction opposite the shot/knockback [V: Vlambeer].
 [ ] Flash on hit 0.12 s [V: Godot].
 [ ] Knockback on enemy AND player (recoil) [V: Vlambeer list].
 [ ] 3-layer sound; pitch random 0.92-1.08 [V]; combo pitch +1 semitone per chain step up to 12 [H]; 3 variants per sound.
 [ ] Particles: small 8-25, big 40-80 emits; keep under ~500 live for mobile [H].
 [ ] Muzzle flash: first frame a circle [V: Vlambeer]; trails, landing dust, shells, smoke persist [V].
 [ ] Death/explosion variety: 33% of kills explode [V: Vlambeer example].
 [ ] Slow motion 0.3x for 0.4-0.6 s on the last target or the finisher [H].
 [ ] Permanent debris/paint; cap about 300 parts, despawn 10 s after rest [H].
 [ ] Anticipation 80-120 ms for heavy, 0-40 ms for light; recovery 100-200 ms [H].

Motion and tweens
 [ ] Landing squash (1.3, 0.7) returned in about 0.12-0.2 s [V for scale: Godot; duration H].
 [ ] Pop-in with Back easing overshoot about 10% over 0.2 s; rewards Elastic; movement Quad Out [H].
 [ ] Button press scale 0.92 over 0.08 s then Back Out [H].
 [ ] Counter tick-up 0.4-0.8 s Quad Out, with a sound tick that rises in pitch [H].
 [ ] Camera look-ahead smoothing exp(-4 dt) [V: Godot]; 2-3% zoom on heavy impact for 0.1 s [H].

Reward cadence
 [ ] Small reward every 20-30 s [V: Vampire Survivors analysis ~23 s]; upgrade choice every 40-60 s [H].
 [ ] First purchase under 30 s [H; AdCap's first stand free [V]].
 [ ] Chest/roll reveal 1.0-1.5 s, most polished animation in the game [V].
 [ ] First several rolls generous (scripted) then taper [V].

Assists (invisible)
 [ ] Hitboxes +20-30%; aim cone 10-15 degrees; pickup magnet 6-10 studs [H].
 [ ] Extra attempt after 3 fails, never removed [H; game-design.md].
 [ ] Retry in under 3 s [H].

Scene
 [ ] 2+ motion sources per screen (wind, particles, water) [H].
 [ ] Ambient audio: 2 loops + random one-shots every 8-20 s [H].
 [ ] Bloom 0.3-0.8; SunRays 0.05-0.12; Atmosphere density 0.25-0.4 [H].

---------------------------------------------------------------------

