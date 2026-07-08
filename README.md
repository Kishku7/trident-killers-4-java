# Trident Killers 4 Java - Build Guide (minecraft-1.20-26.3 branch)

This branch is the unified Trident Killers 4 Java source tree. One codebase builds every
supported target - Fabric, Forge, and NeoForge - across Minecraft 1.20 through 26.3. It is a
server-side, mixin-only mod (no client code, no assets beyond an icon, no Fabric API runtime
dependency).

For what Trident Killers 4 Java is and how it plays, see the
[landing page](https://github.com/Kishku7/trident-killers-4-java). Questions or bug reports:
https://github.com/Kishku7/mod_support/issues

## What you need installed

The mod builds on Windows using PowerShell build scripts and per-cell Gradle wrappers.

**Required:**

- **Windows + PowerShell 7 (`pwsh`)** - the build scripts are `.ps1` and call `gradlew.bat`.
- **Python 3 with Cog (`cogapp`) on `PATH`:**

      pip install cogapp

  Cog is the code generator that resolves cross-version API drift. It is invoked
  automatically by the build scripts, so it must be installed before you build. The
  generator brain is `_codegen/compat.py` (pure Python, in-repo).
- **JDKs, installed and discoverable by Gradle's toolchain detection.** There is no
  foojay auto-download configured, so you must install these yourself:
    - JDK 17 (Temurin/Adoptium)
    - JDK 21
    - JDK 25

  Which JDK each target uses is in the matrix below. Install all three to build the whole
  tree, or just the one(s) for the cells you care about.

**Provided for you (do NOT install manually):**

- **Gradle** - each cell ships a wrapper (`gradlew.bat`). Pre-26 cells use Gradle 8.x;
  the unified 26 cells use Gradle 9.x.
- **Loader SDKs and dependencies** - Gradle downloads them on first build: Fabric Loom,
  NeoForge ModDevGradle, and Forge (ForgeGradle 6). An internet connection is required the
  first time each cell is built. The mod depends on no runtime loader API (Fabric API is
  `compileOnly` only), so no API jar ships in the build.

## How to build

From the repo root, run the loader script for what you want. With no argument it builds every
cell for that loader into `dist/`; pass one or more version labels to build just those.

    pwsh scripts/build-fabric.ps1                # all Fabric cells (1.20.4..1.21.11 + 26.1/26.2/26.3)
    pwsh scripts/build-fabric.ps1 26.3           # one 26-line target
    pwsh scripts/build-fabric.ps1 1.21.8 26.1    # a pre-26 cell and a 26 target
    pwsh scripts/build-neoforge.ps1              # all NeoForge cells (1.20.1..1.21.11 + 26.1/26.2)
    pwsh scripts/build-neoforge.ps1 26.2         # one 26-line target
    pwsh scripts/build-forge.ps1                 # all Forge cells (1.20.1..1.21.11 except 1.21.9; no 26 - FG6 can't build unobf 26.x)
    pwsh scripts/build-forge.ps1 1.20.1          # one Forge cell

All jars land in `dist/`. Every cell - pre-26 per-version cells AND the unified 26 cells -
runs Cog code-generation automatically (`scripts/cog-gen.ps1`) before compiling. The 26 cells
additionally take a `-P` version matrix (Minecraft version, loader-dep version and range,
pack_format) from the build script.

## Toolchain matrix

| Loader   | MC versions                                          | JDK | Gradle |
|----------|------------------------------------------------------|-----|--------|
| Fabric   | 1.20.4                                               | 17  | 8.x    |
| Fabric   | 1.20.6, 1.21.1, 1.21.5, 1.21.8, 1.21.11             | 21  | 8.x    |
| Fabric   | 26 (26.1.2 / 26.2 / 26.3-snapshot-3)                | 25  | 9.x    |
| Forge    | 1.20.1                                               | 17  | 8.x    |
| Forge    | 1.20.6, 1.21.1, 1.21.5, 1.21.8, 1.21.10, 1.21.11     | 21  | 8.x    |
| NeoForge | 1.20.1, 1.20.4                                       | 17  | 8.x    |
| NeoForge | 1.20.6, 1.21.1, 1.21.5, 1.21.8, 1.21.11             | 21  | 8.x    |
| NeoForge | 26 (26.1.2 / 26.2)                                   | 25  | 9.x    |

Notes:

- **Forge** builds through 1.21.11 here (FG6). 1.21.9 is skipped (gated / locked out); there is no
  Forge cell for MC 26 (FG6 cannot build the unobfuscated 26.x, and there is no FG7).
- **NeoForge 1.20.1** is a Forge-1.20.1 fork (classic SRG runtime): its cell is Cog-generated
  with `-Loader Forge` so the mixin refmap gets the classic-SRG key. Every other NeoForge cell
  uses `-Loader NeoForge`.
- **MC 26.3** has a Fabric build (pinned to `26.3-snapshot-3`) but no NeoForge or Forge yet -
  NeoForge has not shipped for 26.3 and there is no Forge for MC 26.

## The four build regimes

One source tree, but the loaders reach the compiler four different ways:

1. **Fabric pre-26 (loom + remap)** - fabric-loom on the intermediary runtime; Cog emits the
   correct mojmap symbols as real source and loom remaps them at build time.
2. **Fabric 26 (loom, mojmap)** - fabric-loom on the mojmap runtime; the unified `Fabric/26`
   cell driven by the `-P` version matrix.
3. **Forge (FG6) and the NeoForge-1.20.1 fork** - ForgeGradle 6 on JDK 17/21; the classic-SRG
   runtime, so those cells Cog-generate against direct compiled access (`-Loader Forge`).
4. **Modern NeoForge (`net.neoforged.moddev`)** - ModDevGradle for 1.20.4..1.21.11 and the
   unified `NeoForge/26` cell.

## Repository layout

| Directory            | What it is |
|----------------------|------------|
| `shared_minecraft/`  | The single source of truth - MC-coupled core + mixins (`TridentKillerLogic`, `LivingEntityAccessor`, `ThrownTridentMixin`), the mixins.json, pack.mcmeta, and the icon asset. The 26 cells srcDir this directly; pre-26 cells receive a Cog-materialised copy. |
| `Fabric/`, `Forge/`, `NeoForge/` | Per-loader builds; one `<version>` subfolder per pre-26 MC cell, plus the unified `26/` cell (Fabric and NeoForge). Each cell holds only its loader entrypoint + templated manifest. |
| `_codegen/`          | Cog generator: `compat.py` (the cross-version "era brain") + `cog_sources/` (the Cog-instrumented drift files - the SOLE source of the drifting mixin/logic code). |
| `scripts/`           | The build scripts (`build-<loader>.ps1`), `cog-gen.ps1`, and `_metadata.py` (the issue-URL single-source stamp/check). |
| `docs/`              | Developer specs (gitignored - not part of any published jar). |
| `dist/`              | Build output (generated). |

## How the code generation works

Cross-version API drift is resolved at build time by Cog, driven by `_codegen/compat.py`. The
26 `shared_minecraft` tree is the master; every drift point (package moves, pickup/enchant/hurt
API renames, NBT era, owner/credit changes) is a conditional in `compat.py` that reproduces the
26 master byte-for-byte for MC 26+ and emits the correct older symbol for each earlier era.

For each cell, `scripts/cog-gen.ps1`:

1. Wipes and recreates `<Cell>/gen/` (a build artifact, never committed).
2. Copies `shared_minecraft/src/main/{java,resources}` into `<Cell>/gen/` verbatim.
3. Swaps in the Cog-instrumented drift files from `_codegen/cog_sources/`.
4. Adds the presence-gated shims for that MC version (e.g. `AbstractArrowInvoker` on 1.20.x,
   `ProjectileAccessor` before 1.21.6, `NbtBridge` for the 1.21.2..1.21.5 bridge era).
5. Runs `cog -r -D mcver=<v>` over the Cog files with `compat.py` on `sys.path`.
6. Regenerates the mixins.json `mixins[]` + `compatibilityLevel` to match the files actually
   present for that version.

The cell's Gradle build compiles `<Cell>/gen/`, not `shared_minecraft` directly - which is why
Cog must be installed before building.

Direct-compile (Cog) is used rather than a reflection facade because pre-26 Fabric runs on the
intermediary runtime and Forge/NeoForge 1.20.1-1.20.4 run SRG: reflection by mojmap name misses
on those runtimes, whereas Cog emits the correct symbol as real source that the loader remaps at
load time. Cog therefore works on every loader and every runtime.

## Credits / License

Trident Killers 4 Java is a clean-room implementation of the Bedrock-Edition trident-killer
behaviour, maintained by Kishku7. All rights reserved.
