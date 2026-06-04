# TK4J Tooling

Build/verify/release tooling for trident-killers-4-java multi-loader support.
Paths containing `<WORKSPACE>` are placeholders for the local workspace roots;
substitute your own paths before running.

## Branch map

| Branch | Contents |
|---|---|
| `main` | Fabric source, MC 26.1.2 (fabric + quilt verified) |
| `fabric-quilt/{family}` | Fabric source per MC family (1.20.4, 1.20.6, 1.21.1, 1.21.5, 1.21.8, 1.21.11); jars verified on both Fabric and Quilt |
| `forge-neoforge/1.20.4` | Forge build project, 1.20.4 family; jar verified on Forge 1.20.1 and NeoForge 1.20.1 (NeoForge forked Forge mid-1.20.1, so one jar serves both) |
| `forge/{family}` | Forge build projects (1.20.6, 1.21.1, 1.21.5, 1.21.8). Forge 1.21.11/26.1.2 skipped: FG6 toolchain cannot build them |
| `neoforge/{family}` | NeoForge build projects (1.20.6, 1.21.1, 1.21.5, 1.21.8, 1.21.11, 26.1.2) |
| `tooling` | This branch |

## Layout

- `scaffold/` - generates forge/neoforge build projects from a family branch's mixin sources
  (note: some families carry manual patches on top of the scaffold; the `forge/*` and
  `neoforge/*` branches are the ground truth).
- `harness/` - RCON-driven compat test harnesses (fabric/quilt/forge/neoforge) plus sweep
  drivers. Sequential only: shared RCON port 25575. The `tk4jtest` RCON password is a
  localhost-only test constant.
- `merge/` - per-family universal jar production:
  - Per-loader jars are merged with Forgix 2.0 (https://github.com/PacifistMC/Forgix, built
    from source) via its CLI: `java -cp Forgix.jar io.github.pacifistmc.forgix.Forgix
    mergeJars --output merged.jar --fabric a.jar --forge b.jar --neoforge c.jar`.
    WARNING: Forgix mutates its input jars - feed it copies.
  - `ForgeOnlyMixinPlugin.java` must be compiled (vs mixin 0.8.5 + asm-tree, `-proc:none`,
    `--release 17`) and injected into any merged jar that contains BOTH Forge and NeoForge,
    with `"plugin": "com.kishku7.tridentkillers4java.ForgeOnlyMixinPlugin"` added to the
    forge mixin config. Reason: NeoForge 20.5+ honors the manifest `MixinConfigs` attribute
    (even from jars it does not recognize as mods), which double-applies the forge config
    alongside the neoforge `[[mixins]]` declaration and crashes at boot; Forge itself ignores
    toml-declared mixins, so the manifest attribute cannot simply be removed.

## JDK matrix

| Target | JDK |
|---|---|
| 1.20.x builds/servers | 17 |
| 1.20.5 - 1.21.x | 21 |
| MC 26.x servers | 25 |
| Forgix build | 24 (Gradle 8.14) |
