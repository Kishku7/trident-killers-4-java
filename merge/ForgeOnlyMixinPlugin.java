package com.kishku7.tridentkillers4java;

import org.objectweb.asm.tree.ClassNode;
import org.spongepowered.asm.mixin.extensibility.IMixinConfigPlugin;
import org.spongepowered.asm.mixin.extensibility.IMixinInfo;

import java.util.List;
import java.util.Set;

/**
 * Gates the Forge mixin config so it never applies on modern NeoForge (20.5+),
 * where the manifest MixinConfigs attribute is also honored and would otherwise
 * double-apply alongside the NeoForge config declared in neoforge.mods.toml.
 */
public class ForgeOnlyMixinPlugin implements IMixinConfigPlugin {
    private static final boolean MODERN_NEOFORGE = detect();

    private static boolean detect() {
        try {
            Class.forName("net.neoforged.fml.loading.FMLLoader", false, ForgeOnlyMixinPlugin.class.getClassLoader());
            return true;
        } catch (Throwable t) {
            return false;
        }
    }

    @Override public void onLoad(String mixinPackage) { }
    @Override public String getRefMapperConfig() { return null; }
    @Override public boolean shouldApplyMixin(String targetClassName, String mixinClassName) { return !MODERN_NEOFORGE; }
    @Override public void acceptTargets(Set<String> myTargets, Set<String> otherTargets) { }
    @Override public List<String> getMixins() { return null; }
    @Override public void preApply(String targetClassName, ClassNode targetClass, String mixinClassName, IMixinInfo mixinInfo) { }
    @Override public void postApply(String targetClassName, ClassNode targetClass, String mixinClassName, IMixinInfo mixinInfo) { }
}
