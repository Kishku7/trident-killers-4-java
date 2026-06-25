package com.kishku7.tridentkillers4java.mixin;

import com.kishku7.tridentkillers4java.TridentKillerLogic;
import com.kishku7.tridentkillers4java.TridentKillers;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.projectile.arrow.AbstractArrow;
import net.minecraft.world.entity.projectile.arrow.ThrownTrident;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.UUID;

/**
 * Trident-killer behavior on the thrown trident (clean-room; see FUNCTIONAL_SPEC.md).
 *
 * A trident becomes "killer-identified" the first time a piston actively moves a
 * block/head into its space (R-2). Identified tridents: never despawn (FR-11),
 * are position-locked against every non-piston influence (FR-9, FR-10), pulse
 * damage on each piston cycle (FR-1..FR-3), and may be picked up by any player
 * (FR-12). Tridents never piston-pulsed are left 100% vanilla (FR-14).
 */
@Mixin(ThrownTrident.class)
public abstract class ThrownTridentMixin extends AbstractArrow {

    @Unique
    private boolean tk4j$identified = false;

    @Unique
    private double tk4j$anchorX;

    @Unique
    private double tk4j$anchorY;

    @Unique
    private double tk4j$anchorZ;

    @Unique
    private UUID tk4j$ownerUuid = null;

    /** True once anchor fields hold a valid pre-piston resting position. */
    @Unique
    private boolean tk4j$anchorValid = false;

    protected ThrownTridentMixin(EntityType<? extends AbstractArrow> entityType, Level level) {
        super(entityType, level);
    }

    @Inject(method = "tick", at = @At("TAIL"))
    private void tk4j$tick(CallbackInfo ci) {
        if (this.level().isClientSide()) {
            return;
        }
        ThrownTrident self = (ThrownTrident) (Object) this;

        if (this.tk4j$identified) {
            // FR-13b: a Loyalty return (noPhysics flight) is vanilla - leave it alone.
            if (this.isNoPhysics()) {
                return;
            }
            // FR-9 + FR-10: hard position lock. Only the killer state moves nothing;
            // mob pushes, block updates, and gravity drift are all reverted here.
            if (this.getX() != this.tk4j$anchorX
                    || this.getY() != this.tk4j$anchorY
                    || this.getZ() != this.tk4j$anchorZ) {
                this.setPos(this.tk4j$anchorX, this.tk4j$anchorY, this.tk4j$anchorZ);
            }
            this.setDeltaMovement(Vec3.ZERO);
            if (!this.isInGround()) {
                this.setInGround(true);
            }

            // FR-1/FR-2: pulse on EVERY tick a piston is actively moving in our space.
            // Vanilla hurt immunity (10 ticks) rate-limits this to ~1 effective hit per
            // piston cycle; ticking every active tick wins the race against vanilla's
            // own entity push, which can shove a mob out of the kill zone mid-cycle.
            if (TridentKillerLogic.pistonActiveNear(self)) {
                TridentKillerLogic.firePulse(self, this.tk4j$ownerUuid);
            }
            return;
        }

        // Not identified: leave vanilla behavior completely untouched (FR-14)
        // except to watch for the first qualifying piston pulse while stuck.
        if (!this.isInGround()) {
            this.tk4j$anchorValid = false; // in flight - no resting position yet
            return;
        }
        if (TridentKillerLogic.pistonActiveNear(self)) {
            this.tk4j$identified = true;
            // Anchor at the PRE-PUSH resting position recorded on earlier quiet ticks
            // (vanilla may already have displaced us this tick); fall back to current.
            if (!this.tk4j$anchorValid) {
                this.tk4j$anchorX = this.getX();
                this.tk4j$anchorY = this.getY();
                this.tk4j$anchorZ = this.getZ();
                this.tk4j$anchorValid = true;
            }
            this.setPos(this.tk4j$anchorX, this.tk4j$anchorY, this.tk4j$anchorZ);
            if (this.tk4j$ownerUuid == null && this.owner != null) {
                this.tk4j$ownerUuid = this.owner.getUUID();
            }
            TridentKillerLogic.firePulse(self, this.tk4j$ownerUuid);
            TridentKillers.LOGGER.info(
                    "Trident at ({}, {}, {}) is now killer-identified (owner {}).",
                    this.tk4j$anchorX, this.tk4j$anchorY, this.tk4j$anchorZ, this.tk4j$ownerUuid);
        } else {
            // Quiet tick while stuck: remember this as the resting position.
            this.tk4j$anchorX = this.getX();
            this.tk4j$anchorY = this.getY();
            this.tk4j$anchorZ = this.getZ();
            this.tk4j$anchorValid = true;
        }
    }

    /** FR-11: identified tridents never despawn. */
    @Inject(method = "tickDespawn", at = @At("HEAD"), cancellable = true)
    private void tk4j$neverDespawn(CallbackInfo ci) {
        if (this.tk4j$identified) {
            ci.cancel();
        }
    }

    /** FR-12: any player may pick up an identified trident (Bedrock-style pickup). */
    @Redirect(
            method = "playerTouch",
            at = @At(
                    value = "INVOKE",
                    target = "Lnet/minecraft/world/entity/projectile/arrow/ThrownTrident;ownedBy(Lnet/minecraft/world/entity/Entity;)Z"))
    private boolean tk4j$anyPlayerPickup(ThrownTrident self, Entity player) {
        return this.tk4j$identified || this.ownedBy(player);
    }

    @Inject(method = "addAdditionalSaveData", at = @At("TAIL"))
    private void tk4j$save(ValueOutput output, CallbackInfo ci) {
        output.putBoolean("tk4j_identified", this.tk4j$identified);
        if (this.tk4j$identified) {
            output.putDouble("tk4j_anchor_x", this.tk4j$anchorX);
            output.putDouble("tk4j_anchor_y", this.tk4j$anchorY);
            output.putDouble("tk4j_anchor_z", this.tk4j$anchorZ);
        }
        if (this.tk4j$ownerUuid != null) {
            output.putString("tk4j_owner", this.tk4j$ownerUuid.toString());
        }
    }

    @Inject(method = "readAdditionalSaveData", at = @At("TAIL"))
    private void tk4j$load(ValueInput input, CallbackInfo ci) {
        this.tk4j$identified = input.getBooleanOr("tk4j_identified", false);
        if (this.tk4j$identified) {
            this.tk4j$anchorX = input.getDoubleOr("tk4j_anchor_x", this.getX());
            this.tk4j$anchorY = input.getDoubleOr("tk4j_anchor_y", this.getY());
            this.tk4j$anchorZ = input.getDoubleOr("tk4j_anchor_z", this.getZ());
            this.tk4j$anchorValid = true;
        }
        String ownerString = input.getStringOr("tk4j_owner", "");
        if (!ownerString.isEmpty()) {
            try {
                this.tk4j$ownerUuid = UUID.fromString(ownerString);
            } catch (IllegalArgumentException ignored) {
                this.tk4j$ownerUuid = null;
            }
        }
    }
}
