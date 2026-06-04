$work = '<WORKSPACE>\Minecraft\mods\tk4j-merged'
$stage = '<WORKSPACE>\Minecraft\mods\trident-killers-4-java'
$java = 'C:\Program Files\Eclipse Adoptium\jdk-25.0.1.8-hotspot\bin\java.exe'
$forgix = '<WORKSPACE>\Minecraft\mods\Forgix\build\libs\Forgix-2.0.0-SNAPSHOT.5.1.jar'
$log = "$work\merge-all.log"
"=== MERGE ALL FAMILIES $(Get-Date) ===" | Out-File $log -Encoding utf8
$families = @(
  @{ f='1.20.6';  loaders=@('fabric','forge','neoforge') },
  @{ f='1.21.1';  loaders=@('fabric','forge','neoforge') },
  @{ f='1.21.5';  loaders=@('fabric','forge','neoforge') },
  @{ f='1.21.8';  loaders=@('fabric','forge','neoforge') },
  @{ f='1.21.11'; loaders=@('fabric','neoforge') },
  @{ f='26.1.2';  loaders=@('fabric','neoforge') }
)
foreach ($fam in $families) {
  $f = $fam.f
  $in = "$work\inputs\$f"
  New-Item -ItemType Directory -Force -Path $in | Out-Null
  $args = @('mergeJars','--output',"$work\trident-killers-4-java-1.2+$f-merged.jar")
  foreach ($l in $fam.loaders) {
    $suffix = if ($l -eq 'fabric') { '' } else { "-$l" }
    $src = "$stage\trident-killers-4-java-1.2+$f$suffix.jar"
    Copy-Item $src "$in\" -Force
    $args += @("--$l", "$in\trident-killers-4-java-1.2+$f$suffix.jar")
  }
  "--- $f ---" | Out-File $log -Append -Encoding utf8
  & $java -cp $forgix io.github.pacifistmc.forgix.Forgix @args 2>&1 | Select-String -Pattern 'Successfully|Error' | Out-File $log -Append -Encoding utf8
}
'MERGES DONE' | Out-File "$work\merge-all.done" -Encoding utf8
