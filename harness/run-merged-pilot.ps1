Set-Location '<WORKSPACE>\Minecraft\tk4j-compat-tests'
$jar = '<WORKSPACE>\Minecraft\mods\tk4j-merged\trident-killers-4-java-1.2+1.20.4-merged.jar'
$log = 'merged-pilot.log'
"=== MERGED PILOT 1.20.4 family — $(Get-Date) ===" | Out-File $log -Encoding utf8
$results = @()
function Run-Test($name, $cmd) {
    "--- $name : $cmd ---" | Out-File $script:log -Append -Encoding utf8
    $out = Invoke-Expression "$cmd 2>&1" | Out-String
    $out | Out-File $script:log -Append -Encoding utf8
    $pass = $out -match 'ALL PASS'
    if (-not $pass -and $out -match 'FAIL') {
        "RETRY (warm) $name" | Out-File $script:log -Append -Encoding utf8
        $out2 = Invoke-Expression "$cmd 2>&1" | Out-String
        $out2 | Out-File $script:log -Append -Encoding utf8
        $pass = $out2 -match 'ALL PASS'
    }
    $script:results += "{0}: {1}" -f $name, $(if ($pass) {'PASS'} else {'FAIL'})
}
Run-Test 'fabric-1.20.1'   "python tk4j_compat_test.py 1.20.1 `"$jar`""
Run-Test 'fabric-1.20.4'   "python tk4j_compat_test.py 1.20.4 `"$jar`""
Run-Test 'quilt-1.20.1'    "python tk4j_quilt_test.py 1.20.1 `"$jar`""
Run-Test 'forge-1.20.1'    "python tk4j_forge_test.py 1.20.1 47.3.0 `"$jar`""
Run-Test 'neoforge-1.20.1' "python tk4j_neoforge_test.py 1.20.1 47.1.106 `"$jar`""
"=== SUMMARY ===" | Out-File $log -Append -Encoding utf8
$results | Out-File $log -Append -Encoding utf8
$results | Out-File 'merged-pilot.done' -Encoding utf8
