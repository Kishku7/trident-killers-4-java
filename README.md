# Trident Killers 4 Java - branch `26.2`

Source for the Minecraft **26.2 (pre-release)** line. Each loader has its own folder (`fabric/`, `forge/`,
`neoforge/`) with one subfolder per Minecraft version that source tree targets - separate source trees and
separate binaries per loader, even at fork points. Server-side mod.

> **Pre-release line.** Modrinth **beta** only; no GitHub release until 26.2 is stable. The NeoForge build targets a local NeoForge 26.2 alpha (no public NeoForge 26.2 yet).

## Platforms

- [`fabric/`](fabric) (+ Quilt) - 1 build(s); see its README for versions and exclusions.
- [`neoforge/`](neoforge) - 1 build(s); see its README for versions and exclusions.

## Not supported on this line

- **Forge** is not built for the 26.x line - there is no working Forge toolchain for 26.x (ForgeGradle 6 cannot build unobfuscated Minecraft and there is no FG7).

## Build

```
cd <loader>/<version>
./gradlew build      # Windows: .\gradlew.bat build
```

Output: `build/libs/trident-killers-4-java-*.jar`. Requires JDK 25.

## Links

- Other branches: [`1.20.x`](https://github.com/Kishku7/trident-killers-4-java/tree/1.20.x), [`1.21.x`](https://github.com/Kishku7/trident-killers-4-java/tree/1.21.x), [`26.1`](https://github.com/Kishku7/trident-killers-4-java/tree/26.1)
- Overview: [`main`](https://github.com/Kishku7/trident-killers-4-java/tree/main)
- Reusable build/test scripts: [`tooling`](https://github.com/Kishku7/trident-killers-4-java/tree/tooling)
- Modrinth: https://modrinth.com/mod/trident-killers-4-java
- Releases: https://github.com/Kishku7/trident-killers-4-java/releases

By Kishku7. All Rights Reserved.
