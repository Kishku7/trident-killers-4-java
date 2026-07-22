# build-fabric.ps1 -- TK4J Fabric builds: the unified 26 matrix (Fabric/26) + pre-26 cog cells (Fabric/<v>).
# Every cell is now cog-driven (cog_sources is the SOLE source of the drift files): each build runs
# scripts/cog-gen.ps1 to materialise gen/, then that cell's gradlew clean build, then copies the jar
# to dist/. Usage: pwsh scripts/build-fabric.ps1 [cell ...]   (none = all; e.g. 26.3 ; 1.21.8 26.1)
param([string[]]$Only)
$ErrorActionPreference = "Stop"
$repo   = Split-Path $PSScriptRoot -Parent
$loader = "Fabric"
$root   = Join-Path $repo $loader
$dist   = Join-Path $repo "dist"
$cogGen = Join-Path $PSScriptRoot "cog-gen.ps1"
New-Item -ItemType Directory -Force -Path $dist | Out-Null

# 26 matrix. pack_format per Memory/knowledge/pack-formats.md (26.1=84, 26.2=88, 26.3=92).
# 26.3 pinned to snapshot-4 EXCLUSIVELY: dep uses the Fabric-normalized alpha form (26.3-alpha.4),
# not the raw snapshot id (loader rejects the raw id). snap-4 = alpha.4, pack_format 92. TK4J has NO fabric-api runtime dep (compileOnly only).
$m26 = [ordered]@{
  "26.1" = @{ mc="26.1.2";          api="0.145.3+26.1.1"; loader="0.18.6"; lo="26.1-";        hi="26.2";          pf="84" }
  "26.2" = @{ mc="26.2";            api="0.152.1+26.2";   loader="0.19.3"; lo="26.2-";        hi="26.3";          pf="88" }
  "26.3" = @{ mc="26.3-snapshot-5"; api="0.155.3+26.3";   loader="0.19.3"; lo="26.3-alpha.5"; hi="26.3-alpha.6";  pf="93" }
}
# Auto-discover pre-26 cells from the dirs (everything under Fabric/ except the 26 matrix cell).
$preCells = @(Get-ChildItem $root -Directory -EA SilentlyContinue | Where-Object { $_.Name -ne "26" } | Select-Object -ExpandProperty Name | Sort-Object)
$targets = if ($Only) { $Only } else { $preCells + @($m26.Keys) }

function Copy-Jar($cell, $label) {
  $jar = Get-ChildItem (Join-Path $cell "build\libs") -Filter "trident-killers-4-java-*.jar" |
         Where-Object { $_.Name -notmatch 'sources|dev|slim' } | Sort-Object LastWriteTime | Select-Object -Last 1
  if (-not $jar) { throw "No built jar for Fabric/$label" }
  Copy-Item $jar.FullName (Join-Path $dist $jar.Name) -Force
  Write-Host "  -> dist $($jar.Name)"
}

function Build-26($v) {
  $cell = Join-Path $root "26"; $m = $m26[$v]
  $modver = (Select-String -Path (Join-Path $cell "gradle.properties") -Pattern '^mod_version=(.+)$').Matches[0].Groups[1].Value
  Write-Host "=== TK4J Fabric/26 -> $v  (mc=$($m.mc)  pf=$($m.pf)) ==="
  # 26.x cog source is uniform across all 26.x; cog-gen once with the target version is fine.
  & $cogGen -Cell "$loader/26" -McVer $m.mc -Loader $loader
  if ($LASTEXITCODE -ne 0) { throw "cog-gen FAILED for Fabric/26 -> $v" }
  Push-Location $cell
  & ".\gradlew.bat" clean build "-Pminecraft_version=$($m.mc)" "-Pfabric_api_version=$($m.api)" "-Ploader_version=$($m.loader)" "-Pmc_lower=$($m.lo)" "-Pmc_upper=$($m.hi)" "-Ppack_format=$($m.pf)" --no-daemon
  $rc = $LASTEXITCODE; Pop-Location
  if ($rc -ne 0) { throw "Fabric build FAILED for $v" }
  Copy-Jar $cell $v
}

function Build-PreCell($v) {
  $cell = Join-Path $root $v
  if (-not (Test-Path $cell)) { throw "Unknown Fabric cell '$v' (have: $($preCells -join ', ') ; 26 line: $($m26.Keys -join ', '))" }
  Write-Host "=== TK4J Fabric/$v  (pre-26 cog cell) ==="
  & $cogGen -Cell "$loader/$v" -McVer $v -Loader $loader
  if ($LASTEXITCODE -ne 0) { throw "cog-gen FAILED for Fabric/$v" }
  Push-Location $cell
  & ".\gradlew.bat" clean build --no-daemon
  $rc = $LASTEXITCODE; Pop-Location
  if ($rc -ne 0) { throw "Fabric build FAILED for $v" }
  Copy-Jar $cell $v
}

foreach ($t in $targets) {
  if ($m26.Contains($t)) { Build-26 $t } else { Build-PreCell $t }
}
Write-Host "Fabric builds complete. dist: $dist"
