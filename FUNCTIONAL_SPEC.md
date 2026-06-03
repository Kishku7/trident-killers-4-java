# Functional Specification — trident-killers-4-java

**Project:** `trident-killers-4-java` — Fabric mod, Minecraft: Java Edition.
**Date:** 2026-06-03.
**Companion:** see `CLEANROOM.md`.

> **Source of this spec (clean-room):** This document describes a *behavior* — the native
> "trident killer" capability of Minecraft **Bedrock Edition** — in our own words, derived from
> public descriptions of that mechanic and from observed gameplay. It is **not** transcribed from,
> and does not reference, any third-party implementation's source code, data files, namespaces, or
> text (including the a third-party author datapack). Implementation code for this mod is to be
> written from THIS spec only. References listed at the end are to public *behavioral* descriptions,
> not to any author's source.

---

## 1. Purpose & scope

Bring the Bedrock-Edition "trident killer" capability to Java Edition: a player-thrown trident that
is kept in motion by a piston deals damage to nearby mobs, with the kills credited to the player who
threw the trident — so Looting and player-kill drops apply. This is a mob-farm killing mechanism.

**In scope:** the damage, kill-credit, persistence, pickup, and movement behavior of a thrown
trident **after it has been moved by a piston at least once**.
**Out of scope (non-goals):** any new blocks, items, GUIs, recipes, or contraption designs. The mod
changes the *behavior* of an existing thrown trident; players build the redstone themselves.
**Server-side only** — the mod MUST NOT require a client mod (see FR-13).

## 2. Definitions

- **Thrown trident:** a trident entity in the world after a player has thrown it (the existing Java
  thrown-trident projectile entity), as opposed to a trident item in an inventory.
- **Piston move:** a change in the trident's position caused by a piston (sticky or normal), whether
  directly or via a block the piston pushes (see Open Research R-1).
- **Identified trident (killer-identified):** a thrown trident that has been moved by a piston **at
  least once**. Identification is a one-way flag set on the first piston move; the modified behavior
  in §3 applies **only** to identified tridents.
- **Thrower / owner:** the player recorded as the entity that launched the trident.
- **Target mob:** a damageable non-player `LivingEntity` whose hitbox intersects the trident.
- **Resting height:** the trident's Y position in its thrown/settled state, used by the height-reset
  rule (FR-9).

## 3. Behavioral requirements

Each requirement is a behavior, not an implementation. **Unless stated otherwise, every requirement
applies only to *identified* tridents (§2).** A thrown trident that has never been piston-moved is
left entirely to vanilla and other mods (FR-14).

### Damage
- **FR-1 — Motion-gated damage.** An identified trident deals contact damage only while it is moving
  (being piston-driven). A stationary identified trident deals no damage.
- **FR-2 — Repeated hits via reset.** A moving identified trident may damage mobs repeatedly over
  time, gated by the piston cycle (Bedrock allows a new hit after the trident has touched a solid
  block since its last hit; the piston provides that reset each cycle). Result: a steady kill rate.
- **FR-3 — All mobs in hitbox.** On a qualifying hit, **all** target mobs whose hitboxes intersect
  the trident are damaged (no single-target gating, no sweeping-edge requirement).
- **FR-4 — Mobs only; nothing else.** An identified trident damages **only** mobs. It SHALL NOT
  damage players, items, XP orbs, other projectiles, or any non-mob entity. (See FR-5 for players.)
- **FR-5 — Players never damaged.** Once an identified trident's throw has hit anything, no player is
  ever damaged by that piston-moved trident. (No PvP via trident killers.)
- **FR-6 — Damage characteristics.** Contact damage matches vanilla trident damage including the
  Impaling enchantment bonus against the entities Impaling applies to. **Hitbox = default trident
  hitbox** (no custom range).
- **FR-7 — Durability.** Subsequent hits from the same throw consume no additional trident
  durability beyond vanilla's normal throw cost.

### Kill credit, loot, XP
- **FR-8a — Player kill credit & loot regardless of login.** Damage is attributed to the trident's
  thrower so kills count as player kills (Looting applies, player-kill-gated drops appear). Loot
  items drop **even if the owner is not logged in**.
- **FR-8b — XP suppression when owner offline.** If the owner is **not logged in**, experience SHALL
  NOT drop from these kills; if XP does drop, it SHALL despawn within 15 seconds (so XP cannot pile
  up unattended). When the owner is online, XP behaves normally.

### Persistence, movement, pickup
- **FR-9 — Height reset (anti-sink).** Capture the trident's height before a piston move. After the
  move, if the trident has moved **down** at all, reset its Y back to the pre-move resting height, so
  it cannot drift/sink over repeated cycles.
- **FR-10 — No mob-induced movement.** Java allows mob hitboxes to push trident entities. For an
  identified trident, **no mob hitbox may affect the trident's position at all** — only piston-driven
  movement may move it. Mob collisions deal damage (FR-1..3) but never displace the trident.
- **FR-11 — Infinite persistence.** An identified trident never despawns on its own (no despawn
  timer). It persists indefinitely until a player picks it up (FR-12).
- **FR-12 — Any-player pickup.** An identified trident may be picked up by **any** player, not only
  its owner (mirroring Bedrock, where any player can pick up a thrown trident). Pickup removes it
  from the world and ends its persistence.

### Enchantment interactions
- **FR-13a — Channeling:** ignored (no effect in a killer).
- **FR-13b — Loyalty:** auto-returns the trident to the owner after a hit — this is vanilla behavior
  we cannot change; documented so it is expected, not a bug.
- **FR-13c — Riptide:** never thrown in normal use; if present on the trident, it is ignored.

### Platform
- **FR-13 — Server-side only.** The mod is server-side only and MUST NOT require any client mod to
  function (consistent with the project-wide project rule).

### Untouched tridents
- **FR-14 — Hands off un-piston-moved tridents.** A thrown trident that has **not** been moved by a
  piston at least once is left entirely to default behavior. If it hits the ground and vanilla (or
  another mod) would despawn it, it despawns; we do not interfere with, persist, or re-flag any
  trident that has never been piston-moved.

## 4. Open research items (resolve before / during implementation)

- **R-1 — Piston vs carpet movement. [PARTIALLY ANSWERED 2026-06-03]** a third-party author's datapack design has
  the player throw the trident onto a **carpet**, and the trident "rides" the carpet to get its hits.
  Finding: the carpet is primarily compensating for a **Java mechanic difference**, not just a code
  shortcoming. In standard Java, a trident that hits a block before reaching a mob deals **no** damage
  (Bedrock keeps damaging through blocks) — and a stuck trident is not relocated by a piston the way
  Bedrock relocates it. A **datapack cannot change** that collision rule; it can only carry the trident
  on a movable block (carpet) and apply effects via commands, so the carpet is the datapack-level
  vehicle for keeping the trident "in motion." As a **mod with mixins** we can address the root
  mechanic directly and will **not** require a carpet. Still worth a quick in-game confirmation in
  26.1.2 (see R-3).
> **RESOLVED 2026-06-03 (maintainer):** The 25w41a behavior was a bug and Mojang **patched it back out** - they do not want it on Java. **26.1.2 has NO native trident killer.** Therefore this mod implements the **full core mechanic (FR-1..FR-7)** as well as the control layer (FR-5, FR-8b, FR-9, FR-10, FR-11, FR-12). **CONFIRMED by the maintainer's in-game test 2026-06-03: vanilla 26.1.2 has no trident-killer behavior.** R-3 is closed. Decision to build a mod (not a datapack) is locked.

- **R-3 — Native Java trident-killer support in 26.1.2 (MUST TEST BEFORE BUILDING). [NEW 2026-06-03]**
  Java snapshot **25w41a** (late 2025) reportedly added the Bedrock trident-killer behavior natively
  ("works identically to Bedrock"). It is listed on the bug tracker as unintended, so Mojang may have
  patched it out before/after the 26.1.x release line. **The production server runs 26.1.2.** We must determine
  whether 26.1.2 already does the core mechanic natively:
    - If **yes**: the basic kill mechanic is free, and this mod's value narrows to the *extra controls*
      the maintainer specified — XP suppression when owner offline (FR-8b), infinite persistence (FR-11),
      any-player pickup (FR-12), anti-sink height reset (FR-9), no mob-induced movement (FR-10),
      players-never-hit (FR-5). The mod would augment/refine native behavior rather than create it.
    - If **no** (patched out): the mod must implement the core mechanic (FR-1..FR-7) as well.
  Test (26.1.2, dev server / Fabric_Testing): build a piston clock with a thrown trident **without a
  carpet**, spawn mobs, and observe whether (1) the trident damages mobs after passing a block, and
  (2) the piston moves the stuck trident at all. Compare with the carpet variant.
- **R-2 — Identification signal.** Depending on R-1, define exactly what event flags a trident as
  identified: direct piston displacement of the entity, or displacement caused by a piston-pushed
  block under/around it. Must be robust enough not to false-trigger on mob pushes (which FR-10
  blocks anyway) or normal flight.

## 5. Acceptance / test plan (behavioral)

- **T-1:** Throw a trident into a 2-piston clock over a hopper; mobs funneled by water die at a
  steady rate; drops collect. (FR-1, FR-2.)
- **T-2:** Looting III on the thrown trident measurably increases drops. (FR-8a.)
- **T-3:** With owner online, killed mobs drop collectable XP. With owner offline, XP does not
  accumulate (no drop, or despawns ≤15s). (FR-8a, FR-8b.)
- **T-4:** Farm runs unattended indefinitely; the identified trident never despawns. (FR-11.)
- **T-5:** A second (non-owner) player can pick up the identified trident. (FR-12.)
- **T-6:** Trident durability unchanged across many kills from one throw. (FR-7.)
- **T-7:** Impaling increases damage to applicable mobs; default hitbox confirmed. (FR-6.)
- **T-8:** No player is damaged by the moving trident; no items/XP-orbs/projectiles are damaged.
  (FR-4, FR-5.)
- **T-9:** Mobs crowding the trident do not push it off position; only the piston moves it. (FR-10.)
- **T-10:** Over many cycles the trident does not sink below its resting height. (FR-9.)
- **T-11:** A thrown trident that is never piston-moved follows vanilla/other-mod despawn behavior
  unchanged. (FR-14.)

## 6. References (behavior only — NOT source code)

- Minecraft Wiki — Trident (thrown-trident mechanics / Bedrock damage behavior):
  https://minecraft.wiki/w/Trident
- Public community description of the Bedrock trident-killer mechanic (piston clock keeps the
  trident moving; subsequent hits count as player damage so XP/Looting apply; no extra durability):
  https://www.sportskeeda.com/minecraft/how-make-trident-killer-minecraft-bedrock

*These references describe the publicly known Bedrock behavior. No third-party mod or datapack source
was used in writing this spec.*
