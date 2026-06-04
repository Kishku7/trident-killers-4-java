param([Parameter(Mandatory)][string]$Family,
      [Parameter(Mandatory)][string]$Branch,
      [Parameter(Mandatory)][string]$NeoVer,
      [Parameter(Mandatory)][string]$McRange,
      [Parameter(Mandatory)][string]$NeoRange,
      [string]$JavaVer = "21")
# Scaffold a TK4J NeoForge project from a family branch (pattern proven by tk4j-neoforge-pilot).
$ErrorActionPreference = "Stop"
$mods  = "<WORKSPACE>\Minecraft\mods"
$repo  = "$mods\trident-killers-4-java"
$pilot = "$mods\tk4j-forge-pilot"
$p     = "$mods\tk4j-neoforge-$Family"

New-Item -ItemType Directory -Force -Path "$p\src\main\resources\META-INF","$p\gradle\wrapper" | Out-Null
Copy-Item "$pilot\gradlew","$pilot\gradlew.bat" $p -Force
Copy-Item "$pilot\gradle\wrapper\*" "$p\gradle\wrapper\" -Force
Copy-Item "$pilot\.gitignore" $p -Force -ErrorAction SilentlyContinue

# copy java sources + mixins.json from the branch (raw bytes via tar)
Push-Location $repo
cmd /c "git archive $Branch src/main/java src/main/resources/trident_killers_4_java.mixins.json > `"$env:TEMP\tk4j-src.tar`""
Pop-Location
tar -xf "$env:TEMP\tk4j-src.tar" -C $p
Remove-Item "$env:TEMP\tk4j-src.tar"

# NeoForge entrypoint replaces the Fabric one (keeps MOD_ID + LOGGER for the mixin)
@"
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
"@ | Out-File "$p\src\main\java\com\kishku7\tridentkillers4java\TridentKillers.java" -Encoding ascii

@"
plugins {
    id 'eclipse'
    id 'net.neoforged.moddev' version '2.0.141'
}

version = '1.2+$Family-neoforge'
group = 'com.kishku7'
base { archivesName = 'trident-killers-4-java' }

java.toolchain.languageVersion = JavaLanguageVersion.of($JavaVer)

neoForge {
    version = '$NeoVer'
}

tasks.withType(JavaCompile).configureEach {
    options.encoding = 'UTF-8'
}
"@ | Out-File "$p\build.gradle" -Encoding ascii

@"
pluginManagement {
    repositories {
        gradlePluginPortal()
        maven { url = 'https://maven.neoforged.net/releases' }
    }
}
plugins {
    id 'org.gradle.toolchains.foojay-resolver-convention' version '0.8.0'
}
rootProject.name = 'tk4j-neoforge-$Family'
"@ | Out-File "$p\settings.gradle" -Encoding ascii

@"
org.gradle.jvmargs=-Xmx3G
org.gradle.daemon=false
org.gradle.java.home=C:/Program Files/Eclipse Adoptium/jdk-21.0.9.10-hotspot
"@ | Out-File "$p\gradle.properties" -Encoding ascii

@"
modLoader="javafml"
loaderVersion="[1,)"
license="All Rights Reserved"
issueTrackerURL="https://github.com/Kishku7/trident-killers-4-java/issues"

[[mods]]
modId="trident_killers_4_java"
version="`${file.jarVersion}"
displayName="Trident Killers 4 Java"
authors="Kishku7"
description='''Brings the Bedrock-Edition trident-killer capability to Java Edition. Server-side only.'''

[[mixins]]
config="trident_killers_4_java.mixins.json"

[[dependencies.trident_killers_4_java]]
    modId="neoforge"
    type="required"
    versionRange="$NeoRange"
    ordering="NONE"
    side="SERVER"

[[dependencies.trident_killers_4_java]]
    modId="minecraft"
    type="required"
    versionRange="$McRange"
    ordering="NONE"
    side="SERVER"
"@ | Out-File "$p\src\main\resources\META-INF\neoforge.mods.toml" -Encoding ascii

Write-Host "scaffolded $p"
