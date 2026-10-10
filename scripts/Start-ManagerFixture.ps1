param([switch]$HiddenStartup, [switch]$ReleaseBuild, [switch]$InstalledDebug, [switch]$InstalledRelease)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskFixture = Join-Path $taskRoot 'test-fixtures\manager-desktop-acceptance'
if (!(Test-Path -LiteralPath (Join-Path $taskFixture 'home\.workbuddy-manager\accounts.json'))) { throw 'Prepare fiction-only fixture accounts before launching' }
$taskProfile = if ($ReleaseBuild) { 'release' } else { 'debug' }
$taskExe = Join-Path $taskRoot "test-fixtures\cargo-target\$taskProfile\workbuddy-manager.exe"
if ($InstalledDebug) { $taskExe = Join-Path $taskRoot 'test-fixtures\install-manager-debug\workbuddy-manager.exe'; $taskProfile = 'installed-debug' }
if ($InstalledRelease) { $taskExe = Join-Path $taskRoot 'test-fixtures\install-manager-release\workbuddy-manager.exe'; $taskProfile = 'installed-release' }
if (!(Test-Path -LiteralPath $taskExe)) { throw 'Build Manager first' }
$taskNames = @('WB_SWITCH_HOME', 'APPDATA', 'LOCALAPPDATA', 'WB_SWITCH_SCREENSHOT_DEMO')
$taskPrevious = @{}
foreach ($taskName in $taskNames) { $taskPrevious[$taskName] = [Environment]::GetEnvironmentVariable($taskName, 'Process') }
try {
    $env:WB_SWITCH_HOME = Join-Path $taskFixture 'home'
    $env:APPDATA = Join-Path $taskFixture 'appdata'
    $env:LOCALAPPDATA = Join-Path $taskFixture 'localappdata'
    Remove-Item -LiteralPath Env:\WB_SWITCH_SCREENSHOT_DEMO -ErrorAction SilentlyContinue
    $taskParameters = @{FilePath=$taskExe;WindowStyle='Hidden';PassThru=$true}
    if ($HiddenStartup) { $taskParameters.ArgumentList = @('--hidden') }
    $taskProcess = Start-Process @taskParameters
    Write-Output "Launched fixture-only Manager PID $($taskProcess.Id), profile $taskProfile, hidden argument $HiddenStartup"
} finally {
    foreach ($taskName in $taskNames) { [Environment]::SetEnvironmentVariable($taskName, $taskPrevious[$taskName], 'Process') }
}
