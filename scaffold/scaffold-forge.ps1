param([Parameter(Mandatory)][string]$Family,
      [Parameter(Mandatory)][string]$Branch,
      [Parameter(Mandatory)][string]$ForgeVer,   # e.g. 1.20.6-50.2.8
      [Parameter(Mandatory)][string]$McVer,      # mappings version, e.g. 1.20.6
      [Parameter(Mandatory)][string]$McRange,
      [Parameter(Mandatory)][string]$LoaderRange)
# Scaffold a TK4J modern-Forge project (pattern proven by tk4j-forge-1.21.1).
$ErrorActionPreference = "Stop"
$mods  = "<WORKSPACE>\Minecraft\mods"
$repo  = "$mods\trident-killers-4-java"
$pilot = "$mods\tk4j-forge-pilot"
$p     = "$mods\tk4j-forge-$Family"

New-Item -ItemType Directory -Force -Path "$p\src\main\resources\META-INF","$p\gradle\wrapper" | Out-Null
Copy-Item "$pilot\gradlew","$pilot\gradlew.bat" $p -Force
Copy-Item "$pilot\gradle\wrapper\*" "$p\gradle\wrapper\" -Force
Copy-Item "$pilot\.gitignore" $p -Force -ErrorAction SilentlyContinue

Push-Location $repo
cmd /c "git archive $Branch src/main/java src/main/resources/trident_killers_4_java.mixins.json > `"$env:TEMP\tk4j-src.tar`""
Pop-Location
tar -xf "$env:TEMP\tk4j-src.tar" -C $p
Remove-Item "$env:TEMP\tk4j-src.tar"

# 1.21.11: mojmap moved AbstractArrow/ThrownTrident to ...projectile.arrow (imports AND descriptors)
if ($Family -eq "1.21.11") {
    $enc = New-Object System.Text.UTF8Encoding $false
    foreach ($f in Get-ChildItem "$p\src" -Recurse -Filter *.java) {
        $c = [System.IO.File]::ReadAllText($f.FullName)
        $n = $c.Replace("net.minecraft.world.entity.projectile.AbstractArrow","net.minecraft.world.entity.projectile.arrow.AbstractArrow")
        $n = $n.Replace("net.minecraft.world.entity.projectile.ThrownTrident","net.minecraft.world.entity.projectile.arrow.ThrownTrident")
        $n = $n.Replace("net/minecraft/world/entity/projectile/ThrownTrident","net/minecraft/world/entity/projectile/arrow/ThrownTrident")
        $n = $n.Replace("net/minecraft/world/entity/projectile/AbstractArrow","net/minecraft/world/entity/projectile/arrow/AbstractArrow")
        if ($n -ne $c) { [System.IO.File]::WriteAllText($f.FullName, $n, $enc) }
    }
}

@"
package com.kishku7.tridentkillers4java;

import net.minecraftforge.fml.common.Mod;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Trident Killers 4 Java - Forge entrypoint. All behavior lives in mixins;
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
    id 'net.minecraftforge.gradle' version '[6.0,6.2)'
    id 'org.spongepowered.mixin' version '0.7.+'
}

version = '1.2+$Family-forge'
group = 'com.kishku7'
base { archivesName = 'trident-killers-4-java' }

java.toolchain.languageVersion = JavaLanguageVersion.of(21)

minecraft {
    mappings channel: 'official', version: '$McVer'
    copyIdeResources = true
}

mixin {
    add sourceSets.main, 'trident_killers_4_java.refmap.json'
    config 'trident_killers_4_java.mixins.json'
}

dependencies {
    minecraft 'net.minecraftforge:forge:$ForgeVer'
    annotationProcessor 'org.spongepowered:mixin:0.8.5:processor'
}

tasks.withType(JavaCompile).configureEach {
    options.encoding = 'UTF-8'
}

// Forge 1.20.6+ runs mojmap at runtime; FG6 skips reobf so the mixin plugin's
// manifest wiring does nothing - the MixinConfigs attribute must be explicit.
jar {
    manifest {
        attributes 'MixinConfigs': 'trident_killers_4_java.mixins.json'
    }
}
"@ | Out-File "$p\build.gradle" -Encoding ascii

@"
pluginManagement {
    repositories {
        gradlePluginPortal()
        maven { url = 'https://maven.minecraftforge.net/' }
        maven { url = 'https://repo.spongepowered.org/repository/maven-public/' }
    }
}
plugins {
    id 'org.gradle.toolchains.foojay-resolver-convention' version '0.8.0'
}
rootProject.name = 'tk4j-forge-$Family'
"@ | Out-File "$p\settings.gradle" -Encoding ascii

@"
org.gradle.jvmargs=-Xmx3G
org.gradle.daemon=false
org.gradle.java.home=C:/Program Files/Eclipse Adoptium/jdk-21.0.9.10-hotspot
"@ | Out-File "$p\gradle.properties" -Encoding ascii

@"
modLoader="javafml"
loaderVersion="$LoaderRange"
license="All Rights Reserved"
issueTrackerURL="https://github.com/Kishku7/trident-killers-4-java/issues"

[[mods]]
modId="trident_killers_4_java"
version="`${file.jarVersion}"
displayName="Trident Killers 4 Java"
authors="Kishku7"
description='''Brings the Bedrock-Edition trident-killer capability to Java Edition. Server-side only.'''

[[dependencies.trident_killers_4_java]]
    modId="forge"
    mandatory=true
    versionRange="$LoaderRange"
    ordering="NONE"
    side="SERVER"

[[dependencies.trident_killers_4_java]]
    modId="minecraft"
    mandatory=true
    versionRange="$McRange"
    ordering="NONE"
    side="SERVER"
"@ | Out-File "$p\src\main\resources\META-INF\mods.toml" -Encoding ascii

Write-Host "scaffolded $p"
