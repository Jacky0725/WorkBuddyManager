# WorkBuddy 国内版 5.7.7 兼容核验

日期：2026-10-10。用户授权原文：“授权读写兼容核验”。本轮完成实际版本和数据库结构核验，以及重建空结构上的虚构数据读写测试；尚未通过官方业务兼容验收。

## 实际环境与执行范围

| 项目 | 实际证据 |
| --- | --- |
| 官方安装 | D:\Program Files\WorkBuddy\WorkBuddy.exe，PE FileVersion 5.7.7，ProductVersion 5.7.7.0 |
| Windows | Windows 11 家庭中文版 25H2，10.0.26200 x64 |
| 数据目录 | C:\Users\admin\.workbuddy |
| 主数据库 | workbuddy.db：11 表、14 个显式索引；sessions 40 列；schema_version 57，user_version 0 |
| 映射数据库 | edge-sync-mapping-v4.db：3 表、1 个显式索引 |
| 官方进程 | 观察时仍运行，本轮未关闭 |
| 写入范围 | 从观察到的 DDL 重建隔离空库，写入虚构身份和正文，运行 Manager 实际算法 |

Windows 11 22H2 是此前用户报告值，不能由本机 25H2 结果推断通过；Windows 10、国际版未测试。环境证据见 [phase08-observed-environment.json](evidence/phase08-observed-environment.json)。

只读探针使用 SQLite mode=ro、query_only、只允许结构查询的 SQL authorizer 和读事务，拒绝业务表 SELECT、函数调用、写入、ATTACH 及 PRAGMA 赋值。只采集表/索引 DDL、列、外键和数据库结构设置。读事务提供每个数据库自身的一致结构观察，不宣称两库之间有原子快照，也没有导出真实数据的完整备份。没有读取 Token、认证文件、日志、真实会话正文或业务行，没有真正登录、签到或修改官方数据库。

主库两次结构观察的 SHA256 相同：`60f8b135b51659f0afbdef9d562f9aa1253fb085aabd46e7b5c0234e8ad61de4`。映射库结构观察 SHA256：`debe65eaa2398142197da2fd7ba5b191a2233249c04c441a54f22c405c669d83`。这些是规范化结构元数据的哈希，不是数据库文件哈希，也不是可信版本 allowlist。

## 隔离算法验证

两份 SQL fixture 的重建 sqlite_schema 与观察到的 DDL 对应一致；不含真实记录。app `5c1e50fcbab4aeaa86d90d3ca27ea3cb178b7cbf` 只增加测试模块和 fixture，运行时代码与生产门禁未变。

| 新增用例 | 验证结果及边界 |
| --- | --- |
| 本地会话复制 | 新 UUID 和目标 owner；源行/源正文保留；transport=local；不预写 edge 映射；数据库完整性通过 |
| 手动增量同步 | 实际预览和 FastForward 后目标正文更新；源正文、目标 owner、标题和备注保留；无待恢复操作 |
| WAL 一致备份 | 未 checkpoint 的虚构行进入 Backup API 快照；快照独立可读、完整性通过 |
| 复制行事务失败 | 注入虚构触发器失败后不留下目标行；源行保留；完整性通过。此项只验证行事务，不替代跨文件崩溃恢复验收 |
| 云绑定与删除标记现状 | 确认现有算法原样复制云绑定，并确认 deleted_at=-1 不被现有 owner 查询识别；这是风险行为记录，不能解释为云会话兼容通过 |

核心 Rust 共 **804 passed，0 failed/ignored**（731 单元 + 73 集成用例），包含上述 5 个新增用例。Python 探针保护 **3 passed**，覆盖不返回虚构业务内容/不改数据库字节、拒绝业务读取及写入、识别未 checkpoint 的 WAL 结构。host/前端未改动，本轮没有重复其阶段 07 测试；不可把不同轮次计数合并成全工程新结果。

首轮探针的 SQL LIKE 因函数权限拒绝而失败，已改为 Python 过滤内部名称。首轮 Python 测试在 Windows 临时目录清理时因连接未关闭失败，已使用明确 close；失败记录与修正后的结果均保留。证据见 [算法与结构结果](evidence/phase08-compatibility-results.json)、[核心日志](evidence/phase08-core-tests.log)、[探针日志](evidence/phase08-schema-probe-tests.log)、[首轮探针失败](evidence/phase08-probe-first-failure.json)、[首轮清理失败](evidence/phase08-schema-probe-first-failed-tests.log)。

复查隔离测试：

```powershell
python scripts/test-schema-probe.py
./scripts/Test-Development.ps1 -Target Core
```

`python scripts/probe-workbuddy-schema.py --version 5.7.7 --output docs/evidence/NEW-SCHEMA-EVIDENCE.json` 会再次读取实际安装的数据库结构，仅应在对应授权环境执行；参数是独立观察到的版本记录，不会自动验证 PE。输出文件必须事先不存在，以保留历史证据。

## 尚未解决的官方语义

sessions 新字段包括 transport、group_id/group_title、buddy_snapshot_id/buddy_binding_json 及同步/可见性状态。结构中还存在 buddy_snapshots。现有按列复制会保留这些值，虚构用例证明跨 owner 复制后 transport=cloud、group_id、buddy_snapshot_id 未变。不能仅修改 user_id 就推断云身份、分组和快照仍有效；也不能在未知含义下随意清空这些字段。

官方云部分索引使用 `transport='cloud' AND deleted_at=-1`，当前 Manager 的 owner/部分会话查询使用 `deleted_at IS NULL`。这证明结构条件有差异，但不能仅从索引推出全部本地或云会话的活动/删除约定。需官方行为或受控测试事实后再选择过滤规则，不能直接将 NULL 和 -1 全部当作可写会话。

映射库有 conversation 映射、附件缓存和图片映射结构。当前复制不预写 edge 映射，本轮只证明虚构复制保持空映射，尚未证明官方客户端能够建立正确映射、展示附件或安全接管云会话。正文兼容也只基于虚构 JSONL，真实格式和客户端显示尚未验收。

任务书 [12 节](PROJECT_TASK_V1.md) 原文要求“遇到以下情况时必须停止相关高风险操作并报告”，列举“无法确定协议或授权边界”“客户端数据库 schema 不兼容”等条件。本轮已观察到复制/查询规则与新增结构的差异，且云字段语义未知，因此暂停受影响的生产写入；这里不是宣称整个 5.7.7 schema 已被判定不兼容。10.3 原文要求“需要用户明确授权后，才允许进行真正的登录、签到或会话迁移测试。”这是尚缺事实证据导致的限制，不是遗漏已收到的读写核验授权。生产版本 allowlist 仍为空，签到/积分请求及会话写入入口继续关闭。

## 下一步与产物关系

先确定版本及本地/云会话的支持范围、删除状态、云绑定/快照和附件复制规则，再形成空白测试项目上的具体操作清单、备份校验及回滚办法，才能开展受控官方客户端业务验收。真实三账号切换、会话保留、一次签到、系统登录自启动、双系统验收和许可源对应仍未完成，不标记整份任务书完成。

阶段 07 安装候选仍固定于 app `5c493712b9e6d381b67677dd565c45b9f257d4e0`，没有因测试新增而重打包。根工程开发 bundle 已包含 `5c1e50f`；候选目录的源码、bundle、哈希和报告保持冻结。候选校验按清单中的历史提交验证，不能把当前开发 HEAD 与历史候选混为同一产物。

后续阶段 09 静态读取已安装程序，确认本地 NULL / 云 -1 活动条件，并增加云、Buddy/官方分组绑定的拒绝规则；当前算法不再允许本节记录的云绑定复制。阶段 08 的事实、测试和提交保留为历史，最新开发行为见 [本地迁移范围](15-local-session-transfer-policy.md)。生产入口仍未开放。
