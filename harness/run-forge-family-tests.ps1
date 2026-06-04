$ErrorActionPreference = "Continue"
$tests = "<WORKSPACE>\Minecraft\tk4j-compat-tests"
$mods  = "<WORKSPACE>\Minecraft\mods"
$stage = "<WORKSPACE>\Minecraft\mods\trident-killers-4-java"
$out   = "$tests\forge-family-tests.log"

$fams = @(
  @{ f="1.20.6";  forge="50.2.8"  },
  @{ f="1.21.5";  forge="55.1.10" },
  @{ f="1.21.8";  forge="58.1.18" },
  @{ f="1.21.11"; forge="61.1.8"  }
)

# build all, sequentially
foreach ($x in $fams) {
    $f = $x.f; $p = "$mods\tk4j-forge-$f"
    "=== BUILD FORGE $f ===" | Add-Content $out
    Push-Location $p
    & "$p\gradlew.bat" build --no-daemon --console=plain *>> $out
    Pop-Location
    $jar = "$p\build\libs\trident-killers-4-java-1.2+$f-forge.jar"
    if (Test-Path $jar) { "=== $f BUILD OK ===" | Add-Content $out }
    else { "=== $f BUILD FAILED ===" | Add-Content $out }
}

# test all, sequentially (shared RCON)
foreach ($x in $fams) {
    $f = $x.f; $forge = $x.forge
    $jar = "$mods\tk4j-forge-$f\build\libs\trident-killers-4-java-1.2+$f-forge.jar"
    if (-not (Test-Path $jar)) { "=== $f SKIP TEST (no jar) ===" | Add-Content $out; continue }
    "=== TEST FORGE $f ($forge) ===" | Add-Content $out
    & python "$tests\tk4j_forge_test.py" $f $forge $jar *>> $out
    $rc = $LASTEXITCODE
    "--- exit: $rc ---" | Add-Content $out
    if ($rc -eq 2) {
        "=== RETRY FORGE $f (warm) ===" | Add-Content $out
        & python "$tests\tk4j_forge_test.py" $f $forge $jar *>> $out
        $rc = $LASTEXITCODE
        "--- retry exit: $rc ---" | Add-Content $out
    }
    if ($rc -eq 0) {
        Copy-Item $jar $stage -Force
        "staged $f jar" | Add-Content $out
    }
}
"=== FORGE FAMILY RUN COMPLETE ===" | Add-Content $out
