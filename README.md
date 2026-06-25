# Trident Killers 4 Java -- MC 26.x (unified line)

Server-side mod bringing the Bedrock trident-killer mechanic to Java. One source tree builds every
supported 26.x version on both loaders.

Layout (shared standard):
- shared_minecraft/ -- MC-coupled core + mixins (TridentKillerLogic, LivingEntityAccessor,
  ThrownTridentMixin) + mixins.json + pack.mcmeta + assets. Single source of truth, srcDir'd per loader.
- Fabric/ -- Fabric entrypoint only (TridentKillers, ModInitializer) + templated fabric.mod.json.
- NeoForge/ -- NeoForge entrypoint only (TridentKillers, @Mod) + neoforge.mods.toml.

Build: `pwsh build-all-fabric.ps1` (26.1.2/26.2/26.3-snapshot-1) and `pwsh build-all-neoforge.ps1`
(26.1.2/26.2). Toolchain: JDK25, fabric-loom 1.16, ModDevGradle 2.0.141.
