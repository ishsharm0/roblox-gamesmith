# Combat systems

Combat is a judgement verb (timing, spacing, aim) with stakes. Feel comes from the client; truth comes
from the server. Read `mechanics-and-fun.md` first; this file is the plumbing.

## Shape of a hit

1. **Client** reads input, plays the swing animation and sound at once, and fires
   `Combat:FireServer("Swing", weaponId, aimDir)` (aim as a unit vector, nothing else).
2. **Server** checks: weapon owned and equipped, cooldown elapsed (server clock), player alive and in a
   state that allows attacks.
3. **Server** finds targets itself: a shape query (`workspace:GetPartBoundsInBox` / `GetPartsInPart` /
   `Blockcast` / `Spherecast`) in front of the attacker's server-side root, filtered to hittable
   characters, with a range a little bigger than the client sees (latency slack, usually +2-4 studs).
4. **Server** applies damage from its own weapon table, sets i-frames, fires `Hit` feedback to the
   attacker (confirm marker) and the victim (flash, knockback).
5. **Clients** play impact effects: hit-stop (freeze the attacker's animation 40-80 ms), camera
   shake, a damage number, particles.

The client may draw a hit marker optimistically, but health only changes from the server.

## Projectiles

- Fast bullets: hitscan on the server (raycast from the server's root/head position along the client's
  aim direction, with a sanity check that the aim is within ~30° of where the character faces).
- Slow projectiles (arrows, fireballs): simulate on the server with a few raycasts per step, and draw a
  client copy that starts instantly; the server's copy decides.
- Lag compensation (rewinding targets) is rarely worth the complexity; generous hitboxes and short
  ranges cover most of it.

## Health and death

- `Humanoid.Health` for characters is replicated and simple; for NPCs or custom bodies, keep health
  in an attribute.
- Damage goes through one function `Combat.damage(target, amount, source, kind)` that checks teams,
  i-frames, shields and logs kills. Never let scattered scripts change health.
- On death: credit the last damager within a window (assists optional), drop or keep items by the
  genre's rule, respawn with a short invulnerability.

## Feel checklist

- [ ] Anticipation (short wind-up), action, recovery on every attack; the recovery is the
      punishable window.
- [ ] Hit-stop, flash and knockback on every confirmed hit; distinct sounds for hit, block and miss.
- [ ] Cooldowns visible (radial fill on the button).
- [ ] Damage numbers readable on a phone, pooled, and limited per second.
- [ ] Enemies telegraph attacks (colour, sound, pose) at least 0.4 s before they land.

## NPC enemies

- A state machine per enemy (idle, notice, chase, attack, recover, return), stepped at 5-10 Hz on the
  server, not per frame.
- `PathfindingService` for chasing across obstacles; recompute every 0.5-1 s or when blocked, not each
  step. Simple open arenas can steer straight at the target.
- Server owns NPC physics (`SetNetworkOwner(nil)`) or NPCs jitter as ownership flips between players.
- Spawn in waves with a cap per player; despawn far-away idle NPCs.

## Balancing

- One table of weapons and enemies in `shared/Config` (damage, range, cooldown, health, speed), so
  the curve is visible and testable.
- Time-to-kill is the number to tune: 3-6 hits for a fair fight, 1-2 for fodder.
- A bot scenario that fights a wave with the real remotes catches cooldown and hitbox bugs.

## Exploits to expect

Remote spam (rate limit per weapon), reach hacks (server range check), aimbots (accept; design so
aim isn't everything), damage claims (server-side damage only), invincibility (server owns health),
teleport-kills (distance check against the server position).
