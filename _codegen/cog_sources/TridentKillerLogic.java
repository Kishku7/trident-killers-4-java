package com.kishku7.tridentkillers4java;

//[[[cog
// import cog, compat
// cog.outl(compat.logic_imports(mcver, loader))
//]]]
//[[[end]]]

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

    //[[[cog
    // import cog, compat
    // cog.outl(compat.credit_fields(mcver))
    //]]]
    //[[[end]]]

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
    // hurtOrSimulate (used on the valueio/credit era) is @Deprecated upstream but is the
    // intended damage entrypoint here; suppress the -Xlint:all deprecation note.
    @SuppressWarnings("deprecation")
    public static void firePulse(ThrownTrident trident, UUID ownerUuid) {
        if (!(trident.level() instanceof ServerLevel serverLevel)) {
            return;
        }
        boolean ownerOnline = ownerUuid != null
                && serverLevel.getServer().getPlayerList().getPlayer(ownerUuid) != null;

        //[[[cog
        // import cog, compat
        // cog.outl(compat.pickup_stmt(mcver))
        //]]]
        //[[[end]]]

        //[[[cog
        // import cog, compat
        // cog.outl(compat.damage_source_setup(mcver))
        //]]]
        //[[[end]]]

        AABB hitBox = trident.getBoundingBox().inflate(HIT_INFLATE);
        List<Entity> targets = serverLevel.getEntities(trident, hitBox,
                e -> e instanceof Mob && e.isAlive() && !(e instanceof Player));

        for (Entity target : targets) {
            Mob mob = (Mob) target;

            //[[[cog
            // import cog, compat
            // cog.outl(compat.enchant_damage_stmt(mcver))
            //]]]
            //[[[end]]]

            //[[[cog
            // import cog, compat
            // cog.outl(compat.credit_in_loop(mcver))
            //]]]
            //[[[end]]]

            boolean suppressXp = !ownerOnline; // owner offline OR no owner -> no XP piles up (FR-8b)
            LivingEntityAccessor xs = (LivingEntityAccessor) mob;
            boolean previousSkip = xs.tk4j$getSkipDropExperience();
            if (suppressXp) {
                xs.tk4j$setSkipDropExperience(true);
            }

            //[[[cog
            // import cog, compat
            // cog.outl(compat.hurt_call(mcver))
            //]]]
            //[[[end]]]

            // If the mob survived, restore its XP flag so a later legitimate death is unaffected.
            if (suppressXp && mob.isAlive()) {
                xs.tk4j$setSkipDropExperience(previousSkip);
            }
        }
    }
    //[[[cog
    // import cog, compat
    // cog.out(compat.turret_helpers(mcver))
    //]]]
    //[[[end]]]
}
