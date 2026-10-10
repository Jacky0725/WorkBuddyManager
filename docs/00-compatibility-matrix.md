# 阶段 00：兼容性矩阵

日期：2026-10-08。`存在源码`、`隔离测试通过`、`真实环境验证` 分开记录。

| 能力 | 国内版 | 国际版 | 本次证据 | 任务书差距/门禁 |
| --- | --- | --- | --- | --- |
| 账号增删备注 | 有源码 | 有源码 | account/commands/前端现有实现与单测 | 跨 region uid 唯一性修正；统一能力与状态模型 |
| 用户交互授权 | 插件 state/token 流程 | workbuddy-ai 流程 | oauth/variant 源码 | 无真实登录，scope/audience/issuer 未验证 |
| 桌面切换 | 有源码 | 有源码 | auth_file/process/switch 单测 | 无真实切换；先加固凭证与全流程锁/恢复 |
| 5.6 加密信封 | 原样保留写回 | 依档位与文件格式 | envelope 单测 | 不解密真实信封；无法用于签到时提示独立重新授权 |
| 会话保留 | 保留原 owner 数据 | 依客户端布局 | session/switch 单测 | 无真实 A→B→C→A 验证 |
| 会话复制 | 有源码 | 布局同构才支持 | SQLite/JSONL fixture 单测 | 活动客户端写入门禁与一致性复制备份补强 |
| 手动增量同步 | 有源码 | 布局同构才支持 | SHA256、baseline、preview、恢复用例 | 官方客户端版本/schema allowlist 未建立 |
| 分歧/取消 | diverge + 显式覆盖 | 同核心逻辑 | session_link/session 测试 | 取消零写入、附件提示需 UI 回归 |
| WAL 一致备份 | 同步有 Backup API | 同布局 | snapshot_workbuddy_db/quick_check | 复制是 raw DB/WAL/SHM copy，需统一一致性快照 |
| 备份恢复产品 | 操作临时快照与恢复 | 同核心逻辑 | 中断恢复 fixture | 成功备份会清理；缺长期安全备份/恢复页 |
| 签到 | 有 Rust 代码 | Unsupported，发请求前跳过 | core 测试 | 私有接口风险，真实功能 disabled 直至边界确认 |
| 自动签到 | 当前按 Local/窗口 | 不适用 | 调度纯逻辑测试 | 改为 UTC+8 09:15、补执行开关、持久日幂等 |
| 积分与套餐到期 | 有解析器 | 有分区回退 | 解析测试 | 非公开字段；真实接口未验证 |
| Token 统计 | 有解析器 | 有解析器 | 本地虚构日志解析测试 | 真实日志未读，数据根隔离需保持 |
| DPAPI manager 凭证 | Switch 普通 JSON；Helper DPAPI | 同 | 源码检查 | 不允许接入真实账号直到统一安全存储完成 |
| 单实例/自启动 | Tauri 插件已有 | 共用 host | 源码检查 | 未启用自启动；跨数据 host 调度锁需补强 |
| Windows 10/11 x64 | 开发 host 可编译 core/server/前端 | 相同二进制 | 本机工具与测试记录 | 双 OS 安装/卸载、真实桌面运行尚未验收 |
| 国际自动活跃 | 不适用 | Helper 有模拟客户端请求 | ActiveChat 等源码 | 明确排除，不移植、不执行 |

WorkBuddy 官方客户端版本没有通过读取本机生产安装或数据确定；不能声称对某个真实客户端版本兼容。代码提到 5.x/5.6 是上游实现背景，需经 fixture schema 与获授权测试环境确认后成为支持矩阵。

禁止把 schema 表存在当成完整兼容验证，或把 current target 非活跃当作整个共享 SQLite 数据库无人写入。

## 阶段 07 当前状态（2026-10-10）

上表保留阶段 00 当时审查结论。后续已实现 Manager DPAPI 凭证/加密备份、一致 SQLite 快照、UTC+8 持久调度、本机会话和独立 UI；自动回归 848 Rust + 35 前端通过。Windows 11 家庭中文版 25H2 / 10.0.26200 x64 已完成虚构资料正常桌面和隔离安装/卸载/重装验收。

国内版 v5.7.7 与 Windows 11 22H2 是用户报告目标，官方客户端版本/schema 未读取核验，22H2 和 Windows 10 未实测。真实授权、三账号切换/会话保留、签到/积分及生产会话复制/同步全部未执行；生产请求/写入保持禁用。不能把历史源码能力或当前 fixture 回归当作官方客户端兼容认证。逐项范围见 `11-known-limitations.md` 和 `13-acceptance-plan.md`。

## 阶段 08 当前状态（2026-10-10）

已收到用户“授权读写兼容核验”。实际安装 PE FileVersion 为 5.7.7、ProductVersion 为 5.7.7.0；本机 OS 仍为 Windows 11 25H2。只读采集 workbuddy.db（11 表、14 显式索引，sessions 40 列）和 edge-sync-mapping-v4.db（3 表、1 显式索引）的结构元数据，未读取凭证或业务记录。历史阶段 00/07 的“未读取”结论保留用于追溯，当前以本节为准。

在重建空结构与虚构会话上运行实际复制、增量同步、WAL 备份和事务回滚算法，核心 Rust 804 与 Python 结构探针 3 用例通过。云绑定原样复制及 deleted_at=-1/NULL 差异已记录为未解决事项，未据此加入官方版本 allowlist。真实官方业务、国际版、Windows 10/11 22H2 未验收，生产写入/请求门禁仍关闭。详见 `14-workbuddy-577-compatibility.md`。
