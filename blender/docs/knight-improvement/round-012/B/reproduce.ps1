param(
    [string]$Blender='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe',
    [string]$Python='C:/Users/toby/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
)
$ErrorActionPreference='Stop'
$EvidenceDir=$PSScriptRoot
function Run-Blender([string]$scriptName, [string[]]$scriptArgs) {
    & $Blender -b --python-exit-code 1 -P (Join-Path $EvidenceDir $scriptName) -- @scriptArgs
    if ($LASTEXITCODE -ne 0) { throw "$scriptName failed" }
}
function Run-Python([string]$scriptName, [string[]]$scriptArgs) {
    & $Python -B (Join-Path $EvidenceDir $scriptName) @scriptArgs
    if ($LASTEXITCODE -ne 0) { throw "$scriptName failed" }
}
Run-Blender 'section_grid.py' @('parent')
Run-Blender 'atlas_input.py' @()
Run-Python 'pigment.py' @()
Run-Blender 'carve.py' @('build','16','studio','orbit')
Run-Blender 'measure.py' @('parent','knight')
Run-Blender 'section_grid.py' @('knight')
Run-Blender 'qa_geometry.py' @('knight')
Run-Blender 'verify.py' @()
Run-Blender 'moving.py' @()
Run-Blender 'finish_probe.py' @('parent','knight')
Run-Python 'light.py' @('--final')
Run-Python 'report.py' @()
