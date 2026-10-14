# WorkBuddy 5.8.2 本地会话写入验收（2026-10-14）

范围：Windows 11 国内版 WorkBuddy 5.8.2，`D:\codex\WorkBuddyManage` 中无附件、文件历史备份、Buddy 或分组绑定的虚构本地会话。客户端已退出，先备份主数据库、映射数据库、源正文和 Manager 关联记录；两个数据库快照的完整性检查均为 `ok`。

- 5.8.2 可执行文件 SHA-256：`ffbcf6d43caed2868ce876948bf63e78fa244109282681fb6a1f9f534d717552`。主库和映射库结构摘要与 5.8.1 已验证结构一致。
- 通过现有复制入口完成 A→B、B→C，各生成一条目标会话，无错误；A/B/C 三条数据库记录分别归属各自账号，均为未删除的本地会话，工作区相同。
- 三份 JSONL 正文仅会话 ID 不同；关联表中只有一个包含 A/B/C 的三成员组，两次操作均为 `completed`，无未完成操作。
- 写后主库和映射库 `PRAGMA integrity_check` 均为 `ok`；切换测试后官方登录态恢复到账号 C。
- `cargo test -p wb-switch-core --test session_safety`：8 通过；`cargo test -p wb-switch-core modules::session::tests`：101 通过。
- `./scripts/Build-Manager.ps1 -EvidencePrefix phase24` 成功生成可执行文件与 NSIS 安装包；候选文件位于 `release/0.2.0-alpha.3/session-582-candidate-20261014/`，尚未安装或发布。

用户随后确认：账号 C 下的副本在官方 5.8.2 客户端中可见且可正常打开。复制的落盘和客户端读取因此通过本轮验收。

用户又在 C 的虚构会话中追加一条纯文字并退出客户端。新增后 C 为 17 条、B 为 11 条，双方无外部资源引用；预览仅给出 `fastForward` 模式。于 `%USERPROFILE%\.workbuddy-manager\backups\acceptance-582-sync-20261014-104821` 备份后执行 C→B 一次：`synced=1`、`skipped=0`、`errors=0`、`needsRecovery=false`。写后 B 与 C 均为 17 条，除会话 ID 外正文一致；主库和映射库完整性检查为 `ok`，无未完成操作。为核验客户端读取，当前暂切到账号 B，等待用户打开确认，随后须恢复原账号 C。

恢复路径目前只有自动化测试，没有本次真实客户端端到端验收。云会话、Buddy、附件及非空文件历史引用仍保持写入门禁，不属于本次开放范围。

验收前备份：`%USERPROFILE%\.workbuddy-manager\backups\acceptance-582-local-copy-20261014-103602`。
