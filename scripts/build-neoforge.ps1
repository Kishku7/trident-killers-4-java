# build-neoforge.ps1 -- TK4J NeoForge builds into dist/.
# Covers BOTH the pre-26 per-version cells (NeoForge/<v>, cog-gen + gradlew) AND the unified 26 line
# (NeoForge/26, -P matrix + pack_format range-form). MC 26.3 has NO NeoForge upstream yet, so the 26
# line is 26.1/26.2 only. cog_sources is the SOLE source of the drift files -- every cell (incl. the
# 26 cell, now cog-driven) runs cog-gen before gradlew. Pre-26 cells auto-discovered. Lives in scripts/.
#
# NeoForge/1.20.1 is a Forge-1.20.1 fork (SRG runtime): cog-gen uses -Loader Forge there so the
# mixins.json gets the classic-SRG refmap key. Every other NeoForge cell uses -Loader NeoForge.
#
# Usage:
#   pwsh scripts/build-neoforge.ps1               # build EVERYTHING (all pre-26 cells + 26.1/26.2)
#   pwsh scripts/build-neoforge.ps1 1.21.8        # build one pre-26 cell
#   pwsh scripts/build-neoforge.ps1 26.2          # build one 26.X target
param([string[]]$Only)
$ErrorActionPreference = "Stop"
$repo   = Split-Path $PSScriptRoot -Parent
$loader = "NeoForge"
$root   = Join-Path $repo $loader
$dist   = Join-Path $repo "dist"
$cogGen = Join-Path $PSScriptRoot "cog-gen.ps1"
New-Item -ItemType Directory -Force -Path $dist | Out-Null

# 26-line matrix (unified NeoForge/26 cell; -P + pack_format). pack_format per Memory/knowledge/pack-formats.md.
$m26 = [ordered]@{
  "26.1" = @{ mc="26.1.2"; nf="26.1.0.15-beta"; nfRange="[26.1.0.0-beta,)"; mcRange="[26.1,26.2)"; pf="84" }
  "26.2" = @{ mc="26.2";   nf="26.2.0.1-beta";  nfRange="[26.2.0-alpha,)"; mcRange="[26.2,26.3)"; pf="88" }
}
# Auto-discover pre-26 cells (everything under NeoForge/ except the 26 matrix cell).
$preCells = @(Get-ChildItem $root -Directory | Where-Object { $_.Name -ne "26" } | Select-Object -ExpandProperty Name | Sort-Object)

if ($Only) {
  $targets = $Only
  foreach ($t in $targets) {
    if (-not $m26.Contains($t) -and $preCells -notcontains $t) {
      throw "Unknown NeoForge target '$t' (pre-26 cells: $($preCells -join ', ') ; 26 line: $($m26.Keys -join ', '))"
    }
  }
} else {
  $targets = @($preCells) + @($m26.Keys)
}

function Copy-Jar($cell, $label) {
  $jar = Get-ChildItem (Join-Path $cell "build\libs") -Filter "trident-killers-4-java-*.jar" |
         Where-Object { $_.Name -notmatch 'sources|dev|slim|noshade' } | Sort-Object LastWriteTime | Select-Object -Last 1
  if (-not $jar) { throw "No built jar for NeoForge/$label" }
  Copy-Item $jar.FullName (Join-Path $dist $jar.Name) -Force
  Write-Host "  -> dist $($jar.Name)"
}

function Build-PreCell($v) {
  $cellPath = Join-Path $root $v
  # NeoForge 1.20.1 is a Forge fork -> cog-gen with -Loader Forge (classic-SRG refmap); else NeoForge.
  $cogLoader = if ($v -eq "1.20.1") { "Forge" } else { "NeoForge" }
  Write-Host "=== TK4J $loader/$v  (pre-26 cog cell, cogLoader=$cogLoader) ==="
  & $cogGen -Cell "$loader/$v" -McVer $v -Loader $cogLoader
  if ($LASTEXITCODE -ne 0) { throw "cog-gen FAILED for $loader/$v" }
  Push-Location $cellPath
  & ".\gradlew.bat" clean build --no-daemon
  $rc = $LASTEXITCODE; Pop-Location
  if ($rc -ne 0) { throw "Build FAILED for $loader/$v" }
  Copy-Jar $cellPath $v
}

function Build-26($v) {
  $cell = Join-Path $root "26"
  $m = $m26[$v]
  Write-Host "=== TK4J $loader/26 -> $v  (mc=$($m.mc)  neoforge=$($m.nf)  pack_format=$($m.pf)) ==="
  # 26.x cog source is uniform across all 26.x; cog-gen once with the target version is fine.
  & $cogGen -Cell "$loader/26" -McVer $m.mc -Loader $loader
  if ($LASTEXITCODE -ne 0) { throw "cog-gen FAILED for $loader/26 -> $v" }
  Push-Location $cell
  & ".\gradlew.bat" clean build "-Pminecraft_version=$($m.mc)" "-Pneo_version=$($m.nf)" "-Pneoforge_range=$($m.nfRange)" "-Pmc_range=$($m.mcRange)" "-Ppack_format=$($m.pf)" --no-daemon
  $rc = $LASTEXITCODE; Pop-Location
  if ($rc -ne 0) { throw "Build FAILED for $v" }
  Copy-Jar $cell $v
}

foreach ($t in $targets) {
  if ($m26.Contains($t)) { Build-26 $t } else { Build-PreCell $t }
}
Write-Host "NeoForge build complete. Jars in $dist"
