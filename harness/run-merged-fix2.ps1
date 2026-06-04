Set-Location '<WORKSPACE>\Minecraft\tk4j-compat-tests'
$fixed = '<WORKSPACE>\Minecraft\mods\tk4j-merged\fixed2'
$log = 'merged-fix2.log'
"=== GATED DUAL-FAMILY VERIFY $(Get-Date) ===" | Out-File $log -Encoding utf8
$results = @()
function Run-Test($name, $cmd) {
    "--- $name ---" | Out-File $script:log -Append -Encoding utf8
    $out = Invoke-Expression "$cmd 2>&1" | Out-String
    $out | Out-File $script:log -Append -Encoding utf8
    $pass = $out -match 'ALL PASS'
    if (-not $pass) {
        "RETRY (warm) $name" | Out-File $script:log -Append -Encoding utf8
        $out2 = Invoke-Expression "$cmd 2>&1" | Out-String
        $out2 | Out-File $script:log -Append -Encoding utf8
        $pass = $out2 -match 'ALL PASS'
    }
    $script:results += "{0}: {1}" -f $name, $(if ($pass) {'PASS'} else {'FAIL'})
    $script:results | Out-File 'merged-fix2.progress' -Encoding utf8
}
$plan = @(
  @{ f='1.20.6'; forge='50.2.8';  neo='20.6.139' },
  @{ f='1.21.1'; forge='52.1.14'; neo='21.1.233' },
  @{ f='1.21.5'; forge='55.1.10'; neo='21.5.97'  },
  @{ f='1.21.8'; forge='58.1.18'; neo='21.8.53'  }
)
foreach ($p in $plan) {
  $f = $p.f
  $jar = "$fixed\trident-killers-4-java-1.2+$f-merged.jar"
  Run-Test "GATED-forge-$f"    "python tk4j_forge_test.py $f $($p.forge) `"$jar`""
  Run-Test "GATED-neoforge-$f" "python tk4j_neoforge_test.py $f $($p.neo) `"$jar`""
}
Run-Test "GATED-fabric-1.20.6" "python tk4j_compat_test.py 1.20.6 `"$fixed\trident-killers-4-java-1.2+1.20.6-merged.jar`""
"=== SUMMARY ===" | Out-File $log -Append -Encoding utf8
$results | Out-File $log -Append -Encoding utf8
$results | Out-File 'merged-fix2.done' -Encoding utf8
