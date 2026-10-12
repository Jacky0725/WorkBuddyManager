# 已执行测试与当前数据状态核对

日期：2026-10-12。用户确认账号 A=国内版工作号、B=国内版个人号、C=国内版备用号；先给出 `D:\WorkBuddy\TestProject`，随后明确当前要核对的测试项目为 `D:\codex\WorkBuddyManage`。用户指出“测试文字 123”测试已在此前对话执行。本轮不重复复制、同步、登录或签到。

## 历史测试能证明什么

[阶段 11 实测报告](17-real-account-acceptance-report.md)及对应证据记录了 2026-10-10 在官方 WorkBuddy **5.7.7** 下的 A→B 本地会话复制、官方界面加载，以及 B 后续交互；A 原会话 ID 为 `42754e64-2a01-48a8-bda1-7ffa6010d772`，B 复制 ID 为 `260dddb6-93d6-415b-8626-7307886a95e5`，项目为 `D:/codex/WorkBuddyManage`。该报告明确将 C 列为计划，不能把 A/B 历史结果记作 A→B→C→A 通过。历史报告中的“通过”只针对当时的人工观察，不能代替当前 5.8.1 状态与保留性验证。

## 本轮只读现状

只对上述两个精确会话 ID 查询当前 `~/.workbuddy/workbuddy.db` 的 ID、owner、cwd、transport、deleted_at；使用 SQLite `mode=ro` 与 `query_only=ON`，未读取正文、标题或其他会话记录。官方客户端当前为 **5.8.1**。
本轮的限定范围和结果另存于 [phase13-confirmed-test-scope-current-state.json](evidence/phase13-confirmed-test-scope-current-state.json)。

| 项目 | 2026-10-12 观察 |
| --- | --- |
| 测试项目路径 | `D:\codex\WorkBuddyManage` 存在；先前给出的 `D:\WorkBuddy\TestProject` 不存在 |
| A 原会话 | 当前库存在；owner `686f63f2-c0e9-426c-8c98-a333a673589f`，cwd `D:/codex/WorkBuddyManage`，transport=`local`，deleted_at=`NULL`；对应 JSONL 存在 |
| B 复制会话 | 当前库无 `260dddb6-93d6-415b-8626-7307886a95e5`；阶段 11 记录的对应 JSONL 路径当前也不存在。项目目录下另有同 ID 的 101 字节 `.file-rollback.ndjson` 文件；未读取其内容或认定其可恢复 |
| Manager 账号索引 | `~/.workbuddy-manager/accounts.json` 有 2 条国内版 workbuddy 元数据，UID 分别对应 A、B；未见 C 的账号条目。未读取凭证 |
| 历史基线备份 | `test-fixtures/acceptance-backup/` 中数据库与 A JSONL 备份均存在，SHA-256 与其 manifest 匹配；该备份是在 A→B 测试前创建，不含 B 复制会话，不能当作当前完整库恢复点 |

当前没有 B 会话，不足以判断其消失原因；可能经过后续恢复、切换数据集或其他操作，本轮未作归因，也未写入或恢复任何文件。A JSONL 当前长度已大于测试前备份，故旧备份更不能直接覆盖当前数据。阶段 11 的“会话保留”结论需要标为**历史观察，当前状态未复现**。

## 未完成的验收

1. 当前 5.8.1 下 A/B/C 完整切换与保留：C 尚未加入 Manager 账号索引，且没有 C 的测试会话；当前 B 复制会话缺失。先由用户在官方流程完成 C 的登录/添加，并在测试项目创建仅含虚构文字的会话。无需提供密码或 Token。
2. 当前 5.8.1 会话复制/增量同步：须以明确的新测试会话 ID 开始，在独立备份和回滚校验后执行；不得用历史 ID 推断仍有 B 的测试副本，也不得覆盖现存 A 正文。
3. 第三方签到/积分接口授权：仍缺服务方对第三方调用的明确授权及适用凭证 scope；见 [5.8.1 授权与兼容报告](17-authorization-and-581-compatibility.md)。保持生产门禁关闭。

此记录只更新证据状态，不触发登录、网络接口调用或官方数据库写入。
