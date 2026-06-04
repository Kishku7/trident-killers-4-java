$ErrorActionPreference = "Continue"
$tests = "<WORKSPACE>\Minecraft\tk4j-compat-tests"
$jars = "<WORKSPACE>\Minecraft\mods\trident-killers-4-java"
$vers = @("1.20.6","1.21.1","1.21.5","1.21.8","1.21.11","26.1.2")
foreach ($v in $vers) {
    $jar = Join-Path $jars "trident-killers-4-java-1.1+$v.jar"
    "=== QUILT SWEEP: $v ===" | Add-Content "$tests\quilt-sweep.log"
    & python "$tests\tk4j_quilt_test.py" $v $jar *>> "$tests\quilt-sweep.log"
    "--- exit: $LASTEXITCODE ---" | Add-Content "$tests\quilt-sweep.log"
}
"=== SWEEP COMPLETE ===" | Add-Content "$tests\quilt-sweep.log"
