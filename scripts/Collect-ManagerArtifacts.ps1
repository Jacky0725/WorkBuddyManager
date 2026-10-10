param([switch]$RefreshMetadata)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskConfig = Get-Content -LiteralPath (Join-Path $taskRoot 'app\src-tauri\tauri.conf.json') -Raw | ConvertFrom-Json
$taskVersion = $taskConfig.version
if ($taskVersion -notmatch '^\d+\.\d+\.\d+-alpha\.\d+$') { throw 'This collector only handles experimental alpha candidates' }
$taskOutput = Join-Path $taskRoot "release\$taskVersion\local-candidate"
if ((Test-Path -LiteralPath $taskOutput) -and !$RefreshMetadata) { throw 'Existing candidate output; retain it rather than overwrite' }
$taskInstall = Join-Path $taskRoot 'test-fixtures\install-manager-release'
$taskInstaller = Join-Path $taskRoot "test-fixtures\cargo-target\release\bundle\nsis\WorkBuddy Manager_$($taskVersion)_x64-setup.exe"
$taskAppSha = (& git -C (Join-Path $taskRoot 'app') rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'No verified app Git SHA' }
if (@(& git -C (Join-Path $taskRoot 'app') status --porcelain).Count -ne 0 -or $LASTEXITCODE -ne 0) { throw 'Commit app changes before collecting a source archive' }
if ($RefreshMetadata) {
    $taskOldManifest = Get-Content -LiteralPath (Join-Path $taskOutput 'manifest.json') -Raw | ConvertFrom-Json
    if ($taskOldManifest.version -ne $taskVersion -or $taskOldManifest.app_commit -ne $taskAppSha) { throw 'Metadata refresh cannot change the candidate source/version' }
    $taskResolvedOutput = (Resolve-Path -LiteralPath $taskOutput).Path
    foreach ($taskOldFile in $taskOldManifest.files) {
        $taskOldPath = [IO.Path]::GetFullPath((Join-Path $taskOutput $taskOldFile.name))
        if (!$taskOldPath.StartsWith($taskResolvedOutput + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Manifest path escapes candidate' }
        if ((Get-FileHash -LiteralPath $taskOldPath -Algorithm SHA256).Hash -ne $taskOldFile.sha256) { throw "Existing candidate changed: $($taskOldFile.name)" }
    }
} else {
    foreach ($taskFile in @($taskInstaller,(Join-Path $taskInstall 'workbuddy-manager.exe'),(Join-Path $taskInstall 'THIRD_PARTY_NOTICES.md'))) {
        if (!(Test-Path -LiteralPath $taskFile)) { throw "Required optimized artifact missing: $taskFile" }
    }
    New-Item -ItemType Directory -Path $taskOutput | Out-Null
    Copy-Item -LiteralPath $taskInstaller -Destination $taskOutput
    Copy-Item -LiteralPath (Join-Path $taskInstall 'workbuddy-manager.exe') -Destination $taskOutput
    foreach ($taskName in @('LICENSE','THIRD_PARTY_NOTICES.md','licenses')) {
        Copy-Item -LiteralPath (Join-Path $taskInstall $taskName) -Destination $taskOutput -Recurse
    }
    $taskSourceZip = Join-Path $taskOutput "WorkBuddyManager-$taskVersion-source.zip"
    & git -C (Join-Path $taskRoot 'app') archive --format=zip "--output=$taskSourceZip" HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Source archive failed' }
    Copy-Item -LiteralPath (Join-Path $taskRoot 'docs\evidence\app-development.bundle') -Destination $taskOutput
}
Copy-Item -LiteralPath (Join-Path $taskRoot 'docs\08-installation.md') -Destination (Join-Path $taskOutput 'INSTALLATION.md')
Copy-Item -LiteralPath (Join-Path $taskRoot 'docs\10-release-notes.md') -Destination (Join-Path $taskOutput 'RELEASE_NOTES.md')
Copy-Item -LiteralPath (Join-Path $taskRoot 'docs\11-known-limitations.md') -Destination (Join-Path $taskOutput 'KNOWN_LIMITATIONS.md')
Copy-Item -LiteralPath (Join-Path $taskRoot 'docs\06-testing.md') -Destination (Join-Path $taskOutput 'TEST_REPORT.md')
Copy-Item -LiteralPath (Join-Path $taskRoot 'docs\09-user-guide.md') -Destination (Join-Path $taskOutput 'USER_GUIDE.md')
Copy-Item -LiteralPath (Join-Path $taskRoot 'docs\07-security-review.md') -Destination (Join-Path $taskOutput 'SECURITY_REVIEW.md')
Copy-Item -LiteralPath (Join-Path $taskRoot 'docs\13-acceptance-plan.md') -Destination (Join-Path $taskOutput 'ACCEPTANCE_PLAN.md')
$taskEvidenceOutput = Join-Path $taskOutput 'evidence'
New-Item -ItemType Directory -Path $taskEvidenceOutput -Force | Out-Null
Get-ChildItem -LiteralPath (Join-Path $taskRoot 'docs\evidence') -File -Filter 'phase07-*' | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $taskEvidenceOutput
}
$taskUiOutput = Join-Path $taskEvidenceOutput 'manager-ui'
New-Item -ItemType Directory -Path $taskUiOutput -Force | Out-Null
Get-ChildItem -LiteralPath (Join-Path $taskRoot 'docs\evidence\manager-ui') -File | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $taskUiOutput
}
$taskRustLog = Get-Content -LiteralPath (Join-Path $taskEvidenceOutput 'phase07-all-tests.log') -Raw
$taskRustSummaries = [regex]::Matches($taskRustLog, 'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;')
if ($taskRustSummaries.Count -eq 0 -or $taskRustLog -match 'test result: FAILED') { throw 'Missing or failed final Rust summary' }
$taskRustCount = 0
foreach ($taskSummary in $taskRustSummaries) {
    if ([int]$taskSummary.Groups[2].Value -ne 0 -or [int]$taskSummary.Groups[3].Value -ne 0) { throw 'Final Rust suite failed or ignored tests' }
    $taskRustCount += [int]$taskSummary.Groups[1].Value
}
$taskFrontendLog = Get-Content -LiteralPath (Join-Path $taskEvidenceOutput 'phase07-frontend-final-tests.log') -Raw
$taskFrontendSummary = [regex]::Match($taskFrontendLog, '(?m)^\s*Tests\s+(\d+) passed \((\d+)\)')
if (!$taskFrontendSummary.Success -or $taskFrontendSummary.Groups[1].Value -ne $taskFrontendSummary.Groups[2].Value) { throw 'Missing or unsuccessful final frontend summary' }
$taskFrontendCount = [int]$taskFrontendSummary.Groups[1].Value
$taskReadme = @'
# WorkBuddy Manager 本地实验候选

这是未签名的 Windows x64 优化构建，尚未正式发布。
真实三账号登录/切换、真实签到/积分及官方会话迁移尚未验收，生产签到和会话写入保持关闭。
阅读 INSTALLATION.md、RELEASE_NOTES.md 和 KNOWN_LIMITATIONS.md 后再试用。
用户指南、安全审查、当前验收范围和测试报告分别在 USER_GUIDE.md、SECURITY_REVIEW.md、ACCEPTANCE_PLAN.md、TEST_REPORT.md。
evidence/ 保存本轮原始日志及截图；TEST_REPORT.md 中较早阶段的历史日志仍在完整工程中。
安装器为当前用户安装，需要 WebView2；使用端无需 Go、Rust、Node.js。
默认数据目录：%USERPROFILE%\.workbuddy-manager。普通资料导出不是凭证备份。
本目录可执行文件是 NSIS 安装后保留的版本；它与构建缓存文件可能只存在 Tauri bundle type 标记差异。
不要把本地候选当作经过平台许可或生产兼容认证的正式产品。
'@
$taskReadme | Set-Content -LiteralPath (Join-Path $taskOutput 'README.md') -Encoding utf8
$taskFiles = @()
$taskResolvedOutput = (Resolve-Path -LiteralPath $taskOutput).Path
foreach ($taskFile in (Get-ChildItem -LiteralPath $taskOutput -File -Recurse | Sort-Object FullName)) {
    if ($taskFile.FullName -eq (Join-Path $taskOutput 'manifest.json') -or $taskFile.FullName -eq (Join-Path $taskOutput 'SHA256SUMS.txt')) { continue }
    $taskRelativeName = $taskFile.FullName.Substring($taskResolvedOutput.Length + 1).Replace('\','/')
    $taskSignature = if ($taskFile.Extension -eq '.exe') { (Get-AuthenticodeSignature -LiteralPath $taskFile.FullName).Status.ToString() } else { $null }
    $taskFiles += [ordered]@{name=$taskRelativeName;path=$taskFile.FullName;bytes=$taskFile.Length;sha256=(Get-FileHash -LiteralPath $taskFile.FullName -Algorithm SHA256).Hash;authenticode_status=$taskSignature}
}
$taskManifest = [ordered]@{
    product='WorkBuddy Manager';version=$taskVersion;classification='local experimental candidate, not public release';build_profile='release optimized';target='Windows x64';app_commit=$taskAppSha
    upstream_switch_commit='9eb3f2a21ff3c3c85fef2f89e693c48792050ba1';upstream_helper_commit='10caebd9a1a848871ed5ada57d9c66d56d2e7a48'
    code_signed=$false;smartscreen_trust_verified=$false;rust_tests_passed=$taskRustCount;frontend_tests_passed=$taskFrontendCount;test_evidence=@('evidence/phase07-all-tests.log','evidence/phase07-frontend-final-tests.log');real_account_tests_executed=$false;production_checkin_enabled=$false;production_session_writes_enabled=$false
    license_release_source_correspondence_verified=$false;source_archive_includes_historical_upstream_assets=$true;files=$taskFiles
}
$taskManifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskRoot 'docs\evidence\windows-manager-artifacts.json') -Encoding utf8
$taskManifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskOutput 'manifest.json') -Encoding utf8
$taskFiles | ForEach-Object { "$($_.sha256)  $($_.name)" } | Set-Content -LiteralPath (Join-Path $taskOutput 'SHA256SUMS.txt') -Encoding utf8
Write-Output $taskOutput
Write-Output "Product source commit: $taskAppSha"
