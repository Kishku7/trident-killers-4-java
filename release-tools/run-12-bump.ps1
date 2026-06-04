$ErrorActionPreference = "Continue"
$repo  = "<WORKSPACE>\Minecraft\mods\trident-killers-4-java"
$tests = "<WORKSPACE>\Minecraft\tk4j-compat-tests"
$stage = "<WORKSPACE>\Minecraft\mods\trident-killers-4-java"
$out   = "<WORKSPACE>\Minecraft\mods\bump-12.log"

"=== 1.2 BUMP DRIVER START $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Add-Content $out

# family -> branch (test version == family name; jars named for newest supported version)
$fams = @(
  @{ f="1.20.4";  br="mc/1.20.4"  },
  @{ f="1.20.6";  br="mc/1.20.6"  },
  @{ f="1.21.1";  br="mc/1.21.1"  },
  @{ f="1.21.5";  br="mc/1.21.5"  },
  @{ f="1.21.8";  br="mc/1.21.8"  },
  @{ f="1.21.11"; br="mc/1.21.11" },
  @{ f="26.1.2";  br="main"       }
)

Set-Location $repo
foreach ($x in $fams) {
    $f = $x.f; $br = $x.br
    "=== FAMILY $f (branch $br) $(Get-Date -Format HH:mm:ss) ===" | Add-Content $out
    git checkout $br 2>&1 | Add-Content $out
    git pull --ff-only 2>&1 | Add-Content $out

    # bump mod_version 1.1+X -> 1.2+X (ASCII file; safe with .NET IO)
    $gp = Join-Path $repo "gradle.properties"
    $txt = [IO.File]::ReadAllText($gp)
    if ($txt -match 'mod_version=1\.2\+') {
        "$f already bumped to 1.2" | Add-Content $out
    } elseif ($txt -match 'mod_version=1\.1\+') {
        $txt = $txt -replace 'mod_version=1\.1\+', 'mod_version=1.2+'
        [IO.File]::WriteAllText($gp, $txt)
        "$f gradle.properties bumped to 1.2" | Add-Content $out
    } else {
        "$f UNEXPECTED mod_version line - SKIP" | Add-Content $out
        git checkout -- gradle.properties
        continue
    }

    # build
    & .\gradlew.bat build 2>&1 | Add-Content $out
    $jar = Join-Path $repo "build\libs\trident-killers-4-java-1.2+$f.jar"
    if (-not (Test-Path $jar)) {
        "$f BUILD FAILED (no jar) - reverting bump" | Add-Content $out
        git checkout -- gradle.properties
        continue
    }
    "$f built: $jar" | Add-Content $out

    # reverify on real Fabric server (sequential; shared RCON 25575)
    & python "$tests\tk4j_compat_test.py" $f $jar *>> $out
    $rc = $LASTEXITCODE
    "--- $f harness exit: $rc ---" | Add-Content $out
    if ($rc -eq 2) {
        "=== RETRY $f (warm) ===" | Add-Content $out
        & python "$tests\tk4j_compat_test.py" $f $jar *>> $out
        $rc = $LASTEXITCODE
        "--- $f retry exit: $rc ---" | Add-Content $out
    }

    if ($rc -eq 0) {
        Copy-Item $jar $stage -Force
        git add gradle.properties
        git commit -m "release: v1.2+$f - multi-loader campaign (Forge/NeoForge/Quilt support); Fabric jar reverified" 2>&1 | Add-Content $out
        "$f PASS - staged + committed (NOT pushed)" | Add-Content $out
    } else {
        git checkout -- gradle.properties
        "$f FAIL - bump reverted, NOT staged" | Add-Content $out
    }
}
"=== 1.2 BUMP DRIVER DONE $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Add-Content $out
