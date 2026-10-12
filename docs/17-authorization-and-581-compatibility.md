# 授权与 WorkBuddy 5.8.1 兼容性核验

日期：2026-10-12。此报告只陈述本轮实际完成的核验；不把结构相似、用户对本地测试的授权或历史 5.7.7 结果等同于服务接口授权或 5.8.1 业务兼容放行。

## 授权边界

用户此前明确回复“授权读写兼容核验”，本轮再次要求“现在完成授权与兼容性验证”。这足以继续本地兼容性核验；并不代替服务方对第三方签到、积分接口、凭证用途的授权。用户说三个测试账号和空白项目已准备好，但尚未提供 A/B/C 备注、当前空白项目路径和测试会话 ID。阶段 11 的 A/B 记录位于旧路径 `D:/codex/WorkBuddyManage`，不能据此选择当前测试数据或推定 C 已验收。

本轮查阅 [官方 Windows 安装与登录指南](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Installation-Win-Guide)、[官方自动化说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Automation-Guide)、[官方积分说明](https://www.codebuddy.cn/docs/workbuddy/Credits)。它们描述官方客户端登录、客户端内定时任务和积分使用，没有提供 WorkBuddy Manager 第三方调用 billing 签到/积分接口的公开授权流程、scope 或 API 兼容保证。未在这些资料中找到授权，不等于断言服务方绝不授权；截至本轮，项目没有可核验的授权依据。阶段 11 留存的 401/404 探测见 [phase11-checkin-auth-probe.json](evidence/phase11-checkin-auth-probe.json)；本轮没有读取 Token、重试私有端点或提交签到。

当前源码的 `Checkin` 和 `PointsRead` 能力仍标为 `Unverified`，请求入口被 `api_capability_error` 拦截；统一计划的 `production_enabled` 仍为 `false`，采用禁用的生产适配器。静态检查覆盖桌面手动/批量、服务端入口和计划入口；这不是在已安装历史候选二进制上做出的动态网络证明。真实签到、积分读取与自动调度继续关闭。

## 本机 5.8.1 结构与程序观察

安装文件 `D:\Program Files\WorkBuddy\WorkBuddy.exe` 的 PE FileVersion 为 **5.8.1**、ProductVersion 为 **5.8.1.0**。本机 Windows 为 Windows 11 家庭中文版 `10.0.26200` x64（与用户早先报告的 22H2 不同）；官方 WorkBuddy 和历史 Manager 候选在核验时均运行，没有结束进程。

本轮运行只读 SQLite 探针：`mode=ro`、`query_only`、只允许 schema/PRAGMA 元数据的 authorizer；未读取业务行、凭证或会话正文，没有写官方库。完整结构与哈希见 [phase12-workbuddy-581-schema-metadata.json](evidence/phase12-workbuddy-581-schema-metadata.json)。与 [5.7.7 基线](evidence/phase08-workbuddy-schema-metadata.json)比较：

| 数据库 | 5.7.7 结构 SHA-256 | 5.8.1 结构 SHA-256 | 事实 |
| --- | --- | --- | --- |
| `workbuddy.db` | `60f8b135b51659f0afbdef9d562f9aa1253fb085aabd46e7b5c0234e8ad61de4` | `a95c7b4e5e024d73522abacf2fde7af1136aebf73108b99eb63655410b83aac6` | `schema_version` 57→58；`automations` 新增 `wecom_bot_chat_id TEXT`；`sessions` 对象定义未变 |
| `edge-sync-mapping-v4.db` | `debe65eaa2398142197da2fd7ba5b191a2233249c04c441a54f22c405c669d83` | 相同 | 对象结构未变；`user_version` 0→1，仍需按版本区分 |

静态读取安装包程序的三个指定成员，结果见 [phase12-workbuddy-581-installed-code-facts.json](evidence/phase12-workbuddy-581-installed-code-facts.json)。5.8.1 不再有 `main/conversations.js`；`main/handlers.js` 仅 96 字节，旧的 Buddy 引用检查等模式不能在此复核；`main/server.js` 仍出现本地 `deleted_at IS NULL` 和云 `deleted_at=-1` 查询模式。模式缺失只说明旧定位方法失效，不证明约束已删除或迁移安全。与 5.7.7 的程序归档哈希也不同。

## 验收判定与下一步条件

| 能力 | 本轮判定 | 仍需事实 |
| --- | --- | --- |
| 本地结构读取 | 已通过 5.8.1 元数据核验 | 无业务行/正文结论 |
| A/B 桌面切号 | 历史 5.7.7 人工观察；5.8.1 未复验 | 当前 A/B/C 测试账号与空白项目、官方进程退出后的受控操作 |
| 本地纯文字会话复制与增量同步 | 隔离 fixture 和历史 5.7.7 A/B 记录；5.8.1 未放行 | 当前测试会话精确 ID、5.8.1 客户端接管、独立备份/哈希与可验证恢复 |
| 云、Buddy、官方分组、附件 | 未放行 | 各自的身份、引用和正文规则 |
| 签到与积分 | 授权和接口未验证，生产门禁关闭 | 服务方明确提供的第三方接口授权、适用凭证 scope/issuer/audience 与受控真实验收 |
| Windows 10/11 22H2、国际版 | 未验收 | 对应独立环境与版本 |

执行真实会话写入前，须收到只含虚构文字的当前 A/B/C 测试范围，复核 WorkBuddy 5.8.1 会话类型/正文格式，建立当前库与正文的一致备份、哈希和回滚步骤，并在官方进程安全退出后执行。`require_verified_client` 继续关闭，不能因 `sessions` 结构未变而自动放行。签到/积分则需单独取得服务接口授权，不能靠更换路径、模拟官方客户端头或重试私有路由来推断许可。

本轮探针保护测试：`python scripts/test-schema-probe.py`，3 passed；`Test-Development.ps1 -Target Core`，807 passed、0 failed，完整输出见 [phase12-core-tests.log](evidence/phase12-core-tests.log)。两份历史证据文件未覆盖；脚本现要求显式指定新的输出文件，并拒绝覆盖已有证据。
