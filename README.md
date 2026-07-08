# Trident Killers 4 Java

**Bedrock-style trident killers for Minecraft: Java Edition.** Server-side, no dependencies.

Throw a trident, push a piston into it to lock it, and the locked trident kills mobs in its hitbox
with full player credit - the core of XP and drop farms. Kill credit, Looting, and player-only drops
all work, even while you are offline (loot keeps flowing; XP is suppressed). It damages mobs only, so
players are safe in the kill zone, and a trident you never piston-move stays fully vanilla. No carpet
or datapack tricks - it works at the game level.

## Using it

Install it on the **server** - it does nothing client-side, and vanilla clients can join. Build a
normal trident killer (throw a trident, push a piston into it) and mobs that enter the locked trident
die with full player credit. Adds no blocks, items, or commands.

## Supported versions

Minecraft **1.20 through 26.3**, from one codebase:

- **Fabric** / **Quilt** - every version, 1.20 through 26.3.
- **NeoForge** - 1.20.1 through 1.21.11, plus 26.1 and 26.2.
- **Forge** - 1.20 through 1.21.11, except 1.21.9 (no Forge on the 26 line).

No Fabric API dependency. On the Modrinth page, pick the file that matches your Minecraft version and
loader.

## Links

- **Download:** https://modrinth.com/mod/trident-killers-4-java
- **Source:** the [`minecraft-1.20-26.3`](https://github.com/Kishku7/trident-killers-4-java/tree/minecraft-1.20-26.3) branch
- **Issues:** https://github.com/Kishku7/mod_support/issues

By Kishku7. All Rights Reserved.
