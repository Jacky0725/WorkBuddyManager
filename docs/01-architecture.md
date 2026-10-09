# 阶段 01：工程与基线结构

## 工程安排

根仓库记录任务书、审查、构建证据和 submodule pins。`upstream/workbuddy-switch` 与 `upstream/workbuddy-helper` 固定在发布标签并保持源码不改动。`app` 从主项目完整本地 Git 仓库复制，保留历史，开发分支 `develop/workbuddy-manager`，上游远端来源保持 GitHub URL；不向原作者仓库推送。

主工程继续使用 React/TypeScript 前端、Tauri 2 host、wb-switch-core 业务层。Go Helper 只作行为参考，不启动长驻 Helper HTTP 服务。上游 Agent Companion runtime 属于已有功能的辅助进程，与合并两个工具长期互调是不同的架构问题，后续需决定是否保留并为其隔离权限。

## 测试与产物

`scripts/Test-Baseline.ps1` 校验上游 SHA 与工作树，注入 WB_SWITCH_HOME/APPDATA/LOCALAPPDATA，并运行单个目标测试；执行后恢复进程环境。只运行测试，不登录、签到或切换 WorkBuddy。

桌面原版资源构建使用上游 `npm run build:desktop`，实际编译 companion runtime。打包专用 overlay `scripts/baseline-tauri-config.json` 在资源已准备后跳过重复 beforeBuild，关闭需要上游签名密钥的 updater artifact 生成，便于保存未签名本地基线安装器。此 overlay 不代表统一产品发布配置；安装器不得安装到用户正式环境或分发为 WorkBuddy Manager。

原版桌面测试先复现 E0425，随后 app 中单行限定测试调用修复（`ccd7552`），34 个 Windows 桌面测试通过；没有更改托盘运行时行为。构建记录和哈希保存在 docs/evidence。真实 UI 启动、安装和卸载不计作完成，只有实际验证后才能更新状态。阶段 01 尚未添加任何新业务功能；阶段 02 及之后必须遵守阶段门禁。

原版 x64 NSIS debug 基线已构建成功并保存哈希；Authenticode 状态在 artifact 清单中记录。app 的本地开发提交通过 incremental Git bundle 保存，依赖固定上游基线；bundle 已在拥有该基线的仓库中 verify 成功。不向原作者仓库推送本地分支，也不把无法远端取得的 submodule SHA 当作已公开源码。

阶段 01 状态：编译、现有测试与原版打包已验证；安全隔离的真实桌面 UI 启动、安装/卸载未执行。当前没有可用于该验收的 native UI 控制通道，不用普通生产模式启动代替可视验收。后续隔离开发状态见 `02-account-and-credentials.md`；阶段 01 的可视验收没有因此被计作完成。
