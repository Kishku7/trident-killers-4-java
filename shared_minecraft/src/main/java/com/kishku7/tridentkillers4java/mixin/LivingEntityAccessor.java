package com.kishku7.tridentkillers4java.mixin;

import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** Accessor for LivingEntity.skipDropExperience (FR-8b: XP suppression while owner offline). */
@Mixin(LivingEntity.class)
public interface LivingEntityAccessor {

    @Accessor("skipDropExperience")
    boolean tk4j$getSkipDropExperience();

    @Accessor("skipDropExperience")
    void tk4j$setSkipDropExperience(boolean value);
}
