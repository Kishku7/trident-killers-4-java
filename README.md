# Trident Killers 4 Java

**Bedrock-style trident killers for Minecraft: Java Edition.** Throw a trident, point a piston at it, and the locked trident kills mobs with full player credit - the heart of XP and drop farms. It works at the game level (no carpet gimmicks): the trident never drifts, sinks, or despawns; it damages **mobs only** (players are safe in the kill zone); and kill credit, Looting, and player-only drops all work - even while you're offline (loot keeps flowing, XP is suppressed so orbs don't pile up). Server-side mod.

[![Discord](https://img.shields.io/badge/Discord-Join-5865F2?logo=discord&logoColor=white)](https://discord.gg/2ZxzbCzAHe)

## Branches

Source is organized by Minecraft line. Each branch holds its loader sources in `fabric/`, `forge/`, and
`neoforge/` folders, with one subfolder per Minecraft version that loader targets - separate source trees
and separate binaries per loader, even at fork points (Forge 1.20.1 and NeoForge 1.20.1 are distinct
trees/jars). `main` (this branch) is the overview; reusable build/test scripts live on the `tooling` branch.

- [1.20.x](https://github.com/Kishku7/trident-killers-4-java/tree/1.20.x) - Minecraft 1.20 - 1.20.6
- [1.21.x](https://github.com/Kishku7/trident-killers-4-java/tree/1.21.x) - Minecraft 1.21 - 1.21.11
- [26.1](https://github.com/Kishku7/trident-killers-4-java/tree/26.1) - Minecraft 26.1 - 26.1.2
- [26.2](https://github.com/Kishku7/trident-killers-4-java/tree/26.2) - Minecraft 26.2 (pre-release)

## Supported platforms

| MC line | Fabric / Quilt | Forge | NeoForge |
| --- | --- | --- | --- |
| `1.20.x` (1.20 - 1.20.6)   | 1.20 - 1.20.6 (+ Quilt)   | 1.20.1, 1.20.5 - 1.20.6 | 1.20.1, 1.20.2 - 1.20.4, 1.20.5 - 1.20.6 |
| `1.21.x` (1.21 - 1.21.11)  | 1.21 - 1.21.11 (+ Quilt)  | 1.21.1, 1.21.5, 1.21.8 | 1.21.1, 1.21.5, 1.21.8, 1.21.11 |
| `26.1` (26.1 - 26.1.2)     | 26.1 - 26.1.2 (+ Quilt)   | - | 26.1.2 |
| `26.2` (pre-release)       | 26.2 (+ Quilt)            | - | 26.2 |

- **Forge** is supported through **1.21.8** (the FG6 ceiling - no working Forge toolchain for 1.21.9+ or
  26.x). The 1.20.2 - 1.20.4 range is covered on NeoForge (a dedicated gap build); a Forge build for that
  range is not yet made (tracked as future work).
- **Quilt** runs the Fabric jar on **every** line, including 26.x. Trident Killers has **no Fabric API
  dependency**, so Quilt Loader runs it directly (on 26.x, Quilt Loader needs the launch flag
  `-Dloader.experimental.minecraft.targetNamespace=official`).
- **No dependencies** - server-side mixins only.

## Using it

Install it on the **server** (it does nothing client-side). Then build a normal trident killer: throw a trident into a spot and push a piston into the trident so it locks in place. Mobs that move into the locked trident take damage and die with full player credit - so Looting, kill credit, and player-only drops all apply, and it keeps farming while you are offline.

Adds **no blocks, items, or commands**, and has **no dependencies** - it changes trident behaviour through server-side mixins only. A vanilla client can join a server running it.

## Downloads

- Releases: https://github.com/Kishku7/trident-killers-4-java/releases
- Modrinth: https://modrinth.com/mod/trident-killers-4-java
- Discord: https://discord.gg/2ZxzbCzAHe

By Kishku7. All Rights Reserved.
