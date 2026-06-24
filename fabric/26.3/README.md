# Trident Killers 4 Java - Fabric 26.2 (Minecraft 26.2 (pre-release))

This source tree builds the **Fabric** binary for **Minecraft 26.2 (pre-release)**. Server-side mod.

- Loader: Fabric
- Minecraft: 26.2 (pre-release)
- Java: 25
- Toolchain: fabric-loom, built vs 26.2-rc-2
- Quilt: yes (Quilt loads the Fabric jar - 26.x needs the `targetNamespace=official` launch flag)

## Build

```
./gradlew build      # Windows: .\gradlew.bat build
```

Output: `build/libs/trident-killers-4-java-*.jar`

Part of the [`26.2` branch](https://github.com/Kishku7/trident-killers-4-java/tree/26.2). [Modrinth](https://modrinth.com/mod/trident-killers-4-java) - [Releases](https://github.com/Kishku7/trident-killers-4-java/releases).
