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
$MissionDir=(Resolve-Path (Join-Path $EvidenceDir '../../..')).Path
Run-Blender 'map.py' @()
Run-Python 'surface.py' @()
Run-Blender 'donor.py' @()
Run-Python 'donor_field.py' @()
Run-Python 'restore.py' @('9')
Run-Blender 'candidate.py' @('save','9','studio','orbit')
Run-Blender 'candidate.py' @('trial','parent','knight')
Run-Blender 'candidate.py' @('turn','knight')
Run-Blender 'candidate.py' @('neutral','parent','knight')
Run-Blender 'verify.py' @()
foreach ($Model in @('parent','knight')) {
    $Scene=Join-Path $EvidenceDir ($Model+'.blend')
    Run-Blender 'rear.py' @($MissionDir,$Scene,(Join-Path $EvidenceDir ('back-'+$Model)))
    Run-Blender 'rear.py' @($MissionDir,$Scene,(Join-Path $EvidenceDir ('back-'+$Model+'-pigment')),'--pigment-only')
}
Run-Python 'study.py' @('parent','knight')
Run-Python 'viewer.py' @()
$PrivateReview=Join-Path $EvidenceDir 'review-copy'
& node (Join-Path $PrivateReview 'scripts/knight/check_viewer.cjs') $PrivateReview
if($LASTEXITCODE -ne 0){throw 'Viewer camera validation failed'}
$env:NODE_PATH='C:/Users/toby/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules'
$env:LISTAUNTON_CHROMIUM_BINARY='C:/Program Files/Google/Chrome/Application/chrome.exe'
& node (Join-Path $PrivateReview 'scripts/knight/check_native_viewer.cjs') $PrivateReview (Join-Path $EvidenceDir 'webgl')
if($LASTEXITCODE -ne 0){throw 'Native WebGL validation failed'}
Run-Python 'report.py' @()
