# Creative methods: ideation, art bible, Blender discipline

Procedures adapted, in our own words, from three open projects. Use them with `concept-gate.md` (is the idea good), `art-direction.md` (how Roblox lighting works) and `blender-pipeline.md`.

- Ideation engine and tension test adapted from `creative-director-skill` by Serge Shima, CC-BY-4.0, https://github.com/smixs/creative-director-skill. Adapted: reworded, reduced to game concepts.
- Lean brief and art-bible lens adapted from `Claude-Code-Game-Studios` by Donchitos, MIT, https://github.com/Donchitos/Claude-Code-Game-Studios.
- Blender review discipline adapted from `blender-kiln` by elithril, MIT, https://github.com/elithril/blender-kiln.

## 1. Ideation engine (write the output in `CONCEPT.md`)
1. Scan first. List 10-20 live games near the territory (`rbx-research`, the charts). Note each one's core verb. You are aiming at a gap, not at the middle.
2. Pick three methods from three different families and run each once:
   - structural: take a proven loop and change one structural rule (who owns the thing, what is scarce, what the timer measures);
   - collision: force two unrelated loops or settings together (a job sim plus a heist; a pet raiser plus a tower defence);
   - inversion: flip the usual player goal or role (defend the thing everyone else steals; the monster is the customer).
3. Generate 8-12 candidates, each a single sentence. Label the first three "warmup": they are the conventional ones your head offers first. Do not pick a warmup idea unless nothing later beats it.
4. Idea level check. Reject a candidate that is only execution (better art, more levels, a new skin) wearing a concept's name.
5. Saturation cap. If three or more live games already share the candidate's core verb, its originality score is capped low however nice the twist sounds. Change the verb, not the skin.
6. Tension test. A good concept has an unresolved pull between players or inside one player (greed against safety, speed against care, helping against winning). If the idea resolves cleanly with no pull, originality is weak: add the pull or drop it.
7. One sentence or no idea. State it in one sentence with the twist in it. If it takes three sentences, you have a feature list, not an idea.
8. Keep the top two. Run each through the gate in `concept-gate.md`; build the one that passes with the clearer five-second clip.

## 2. Lean brief (the page before the build)
Offer two or three concepts as verb-first one-liners ("Smash, sell, and upgrade a wall of eggs"), pick one, then fill six fields, one or two lines each:
- Pitch: the one sentence from 1.7.
- Genre and comparable games.
- Controls: what the thumb or mouse does on phone and desktop.
- Look: three adjectives plus the palette in section 3.
- Question: what the first playable must answer ("is breaking the egg fun for 90 seconds without a reward?"). The first build exists to answer it and nothing else.
- Hooks: what brings a player back tomorrow and what makes them invite a friend.

## 3. Art bible with tests (write `ART.md`; each rule must forbid something)
- **Pillars and design tests.** Name two or three visual pillars. Under each, write a test of the form "when X is ambiguous, choose Y" (when two props compete, pick the one with the clearer silhouette). A principle with no test, or that rules nothing out, is a mood word; delete it.
- **Silhouette at 25%.** Shrink hero characters, key props and pickups to a quarter size on a phone-sized capture. If they cannot be named, redraw the outline before adding detail.
- **Palette of 5-7 roles.** Name each colour's job (ground, hero, danger, reward, UI, accent). A colour with no job is removed.
- **Colour pairs need a backup cue.** For every red/green or similar pair a colour-blind player could confuse, record the second cue: shape, icon, pattern, or sound. Check the capture in greyscale too.
- **Specific beats vague.** One warm lamp per room style, a named material per surface, beats "dark and foreboding".
- **Mood per game state.** Make a table: lobby, play, danger, win, shop; for each, lighting values, fog, post effects and music layer. The states must read as different at a glance on a contact sheet (`visual-review.md`).
- **Cut the ceremony.** One page is enough; do not build a document hierarchy.

## 4. Blender discipline (add to any `blender-kit.md` session)
- Look after every geometry or material phase, never only at the end. After texturing, look from two opposite angles. Numbers (poly count, bounds) do not replace looking.
- Write a one-line log checkpoint (what was done, what was seen) before starting the next phase. Agents skip this unless it is a required step.
- Review renders, headless: a flat matcap or colour pass, two opposite three-quarter views, one from above, one from underneath, as one contact sheet.
- Before rigging or export: apply transforms, then merge doubles in a way that keeps each corner's custom normal, then recalculate normals only where you mean to. A plain merge can re-smooth a faceted mesh and bend most of its corners.
- Never decimate silently. Show before and after counts and a view of each. Warn on a polygon range for the asset class; do not hard-cap.
- Keep the `.blend` as the recovery point: save before each risky step, never overwrite it with an export.
