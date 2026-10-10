# 安装与升级

候选产品：WorkBuddy Manager 0.2.0-alpha.1，Windows x64，普通用户 NSIS 安装，identifier `com.workbuddymanager.app`。本地交付目录为 `D:\codex\WorkBuddyManager\release\0.2.0-alpha.1\local-candidate`；安装包位置与 SHA256 以 `manifest.json` / `SHA256SUMS.txt` 及工程中的 `docs/evidence/windows-manager-artifacts.json` 为准。历史原版安装器不是 Manager 产物。

此版本为本地实验候选，真实账号功能未验收，尚不作为正式版本公开分发。安装器未代码签名；没有 SmartScreen 信任验证。运行需要 Microsoft WebView2，使用端无需安装 Go、Rust 或 Node.js。不要通过自动化绕过 Windows 安全提示。

## 普通用户安装

1. 核对产物清单中的 SHA256，确认版本与来源。
2. 打开 Manager 安装包，选择当前用户安装目录。
3. 首次打开查看账号管理、自动签到、备份与恢复和操作日志。
4. 本地试用使用空账号库；真实授权与导入应在确认测试范围后由用户操作。

Manager 默认数据目录为 `%USERPROFILE%\.workbuddy-manager`，凭证与备份绑定当前 Windows 用户。不会自动迁移旧 `%USERPROFILE%\.wb-switch` 账号库。WorkBuddy 官方登录与数据库仍由官方客户端管理，不在这个数据目录内。

## 升级与回滚

1. 在原 Manager 版本中创建加密备份并确认列表中没有错误。
2. 关闭托盘进程，保留完整 `.workbuddy-manager` 目录副本；不要把普通公开导出当作凭证备份。
3. 阅读新版本存储版本说明，使用对应候选安装包升级。自动更新已关闭。
4. 如升级失败，关闭 Manager，重新安装此前固定版本；仅在存储格式兼容时恢复加密备份。
5. 未改造的 Switch/Helper 不能直接读写 Manager 账号库；不得把 Manager 索引交给旧版本覆盖。

本机 Windows 11 25H2 隔离安装/卸载/重装验证后，三条虚构资料、两份加密备份和每日计划保留，所有 fixture 文件 SHA256 不变；未在 Windows 10 或 11 22H2 验证。具体证据在工程 `docs/06-testing.md`，交付目录中提供 `TEST_REPORT.md`。跨电脑、跨 Windows 用户或重装系统后的 DPAPI 解密不保证可用，应重新授权。

开发复现：`scripts/Test-Development.ps1 -Target All`；`scripts/Build-Manager.ps1` 生成优化构建，`-DebugBuild` 生成本地调试候选。脚本独立测试数据目录，不安装或启动客户端。

交付材料复核：在完整工程运行 `python scripts/verify-manager-candidate.py`，核对完整载荷 SHA256、许可文本、MPL 对应源、源码 ZIP 与 app 提交、开发历史 bundle。`scripts/Collect-ManagerArtifacts.ps1` 首次收集需要已安装在指定 fixture 内的优化版；`-RefreshMetadata` 仅在旧载荷哈希和 app 提交未变化时刷新文档/证据，不替换安装器或源码。校验不代表真实业务兼容或分发审查已经完成。
