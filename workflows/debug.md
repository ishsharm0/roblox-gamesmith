# Debugging loop

A bug report is a guess until it reproduces. Reproduce, observe, form one hypothesis, test it, fix,
then guard against it coming back.

## 1. Reproduce from the shell

- Write the shortest scenario that shows the bug (`scenarios/bug-<name>.luau`): start play, set up the
  state, do the action, `return` what happened. Run it 3 times; note whether it's every time,
  sometimes, or timing-dependent.
- Pull the console (`studio console`) and look for the first error, not the last.
- Capture the moment (`studio shot`) if it's visual.

## 2. Observe before theorizing

- Print or `return` the state at each step: attributes, positions, which branch ran.
- Check both contexts: is the server's view the same as the client's? Many bugs are a mismatch
  (attribute not replicated yet, client acted on stale state).
- Check order: what fired first? Log `os.clock()` with events.
- Look up the symptom in `references/sharp-edges.md`.

## 3. One hypothesis, one test

- State it: "the client reads Phase before Score has replicated".
- Test it with the smallest change that would prove or disprove it (a log line, swapping two lines,
  a probe scenario that repeats one action with exact inputs).
- If the test disagrees, drop the hypothesis. Don't stack fixes for causes you haven't confirmed; a
  wrong fix written into docs misleads every agent after you.

## 4. Fix at the cause

- Fix where the wrong thing happens, not where it shows (don't clamp a UI number that the server
  computed wrong).
- Keep the fix small; refactors go in their own change.

## 5. Guard

- Add the scenario (or a Lune test, if the rule is pure) to the project, so it stays fixed.
- Run `rbxgame check`, the core scenarios, and the bots.
- If it's a pitfall others will hit, add a row to `references/sharp-edges.md`.

## When the bot finds it

Bots are code too. Before blaming the game for a failure that a bot found:
- Re-run with a fixed seed: same failure?
- Probe the one action with zero error. If the probe passes, suspect the bot (stale reads, fixed
  delays instead of waiting for outcomes).
- Make the bot wait for outcomes (an attribute change, a splash), never a fixed time.

## Common Studio debugging tools

- `studio call skill '{"skill_name":"rbx-debug"}'`: Roblox's own debugging guide.
- Breakpoints and the Watch window are in the Studio UI; from the shell, logs and returns are faster.
- `script_grep` over the place finds every writer of a property or every fire of a remote.
