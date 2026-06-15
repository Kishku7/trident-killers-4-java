package com.kishku7.tridentkillers4java;

import net.neoforged.fml.common.Mod;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Trident Killers 4 Java - NeoForge entrypoint. All behavior lives in mixins;
 * nothing to initialize. Server-side only (FR-13).
 */
@Mod(TridentKillers.MOD_ID)
public class TridentKillers {

    public static final String MOD_ID = "trident_killers_4_java";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    public TridentKillers() {
    }
}
