# build-forge.ps1 -- TK4J Forge builds into dist/.
# Forge is pre-26 only (FG6 builds through 1.21.11, except 1.21.9 which is gated/locked out; there is NO 26 Forge cell - FG6 cannot build unobf 26.x), so every
# Forge/<v> cell is cog-gen'd (-Loader Forge) + built. cog_sources is the SOLE source of the drift
# files. Cells are auto-discovered from Forge/. Lives in scripts/ (run from anywhere).
#
# Usage:
#   pwsh scripts/build-forge.ps1               # build every Forge cell
#   pwsh scripts/build-forge.ps1 1.20.1        # build one cell
param([string[]]$Only)
$ErrorActionPreference = "Stop"
$repo   = Split-Path $PSScriptRoot -Parent
$loader = "Forge"
$root   = Join-Path $repo $loader
$dist   = Join-Path $repo "dist"
$cogGen = Join-Path $PSScriptRoot "cog-gen.ps1"
New-Item -ItemType Directory -Force -Path $dist | Out-Null

# Auto-discover pre-26 cells (Forge has no 26 cell; the filter is defensive).
$cells = @(Get-ChildItem $root -Directory | Where-Object { $_.Name -ne "26" } | Select-Object -ExpandProperty Name | Sort-Object)
if ($Only) {
  $targets = $Only
  foreach ($t in $targets) { if ($cells -notcontains $t) { throw "Unknown Forge cell '$t' (have: $($cells -join ', '))" } }
} else {
  $targets = $cells
}

foreach ($v in $targets) {
  $cellPath = Join-Path $root $v
  Write-Host "=== TK4J $loader/$v  (pre-26 cog cell) ==="
  & $cogGen -Cell "$loader/$v" -McVer $v -Loader $loader
  if ($LASTEXITCODE -ne 0) { throw "cog-gen FAILED for $loader/$v" }
  Push-Location $cellPath
  & ".\gradlew.bat" clean build --no-daemon
  $rc = $LASTEXITCODE; Pop-Location
  if ($rc -ne 0) { throw "Build FAILED for $loader/$v" }
  $jar = Get-ChildItem (Join-Path $cellPath "build\libs") -Filter "trident-killers-4-java-*.jar" |
         Where-Object { $_.Name -notmatch 'sources|dev|slim|noshade' } | Sort-Object LastWriteTime | Select-Object -Last 1
  if (-not $jar) { throw "No built jar for $loader/$v" }
  Copy-Item $jar.FullName (Join-Path $dist $jar.Name) -Force
  Write-Host "  -> dist $($jar.Name)"
}
Write-Host "Forge build complete. Jars in $dist"
