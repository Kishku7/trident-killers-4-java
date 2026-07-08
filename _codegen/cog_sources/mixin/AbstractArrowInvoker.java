package com.kishku7.tridentkillers4java.mixin;

import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/**
 * Cross-version access to the arrow's pickup stack. ThrownTrident kept its own
 * tridentItem field only through 1.20.2; 1.20.3+ moved the stack into
 * AbstractArrow. getPickupItem() is declared on AbstractArrow across the whole
 * 1.20 - 1.20.4 range, so this invoker works everywhere with one jar.
 */
@Mixin(AbstractArrow.class)
public interface AbstractArrowInvoker {

    @Invoker("getPickupItem")
    ItemStack tk4j$getPickupItem();
}
