# 阶段 00：原版构建基线

日期：2026-10-08。所有结果区分源代码检查、实际命令结果与未执行项目。

## 环境

| 项目 | 版本/状态 |
| --- | --- |
| Git | 2.54.0.windows.1 |
| Node.js | 24.18.0，较上游 CI 的 22 新；未主动升级 |
| npm | 11.16.0 |
| rustc / Cargo | 1.96.0，stable-x86_64-pc-windows-msvc |
| Rust target | x86_64-pc-windows-msvc 已安装；另有 wasm32-unknown-unknown |
| Go | 系统 PATH 无 Go；项目内下载 go1.26.0 windows/amd64，与 go.mod 一致 |
| Go 来源 | https://go.dev/dl/go1.26.0.windows-amd64.zip；官网 JSON 与实际 SHA256 比对通过 |
| Go SHA256 | 9bbe0fc64236b2b51f6255c05c4232532b8ecc0e6d2e00950bd3021d8a4d07d4 |
| VS Build Tools | 2022 17.14.37411.7；VC.Tools.x86.x64 组件已验证 |
| MSVC | 工具目录 14.44.35207；cl 19.44.35228 x64，不在普通 shell PATH 但可直接访问 |
| Windows SDK | 10.0.26100.0 |
| WebView2 Runtime | 154.0.4258.62，注册表可见 |
| .NET SDK | PATH 未找到，本项目不要求以 .NET 为主体 |

没有升级系统工具链，没有启用系统自启动或计划任务。Go 仅解压在 tools/；缓存与依赖以锁文件为准。

## 隔离

测试进程设置 `WB_SWITCH_HOME` 为 `test-fixtures/baseline-home`，同时将 APPDATA/LOCALAPPDATA 注入 `test-fixtures/baseline-appdata` 与 `baseline-localappdata`。不覆盖 HOME、USERPROFILE 或 CODEX_HOME。core 集成测试另有自身临时目录注入。Cargo 主要测试使用 `test-fixtures/cargo-target`；上游 companion 脚本自带 `target/` 路径，运行前已核对其输出/清理目录均在源码 checkout 内。

未执行 WorkBuddy 切换、登录、正式会话读写或生产 API 请求。原版常规启动可能主动导入本机账号、安装 hook、签到/旅行/保活，禁止直接运行。native UI 的可视验收尚未执行。

## 命令和结果

| 命令 | 实际结果 | 证据 |
| --- | --- | --- |
| git ls-remote / git clone / checkout --detach tag | 两项目成功，完整历史保留 | upstream-pins.json + 固定 submodule |
| npm ci --ignore-scripts | 成功，212 packages；有 1 high vulnerability | switch-npm-ci.log |
| npm test | 24 passed，2 files，0 failed | switch-frontend-test.log |
| npm run build | TypeScript + Vite 成功；大 chunk 告警 | switch-frontend-build.log |
| cargo test --locked -p wb-switch-core | 719 单元 + 5 集成，0 failed，0 ignored；doc-tests 0 | switch-core-test.log |
| cargo test --locked -p wb-switch-server | 9 passed，0 failed | switch-server-test.log |
| cargo fmt --check -p wb-switch-core -p wb-switch-server -p wb-switch-rust | exit 0 | switch-fmt.log（空日志代表无格式差异，退出码已记录） |
| npm run build:desktop | 成功；真实编译 companion runtime 与嵌入页面、复制 dist/companion | switch-desktop-assets-build.log |
| Go 1.26.0 test -json ./... | 135 passed tests、4 skipped、无 fail；模块包测试通过 | helper-test.jsonl |
| Go 1.26.0 vet ./... | exit 0 | helper-vet.log |
| Go 1.26.0 build -trimpath -buildvcs=false ./cmd/workbuddy-helper | exit 0，生成 Windows exe，未运行 | helper-build.log；test-fixtures/baseline-binaries/WorkBuddyHelper.exe |
| npm audit --json | exit 非零；source-map-js high，GHSA-68fv-2mgg-jv7q | switch-npm-audit.json |

Helper 4 个 skip：TestConfigFileRejectsNonRegularTargets、TestStateLoadRejectsSymlinkTarget、TestKeyFileCreatedOnSave、TestPortableKeyRejectsNonRegularTarget。后两项为 Windows 默认 DPAPI 与 portable backend 分支差异，前两项平台/链接条件不满足；不把 skip 算作通过。无代码覆盖率测量。

## 桌面原版失败

桌面 `cargo test --locked -p wb-switch-rust` exit 101，未执行桌面用例：`src-tauri/src/tray.rs:1032` 测试模块未限定调用 `taskbar_uses_light_theme`，报 E0425。完整证据 `switch-desktop-test.log`。另有 1 条 host unused-import 和 18 条 vendored plugin 告警，不隐藏。

阶段 01 只在 `app` 开发分支用 `super::taskbar_uses_light_theme()` 修复测试符号解析，提交 `ccd7552`。修复后 `cargo test --locked -p wb-switch-rust` exit 0，34 passed、0 failed、0 ignored；Windows cfg 用例数与上游 macOS 的用例数不相同。复测独立保存为 `app-desktop-test.log`，不覆盖原失败证据。

Tauri 构建会重新生成 vendored plugin permissions，产生本平台换行/生成文件状态变化；已保存 diff 证据，源码手工修改仅为 app 测试函数限定。构建结束后恢复原版 generated permissions，确认上游 tracked tree 清洁。未使用 git clean 或对用户文件执行删除。

原版 Windows x64 NSIS 基线构建 exit 0，命令：`npm run tauri -- build --debug --bundles nsis --config <scripts/baseline-tauri-config.json> --no-sign -- --locked`。证据 `switch-windows-baseline-build.log`。上游 exe、NSIS、真实 companion runtime 已复制到 `test-fixtures/baseline-binaries/switch-original-v0.1.58/`，SHA256 与大小见 `windows-baseline-artifacts.json`。

该产物是原版 0.1.58 debug 本地基线，未签名、不属于 WorkBuddy Manager 统一产品发布；未安装、未做真实 UI 或 Windows 10/11 双系统验收。没有验证 SmartScreen 信任。阶段 01 的编译/测试/打包部分完成，启动/安装部分仍未验证。

## 已知限制

- 原锁文件含 source-map-js 1.2.1 高危告警；本阶段不自动 npm audit fix。单独开发分支最小修复后再做回归。
- 上游 build:app 脚本面向 macOS，含签名密钥文件读取；未使用。Windows 复用 Tauri CLI / CI NSIS 路线；上游 updater 配置未作为本项目可发布配置。
- 锁版本未变；未用伪造 sidecar/stub 可执行文件冒充完整 baseline。
- GitHub API 403/rate-limit-exceeded，release 和 Issue 获取失败；发布标签由网页与本地 tag SHA 对照，不依赖失败 JSON 推断成功。
- 原版功能自动测试通过不代表 WorkBuddy 官方真实版本兼容或服务方许可。
