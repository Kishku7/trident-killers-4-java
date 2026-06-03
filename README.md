# Trident Killers 4 Java

**Bedrock-style trident killers for Minecraft: Java Edition.** Server-side Fabric mod, MC 26.1.2.

Bedrock players have enjoyed trident killers for years: throw a trident, point a piston at it, and
the moving trident kills mobs with full player credit — the heart of countless XP and drop farms.
Java never had it. Now it does, and the Java version is better than the original.

## Why this mod beats other solutions

**No carpets. No gimmicks.** Datapack-based attempts at Java trident killers can't touch the game's
collision rules, so they resort to making the trident ride a piston-pushed carpet — fragile setups
where the trident falls off, lands somewhere useless, and goes dead. This mod works at the game
level: stick a trident anywhere, aim a piston at it, done. The contraption is exactly as simple as
Bedrock's — simpler, because the trident can't escape.

**The trident is rock-solid.** Once a piston has touched it, the trident is locked in place: it
never drifts, never sinks, can't be shoved around by mobs crowding it, and **never despawns** —
it stays until a player picks it up. Build the farm once; it runs forever.

**Player-safe by design.** The killer damages mobs and *only* mobs. Players are never harmed —
even standing directly inside the kill zone with the pistons running, you take zero damage
(tested). No item destruction, no XP-orb destruction, no PvP griefing vector. Bedrock can't say
the same.

**Kill credit done right.** Kills count as player kills for the thrower: XP drops, Looting
multiplies drops, and player-only drops work. And it keeps working **while you're offline** —
loot keeps flowing into your hoppers, while XP is automatically suppressed so orbs don't pile up
and lag the server while nobody's there to collect them.

**Enchantments behave exactly as they should.**

| Enchantment | Behavior in a killer |
|-------------|---------------------|
| Impaling | Full bonus damage — melts aquatic mobs |
| Looting | Multiplies drops, verified |
| Channeling | Ignored — no surprise lightning in your farm |
| Riptide | Ignored (can't be thrown anyway) |
| Loyalty | Vanilla behavior (returns after a hit — use a non-Loyalty trident for farms) |
| Unbreaking / Mending | The trident takes no durability from killer hits |

**Bedrock-style pickup.** Any player can pick up a killer trident, not just its owner — just like
Bedrock.

**Everything else stays vanilla.** A trident that has never been moved by a piston is completely
untouched: it despawns on the vanilla timer, other mods can manage it freely. This mod governs
only tridents you've deliberately put to work.

**Server-side only.** Drop one jar in the server's `mods` folder. Every client can connect —
vanilla or modded, nothing to install client-side. Works in singleplayer too.

## How to build one

1. Throw a trident where you want the killer.
2. Aim a piston at it and put the piston on a clock.
3. Funnel mobs into the trident. That's it — no carpet, no entity tricks.

Damage lands on each piston extension: vanilla trident damage (8) plus enchantments, hitting every
mob in the trident's hitbox at once. Standard hurt immunity paces it at roughly one hit per piston
cycle, just like Bedrock.

## Requirements

- Minecraft: Java Edition 26.1.2
- Fabric Loader 0.15+
- No other dependencies

## Development & licensing

This mod is an original, independent implementation — it contains no Mojang/Microsoft code and no
code from any other mod or datapack. Development practice and design records: see `CLEANROOM.md`
and `FUNCTIONAL_SPEC.md` in this repository.

All rights reserved. © Kishku7
