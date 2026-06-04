Set-Location '<WORKSPACE>\Minecraft\tk4j-compat-tests'
$work = '<WORKSPACE>\Minecraft\mods\tk4j-merged'
$log = 'merged-sweep.log'
"=== MERGED FAMILY SWEEP $(Get-Date) ===" | Out-File $log -Encoding utf8
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
    $line = "{0}: {1}" -f $name, $(if ($pass) {'PASS'} else {'FAIL'})
    $script:results += $line
    $script:results | Out-File 'merged-sweep.progress' -Encoding utf8
}
$plan = @(
  @{ f='1.20.6';  forge='50.2.8';  neo='20.6.139'  },
  @{ f='1.21.1';  forge='52.1.14'; neo='21.1.233'  },
  @{ f='1.21.5';  forge='55.1.10'; neo='21.5.97'   },
  @{ f='1.21.8';  forge='58.1.18'; neo='21.8.53'   },
  @{ f='1.21.11'; forge=$null;     neo='21.11.42'  },
  @{ f='26.1.2';  forge=$null;     neo='26.1.2.71' }
)
foreach ($p in $plan) {
  $f = $p.f
  $jar = "$work\trident-killers-4-java-1.2+$f-merged.jar"
  Run-Test "fabric-$f"   "python tk4j_compat_test.py $f `"$jar`""
  Run-Test "quilt-$f"    "python tk4j_quilt_test.py $f `"$jar`""
  if ($p.forge) { Run-Test "forge-$f" "python tk4j_forge_test.py $f $($p.forge) `"$jar`"" }
  if ($p.neo)   { Run-Test "neoforge-$f" "python tk4j_neoforge_test.py $f $($p.neo) `"$jar`"" }
}
"=== SUMMARY ===" | Out-File $log -Append -Encoding utf8
$results | Out-File $log -Append -Encoding utf8
$results | Out-File 'merged-sweep.done' -Encoding utf8
