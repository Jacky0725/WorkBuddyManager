param([switch]$DebugBuild, [ValidatePattern('^phase\d+$')][string]$EvidencePrefix = 'phase07')
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskNames = @('WB_SWITCH_HOME', 'APPDATA', 'LOCALAPPDATA', 'CARGO_TARGET_DIR', 'WB_SWITCH_SCREENSHOT_DEMO', 'VITE_DEMO_MODE', 'VITE_PAGES_DEMO')
$taskPrevious = @{}
foreach ($taskName in $taskNames) { $taskPrevious[$taskName] = [Environment]::GetEnvironmentVariable($taskName, 'Process') }
try {
    $env:WB_SWITCH_HOME = Join-Path $taskRoot 'test-fixtures\package-home'
    $env:APPDATA = Join-Path $taskRoot 'test-fixtures\package-appdata'
    $env:LOCALAPPDATA = Join-Path $taskRoot 'test-fixtures\package-localappdata'
    $env:CARGO_TARGET_DIR = Join-Path $taskRoot 'test-fixtures\cargo-target'
    foreach ($taskName in @('WB_SWITCH_SCREENSHOT_DEMO', 'VITE_DEMO_MODE', 'VITE_PAGES_DEMO')) { Remove-Item -LiteralPath "Env:\$taskName" -ErrorAction SilentlyContinue }
    New-Item -ItemType Directory -Path $env:WB_SWITCH_HOME,$env:APPDATA,$env:LOCALAPPDATA -Force | Out-Null
    Push-Location (Join-Path $taskRoot 'app')
    try {
        $taskMode = if ($DebugBuild) { 'debug' } else { 'release' }
        $taskLog = Join-Path $taskRoot "docs\evidence\$EvidencePrefix-manager-$taskMode-build.log"
        $taskArgs = @('run', 'tauri', '--', 'build', '--bundles', 'nsis')
        if ($DebugBuild) { $taskArgs += '--debug' }
        $ErrorActionPreference = 'Continue'
        & npm.cmd @taskArgs *> $taskLog
        $taskExit = $LASTEXITCODE
        $ErrorActionPreference = 'Stop'
        Get-Content -LiteralPath $taskLog -Tail 20
        if ($taskExit -ne 0) { throw "Manager packaging failed ($taskExit); see $taskLog" }
    } finally { Pop-Location }
} finally {
    foreach ($taskName in $taskNames) {
        if ($null -eq $taskPrevious[$taskName]) { Remove-Item -LiteralPath "Env:\$taskName" -ErrorAction SilentlyContinue }
        else { [Environment]::SetEnvironmentVariable($taskName, $taskPrevious[$taskName], 'Process') }
    }
}
