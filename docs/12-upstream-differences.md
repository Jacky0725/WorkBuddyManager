# 与上游的差异记录

基线为 Switch v0.1.58 / `9eb3f2a21ff3c3c85fef2f89e693c48792050ba1`。

| 阶段/提交 | 文件 | 改动 | 验证 |
| --- | --- | --- | --- |
| 01 / app `ccd7552` | src-tauri/src/tray.rs:1032 | 测试调用改为 super::taskbar_uses_light_theme，修复 Windows E0425 | cargo test --locked -p wb-switch-rust：34 passed |
| 02 / app `7c4c0cc` | core 账号/凭证服务、两种 host、前端导出 | DPAPI、独立能力、区域隔离与普通导出白名单 | Rust 786 + 前端 24 passed |
| 03 / app `b85f9c3` | checkin_service 与 Mock HTTP 集成测试 | 严格业务状态、取消、批量、超时核实与仅回环适配器 | core 755 passed，含 12 Mock 测试 |
| 04 / app `7e23cbd` | daily_scheduler、scheduler_clock、Mock 组合测试 | 北京时间、持久幂等、补执行、重启核实与跨进程锁 | Rust 817 + 前端 24 passed，含 18 调度测试 |
| 05 / app `914ae80` | session/session_backup/session_safety、switch、关联组门禁 | 独立 SQLite 快照、运行/版本门禁、事务与外键/路径检查 | Rust 829 + 前端 24 passed，新增 12 会话安全用例 |
| 06 / app `64027f1` | manager_scheduler、双 host、每日计划页、账号卡片与设置 | 配置锁与版本冲突保护、生产门禁、只读演示与中文状态 | Rust 839 + 前端 33 passed；截图/桌面 UI 验收未完成 |

阶段 02 新增 account_repository/credential_store 和 account_security 集成测试；修改账号身份匹配、存储、公开导出、失效提示、桌面切换前凭证门禁与异步刷新 CAS。Tauri 删除命令使用统一带锁服务，列表读坏库返回错误。签到/积分生产入口增加授权边界关闭门禁；前端导出说明与类型同步更新。

core 使用已有锁文件中的 fs2 0.4.3，没有更改其他依赖版本。阶段 02 Rust 786 与前端 24 测试通过。没有迁移生产账号或官方会话库，也没有移植国际仿客户端活动。上游 checkout 不提交手工改动，app 保留完整历史并在独立分支开发。

根仓库新增审查/测试文档、证据采集脚本、隔离测试 wrapper，以及本地打包 overlay。Overlay 跳过已经完成的前端构建并关闭需要上游私钥的 updater artifacts；没有改变上游运行时网络端点或更新身份，不得把原版基线安装器当作统一产品发布。

Tauri 会生成 permissions 并可能调整 Cargo manifest，属于构建副作用；保留相关 diff 记录，并在构建结束恢复固定 checkout，不将它们混入手工修复提交。

阶段 06 移除 host 原随机时间窗口签到循环，后台只读取新配置并记录心跳。生产执行仍禁用，未用环境变量提供放行入口。详细完成范围与未验收项目见 `06-manager-ui.md`。
