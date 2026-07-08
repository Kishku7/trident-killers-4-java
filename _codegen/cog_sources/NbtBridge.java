package com.kishku7.tridentkillers4java;

import net.minecraft.nbt.CompoundTag;

import java.lang.reflect.Method;

/**
 * Cross-version CompoundTag access for 1.21.2 - 1.21.5 in one jar.
 *
 * 1.21.5 reworked tag getters (getString(String) -> getStringOr(String, String) /
 * Optional variants). Method NAMES are remapped at runtime, so this bridge finds
 * methods by SHAPE, and the mod persists all of its state as STRINGS because the
 * string get/put signatures are unambiguous in both eras:
 *   write: void (String, String)         -> putString (both eras)
 *   read:  String (String)               -> getString (&lt;= 1.21.4)
 *          String (String, String)       -> getStringOr (1.21.5+)
 */
public final class NbtBridge {

    private static final Method PUT_STRING;
    private static final Method GET_STRING;      // (String) -> String, or null on 1.21.5+
    private static final Method GET_STRING_OR;   // (String, String) -> String, or null pre-1.21.5

    static {
        Method put = null, get = null, getOr = null;
        for (Method m : CompoundTag.class.getMethods()) {
            Class<?>[] p = m.getParameterTypes();
            if (m.getReturnType() == void.class && p.length == 2
                    && p[0] == String.class && p[1] == String.class) {
                put = m;
            } else if (m.getReturnType() == String.class && p.length == 1 && p[0] == String.class) {
                get = m;
            } else if (m.getReturnType() == String.class && p.length == 2
                    && p[0] == String.class && p[1] == String.class) {
                getOr = m;
            }
        }
        PUT_STRING = put;
        GET_STRING = get;
        GET_STRING_OR = getOr;
        if (PUT_STRING == null || (GET_STRING == null && GET_STRING_OR == null)) {
            throw new IllegalStateException("NbtBridge: no compatible CompoundTag string accessors found");
        }
    }

    private NbtBridge() {
    }

    public static void putString(CompoundTag tag, String key, String value) {
        try {
            PUT_STRING.invoke(tag, key, value);
        } catch (ReflectiveOperationException e) {
            throw new IllegalStateException("NbtBridge.putString failed", e);
        }
    }

    /** Returns the stored string or "" when absent. */
    public static String getString(CompoundTag tag, String key) {
        try {
            if (GET_STRING_OR != null) {
                return (String) GET_STRING_OR.invoke(tag, key, "");
            }
            String v = (String) GET_STRING.invoke(tag, key);
            return v == null ? "" : v;
        } catch (ReflectiveOperationException e) {
            throw new IllegalStateException("NbtBridge.getString failed", e);
        }
    }
}
