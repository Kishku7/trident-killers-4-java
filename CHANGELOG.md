# Changelog

All notable changes to Trident Killers 4 Java are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] - 2026-08-01 audit

### Fixed
- **Claim ranges now match the loader gates.** Every pre-26 Forge and NeoForge jar declared an MC
  range whose oldest versions its own loader floor refused, so those versions could never load.
  Each range now starts at the first version the jar's loader actually admits, and the open-ended
  NeoForge dependency ranges are closed to the cell's own series.
- **pack.mcmeta on MC 1.21.9-1.21.11.** The Fabric and NeoForge jars for that span no longer ship a
  pack.mcmeta at all (both loaders generate correct metadata themselves); the Forge jars declare the
  exact data-pack format (1.21.10 -> 88, 1.21.11 -> 94). Removes the "couldn't load pack metadata"
  warning and the dropped resource pack.
- **AbstractArrow constructor era boundary** in the code generator was off by one version: the
  ItemStack parameter arrives at MC 1.20.3, not 1.20.2.

### Added
- **Ten new build targets**: Forge 1.20.2 and 1.20.4; NeoForge 1.21, 1.21.2, 1.21.3, 1.21.4, 1.21.6,
  1.21.7, 1.21.9 and 1.21.10. Every one boots on a dedicated server.

## [1.2.12] - 2026-07-28

### Changed
- **Fabric 26.3 cell moved to MC 26.3-snapshot-6** (from snapshot-5): fabric-api
  `0.155.3+26.3` -> `0.156.1+26.3`, `pack_format` `93` -> `94`, exclusive window
  `[26.3-alpha.5, 26.3-alpha.6)` -> `[26.3-alpha.6, 26.3-alpha.7)`.

### Notes
- **No source change required.** The whole tree was scanned against every snapshot-6 breaking
  surface (worldgen noise overhaul, Entity invulnerability split, `startSleeping` void ->
  boolean, `SharedSuggestionProvider` filter parameter, `InputWithModifiers.getDigit()`
  removal, options-screen reshuffle, terrain multidraw path, block-entity loot helpers) with
  zero hits.

## [1.2.11] - 2026-07-27
### Changed
- NeoForge 26 cells rebuilt against the now-PUBLISHED NeoForge builds: 26.1 -> 26.1.2.87, 26.2 -> 26.2.0.35-beta (previously 26.1.0.15-beta / 26.2.0.1-beta - the 26.1 pin was the stalest in the matrix). Dependency ranges and pack_format unchanged.
- mavenLocal() removed from the NeoForge/26 cell. No source or behaviour change; server-boot smoketested on both cells.

## [1.2.10] - 2026-07-21
### Changed
- MC 26.3 Fabric build advanced from 26.3-snapshot-4 to 26.3-snapshot-5 (Fabric API 0.155.3+26.3, pack_format 93, dep 26.3-alpha.5). Loads and renders in-world on the snapshot's reworked GPU/shader pipeline with no source changes; verified on the headless client harness.

## [1.2.9] - 2026-07-08
Consolidation release. Unifies the entire 1.20 through 26.3 matrix onto one single-source
(Cog) tree and brings every loader and line to a single version. Adds Forge 1.21.10 and
Forge 1.21.11 (server-boot smoketested). Builds are `-Xlint:all` clean with correct
per-version pack.mcmeta. No gameplay change from the 1.2.x line - a maintenance and
consolidation revision bump.

## [1.2.8] - 2026-07-08
Minecraft 26.3-snapshot-3 Fabric port. No gameplay change.

## [1.2.6] - 2026-06-17
Minecraft 26.2 stable support (Fabric and NeoForge), server-only. Confirmed in-game on
NeoForge 26.2.

## [1.2] - 2026-06-04
Multi-loader release: Forge, NeoForge, and Quilt support added across every Minecraft family
alongside the existing Fabric builds. Server-side, no loader API dependency.

## [1.1] - 2026-06-03
Extended Minecraft coverage: the 1.21 family split into version-matched builds
(1.21.1 / 1.21.5 / 1.21.8 / 1.21.11), plus 1.20.x support (1.20-1.20.4 and 1.20.5-1.20.6).

## [1.0] - 2026-06-03
Initial release. Core Bedrock-style trident-killer mechanic on Minecraft 26.1.2 (Fabric):
piston-locked tridents damage mobs in their hitbox with full player kill credit, Looting and
player-only drops, offline loot with XP suppression, and anti-despawn / anti-sink behavior.
Clean-room implementation from the functional spec.
