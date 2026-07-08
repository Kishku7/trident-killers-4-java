"""Trident Killers 4 Java cross-version "era brain" for Cog code generation.

Given an MC version string (mcver), this module returns the correct per-era code
fragments for each mixin/logic drift point identified in docs/COG-SPEC.md. Cog source
files import this module and call its helpers inside //[[[cog ... //]]] blocks so ONE
shared_minecraft source (the 26 master) can be direct-compiled correctly for every MC
version the mod claims.

Rationale for direct-compile (Cog) rather than a reflection facade: pre-26 Fabric runs on
the INTERMEDIARY runtime, so reflection-by-mojmap-name misses there. Cog emits the correct
mojmap symbol as real source, which loom then remaps at build time. Cog therefore works on
every loader + every runtime.

ASCII-only. Plain Python, no third-party deps beyond the stdlib.

The 26 master is the "26 branch" of every conditional below: every helper reproduces the
26 master byte-for-byte when given a v[0] >= 26 mcver. Multi-line code-emitting helpers carry
ABSOLUTE indentation (the exact leading spaces of the final file), and their cog markers sit at
COLUMN 0 in the cog_source, so cog inserts the returned text verbatim (cogapp prepends the
marker's own indentation to every emitted line; a column-0 marker prepends nothing).

Drift axes (docs/COG-SPEC.md):
  package          projectile (pre-26) vs projectile.arrow (26)
  pickup           AbstractArrowInvoker (v<1.21) vs getWeaponItem() (v>=1.21)
  enchant          getMobType (v<1.20.5) / getType (1.20.5..1.20.6) / modifyDamage (v>=1.21)
  hurt             hurt (v<1.21.2) vs hurtOrSimulate (v>=1.21.2)
  inground         field inGround (v<1.21.2) vs method isInGround/setInGround (v>=1.21.2)
  nbt              compound (v<1.21.2) / bridge (1.21.2..1.21.5) / valueio (v>=1.21.6)
  owner            ProjectileAccessor (v<1.21.6) vs this.owner.getUUID() (v>=1.21.6)
  credit           turret (v<1.21.6) vs setLastHurtByPlayer (v>=1.21.6)
  turret_ctor      reflective (v<1.20.5, i.e. 1.20.4) vs direct (else, turret era only)
  redirect_desc    the @Redirect ownedBy target descriptor (.arrow. insertion for 26)
  presence         AbstractArrowInvoker (1.20.x) / ProjectileAccessor (v<1.21.6) / NbtBridge (bridge era)
"""

import sys


# ---------------------------------------------------------------------------
# Version parsing
# ---------------------------------------------------------------------------

def _parse(mcver):
    """Parse an MC version string into a comparable tuple of ints.

    Accepts forms like "1.21.8", "1.21", "26", "26.3", "26.3-snapshot-2".
    A trailing "-<qualifier>" (snapshot/pre/rc) is dropped for ordering; the
    numeric prefix decides the era (prerelease-inclusive by design).
    """
    core = str(mcver).strip()
    for sep in ("-", "+", " "):
        if sep in core:
            core = core.split(sep, 1)[0]
    parts = []
    for tok in core.split("."):
        num = ""
        for ch in tok:
            if ch.isdigit():
                num += ch
            else:
                break
        parts.append(int(num) if num else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


# ---------------------------------------------------------------------------
# Coarse era booleans (used by several helpers and by cog-gen presence gating)
# ---------------------------------------------------------------------------

def is_26(mcver):
    """True on the 26.x line (major >= 26): the shared_minecraft master shape."""
    return _parse(mcver)[0] >= 26


def has_abstractarrow_invoker(mcver):
    """Is the AbstractArrowInvoker shim present? Only the 1.20.x cells use it for pickup.

    The invoker reads AbstractArrow.getPickupItem(); getWeaponItem() (used from 1.21) does not
    exist on the 1.20 line, so 1.20.x pickup must go through this @Invoker. Present iff the cell
    is on the 1.20.* line."""
    v = _parse(mcver)
    return v[0] == 1 and v[1] == 20


def has_projectile_accessor(mcver):
    """Is the ProjectileAccessor shim present? Needed to read the stored owner UUID while the
    owner is offline, on every version before the public Projectile.getOwner()/owner field path
    used from 1.21.6. Present iff v < (1,21,6)."""
    return _parse(mcver) < (1, 21, 6)


def has_nbt_bridge(mcver):
    """Is the NbtBridge shim present? Bridge era only (1.21.2 <= v < 1.21.6), where CompoundTag's
    typed accessors changed shape and the mod routes NBT through reflective string accessors."""
    v = _parse(mcver)
    return (1, 21, 2) <= v < (1, 21, 6)


def compat_level(mcver):
    """pre-26 mixins.json compatibilityLevel. JAVA_17 on the 1.20.* line, JAVA_21 otherwise.

    (Classic-SRG Forge < 1.21.2 also wants JAVA_17; cog-gen handles that Forge override the same
    way Chunksmith does, so this base rule keys purely on the 1.20.* line.)"""
    v = _parse(mcver)
    if v < (1, 20, 5):
        return "JAVA_17"
    return "JAVA_21"


def forge_needs_refmap(mcver):
    """Does a classic-Forge (ForgeGradle 6) cell for this MC version need a mixin refmap key?

    Classic Forge runs SRG-mapped at runtime up to and including the 1.20.4 line, so the mixin
    loader needs the refmap to resolve targets by name -> the "refmap" key is MANDATORY there.
    From MC 1.20.6 (FG 6.0.16+, official Mojang mappings at runtime) no refmap is consulted -> the
    key must be ABSENT. Loader-specific: cog-gen only calls this when -Loader Forge. Boundary ==
    the ancient line (1.20.1 / 1.20.4): True there, False from 1.20.6 onward."""
    v = _parse(mcver)
    return v[0] == 1 and v[1] == 20 and v[2] < 5


# ---------------------------------------------------------------------------
# package -- ThrownTrident / AbstractArrow live in ...projectile (pre-26) vs
# ...projectile.arrow (26). Emitted as the package segment for import lines.
# ---------------------------------------------------------------------------

def projectile_package(mcver, loader=None):
    """The entity-projectile package for ThrownTrident/AbstractArrow: the '.arrow' subpackage
    landed at MC 1.21.11 (verified on-disk: 1.21.9 = ...projectile ; 1.21.11 and 26.x =
    ...projectile.arrow). The deciding axis is the COMPILE classpath, not the nominal cell
    version: NeoForge/Forge cells compile against their true version, but Fabric cells compile
    against the FLOOR of their range (e.g. the Fabric 1.21.11 cell compiles vs 1.21.9, where the
    class is still ...projectile). So Fabric never takes the .arrow subpackage pre-26; 26.x is
    .arrow on every loader (the master shape). v >= 26: .arrow ; else .arrow iff
    v >= 1.21.11 AND loader is not Fabric."""
    v = _parse(mcver)
    if v[0] >= 26:
        return "net.minecraft.world.entity.projectile.arrow"
    if v >= (1, 21, 11) and loader != "Fabric":
        return "net.minecraft.world.entity.projectile.arrow"
    return "net.minecraft.world.entity.projectile"


def redirect_descriptor(mcver, loader=None):
    """The @Redirect @At target descriptor for ThrownTrident.ownedBy in playerTouch.

    Only the '.../arrow/...' insertion differs across eras (STRING-in-annotation -> Cog is
    mandatory; a reflection facade cannot touch it)."""
    pkg = projectile_package(mcver, loader).replace(".", "/")
    return "L%s/ThrownTrident;ownedBy(Lnet/minecraft/world/entity/Entity;)Z" % pkg


# ---------------------------------------------------------------------------
# pickup -- how the trident's pickup ItemStack is obtained.
# ---------------------------------------------------------------------------

def pickup_stack_expr(mcver):
    """Expression yielding the trident's pickup ItemStack (used to build tridentStack).

    v < (1,21): getWeaponItem() does not exist -> read AbstractArrow.getPickupItem() via the
    AbstractArrowInvoker shim. v >= (1,21): trident.getWeaponItem()."""
    if _parse(mcver) < (1, 21):
        return "((AbstractArrowInvoker) trident).tk4j$getPickupItem()"
    return "trident.getWeaponItem()"


def pickup_stmt(mcver):
    """The trident-pickup ItemStack binding.

    turret era (v<1.21.6): 'ItemStack tridentStack = <pickup>;' -- the turret needs the stack in
      hand and enchant reads it. credit era (26 master): NOTHING -- the master never binds a local
      and inlines trident.getWeaponItem() in the enchant call (so no ItemStack import is needed)."""
    if uses_turret(mcver):
        return "ItemStack tridentStack = %s;" % pickup_stack_expr(mcver)
    return ""


# ---------------------------------------------------------------------------
# enchant -- the per-mob damage assignment statement (absolute col-12 indent).
# ---------------------------------------------------------------------------

def enchant_damage_stmt(mcver):
    """The 'float damage = ...;' statement computing enchanted (Impaling) damage for a mob.

    v < (1,20,5)          : legacy EnchantmentHelper.getDamageBonus(stack, MobType) via getMobType()
    (1,20,5) <= v < (1,21): getDamageBonus(stack, EntityType) via getType()
    v >= (1,21)           : EnchantmentHelper.modifyDamage(serverLevel, stack, mob, source, base)
    Absolute col-12 indent (inside the target loop). References the already-bound tridentStack
    local (bound by pickup_stmt in every era)."""
    v = _parse(mcver)
    if v < (1, 20, 5):
        return ("float damage = BASE_DAMAGE\n"
                "        + EnchantmentHelper.getDamageBonus(tridentStack, mob.getMobType()); "
                "// Impaling (FR-6)")
    if v < (1, 21):
        return ("float damage = BASE_DAMAGE\n"
                "        + EnchantmentHelper.getDamageBonus(tridentStack, mob.getType()); "
                "// Impaling (FR-6)")
    # v >= (1,21): modifyDamage. turret eras (1.21.1..1.21.5) read the bound tridentStack local;
    # the credit era (26 master) inlines trident.getWeaponItem() (no tridentStack local exists).
    stack_expr = "tridentStack" if uses_turret(mcver) else "trident.getWeaponItem()"
    return ("float damage = EnchantmentHelper.modifyDamage(\n"
            "        serverLevel, %s, mob, source, BASE_DAMAGE); "
            "// Impaling etc. (FR-6)" % stack_expr)


# ---------------------------------------------------------------------------
# hurt -- the damage-application call (absolute col-12 indent).
# ---------------------------------------------------------------------------

def hurt_call(mcver):
    """The mob damage-application statement: hurt (v<1.21.2) vs hurtOrSimulate (v>=1.21.2)."""
    if _parse(mcver) < (1, 21, 2):
        return "mob.hurt(source, damage);"
    return "mob.hurtOrSimulate(source, damage);"


# ---------------------------------------------------------------------------
# inground -- field access (v<1.21.2) vs accessor methods (v>=1.21.2).
# ---------------------------------------------------------------------------

def inground_get(mcver):
    """Bare expression testing whether the trident is in-ground: 'this.inGround' (field, v<1.21.2)
    vs 'this.isInGround()' (method, v>=1.21.2). Used to compose if-conditions at either indent."""
    if _parse(mcver) < (1, 21, 2):
        return "this.inGround"
    return "this.isInGround()"


def inground_set_block(mcver):
    """The identified-branch 'if (!<inground>) { <set-true>; }' block at absolute col-12 indent."""
    if _parse(mcver) < (1, 21, 2):
        setter = "this.inGround = true;"
    else:
        setter = "this.setInGround(true);"
    return ("if (!%s) {\n"
            "    %s\n"
            "}" % (inground_get(mcver), setter))


def inground_flight_if(mcver):
    """The not-identified-branch 'if (!<inground>) {' opener at absolute col-8 indent (its body +
    closing brace are plain text in the cog_source)."""
    return "if (!%s) {" % inground_get(mcver)


# ---------------------------------------------------------------------------
# owner -- resolving the stored owner UUID on the trident (absolute col-12 indent).
# ---------------------------------------------------------------------------

def owner_resolve_block(mcver):
    """The 'if (ownerUuid == null) { ... }' block assigning tk4j$ownerUuid from the stored owner.

    v < (1,21,6): the owner UUID is read via the ProjectileAccessor shim (@Accessor ownerUUID),
      which resolves even while the owner is offline.
    v >= (1,21,6): read this.owner.getUUID() directly, guarded on this.owner != null (the 26 master)."""
    if _parse(mcver) < (1, 21, 6):
        return ("if (this.tk4j$ownerUuid == null) {\n"
                "    this.tk4j$ownerUuid = ((ProjectileAccessor) this).tk4j$getOwnerUuid();\n"
                "}")
    return ("if (this.tk4j$ownerUuid == null && this.owner != null) {\n"
            "    this.tk4j$ownerUuid = this.owner.getUUID();\n"
            "}")


# ---------------------------------------------------------------------------
# credit -- kill-credit mechanism. Regions in firePulse (all absolute indent).
# ---------------------------------------------------------------------------

def uses_turret(mcver):
    """True on the turret-credit eras (v < 1.21.6): damage is attributed through a non-spawned
    'turret' ServerPlayer so loot-table Looting + killed_by_player work while the owner is offline.
    False from 1.21.6, where mob.setLastHurtByPlayer(UUID, ticks) provides credit directly."""
    return _parse(mcver) < (1, 21, 6)


def credit_fields(mcver):
    """The static fields firePulse's credit strategy needs (class body, absolute col-4 indent).

    turret era: the TURRETS map + NO_OWNER sentinel.
    credit era: the CREDIT_MEMORY_TICKS constant (the 26 master field)."""
    if uses_turret(mcver):
        return ("/** One non-spawned turret player per owner UUID (never added to the world). */\n"
                "private static final Map<UUID, ServerPlayer> TURRETS = new HashMap<>();\n"
                "\n"
                "private static final UUID NO_OWNER = new UUID(0L, 0L);")
    return ("/** Kill-credit memory ticks; mirrors vanilla player-hurt memory window. */\n"
            "private static final int CREDIT_MEMORY_TICKS = 100;")


def damage_source_setup(mcver):
    """The damage-source setup region in firePulse (absolute col-8 indent), before the target loop.

    turret era: build/position the turret ServerPlayer holding a copy of the trident, then
      DamageSource source = trident.damageSources().trident(trident, turret);
    credit era (26 master): resolve trident.getOwner() and fall back to the trident itself."""
    if uses_turret(mcver):
        return (
            "// Turret attacker: a non-spawned player holding the trident, so loot-table\n"
            "// Looting reads the trident's own enchantments and killed_by_player applies.\n"
            "ServerPlayer turret = turretFor(serverLevel, ownerUuid);\n"
            "turret.setPos(trident.getX(), trident.getY(), trident.getZ());\n"
            "turret.setItemSlot(EquipmentSlot.MAINHAND, tridentStack.copy());\n"
            "\n"
            "DamageSource source = trident.damageSources().trident(trident, turret);")
    return (
        "Entity ownerEntity = trident.getOwner(); // resolves only while the owner is loaded/online\n"
        "\n"
        "// Same damage-source convention vanilla uses for trident damage (owner falls back to the trident).\n"
        "DamageSource source = trident.damageSources()\n"
        "        .trident(trident, ownerEntity != null ? ownerEntity : trident);")


def credit_in_loop(mcver):
    """The per-mob kill-credit region inside the target loop (absolute col-12 indent).

    turret era: none (credit flows through the turret attacker) -> a comment placeholder.
    credit era (26 master): mob.setLastHurtByPlayer(ownerUuid, CREDIT_MEMORY_TICKS) when owned."""
    if uses_turret(mcver):
        return "// kill credit flows through the turret attacker (no per-mob call on this MC version)"
    return ("if (ownerUuid != null) {\n"
            "    // Player kill credit by UUID - works with the owner offline (FR-8a).\n"
            "    mob.setLastHurtByPlayer(ownerUuid, CREDIT_MEMORY_TICKS);\n"
            "}")


def turret_helpers(mcver):
    """The turretFor()/newTurret() helper methods (class body, absolute col-4 indent), or nothing.

    turret era: turretFor() caches one non-spawned ServerPlayer per owner + newTurret() builds it.
      newTurret is DIRECT-ctor on 1.20.6/1.21.1/1.21.5 (ClientInformation available) and REFLECTIVE
      on 1.20.4 (the 1.20/1.20.1 3-arg ctor with a 1.20.2+ 4-arg reflective fallback).
    credit era (26 master): no turret helpers at all -> empty string."""
    if not uses_turret(mcver):
        return ""

    common = (
        "\n"
        "private static ServerPlayer turretFor(ServerLevel level, UUID ownerUuid) {\n"
        "    UUID key = ownerUuid != null ? ownerUuid : NO_OWNER;\n"
        "    ServerPlayer turret = TURRETS.get(key);\n"
        "    if (turret == null || turret.isRemoved() || turret.level() != level) {\n"
        "        // Derive a distinct profile UUID so the synthetic turret can NEVER share a\n"
        "        // live player's UUID. Sharing it hijacks PlayerList's per-UUID PlayerAdvancements\n"
        "        // (repoints its player to this connectionless turret), causing a null-connection\n"
        "        // NPE when the real player next triggers an advancement/recipe send.\n"
        "        UUID profileId = UUID.nameUUIDFromBytes(\n"
        "                (\"TK4J_Turret:\" + key).getBytes(java.nio.charset.StandardCharsets.UTF_8));\n"
        "        turret = newTurret(level, new GameProfile(profileId, \"TK4J_Turret\"));\n"
        "        TURRETS.put(key, turret);\n"
        "    }\n"
        "    return turret;\n"
        "}\n")

    if _parse(mcver) < (1, 20, 5):
        # Reflective ctor (1.20.2 - 1.20.4): the ServerPlayer ctor is 4-arg (a ClientInformation
        # param was added in 1.20.2); 1.20/1.20.1 used the 3-arg (server, level, profile). This
        # single 1.20.x jar COMPILES against a 1.20.2+ classpath where the 3-arg ctor does NOT
        # exist, so a direct 'new ServerPlayer(server, level, profile)' would fail to COMPILE (a
        # NoSuchMethodError catch is a runtime guard; the symbol must still resolve). Both ctors
        # are therefore invoked REFLECTIVELY by SHAPE.
        new_turret = (
            "\n"
            "/**\n"
            " * Version-adaptive ServerPlayer construction (single jar, 1.20 - 1.20.4):\n"
            " * 1.20/1.20.1 use (server, level, profile); 1.20.2+ added a ClientInformation\n"
            " * parameter. Both are invoked reflectively (this cell compiles against a 1.20.2+\n"
            " * classpath where the 3-arg ctor is absent); the 4-arg path builds the default\n"
            " * ClientInformation by SHAPE (static no-arg factory returning the same type),\n"
            " * so it works under any runtime mappings without naming the class.\n"
            " */\n"
            "private static ServerPlayer newTurret(ServerLevel level, GameProfile profile) {\n"
            "    try {\n"
            "        for (java.lang.reflect.Constructor<?> c : ServerPlayer.class.getDeclaredConstructors()) {\n"
            "            Class<?>[] params = c.getParameterTypes();\n"
            "            if (params.length == 3\n"
            "                    && params[1] == ServerLevel.class\n"
            "                    && params[2] == GameProfile.class) {\n"
            "                return (ServerPlayer) c.newInstance(level.getServer(), level, profile); // 1.20 / 1.20.1\n"
            "            }\n"
            "            if (params.length == 4\n"
            "                    && params[1] == ServerLevel.class\n"
            "                    && params[2] == GameProfile.class) {\n"
            "                Class<?> clientInfoType = params[3];\n"
            "                Object defaultInfo = null;\n"
            "                for (java.lang.reflect.Method m : clientInfoType.getDeclaredMethods()) {\n"
            "                    if (java.lang.reflect.Modifier.isStatic(m.getModifiers())\n"
            "                            && m.getParameterCount() == 0\n"
            "                            && m.getReturnType() == clientInfoType) {\n"
            "                        defaultInfo = m.invoke(null);\n"
            "                        break;\n"
            "                    }\n"
            "                }\n"
            "                return (ServerPlayer) c.newInstance(level.getServer(), level, profile, defaultInfo); // 1.20.2+\n"
            "            }\n"
            "        }\n"
            "        throw new IllegalStateException(\"No compatible ServerPlayer constructor found\");\n"
            "    } catch (ReflectiveOperationException e) {\n"
            "        throw new IllegalStateException(\"Failed to construct turret player (1.20.x path)\", e);\n"
            "    }\n"
            "}\n")
    else:
        # Direct ctor (1.20.6 / 1.21.1 / 1.21.5): ClientInformation.createDefault() available.
        new_turret = (
            "\n"
            "private static ServerPlayer newTurret(ServerLevel level, GameProfile profile) {\n"
            "    return new ServerPlayer(level.getServer(), level, profile, ClientInformation.createDefault());\n"
            "}\n")

    return common + new_turret


# ---------------------------------------------------------------------------
# import blocks (column-0 -- imports live at the file margin).
# ---------------------------------------------------------------------------

def logic_imports(mcver, loader=None):
    """The full import block for TridentKillerLogic.java (between package and the class javadoc).

    Common imports are always present; the turret eras add GameProfile / ServerPlayer / EquipmentSlot
    / ItemStack / LivingEntity / HashMap / Map (+ ClientInformation on the direct-ctor turret cells,
    NOT the reflective 1.20.4 cell). The ThrownTrident import uses the package axis. The credit era
    (26 master) omits all turret imports."""
    v = _parse(mcver)
    pkg = projectile_package(mcver, loader)
    lines = []
    lines.append("import com.kishku7.tridentkillers4java.mixin.LivingEntityAccessor;")
    if has_abstractarrow_invoker(mcver):
        lines.append("import com.kishku7.tridentkillers4java.mixin.AbstractArrowInvoker;")
    if uses_turret(mcver):
        lines.append("import com.mojang.authlib.GameProfile;")
    lines.append("import net.minecraft.core.BlockPos;")
    lines.append("import net.minecraft.server.level.ServerLevel;")
    if uses_turret(mcver) and v >= (1, 20, 5):
        # Direct-ctor turret cells need ClientInformation (declared before ServerPlayer, mirroring
        # the old-branch import ordering on 1.21.1).
        lines.append("import net.minecraft.server.level.ClientInformation;")
    if uses_turret(mcver):
        lines.append("import net.minecraft.server.level.ServerPlayer;")
    lines.append("import net.minecraft.world.damagesource.DamageSource;")
    lines.append("import net.minecraft.world.entity.Entity;")
    if uses_turret(mcver):
        lines.append("import net.minecraft.world.entity.EquipmentSlot;")
        lines.append("import net.minecraft.world.entity.LivingEntity;")
    lines.append("import net.minecraft.world.entity.Mob;")
    lines.append("import net.minecraft.world.entity.player.Player;")
    lines.append("import %s.ThrownTrident;" % pkg)
    if uses_turret(mcver):
        lines.append("import net.minecraft.world.item.ItemStack;")
    lines.append("import net.minecraft.world.item.enchantment.EnchantmentHelper;")
    lines.append("import net.minecraft.world.level.Level;")
    lines.append("import net.minecraft.world.level.block.entity.BlockEntity;")
    lines.append("import net.minecraft.world.level.block.piston.PistonMovingBlockEntity;")
    lines.append("import net.minecraft.world.phys.AABB;")
    lines.append("")
    if uses_turret(mcver):
        lines.append("import java.util.HashMap;")
    lines.append("import java.util.List;")
    if uses_turret(mcver):
        lines.append("import java.util.Map;")
    lines.append("import java.util.UUID;")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# NBT -- imports + save method + load method (methods at absolute col-4 indent).
# ---------------------------------------------------------------------------

def nbt_kind(mcver):
    """compound (v<1.21.2) / bridge (1.21.2..1.21.5) / valueio (v>=1.21.6)."""
    v = _parse(mcver)
    if v < (1, 21, 2):
        return "compound"
    if v < (1, 21, 6):
        return "bridge"
    return "valueio"


def nbt_imports(mcver):
    """The NBT-related import lines for ThrownTridentMixin, as a list (order-stable).

    compound: net.minecraft.nbt.CompoundTag
    bridge:   net.minecraft.nbt.CompoundTag + com.kishku7.tridentkillers4java.NbtBridge
    valueio:  net.minecraft.world.level.storage.ValueInput + ValueOutput (NO CompoundTag)"""
    k = nbt_kind(mcver)
    if k == "compound":
        return ["import net.minecraft.nbt.CompoundTag;"]
    if k == "bridge":
        return [
            "import com.kishku7.tridentkillers4java.NbtBridge;",
            "import net.minecraft.nbt.CompoundTag;",
        ]
    return [
        "import net.minecraft.world.level.storage.ValueInput;",
        "import net.minecraft.world.level.storage.ValueOutput;",
    ]


def nbt_save_method(mcver):
    """The entire tk4j$save @Inject method (signature + body), per NBT era, absolute col-4 indent."""
    k = nbt_kind(mcver)
    if k == "compound":
        return (
            '@Inject(method = "addAdditionalSaveData", at = @At("TAIL"))\n'
            "private void tk4j$save(CompoundTag tag, CallbackInfo ci) {\n"
            '    tag.putBoolean("tk4j_identified", this.tk4j$identified);\n'
            "    if (this.tk4j$identified) {\n"
            '        tag.putDouble("tk4j_anchor_x", this.tk4j$anchorX);\n'
            '        tag.putDouble("tk4j_anchor_y", this.tk4j$anchorY);\n'
            '        tag.putDouble("tk4j_anchor_z", this.tk4j$anchorZ);\n'
            "    }\n"
            "    if (this.tk4j$ownerUuid != null) {\n"
            '        tag.putString("tk4j_owner", this.tk4j$ownerUuid.toString());\n'
            "    }\n"
            "}")
    if k == "bridge":
        return (
            '@Inject(method = "addAdditionalSaveData", at = @At("TAIL"))\n'
            "private void tk4j$save(CompoundTag tag, CallbackInfo ci) {\n"
            '    NbtBridge.putString(tag, "tk4j_identified", this.tk4j$identified ? "1" : "0");\n'
            "    if (this.tk4j$identified) {\n"
            '        NbtBridge.putString(tag, "tk4j_anchor",\n'
            '                this.tk4j$anchorX + ";" + this.tk4j$anchorY + ";" + this.tk4j$anchorZ);\n'
            "    }\n"
            "    if (this.tk4j$ownerUuid != null) {\n"
            '        NbtBridge.putString(tag, "tk4j_owner", this.tk4j$ownerUuid.toString());\n'
            "    }\n"
            "}")
    return (
        '@Inject(method = "addAdditionalSaveData", at = @At("TAIL"))\n'
        "private void tk4j$save(ValueOutput output, CallbackInfo ci) {\n"
        '    output.putBoolean("tk4j_identified", this.tk4j$identified);\n'
        "    if (this.tk4j$identified) {\n"
        '        output.putDouble("tk4j_anchor_x", this.tk4j$anchorX);\n'
        '        output.putDouble("tk4j_anchor_y", this.tk4j$anchorY);\n'
        '        output.putDouble("tk4j_anchor_z", this.tk4j$anchorZ);\n'
        "    }\n"
        "    if (this.tk4j$ownerUuid != null) {\n"
        '        output.putString("tk4j_owner", this.tk4j$ownerUuid.toString());\n'
        "    }\n"
        "}")


def nbt_load_method(mcver):
    """The entire tk4j$load @Inject method (signature + body), per NBT era, absolute col-4 indent."""
    k = nbt_kind(mcver)
    if k == "compound":
        return (
            '@Inject(method = "readAdditionalSaveData", at = @At("TAIL"))\n'
            "private void tk4j$load(CompoundTag tag, CallbackInfo ci) {\n"
            '    this.tk4j$identified = tag.getBoolean("tk4j_identified");\n'
            "    if (this.tk4j$identified) {\n"
            '        this.tk4j$anchorX = tag.contains("tk4j_anchor_x") ? tag.getDouble("tk4j_anchor_x") : this.getX();\n'
            '        this.tk4j$anchorY = tag.contains("tk4j_anchor_y") ? tag.getDouble("tk4j_anchor_y") : this.getY();\n'
            '        this.tk4j$anchorZ = tag.contains("tk4j_anchor_z") ? tag.getDouble("tk4j_anchor_z") : this.getZ();\n'
            "        this.tk4j$anchorValid = true;\n"
            "    }\n"
            '    String ownerString = tag.getString("tk4j_owner");\n'
            "    if (!ownerString.isEmpty()) {\n"
            "        try {\n"
            "            this.tk4j$ownerUuid = UUID.fromString(ownerString);\n"
            "        } catch (IllegalArgumentException ignored) {\n"
            "            this.tk4j$ownerUuid = null;\n"
            "        }\n"
            "    }\n"
            "}")
    if k == "bridge":
        return (
            '@Inject(method = "readAdditionalSaveData", at = @At("TAIL"))\n'
            "private void tk4j$load(CompoundTag tag, CallbackInfo ci) {\n"
            '    this.tk4j$identified = "1".equals(NbtBridge.getString(tag, "tk4j_identified"));\n'
            "    if (this.tk4j$identified) {\n"
            "        this.tk4j$anchorX = this.getX();\n"
            "        this.tk4j$anchorY = this.getY();\n"
            "        this.tk4j$anchorZ = this.getZ();\n"
            '        String anchor = NbtBridge.getString(tag, "tk4j_anchor");\n'
            '        String[] parts = anchor.split(";");\n'
            "        if (parts.length == 3) {\n"
            "            try {\n"
            "                this.tk4j$anchorX = Double.parseDouble(parts[0]);\n"
            "                this.tk4j$anchorY = Double.parseDouble(parts[1]);\n"
            "                this.tk4j$anchorZ = Double.parseDouble(parts[2]);\n"
            "            } catch (NumberFormatException ignored) {\n"
            "            }\n"
            "        }\n"
            "        this.tk4j$anchorValid = true;\n"
            "    }\n"
            '    String ownerString = NbtBridge.getString(tag, "tk4j_owner");\n'
            "    if (!ownerString.isEmpty()) {\n"
            "        try {\n"
            "            this.tk4j$ownerUuid = UUID.fromString(ownerString);\n"
            "        } catch (IllegalArgumentException ignored) {\n"
            "            this.tk4j$ownerUuid = null;\n"
            "        }\n"
            "    }\n"
            "}")
    return (
        '@Inject(method = "readAdditionalSaveData", at = @At("TAIL"))\n'
        "private void tk4j$load(ValueInput input, CallbackInfo ci) {\n"
        '    this.tk4j$identified = input.getBooleanOr("tk4j_identified", false);\n'
        "    if (this.tk4j$identified) {\n"
        '        this.tk4j$anchorX = input.getDoubleOr("tk4j_anchor_x", this.getX());\n'
        '        this.tk4j$anchorY = input.getDoubleOr("tk4j_anchor_y", this.getY());\n'
        '        this.tk4j$anchorZ = input.getDoubleOr("tk4j_anchor_z", this.getZ());\n'
        "        this.tk4j$anchorValid = true;\n"
        "    }\n"
        '    String ownerString = input.getStringOr("tk4j_owner", "");\n'
        "    if (!ownerString.isEmpty()) {\n"
        "        try {\n"
        "            this.tk4j$ownerUuid = UUID.fromString(ownerString);\n"
        "        } catch (IllegalArgumentException ignored) {\n"
        "            this.tk4j$ownerUuid = null;\n"
        "        }\n"
        "    }\n"
        "}")


# ---------------------------------------------------------------------------
# mixin imports (column-0).
# ---------------------------------------------------------------------------

def mixin_super_ctor(mcver, loader=None):
    """The ThrownTridentMixin super(...) constructor call. AbstractArrow's (EntityType, Level)
    2-arg ctor exists on every version EXCEPT 1.20.2 - 1.20.4, where an ItemStack param was
    added (AbstractArrow(EntityType, Level, ItemStack)); a cell compiling against that era must
    pass a third 'null' so the mixin's synthetic super-call resolves. Like the package axis, the
    deciding factor is the COMPILE classpath: NeoForge/Forge 1.20.4 compiles against true 1.20.4
    (needs the 3-arg), but the Fabric 1.20.4 cell compiles against its floor 1.20.1 (2-arg only;
    a 3-arg null is AMBIGUOUS there vs (EntityType, LivingEntity, Level) -> Fabric must stay 2-arg).
    The mixin is never instantiated at runtime, so the null is inert -- it only needs to COMPILE."""
    v = _parse(mcver)
    if (1, 20, 2) <= v < (1, 20, 5) and loader != "Fabric":
        return "super(entityType, level, null);"
    return "super(entityType, level);"


def mixin_imports(mcver, loader=None):
    """The full import block for ThrownTridentMixin.java. The AbstractArrow / ThrownTrident imports
    use the package axis; the NBT imports vary by era. Everything else is invariant."""
    pkg = projectile_package(mcver, loader)
    lines = []
    lines.append("import com.kishku7.tridentkillers4java.TridentKillerLogic;")
    lines.append("import com.kishku7.tridentkillers4java.TridentKillers;")
    for imp in nbt_imports(mcver):
        # NbtBridge is a mod class -> group with the mod imports; CompoundTag/storage go in the
        # net.minecraft block below.
        if imp.startswith("import com.kishku7"):
            lines.append(imp)
    lines.append("import net.minecraft.world.entity.Entity;")
    lines.append("import net.minecraft.world.entity.EntityType;")
    lines.append("import %s.AbstractArrow;" % pkg)
    lines.append("import %s.ThrownTrident;" % pkg)
    lines.append("import net.minecraft.world.level.Level;")
    for imp in nbt_imports(mcver):
        if imp.startswith("import net.minecraft"):
            lines.append(imp)
    lines.append("import net.minecraft.world.phys.Vec3;")
    lines.append("import org.spongepowered.asm.mixin.Mixin;")
    lines.append("import org.spongepowered.asm.mixin.Unique;")
    lines.append("import org.spongepowered.asm.mixin.injection.At;")
    lines.append("import org.spongepowered.asm.mixin.injection.Inject;")
    lines.append("import org.spongepowered.asm.mixin.injection.Redirect;")
    lines.append("import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;")
    lines.append("")
    lines.append("import java.util.UUID;")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

_TEST_VERSIONS = ["1.20.4", "1.20.6", "1.21.1", "1.21.5", "1.21.8", "1.21.11", "26", "26.3-snapshot-2"]


def main():
    print("TK4J compat.py era matrix")
    print("=" * 90)
    hdr = ("mcver", "26?", "pickup", "hurt", "inGround", "nbt", "turret", "aaInv", "projAcc", "nbtBr")
    print("%-16s %-4s %-9s %-14s %-11s %-9s %-7s %-6s %-8s %-6s" % hdr)
    for v in _TEST_VERSIONS:
        row = (
            v, str(is_26(v)),
            "weapon" if "getWeaponItem" in pickup_stack_expr(v) else "invoker",
            "hurtOrSim" if "hurtOrSimulate" in hurt_call(v) else "hurt",
            "method" if "isInGround" in inground_get(v) else "field",
            nbt_kind(v),
            str(uses_turret(v)),
            str(has_abstractarrow_invoker(v)),
            str(has_projectile_accessor(v)),
            str(has_nbt_bridge(v)),
        )
        print("%-16s %-4s %-9s %-14s %-11s %-9s %-7s %-6s %-8s %-6s" % row)
    print("=" * 90)
    return 0


if __name__ == "__main__":
    sys.exit(main())
