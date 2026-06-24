# Clean-Room Declaration — trident-killers-4-java

**Project:** `trident-killers-4-java` — a Fabric mod for Minecraft: Java Edition.
**Maintainer:** Kishku7
**Date started:** 2026-06-03.
**Status:** Clean-room declaration established before any implementation code is written.

---

## 1. What this mod does

This mod recreates, for Minecraft: **Java Edition**, a gameplay capability that already
exists natively in Minecraft: **Bedrock Edition** — the "trident killer": a redstone/piston
contraption in which a trident kept in motion damages nearby mobs and credits the kill to the
trident's thrower (so looting and player kill-credit apply), and the thrown trident is preserved
from despawning.

The capability being replicated is a **game mechanic / behavior** — a method of operation. It is
not an expressive work. This project reproduces the *behavior*, implemented entirely in original
code.

## 2. What this mod does NOT use

- **No Microsoft / Mojang source code.** The trident-killer behavior is a feature of Mojang's
  Bedrock Edition. This mod does not use, decompile, copy, or derive from any Microsoft or Mojang
  source code to bring that capability to Java Edition. The behavior is reproduced from observed,
  publicly visible gameplay, implemented independently against the public Fabric/Minecraft Java API.
- **No third-party author's code.** This mod has no affiliation with any other author who may have
  implemented a similar capability in Java Edition (datapack, mod, or otherwise). No code, assets,
  data files, or text authored by any such third party have been used, copied, or adapted in this
  mod.
- **No protected expression of any kind** from any source. Only the unprotectable mechanic/behavior
  is reproduced.

## 3. Legal basis (informational — not legal advice)

- **17 U.S.C. § 102(b):** copyright protection never extends to "any idea, procedure, process,
  system, method of operation, concept, principle, or discovery." A game mechanic — a moving
  trident that damages mobs and credits the thrower — is a method of operation, not protectable
  expression.
- **Idea–expression dichotomy / game mechanics:** courts analyzing game-copyright disputes give no
  weight to similarities in rules and mechanics. What is protected is specific creative *expression*
  (art, look-and-feel, distinctive text, distinctive code), not the function. (Cf. *Tetris Holding,
  LLC v. Xio Interactive, Inc.*, 863 F. Supp. 2d 394 (D.N.J. 2012) — copying *rules* is permitted;
  copying *expression* is what infringed.)
- **Merger doctrine / § 102(b) for functional logic:** where a behavior can be expressed in only a
  few ways, expression merges with the idea and is not protectable.
- **Independent creation:** a clean-room implementation written from a behavior-only functional
  spec, with no use of another's protected expression, is original work and not a derivative work.

## 4. Clean-room procedure followed

1. **Behavior-only specification.** The mechanic is documented in our own words as a functional spec
   describing *what it does* (observed in-game / from the public Bedrock behavior) — never by
   transcribing any third party's code, data files, or text. See `FUNCTIONAL_SPEC.md` for the 
   behavioral requirements this mod implements.
2. **Independent implementation.** All Java source in this project is written from that functional
   spec against the public Minecraft Java + Fabric API. No third-party source is open or referenced
   while writing implementation code.
3. **Original identifiers and assets.** Mod id, package names, class names, text, and any
   textures/sounds are this project's own. We do not reuse another author's namespaces, file
   contents, asset files, or distinctive naming.
4. **Contemporaneous record.** This declaration plus the project's git commit history serve as the
   record of independent creation, established before implementation.

## 5. Do / Do-Not (quick reference for contributors)

**Do:** implement the behavior from `FUNCTIONAL_SPEC.md`; use the public Java/Fabric API; create
original assets, names, and code.

**Do NOT:** open, copy, paraphrase, or adapt Mojang/Microsoft source, or any other author's 
mod/datapack source while building this; do not reuse anyone's textures, icons, advancement text, 
namespaces, or distinctive naming.

---

*This document is an internal record of development practice. It is informational and is not legal
advice. If the project's distribution scope changes (e.g., public release, monetization), review the
applicable law and consider professional counsel before publishing.*
