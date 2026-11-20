param(
    [string]$Blender='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe',
    [string]$Python='C:/Users/toby/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
)
$ErrorActionPreference='Stop'
$EvidenceDir=$PSScriptRoot
$MissionDir=(Resolve-Path (Join-Path $EvidenceDir '../../..')).Path
function Run-Blender([string]$ScriptName,[string[]]$ScriptArgs) {
    & $Blender -b --python-exit-code 1 -P (Join-Path $EvidenceDir $ScriptName) -- @ScriptArgs
    if ($LASTEXITCODE -ne 0) {throw "$ScriptName failed"}
}
function Run-Python([string]$ScriptName,[string[]]$ScriptArgs) {
    & $Python -B (Join-Path $EvidenceDir $ScriptName) @ScriptArgs
    if ($LASTEXITCODE -ne 0) {throw "$ScriptName failed"}
}
$Recipe=Get-Content -Raw (Join-Path $EvidenceDir 'recipe.json') | ConvertFrom-Json
Run-Blender 'survey.py' @('parent')
Run-Blender 'lamp_probe.py' @()
Run-Blender 'carve.py' @('build',[string]$Recipe.design,'studio','orbit')
Run-Blender 'verify.py' @()
Run-Blender 'replay.py' @()
Run-Blender 'mesh_check.py' @('parent','knight')
foreach ($Model in @('parent','knight')) {
    $Code=if($Model -eq 'parent'){'parent'}else{'B'}
    $Scene=Join-Path $EvidenceDir ($Model+'.blend')
    Run-Blender 'bilateral_eye.py' @($MissionDir,$Scene,(Join-Path $EvidenceDir ('eyes-'+$Code)))
    Run-Blender 'eye_portraits.py' @($MissionDir,$Scene,(Join-Path $EvidenceDir ('portraits-'+$Code)))
}
Run-Blender 'moving.py' @()
Run-Blender 'common_fixed.py' @()
Run-Python 'study.py' @('parent','knight')
Run-Python 'sweep.py' @('knight')
Run-Python 'socket_sections.py' @($EvidenceDir,'parent','B')
Run-Python 'plot_bilateral_eye.py' @($EvidenceDir,'parent','B')
Run-Python 'viewer.py' @()
$Review=Join-Path $EvidenceDir 'review-copy'
& node (Join-Path $Review 'scripts/knight/check_viewer.cjs') $Review | Tee-Object -FilePath (Join-Path $EvidenceDir 'viewer-check.log')
if($LASTEXITCODE -ne 0){throw 'Viewer camera validation failed'}
$env:NODE_PATH='C:/Users/toby/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules'
$env:LISTAUNTON_CHROMIUM_BINARY='C:/Program Files/Google/Chrome/Application/chrome.exe'
& node (Join-Path $Review 'scripts/knight/check_native_viewer.cjs') $Review (Join-Path $EvidenceDir 'webgl')
if($LASTEXITCODE -ne 0){throw 'Native WebGL validation failed'}
Run-Python 'support.py' @()
Run-Python 'report.py' @()
