$ErrorActionPreference = "Continue"
$mods = "<WORKSPACE>\Minecraft\mods"
$log = "$mods\neoforge-builds.log"
foreach ($f in @("1.20.6","1.21.5","1.21.8","1.21.11")) {
    $p = "$mods\tk4j-neoforge-$f"
    "=== BUILD $f ===" | Add-Content $log
    Push-Location $p
    & "$p\gradlew.bat" build --no-daemon --console=plain *>> $log
    Pop-Location
    $jar = Get-ChildItem "$p\build\libs\*.jar" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($jar) { "=== $f JAR: $($jar.Name) ===" | Add-Content $log }
    else { "=== $f NO JAR (FAILED) ===" | Add-Content $log }
}
"=== ALL BUILDS DONE ===" | Add-Content $log
