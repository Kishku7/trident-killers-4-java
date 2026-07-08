package com.kishku7.tridentkillers4java;

import net.fabricmc.api.ModInitializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Trident Killers 4 Java - server-side mod entrypoint.
 *
 * Brings the Bedrock-Edition trident-killer capability to Java Edition.
 * Clean-room implementation: see CLEANROOM.md and FUNCTIONAL_SPEC.md in the
 * repository root. All behavior is implemented from the functional spec only.
 *
 * Server-side only: this mod must never require a client mod (FR-13).
 */
public class TridentKillers implements ModInitializer {

    public static final String MOD_ID = "trident_killers_4_java";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitialize() {
        LOGGER.info("Trident Killers 4 Java initialized (server-side).");
    }
}
