# Trident Killers 4 Java

Bedrock-style trident killers for Minecraft: Java Edition.

Throw a trident, point a piston at it, and the locked trident kills mobs with full player credit -
the heart of XP and drop farms. Works at the game level (no carpet gimmicks): the trident never
drifts, sinks, or despawns; it damages mobs only (players are safe in the kill zone); and kill
credit, Looting, and player-only drops all work - even while you're offline (loot keeps flowing,
XP is suppressed so orbs don't pile up). Server-side mod.

## Supported platforms

Source for each Minecraft version lives on its own branch, named for the version. `main` (this
branch) is the overview; reusable build/test/merge scripts live on the `tooling` branch.

| Branch    | Minecraft        | Fabric | Quilt | Forge | NeoForge |
| ---       | ---              | :---:  | :---: | :---: | :---:    |
| `1.20.4`  | 1.20 - 1.20.4    | Yes    | Yes   | Yes   | Yes      |
| `1.20.6`  | 1.20.5 - 1.20.6  | Yes    | Yes   | Yes   | Yes      |
| `1.21.1`  | 1.21 - 1.21.1    | Yes    | Yes   | Yes   | Yes      |
| `1.21.5`  | 1.21.2 - 1.21.5  | Yes    | Yes   | Yes   | Yes      |
| `1.21.8`  | 1.21.6 - 1.21.8  | Yes    | Yes   | Yes   | Yes      |
| `1.21.11` | 1.21.9 - 1.21.11 | Yes    | Yes   | -     | Yes      |
| `26.1.2`  | 26.1 - 26.1.2    | Yes    | Yes   | -     | Yes      |

Quilt runs the Fabric build. Each version branch holds its loader sources in subfolders
(`fabric/`, `forge/`, `neoforge/`; 1.20.4 uses `fabric/` + `forge-neoforge/`) plus a BUILD.md.
Requires Fabric API on Fabric/Quilt.

## Downloads

- Releases: https://github.com/Kishku7/trident-killers-4-java/releases
- Modrinth: https://modrinth.com/mod/trident-killers-4-java

By Kishku7. All Rights Reserved.
