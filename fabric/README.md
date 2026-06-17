# Trident Killers 4 Java - Fabric (Minecraft 26.2 (pre-release))

**Fabric** source trees of Trident Killers 4 Java for the Minecraft 26.2 (pre-release) line. Server-side mod. Jars also run on **Quilt**. (On 26.x, Quilt Loader needs `-Dloader.experimental.minecraft.targetNamespace=official`.)
Each version below is its own self-contained source tree (separate binary per loader).

## Builds

| Version | Minecraft | Java | Toolchain |
| --- | --- | --- | --- |
| [`26.2/`](26.2) | 26.2 (pre-release) | 25 | fabric-loom, built vs 26.2-rc-2 |

## Build

```
cd <version>
./gradlew build      # Windows: .\gradlew.bat build
```

Output: `build/libs/trident-killers-4-java-*.jar`. Part of the [`26.2` branch](https://github.com/Kishku7/trident-killers-4-java/tree/26.2).
