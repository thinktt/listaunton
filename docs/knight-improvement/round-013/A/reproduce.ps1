param(
    [string] $Blender = 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe',
    [string] $Python = 'C:/Users/toby/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
)
$ErrorActionPreference = 'Stop'
$Slot = $PSScriptRoot
$Stage = (Get-Item -LiteralPath $Slot).Parent.Parent.Parent.FullName
function Invoke-BlenderScript($Name, [string[]] $Arguments = @()) {
    $Launcher = @('-b','--factory-startup','--python-exit-code','2','--python',(Join-Path $Slot $Name))
    if ($Arguments.Count) { $Launcher += '--'; $Launcher += $Arguments }
    & $Blender @Launcher
    if ($LASTEXITCODE -ne 0) { throw "Blender failed during $Name" }
}
function Invoke-ImageScript($Name, [string[]] $Arguments = @()) {
    & $Python (Join-Path $Slot $Name) @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Image processing failed during $Name" }
}
$Parent = Join-Path $Slot 'parent.blend'
$Model = Join-Path $Slot 'knight.blend'
Invoke-BlenderScript 'survey.py'
Invoke-ImageScript 'finish_input.py'
Invoke-BlenderScript 'sculpt.py'
Invoke-BlenderScript 'preview.py'
Invoke-ImageScript 'study.py'
Invoke-BlenderScript 'head_check.py'
Invoke-BlenderScript 'diagnostic_views.py'
Invoke-BlenderScript 'parent_studio.py'
foreach ($Item in @(@('parent',$Parent),@('A',$Model))) {
    $Name,$File = $Item
    Invoke-BlenderScript 'eye_portraits.py' @($Stage,$File,(Join-Path $Slot "portraits-$Name"))
    Invoke-BlenderScript 'eye_portraits.py' @($Stage,$File,(Join-Path $Slot "turn-eye-$Name"),'--turn')
    Invoke-BlenderScript 'bilateral_eye.py' @($Stage,$File,(Join-Path $Slot "eyes-$Name"))
    Invoke-BlenderScript 'eye_footprint.py' @($Stage,$File,(Join-Path $Slot "fixed-eye-$Name.json"))
}
Invoke-BlenderScript 'moving.py'
Invoke-BlenderScript 'brow_native.py' @($Stage,$Model,(Join-Path $Slot 'source-anchors.json'),(Join-Path $Slot 'brow-native.json'))
Invoke-BlenderScript 'self_intersection.py'
Invoke-BlenderScript 'self_intersection.py' @('--skull')
Invoke-BlenderScript 'evaluated_mesh.py'
Invoke-BlenderScript 'protected.py'
Invoke-BlenderScript 'export_check.py'
Invoke-ImageScript 'eye_turns.py' @($Slot,'parent','A')
Invoke-ImageScript 'socket_sections.py' @($Slot,'parent','A')
Invoke-ImageScript 'measure.py' @('--full')
Invoke-ImageScript 'report.py'
