param(
    [ValidateSet('Accounts', 'Core', 'Hosts', 'All')]
    [string]$Target = 'Accounts'
)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskApp = Join-Path $taskRoot 'app'
if (!(Test-Path -LiteralPath (Join-Path $taskApp 'Cargo.toml'))) { throw 'Missing app workspace' }
$taskNames = @('WB_SWITCH_HOME', 'APPDATA', 'LOCALAPPDATA', 'CARGO_TARGET_DIR', 'WB_SWITCH_SCREENSHOT_DEMO')
$taskPrevious = @{}
foreach ($taskName in $taskNames) { $taskPrevious[$taskName] = [Environment]::GetEnvironmentVariable($taskName, 'Process') }
$taskEvidence = Join-Path $taskRoot 'docs\evidence'
New-Item -ItemType Directory -Path $taskEvidence -Force | Out-Null
try {
    $env:WB_SWITCH_HOME = Join-Path $taskRoot 'test-fixtures\development-home'
    $env:APPDATA = Join-Path $taskRoot 'test-fixtures\development-appdata'
    $env:LOCALAPPDATA = Join-Path $taskRoot 'test-fixtures\development-localappdata'
    $env:CARGO_TARGET_DIR = Join-Path $taskRoot 'test-fixtures\cargo-target'
    $env:WB_SWITCH_SCREENSHOT_DEMO = '1'
    New-Item -ItemType Directory -Path $env:WB_SWITCH_HOME,$env:APPDATA,$env:LOCALAPPDATA -Force | Out-Null
    Push-Location $taskApp
    try {
        $taskRustLog = Join-Path $taskEvidence "development-$($Target.ToLowerInvariant()).log"
        switch ($Target) {
            'Accounts' { & cargo test --locked -p wb-switch-core --test account_security *> $taskRustLog }
            'Core' { & cargo test --locked -p wb-switch-core *> $taskRustLog }
            'Hosts' { & cargo test --locked -p wb-switch-server -p wb-switch-rust *> $taskRustLog }
            'All' { & cargo test --locked -p wb-switch-core -p wb-switch-server -p wb-switch-rust *> $taskRustLog }
        }
        $taskExit = $LASTEXITCODE
        Get-Content -LiteralPath $taskRustLog -Tail 20
        if ($taskExit -ne 0) { throw "Rust tests failed ($taskExit); see $taskRustLog" }
        if ($Target -eq 'All') {
            $taskNpmLog = Join-Path $taskEvidence 'development-frontend-test.log'
            & npm.cmd test *> $taskNpmLog
            if ($LASTEXITCODE -ne 0) { throw "Frontend tests failed; see $taskNpmLog" }
            $taskBuildLog = Join-Path $taskEvidence 'development-frontend-build.log'
            & npm.cmd run build *> $taskBuildLog
            if ($LASTEXITCODE -ne 0) { throw "Frontend build failed; see $taskBuildLog" }
        }
    } finally { Pop-Location }
} finally {
    foreach ($taskName in $taskNames) { [Environment]::SetEnvironmentVariable($taskName, $taskPrevious[$taskName], 'Process') }
}
