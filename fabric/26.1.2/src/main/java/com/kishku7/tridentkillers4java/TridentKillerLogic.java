package com.kishku7.tridentkillers4java;

import com.kishku7.tridentkillers4java.mixin.LivingEntityAccessor;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.arrow.ThrownTrident;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.piston.PistonMovingBlockEntity;
import net.minecraft.world.phys.AABB;

import java.util.List;
import java.util.UUID;

/**
 * Core trident-killer behavior (clean-room; implemented from FUNCTIONAL_SPEC.md).
 *
 * Turret model: an identified trident never travels. A piston actively moving a
 * block (or its head) into the trident's space is a "motion pulse"; each pulse
 * damages all mobs intersecting the trident's hitbox, credited to the thrower.
 */
public final class TridentKillerLogic {

    /** Vanilla thrown-trident base damage (mirrors the vanilla damage convention, FR-6). */
    private static final float BASE_DAMAGE = 8.0F;

    /** Inflation applied to the trident AABB for piston-pulse detection (contraption tolerance). */
    private static final double PISTON_SCAN_INFLATE = 0.25D;

    /** Inflation applied to the trident AABB for target selection (FR-6: default hitbox, small tolerance). */
    private static final double HIT_INFLATE = 0.25D;

    /** Kill-credit memory ticks; mirrors vanilla player-hurt memory window. */
    private static final int CREDIT_MEMORY_TICKS = 100;

    private TridentKillerLogic() {
    }

    /**
     * True while a piston is actively moving a block/head whose space intersects the
     * trident's (inflated) bounding box. Moving-piston block entities only exist
     * during the 2-tick travel window, so this is inherently motion-gated (FR-1).
     */
    public static boolean pistonActiveNear(ThrownTrident trident) {
        Level level = trident.level();
        AABB box = trident.getBoundingBox().inflate(PISTON_SCAN_INFLATE);
        BlockPos center = trident.blockPosition();
        BlockPos.MutableBlockPos cursor = new BlockPos.MutableBlockPos();
        for (int dx = -1; dx <= 1; dx++) {
            for (int dy = -1; dy <= 1; dy++) {
                for (int dz = -1; dz <= 1; dz++) {
                    cursor.set(center.getX() + dx, center.getY() + dy, center.getZ() + dz);
                    BlockEntity be = level.getBlockEntity(cursor);
                    if (be instanceof PistonMovingBlockEntity) {
                        AABB blockSpace = new AABB(
                                cursor.getX(), cursor.getY(), cursor.getZ(),
                                cursor.getX() + 1.0D, cursor.getY() + 1.0D, cursor.getZ() + 1.0D);
                        if (blockSpace.intersects(box)) {
                            return true;
                        }
                    }
                }
            }
        }
        return false;
    }

    /**
     * One motion pulse: damage every mob intersecting the trident's hitbox (FR-2, FR-3).
     * Mobs only - never players, items, or any other entity (FR-4, FR-5).
     * Kill credit goes to the thrower even when offline (FR-8a); XP is suppressed
     * while the owner is offline (FR-8b). No durability cost (FR-7: we never touch it).
     */
    public static void firePulse(ThrownTrident trident, UUID ownerUuid) {
        if (!(trident.level() instanceof ServerLevel serverLevel)) {
            return;
        }
        Entity ownerEntity = trident.getOwner(); // resolves only while the owner is loaded/online
        boolean ownerOnline = ownerUuid != null
                && serverLevel.getServer().getPlayerList().getPlayer(ownerUuid) != null;

        // Same damage-source convention vanilla uses for trident damage (owner falls back to the trident).
        DamageSource source = trident.damageSources()
                .trident(trident, ownerEntity != null ? ownerEntity : trident);

        AABB hitBox = trident.getBoundingBox().inflate(HIT_INFLATE);
        List<Entity> targets = serverLevel.getEntities(trident, hitBox,
                e -> e instanceof Mob && e.isAlive() && !(e instanceof Player));

        for (Entity target : targets) {
            Mob mob = (Mob) target;

            float damage = EnchantmentHelper.modifyDamage(
                    serverLevel, trident.getWeaponItem(), mob, source, BASE_DAMAGE); // Impaling etc. (FR-6)

            if (ownerUuid != null) {
                // Player kill credit by UUID - works with the owner offline (FR-8a).
                mob.setLastHurtByPlayer(ownerUuid, CREDIT_MEMORY_TICKS);
            }

            boolean suppressXp = !ownerOnline; // owner offline OR no owner -> no XP piles up (FR-8b)
            LivingEntityAccessor xs = (LivingEntityAccessor) mob;
            boolean previousSkip = xs.tk4j$getSkipDropExperience();
            if (suppressXp) {
                xs.tk4j$setSkipDropExperience(true);
            }

            mob.hurtOrSimulate(source, damage);

            // If the mob survived, restore its XP flag so a later legitimate death is unaffected.
            if (suppressXp && mob.isAlive()) {
                xs.tk4j$setSkipDropExperience(previousSkip);
            }
        }
    }
}
