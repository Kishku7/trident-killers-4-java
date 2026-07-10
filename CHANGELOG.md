# Changelog

All notable changes to Trident Killers 4 Java are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
