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
Run-Python 'grain.py' @()
Run-Blender 'map.py' @()
Run-Python 'billet.py' @()
Run-Blender 'survey.py' @('parent')
Run-Blender 'carve.py' @('build',[string]$Recipe.design,'studio','orbit')
Run-Blender 'verify.py' @()
Run-Blender 'replay.py' @()
foreach ($Model in @('parent','knight')) {
    $Code=if($Model -eq 'parent'){'parent'}else{'B'}
    $Scene=Join-Path $EvidenceDir ($Model+'.blend')
    Run-Blender 'top_sections.py' @($MissionDir,$Scene,(Join-Path $EvidenceDir ('crest-'+$Code+'.json')))
}
Run-Blender 'preflight.py' @('parent')
Run-Blender 'turn.py' @('parent','knight')
Run-Blender 'controls.py' @('knight')
Run-Python 'study.py' @('knight')
Run-Python 'plot_top_sections.py' @($EvidenceDir,'parent','B')
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
