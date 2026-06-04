$ErrorActionPreference = "Continue"
$tests = "<WORKSPACE>\Minecraft\tk4j-compat-tests"
$mods  = "<WORKSPACE>\Minecraft\mods"
$stage = "<WORKSPACE>\Minecraft\mods\trident-killers-4-java"
$out   = "$tests\neoforge-family-tests.log"

# wait for builds to finish (up to 30 min)
$deadline = (Get-Date).AddMinutes(30)
while ((Get-Date) -lt $deadline) {
    if (Select-String -Path "$mods\neoforge-builds.log" -Pattern "ALL BUILDS DONE" -Quiet) { break }
    Start-Sleep -Seconds 15
}
"builds-done marker seen (or timeout) at $(Get-Date -Format HH:mm:ss)" | Add-Content $out

$fams = @(
  @{ f="1.20.6";  neo="20.6.139"  },
  @{ f="1.21.5";  neo="21.5.97"   },
  @{ f="1.21.8";  neo="21.8.53"   },
  @{ f="1.21.11"; neo="21.11.42"  }
)
foreach ($x in $fams) {
    $f = $x.f; $neo = $x.neo
    $jar = "$mods\tk4j-neoforge-$f\build\libs\trident-killers-4-java-1.2+$f-neoforge.jar"
    if (-not (Test-Path $jar)) { "=== $f SKIP (no jar) ===" | Add-Content $out; continue }
    "=== TEST NEOFORGE $f ($neo) ===" | Add-Content $out
    & python "$tests\tk4j_neoforge_test.py" $f $neo $jar *>> $out
    $rc = $LASTEXITCODE
    "--- exit: $rc ---" | Add-Content $out
    if ($rc -eq 2) {
        # possible cold-start flakiness (proven pitfall) - one warm retry
        "=== RETRY NEOFORGE $f (warm) ===" | Add-Content $out
        & python "$tests\tk4j_neoforge_test.py" $f $neo $jar *>> $out
        $rc = $LASTEXITCODE
        "--- retry exit: $rc ---" | Add-Content $out
    }
    if ($rc -eq 0) {
        Copy-Item $jar $stage -Force
        "staged $f jar" | Add-Content $out
    }
}
"=== NEOFORGE TESTS COMPLETE ===" | Add-Content $out
