# Trident Killers 4 Java

## Branches

Source is organized by Minecraft line. Each branch holds its loader sources in `fabric/`,
`forge/`, and `neoforge/` folders, with one subfolder per Minecraft version that loader targets
(separate source trees and separate binaries per loader, even where one could run another's jar).
`main` (this branch) is the overview; reusable build/test/merge scripts live on the `tooling` branch.

- [1.20.x](https://github.com/Kishku7/trident-killers-4-java/tree/1.20.x) — Minecraft 1.20 – 1.20.6
- [1.21.x](https://github.com/Kishku7/trident-killers-4-java/tree/1.21.x) — Minecraft 1.21 – 1.21.11
- [26.1](https://github.com/Kishku7/trident-killers-4-java/tree/26.1) — Minecraft 26.1 – 26.1.2
- [26.2](https://github.com/Kishku7/trident-killers-4-java/tree/26.2) — Minecraft 26.2 (pre-release)

[![Discord](https://img.shields.io/badge/Discord-Join-5865F2?logo=discord&logoColor=white)](https://discord.gg/2ZxzbCzAHe)

Bedrock-style trident killers for Minecraft: Java Edition.

Throw a trident, point a piston at it, and the locked trident kills mobs with full player credit -
the heart of XP and drop farms. Works at the game level (no carpet gimmicks): the trident never
drifts, sinks, or despawns; it damages mobs only (players are safe in the kill zone); and kill
credit, Looting, and player-only drops all work - even while you're offline (loot keeps flowing,
XP is suppressed so orbs don't pile up). Server-side mod.

## Supported platforms

Per-loader source trees live under each branch's `fabric/` / `forge/` / `neoforge/` folder, one
subfolder per targeted Minecraft version.

| MC line | Fabric / Quilt | Forge | NeoForge |
| --- | --- | --- | --- |
| `1.20.x` (1.20 – 1.20.6)   | 1.20 – 1.20.6   | 1.20.1, 1.20.6        | 1.20.1, 1.20.2 – 1.20.4, 1.20.6 |
| `1.21.x` (1.21 – 1.21.11)  | 1.21 – 1.21.11  | 1.21.1, 1.21.5, 1.21.8 | 1.21.1, 1.21.5, 1.21.8, 1.21.11 |
| `26.1` (26.1 – 26.1.2)     | 26.1 – 26.1.2   | —                     | 26.1.2 |
| `26.2` (pre-release)       | 26.2            | —                     | 26.2 |

Forge support stops at 1.21.8 — there is no working Forge build toolchain for 1.21.9+ or 26.x.
Quilt runs the Fabric build. Requires Fabric API on Fabric / Quilt.

## Downloads

- Releases: https://github.com/Kishku7/trident-killers-4-java/releases
- Modrinth: https://modrinth.com/mod/trident-killers-4-java

By Kishku7. All Rights Reserved.
