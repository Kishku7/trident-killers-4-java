package com.kishku7.tridentkillers4java.mixin;

import net.minecraft.world.entity.projectile.Projectile;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

import java.util.UUID;

/** Access to the projectile's stored owner UUID (resolvable even while the owner is offline). */
@Mixin(Projectile.class)
public interface ProjectileAccessor {

    @Accessor("ownerUUID")
    UUID tk4j$getOwnerUuid();
}
