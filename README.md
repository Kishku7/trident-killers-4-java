# Trident Killers 4 Java

Server-side Fabric mod that brings the Bedrock-Edition **trident killer** capability to
Minecraft: Java Edition (26.1.2).

A player-thrown trident kept in motion by a piston damages nearby mobs, with kills credited
to the thrower — Looting and player-kill drops apply. Java removed this (Bedrock keeps it);
this mod restores it, with additional server-friendly controls.

## Key behavior

- A thrown trident becomes **killer-identified** the first time a piston moves it. Tridents
  never touched by a piston are left 100% vanilla (other mods may govern them freely).
- Identified tridents: damage **mobs only** (never players, items, or anything else), hit all
  mobs in the hitbox, never despawn until a player — any player — picks them up, cannot be
  displaced by mob hitboxes, and auto-correct any downward drift from piston cycles.
- Kill credit + loot work even with the owner offline; XP is suppressed while the owner is
  offline so it cannot pile up.
- Channeling/Riptide ignored; Loyalty behaves as vanilla (returns after a hit).

## Documents

- `CLEANROOM.md` — clean-room declaration: this is an independent implementation of a game
  *mechanic* (Bedrock behavior), using no Microsoft/Mojang code and no third-party author's code.
- `FUNCTIONAL_SPEC.md` — the behavior-only spec all implementation is written from.

## Build

```
.\gradlew.bat build
```

Jar lands in `build\libs\`. MC 26.1.2, Fabric Loom 1.16, Java 25. Server-side only — no client
mod required or permitted as a dependency.

## License

All rights reserved (private project).
