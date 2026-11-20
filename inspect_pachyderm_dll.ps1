[System.AppDomain]::CurrentDomain.add_AssemblyResolve({
    param($sender, $args)
    $name = $args.Name.Split(',')[0]
    $rhinoPath = "C:\Program Files\Rhino 9\System\$name.dll"
    if (Test-Path $rhinoPath) {
        return [System.Reflection.Assembly]::LoadFrom($rhinoPath)
    }
    $pachyPath = "C:\Users\Tarek\AppData\Roaming\McNeel\Rhinoceros\packages\9.0\pachyderm_acoustic_simulation\2.7.0.0\$name.dll"
    if (Test-Path $pachyPath) {
        return [System.Reflection.Assembly]::LoadFrom($pachyPath)
    }
    return $null
})

$pachydermDll = "C:\Users\Tarek\AppData\Roaming\McNeel\Rhinoceros\packages\9.0\pachyderm_acoustic_simulation\2.7.0.0\Pachyderm_Acoustic_Universal.dll"
try {
    $asm = [System.Reflection.Assembly]::LoadFrom($pachydermDll)
    Write-Host "Successfully loaded Pachyderm assembly: " $asm.FullName
    $types = $asm.GetExportedTypes()
    Write-Host "Total exported types: " $types.Count
    $types | Select-Object -First 40 | ForEach-Object { Write-Host " - " $_.FullName }
} catch {
    Write-Host "Load failed: " $_.Exception.ToString()
}
