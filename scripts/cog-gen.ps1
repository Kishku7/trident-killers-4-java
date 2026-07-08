<#
.SYNOPSIS
  Trident Killers 4 Java Cog code-generation driver for one pre-26 cell.

.DESCRIPTION
  Materialises a per-cell, per-MC-version copy of the shared_minecraft source (the 26 master)
  under <Cell>/gen/, with all version drift resolved by Cog (direct-compile, driven by
  _codegen/compat.py). Steps:

    1. Wipe + recreate <Cell>/gen/ (it is a build artifact, never committed).
    2. Copy shared_minecraft/src/main/java + resources -> <Cell>/gen/ verbatim.
    3. Overwrite the drifting files with the Cog-instrumented copies from _codegen/cog_sources/.
    4. Add the presence-gated shims for this MC version:
         - mixin/AbstractArrowInvoker : 1.20.x only (has_abstractarrow_invoker)
         - mixin/ProjectileAccessor   : v < 1.21.6   (has_projectile_accessor)
         - NbtBridge (root pkg)        : 1.21.2..1.21.5 bridge era (has_nbt_bridge)
    5. Run `cog -r -D mcver=<v>` over the Cog files (compat.py on sys.path).
    6. Regenerate <Cell>/gen/src/main/resources/trident_killers_4_java.mixins.json's mixins[] +
       compatibilityLevel to match the mixin/ files actually present for this version.

  The cell's build.gradle srcDirs <Cell>/gen/src/main/{java,resources} (NOT shared_minecraft
  directly), so it compiles the post-Cog output. 26 cells do NOT run cog-gen (they srcDir
  shared_minecraft directly).

.PARAMETER Cell
  Path to the cell dir (e.g. Fabric/1.21.8), relative to the repo root or absolute.

.PARAMETER McVer
  The MC version key (e.g. 1.21.8, 1.21.1, 1.20.4). Drives compat.py era selection.

.PARAMETER Loader
  Loader for this cell. Only Forge changes behaviour: classic-SRG Forge (the ancient 1.20.1/
  1.20.4 line) needs a "refmap" key in trident_killers_4_java.mixins.json; every other
  loader/version omits it. Auto-detected from the cell path when not given.

.EXAMPLE
  ./cog-gen.ps1 -Cell Fabric/1.21.8 -McVer 1.21.8
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Cell,
    [Parameter(Mandatory = $true)][string]$McVer,
    [Parameter(Mandatory = $false)][ValidateSet('Fabric','NeoForge','Forge')][string]$Loader
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent   # cog-gen.ps1 lives in scripts/; repo root is one up
$codegen  = Join-Path $repoRoot '_codegen'
$cogSrc   = Join-Path $codegen 'cog_sources'

# Resolve the cell path (allow relative-to-repo).
if ([System.IO.Path]::IsPathRooted($Cell)) {
    $cellPath = $Cell
} else {
    $cellPath = Join-Path $repoRoot $Cell
}
if (-not (Test-Path $cellPath)) { throw "Cell not found: $cellPath" }

# Resolve the loader (default: infer from the cell path, e.g. "Forge/1.21.1" -> Forge).
if (-not $Loader) {
    $leadSeg = ($Cell -replace '\\', '/').TrimStart('/').Split('/')[0]
    if ($leadSeg -in @('Fabric','NeoForge','Forge')) { $Loader = $leadSeg } else { $Loader = 'Fabric' }
}

$sharedJava = Join-Path $repoRoot 'shared_minecraft/src/main/java'
$sharedRes  = Join-Path $repoRoot 'shared_minecraft/src/main/resources'
if (-not (Test-Path $sharedJava)) { throw "shared_minecraft java not found: $sharedJava" }

$genDir     = Join-Path $cellPath 'gen'
$genJava    = Join-Path $genDir 'src/main/java'
$genRes     = Join-Path $genDir 'src/main/resources'
$mixinPkg   = 'com/kishku7/tridentkillers4java/mixin'
$rootPkg    = 'com/kishku7/tridentkillers4java'

Write-Host "[cog-gen] cell=$Cell mcver=$McVer loader=$Loader"

# --- Step 1: clean gen/ ---
if (Test-Path $genDir) { Remove-Item -Recurse -Force $genDir }
New-Item -ItemType Directory -Force -Path $genJava | Out-Null
New-Item -ItemType Directory -Force -Path $genRes  | Out-Null

# --- Step 2: copy shared_minecraft java + resources verbatim ---
Copy-Item -Recurse -Force (Join-Path $sharedJava '*') $genJava
# pack.mcmeta handling by version line:
#   pre-26 cells own their own per-version pack.mcmeta (cell src/main/resources) -> SKIP the shared
#     one here (the shared copy is the 26 range-form; copying it would duplicate/conflict).
#   26 cells do NOT own a pack.mcmeta (they used to srcDir shared_minecraft directly) -> COPY the
#     shared range-form template into gen/ so it lands in the compiled resources; the 26 cell's
#     processResources still expands ${packFormat}.
Push-Location $codegen
try { $is26 = (& python -c "import compat,sys; sys.stdout.write('1' if compat.is_26('$McVer') else '0')") } finally { Pop-Location }
if (Test-Path $sharedRes) {
    Get-ChildItem -Force $sharedRes | Where-Object { $is26 -eq '1' -or $_.Name -ne 'pack.mcmeta' } | ForEach-Object {
        Copy-Item -Recurse -Force $_.FullName $genRes
    }
}

# --- Step 3: overwrite drifting files with the Cog-instrumented copies ---
# Each entry: cog_source path (relative to _codegen/cog_sources) => destination path RELATIVE to gen java root.
$driftMap = [ordered]@{
    'mixin/ThrownTridentMixin.java' = 'com/kishku7/tridentkillers4java/mixin/ThrownTridentMixin.java'
    'TridentKillerLogic.java'       = 'com/kishku7/tridentkillers4java/TridentKillerLogic.java'
}
foreach ($name in $driftMap.Keys) {
    $src = Join-Path $cogSrc $name
    $dst = Join-Path $genJava $driftMap[$name]
    if (-not (Test-Path $src)) { throw "cog_source missing: $src" }
    Copy-Item -Force $src $dst
}

# --- Step 4: presence-gated shims (query compat.py so the rule lives in ONE place) ---
Push-Location $codegen
try {
    $hasAbstractArrow = (& python -c "import compat,sys; sys.stdout.write('1' if compat.has_abstractarrow_invoker('$McVer') else '0')")
    $hasProjAccessor  = (& python -c "import compat,sys; sys.stdout.write('1' if compat.has_projectile_accessor('$McVer') else '0')")
    $hasNbtBridge     = (& python -c "import compat,sys; sys.stdout.write('1' if compat.has_nbt_bridge('$McVer') else '0')")
    $compatLevelBase  = (& python -c "import compat,sys; sys.stdout.write(compat.compat_level('$McVer'))")
    $forgeNeedsRefmap = (& python -c "import compat,sys; sys.stdout.write('1' if compat.forge_needs_refmap('$McVer') else '0')")
} finally {
    Pop-Location
}

# Classic Forge < 1.21.2 (Forge 51.x bundles Mixin 0.8.5 which rejects JAVA_21) also forces JAVA_17.
Push-Location $codegen
try {
    $forgeOldMixin = if ($Loader -eq 'Forge') { 'True' } else { 'False' }
    $compatLevel   = (& python -c "import compat,sys; v=compat._parse('$McVer'); base='$compatLevelBase'; sys.stdout.write('JAVA_17' if (base=='JAVA_17' or ($forgeOldMixin and v[:3]<(1,21,2))) else base)")
} finally {
    Pop-Location
}

# mixin/AbstractArrowInvoker (1.20.x only)
$aaDst = Join-Path $genJava (Join-Path $mixinPkg 'AbstractArrowInvoker.java')
if ($hasAbstractArrow -eq '1') {
    Copy-Item -Force (Join-Path $cogSrc 'mixin/AbstractArrowInvoker.java') $aaDst
    Write-Host "[cog-gen] + AbstractArrowInvoker (present on $McVer)"
} else {
    if (Test-Path $aaDst) { Remove-Item -Force $aaDst }
    Write-Host "[cog-gen] - AbstractArrowInvoker (absent on $McVer)"
}

# mixin/ProjectileAccessor (v < 1.21.6)
$paDst = Join-Path $genJava (Join-Path $mixinPkg 'ProjectileAccessor.java')
if ($hasProjAccessor -eq '1') {
    Copy-Item -Force (Join-Path $cogSrc 'mixin/ProjectileAccessor.java') $paDst
    Write-Host "[cog-gen] + ProjectileAccessor (present on $McVer)"
} else {
    if (Test-Path $paDst) { Remove-Item -Force $paDst }
    Write-Host "[cog-gen] - ProjectileAccessor (absent on $McVer)"
}

# NbtBridge (root pkg, bridge era only 1.21.2..1.21.5) -- a plain helper class, NOT a mixin.
$nbDst = Join-Path $genJava (Join-Path $rootPkg 'NbtBridge.java')
if ($hasNbtBridge -eq '1') {
    Copy-Item -Force (Join-Path $cogSrc 'NbtBridge.java') $nbDst
    Write-Host "[cog-gen] + NbtBridge (present on $McVer)"
} else {
    if (Test-Path $nbDst) { Remove-Item -Force $nbDst }
    Write-Host "[cog-gen] - NbtBridge (absent on $McVer)"
}

# --- Step 5: run Cog over the drift files (compat.py on PYTHONPATH via -D) ---
$cogTargets = @()
foreach ($name in $driftMap.Keys) {
    $cogTargets += (Join-Path $genJava $driftMap[$name])
}
Push-Location $codegen
try {
    $env:PYTHONPATH = $codegen
    & cog -r -D "mcver=$McVer" -D "loader=$Loader" @cogTargets
    if ($LASTEXITCODE -ne 0) { throw "cog failed (exit $LASTEXITCODE)" }
} finally {
    Pop-Location
}

# --- Step 6: rebuild trident_killers_4_java.mixins.json (in gen/, the compiled resources) ---
$mixinsJsonPath = Join-Path $genRes 'trident_killers_4_java.mixins.json'

# Enumerate mixin classes actually present in gen/'s mixin dir (TK4J is server-only: no client[] block).
$presentMixins = Get-ChildItem -File (Join-Path $genJava $mixinPkg) |
    Where-Object { $_.Extension -eq '.java' } |
    ForEach-Object { $_.BaseName } |
    Sort-Object

$mixinsArray = ($presentMixins | ForEach-Object { "    `"$_`"" }) -join ",`n"

# Classic-SRG Forge (ancient 1.20.1/1.20.4) needs a refmap key; every other loader/version omits it.
$refmapLine = ''
if ($Loader -eq 'Forge' -and $forgeNeedsRefmap -eq '1') {
    $refmapLine = "  `"refmap`": `"trident_killers_4_java.refmap.json`",`n"
    Write-Host "[cog-gen] + refmap key (classic-SRG Forge on $McVer)"
} elseif ($Loader -eq 'Forge') {
    Write-Host "[cog-gen] - refmap key (mojmap-native Forge on $McVer)"
}

$jsonText = @"
{
  "required": true,
  "minVersion": "0.8",
  "package": "com.kishku7.tridentkillers4java.mixin",
  "compatibilityLevel": "$compatLevel",
$($refmapLine)  "mixins": [
$mixinsArray
  ],
  "injectors": {
    "defaultRequire": 1
  }
}
"@
# ASCII, LF line endings.
$jsonText = $jsonText -replace "`r`n", "`n"
[System.IO.File]::WriteAllText($mixinsJsonPath, $jsonText, (New-Object System.Text.UTF8Encoding($false)))

Write-Host "[cog-gen] wrote $($presentMixins.Count) mixins -> trident_killers_4_java.mixins.json (compat=$compatLevel)"
Write-Host "[cog-gen] done: $genJava"
