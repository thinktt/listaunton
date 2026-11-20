param(
    [string] $Blender = 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe',
    [string] $Python = 'C:/Users/toby/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
)
$ErrorActionPreference = 'Stop'
$Candidate = $PSScriptRoot
$Stage = (Get-Item -LiteralPath $Candidate).Parent.Parent.Parent.FullName
function Invoke-BlenderScript($ScriptName, [string[]] $Arguments = @()) {
    $CommandArgs = @('-b', '--factory-startup', '--python-exit-code', '2', '--python', (Join-Path $Candidate $ScriptName))
    if ($Arguments.Count) { $CommandArgs += '--'; $CommandArgs += $Arguments }
    & $Blender @CommandArgs
    if ($LASTEXITCODE -ne 0) { throw "Blender failed during $ScriptName" }
}
function Invoke-ImageScript($ScriptName) {
    & $Python (Join-Path $Candidate $ScriptName)
    if ($LASTEXITCODE -ne 0) { throw "Image processing failed during $ScriptName" }
}
$Parent = Join-Path $Candidate 'parent.blend'
$Model = Join-Path $Candidate 'knight.blend'
$Trace = Join-Path $Candidate 'mane-hollow.json'
Invoke-BlenderScript 'atlas_chart.py'
Invoke-ImageScript 'stain.py'
Invoke-BlenderScript 'sculpt.py'
Invoke-BlenderScript 'preview.py'
Invoke-ImageScript 'study.py'
Invoke-BlenderScript 'turn_check.py'
Invoke-BlenderScript 'diagnostic_views.py'
Invoke-BlenderScript 'paired_walnut.py' @($Stage,$Model,(Join-Path $Candidate 'paired'))
Invoke-BlenderScript 'carving_light.py' @($Stage,$Model,(Join-Path $Candidate 'neutral'))
Invoke-BlenderScript 'self_intersection.py'
Invoke-BlenderScript 'self_intersection.py' @('--skull')
Invoke-BlenderScript 'evaluated_mesh.py'
Invoke-BlenderScript 'protected.py'
Invoke-BlenderScript 'export_check.py'
Invoke-BlenderScript 'measure_depth.py' @($Stage,$Parent,$Trace,(Join-Path $Candidate 'parent-depth.json'))
Invoke-BlenderScript 'measure_depth.py' @($Stage,$Model,$Trace,(Join-Path $Candidate 'candidate-depth.json'))
Invoke-BlenderScript 'measure_flanks.py' @($Stage,$Model,(Join-Path $Candidate 'bilateral'))
$Seat = Join-Path $Candidate 'candidate-seat'
New-Item -ItemType Directory -Force -Path $Seat | Out-Null
Copy-Item -LiteralPath $Trace -Destination (Join-Path $Seat 'mane-hollow.json') -Force
Invoke-BlenderScript 'measure_seat.py' @($Stage,$Parent,$Candidate)
Invoke-BlenderScript 'measure_seat.py' @($Stage,$Model,$Seat)
Invoke-ImageScript 'report.py'
