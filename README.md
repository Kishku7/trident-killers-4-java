# Trident Killers 4 Java

**Bedrock-style trident killers for Minecraft: Java Edition.** Server-side.

Bedrock players have long used trident killers - a thrown trident, locked in place by a piston,
that kills mobs with full player credit - as the heart of XP and drop farms. Java never supported
them. Trident Killers 4 Java brings the mechanic to Java at the game level, with no carpet or
datapack gimmicks.

Throw a trident, push a piston into it so it locks, and the identified trident kills mobs in its
hitbox with full player credit. The trident never drifts, sinks, or despawns; it damages **mobs
only** (players standing in the kill zone are safe); and kill credit, Looting, and player-only
drops all keep working - even while you are offline (loot keeps flowing; XP is suppressed so orbs
do not pile up). A trident you never piston-move behaves exactly like vanilla.

## Using it

Install it on the **server** - it does nothing client-side, and a vanilla client can join a server
running it. Then build a normal trident killer: throw a trident into position and push a piston
into it so the trident locks. Mobs that enter the locked trident take damage and die with full
player credit, so Looting, kill credit, and player-only drops all apply, and the farm keeps running
while you are away.

Adds **no blocks, items, or commands** and has **no dependencies** - it changes trident behaviour
through server-side mixins only.

## Supported versions

Minecraft **1.20 through 26.3**, all from one unified codebase:

- **Fabric** (and **Quilt**) - every supported line, 1.20 through 26.3.
- **NeoForge** - 1.20.1 through 1.21.11, plus the 26.x line (26.1, 26.2).
- **Forge** - 1.20.1, 1.20.6, 1.21.1, 1.21.5, and 1.21.8.

There is no Fabric API dependency, so Quilt Loader runs the Fabric jar directly. On the Modrinth
page, pick the file that matches your Minecraft version and loader.

## Downloads

- **Modrinth:** https://modrinth.com/mod/trident-killers-4-java
- **Releases:** https://github.com/Kishku7/trident-killers-4-java/releases

## Source

A single unified source tree builds every supported target - Fabric, Forge, and NeoForge - across
Minecraft 1.20 through 26.3, on the
[`minecraft-1.20-26.3`](https://github.com/Kishku7/trident-killers-4-java/tree/minecraft-1.20-26.3)
branch.

Questions or bug reports: https://github.com/Kishku7/mod_support/issues

By Kishku7. All Rights Reserved.
