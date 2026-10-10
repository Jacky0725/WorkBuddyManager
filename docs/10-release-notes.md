# 0.2.0-alpha.1 本地候选说明

此候选用于隔离开发验收，尚未正式发布，也未宣称已支持 WorkBuddy 国内版 5.7.7 的真实账号操作。

- 新增统一每日计划界面和双 host 配置服务，北京时间计划、持久幂等与未知结果核实由 Rust 核心实现。
- 新增 DPAPI 账号加密备份、预览确认恢复、索引版本检查与恢复前回滚备份。
- 账号索引与凭证分离，公开导出只含资料；默认独立 `.workbuddy-manager` 数据目录。
- 所有浏览器 API 使用本机会话并验证来源；原生导出由后台系统对话框选择路径。
- 增加日志脱敏、认证写入锁、会话一致快照与生产兼容性门禁。
- 使用独立名称/identifier、自有 WM 标识；关闭上游自动更新、自动网络任务与可选 Companion。
- 更新构建依赖 source-map-js 至锁定 1.2.2，保留所有既有测试失败证据。

优化版 app 提交为 `5c493712b9e6d381b67677dd565c45b9f257d4e0`，功能提交为 `0cd8baa4383efe20f0a342dc1c4534443968697a`，最终提交仅修正许可/对应源入库字节。产物完整 SHA256、签名与构建模式见工程 `docs/evidence/windows-manager-artifacts.json` 或交付目录 `manifest.json`。测试结果见工程 `docs/06-testing.md` 或交付目录 `TEST_REPORT.md`。源历史通过 app Git checkout 和 `app-development.bundle` 保留。Windows 11 25H2 隔离桌面与安装循环通过，848 项 Rust 和 35 项前端测试通过。

尚未完成：真实三账号登录/切换、签到/积分授权及实测、官方会话写入兼容性、Windows 10 与 11 22H2 验收、历史素材/特定依赖发行源对应核对及正式分发审查。具体阶段状态见工程 `docs/11-known-limitations.md` 与 `docs/13-acceptance-plan.md`，交付目录另有 `KNOWN_LIMITATIONS.md`。完整任务书尚未全部验收。
