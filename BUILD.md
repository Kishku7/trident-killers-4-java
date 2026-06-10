# Trident Killers 4 Java - Minecraft 26.1.2

Loaders: Fabric, Quilt, NeoForge  (MC 26.1 - 26.1.2). Quilt runs the Fabric jar.

Per-loader source in subfolders: 
fabric, neoforge
.

## Build
- fabric:  cd fabric && ./gradlew build   -> fabric/build/libs/
- neoforge:  cd neoforge && ./gradlew build   -> neoforge/build/libs/

## Merge to one universal jar (optional - info only)
Merge per-loader jars with Forgix 2.0 (NOT bundled; build from https://github.com/PacifistMC/Forgix, JDK 24):

    java -cp <Forgix-shadow.jar> io.github.pacifistmc.forgix.Forgix mergeJars --output merged.jar --fabric <fabric.jar> [--forge <forge.jar>] [--neoforge <neoforge.jar>]

Reusable harness/merge/release scripts live on the 	ooling branch. 1.21.9+ and 26.x ship per-loader (no Forge).
