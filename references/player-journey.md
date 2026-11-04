# The complete player journey

Use before building a game or repairing a prototype that lacks introduction, onboarding, pacing or
an ending. Passing a mechanics bot is evidence about mechanics, not proof of a finished game.

## Define the experience before adding systems
Write SESSION.md with the actual states, entry/exit conditions, visible objective, player input,
feedback and recovery. Cover arrival/loading, invitation to play, first action, first success,
core loop, stage change, failure/recovery, finish/reward, replay/return and returning-player flow.
Use only states that fit the genre. An intro is an intentional arrival and clear invitation; it need
not be a cutscene or modal. A tutorial teaches through action, not a wall of instructions.

For each early beat specify what the player sees, what they do, what changes and why it matters.
Teach one mechanic at its first use. Use a forgiving first attempt and show the mechanic working.
Avoid explaining future systems before they are relevant. Make longer sequences skippable; do not
force returning players to repeat learned steps. Save onboarding completion separately from progress.
The destination and next action should read in the player's camera, without reading a design document.

## Build the state contract
The server owns progress, rewards and legal transitions. The client renders cameras, UI, input hints
and animation from replicated state. Prevent play/reward processing while in menus or countdowns.
Await real player actions for tutorial completion. Handle death, reconnect, duplicate clicks, delayed
loads and restart during a transition. Returning to the menu must clear pending countdowns safely.
Keep a way to practise/resume distinct from a fresh timed/ranked run.

## Pace the session
Introduce -> demonstrate -> let the player succeed -> vary the challenge -> offer a breather ->
raise the challenge -> pay it off. Stages need a different play or visual beat, not only a smaller
platform radius. Checkpoints celebrate progress and preview the next challenge. Failure gives a
readable cause and a quick, stable recovery, without restarting an entire intro. The finish needs
an earned result, comparison to a personal goal, and an explicit next action (replay/continue/menu).
Do not invent a shop, daily grind or monetization to disguise an empty core loop.

## Review from a clean launch
Test the same entry a real player uses, with fresh data. Activate the real primary button. Play the
tutorial and one complete session; do not begin with a teleport straight onto gameplay. Test a
returning player, tutorial skip, death/fall, pause/menu, result/replay and repeated/invalid requests.
A teleport scenario can isolate rules but cannot validate teaching, camera flow or jump feel.
Record a short walkthrough or a sequence of actual captures: arrival, first action, first success,
stage transition, failure recovery and result/replay. Verify phone and desktop. Claims about a
complete journey require these observations, not screenshots of an empty editor alone.

Primary guidance:
https://create.roblox.com/docs/production/game-design/onboarding
https://create.roblox.com/docs/production/game-design/onboarding-techniques

Studio device-emulator input may need calibration. Compare the requested cursor position, actual
UserInputService mouse location, GUI bounds and native insets before blaming an unresponsive button.
Use observed offsets for that session, not hardcoded offsets for every device. Verify real event
delivery, clean up temporary probes, and keep fullscreen backdrops separate from safe-area controls.
