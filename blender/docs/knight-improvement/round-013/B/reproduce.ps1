param(
    [string]$Blender = 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe',
    [string]$Python = 'C:/Users/toby/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
)
$ErrorActionPreference = 'Stop'
$EvidenceDir = $PSScriptRoot
$MissionDir = (Resolve-Path (Join-Path $EvidenceDir '../../..')).Path
$ParentModel = Join-Path $EvidenceDir 'parent.blend'
$CandidateModel = Join-Path $EvidenceDir 'knight.blend'
function Run-Blender([string]$scriptName, [string[]]$scriptArgs) {
    & $Blender -b --python-exit-code 1 -P (Join-Path $EvidenceDir $scriptName) -- @scriptArgs
    if ($LASTEXITCODE -ne 0) { throw "$scriptName failed" }
}
function Run-Python([string]$scriptName, [string[]]$scriptArgs) {
    & $Python -B (Join-Path $EvidenceDir $scriptName) @scriptArgs
    if ($LASTEXITCODE -ne 0) { throw "$scriptName failed" }
}

Run-Blender 'bilateral_eye.py' @($MissionDir, $ParentModel, (Join-Path $EvidenceDir 'eyes-parent.json'))
Run-Blender 'orbital.py' @('parent')
Run-Blender 'eye_uv.py' @()
Run-Python 'pigment.py' @()
Run-Blender 'carve.py' @('build','17','studio','orbit')
Run-Blender 'mesh_check.py' @('knight')
Run-Blender 'verify.py' @()
Run-Blender 'uv_check.py' @()
Run-Blender 'bilateral_eye.py' @($MissionDir, $CandidateModel, (Join-Path $EvidenceDir 'eyes-B.json'))
Run-Python 'plot_bilateral_eye.py' @($EvidenceDir, 'parent', 'B')
Run-Python 'socket_sections.py' @($EvidenceDir, 'parent', 'B')
Run-Blender 'eye_portraits.py' @($MissionDir, $ParentModel, (Join-Path $EvidenceDir 'portraits-parent'))
Run-Blender 'eye_portraits.py' @($MissionDir, $CandidateModel, (Join-Path $EvidenceDir 'portraits-B'))
Run-Blender 'moving.py' @()
Run-Blender 'common_fixed.py' @()
Run-Python 'study.py' @('parent','knight')
Run-Python 'report.py' @()
