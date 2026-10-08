param(
    [ValidateSet('Core', 'Server', 'Frontend', 'Desktop')]
    [string]$Target = 'Core'
)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskSource = Join-Path $taskRoot 'upstream\workbuddy-switch'
$taskExpected = '9eb3f2a21ff3c3c85fef2f89e693c48792050ba1'
$taskActual = (& git -C $taskSource rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $taskActual -ne $taskExpected) { throw 'Unexpected upstream commit; baseline cancelled.' }
$taskChanges = & git -C $taskSource status --porcelain --untracked-files=no
if ($taskChanges) { throw 'Tracked upstream source is modified; baseline cancelled.' }
$taskEnvNames = @('WB_SWITCH_HOME', 'APPDATA', 'LOCALAPPDATA', 'CARGO_TARGET_DIR', 'WB_SWITCH_SCREENSHOT_DEMO')
$taskPrevious = @{}
foreach ($taskEnvName in $taskEnvNames) { $taskPrevious[$taskEnvName] = [Environment]::GetEnvironmentVariable($taskEnvName, 'Process') }
$taskLog = Join-Path $taskRoot "docs\evidence\rerun-$($Target.ToLowerInvariant()).log"
try {
    $env:WB_SWITCH_HOME = Join-Path $taskRoot 'test-fixtures\baseline-home'
    $env:APPDATA = Join-Path $taskRoot 'test-fixtures\baseline-appdata'
    $env:LOCALAPPDATA = Join-Path $taskRoot 'test-fixtures\baseline-localappdata'
    $env:CARGO_TARGET_DIR = Join-Path $taskRoot 'test-fixtures\cargo-target'
    $env:WB_SWITCH_SCREENSHOT_DEMO = '1'
    New-Item -ItemType Directory -Path $env:WB_SWITCH_HOME, $env:APPDATA, $env:LOCALAPPDATA -Force | Out-Null
    Push-Location $taskSource
    try {
        switch ($Target) {
            'Core' { & cargo test --locked -p wb-switch-core *> $taskLog }
            'Server' { & cargo test --locked -p wb-switch-server *> $taskLog }
            'Frontend' { & npm.cmd test *> $taskLog }
            'Desktop' { & cargo test --locked -p wb-switch-rust *> $taskLog }
        }
        $taskExit = $LASTEXITCODE
        Get-Content -LiteralPath $taskLog -Tail 25
        if ($taskExit -ne 0) { throw "Baseline $Target failed with exit code $taskExit. See $taskLog" }
    } finally { Pop-Location }
} finally {
    foreach ($taskEnvName in $taskEnvNames) { [Environment]::SetEnvironmentVariable($taskEnvName, $taskPrevious[$taskEnvName], 'Process') }
}
