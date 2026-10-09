# 阶段 00：只读源码审查

审查日期：2026-10-08，北京时间。范围为固定提交的源代码和本机隔离测试，不含真实账号、真实 WorkBuddy 数据或生产接口验证。

## 1. 基线与方法

| 项目 | URL | 标签 | SHA | 提交日期 |
| --- | --- | --- | --- | --- |
| Switch | https://github.com/changexbc/workbuddy-switch | v0.1.58 | 9eb3f2a21ff3c3c85fef2f89e693c48792050ba1 | 2026-10-04 12:34:22 +08:00 |
| Helper | https://github.com/autumnsentiment/workbuddy-helper | v1.0.6 | 10caebd9a1a848871ed5ada57d9c66d56d2e7a48 | 2026-09-23 07:16:35 +08:00 |

标签在 GitHub 有发布页；选择发布标签而非自动跟随 main。Switch main 在读取时为 `68468c17b3997d7eed965f1ae1eceb4992aa1efe`，未纳入基线。所选版本只是候选基线，不称为最稳定版本。完整历史已保留，来源和工作树状态见 `evidence/upstream-pins.json`。

文中 Switch 路径相对 `upstream/workbuddy-switch/`；Helper 路径相对 `upstream/workbuddy-helper/`。精确函数声明与行号见 `evidence/source-symbols.json`，测试声明清单见 `evidence/test-inventory.json`。审查以源码为证据，不将 README 功能描述当作验收结果。

## 2. Switch 入口、调用关系与风险

| 项目 | 文件、函数/类型 | 调用关系及事实 | 风险/结论 |
| --- | --- | --- | --- |
| Tauri 与 Rust 结构 | `Cargo.toml`; `src-tauri/Cargo.toml`; `crates/wb-switch-core/Cargo.toml` | workspace 含 core、HTTP server、桌面 host；Tauri 2；core 无 Tauri 依赖 | 可在 core 复用业务逻辑，统一桌面不需要附加 HTTP 管理服务 |
| 前端 | `package.json`; `src/App.tsx`; `src/lib/api.ts` | React 19、TypeScript 5.8、Vite 7、Tailwind 4、Radix、Zustand；api 桥接 invoke / web / demo | 不更换 UI 框架；已有功能远多于任务书要求 |
| Windows 包 | `.github/workflows/build.yml`; `src-tauri/tauri.conf.json`; `scripts/prepare-agent-companion.mjs` | Tauri CLI 先 build:desktop，编译内嵌 runtime，再构建 x64 NSIS | 仍需实际构建；上游更新公钥和 URL 不应沿用为本产品更新源 |
| 账号模型 | `account.rs::load_accounts/save_accounts/account_meta/upsert_collected_account` | `serde_json::Value` 数组；`config.rs::accounts_file` → `WB_SWITCH_HOME/.wb-switch/accounts.json` | 普通 JSON 包含明文 access/refresh token；无 capability 分离 |
| 唯一性 | `account.rs::upsert_collected_account/find_account` | 采集合并按 uid 优先、email 兜底；find 可按 id 或 uid | 采集合并未将 region 纳入匹配；同 uid 跨区可能混合，阶段 02 必修 |
| 授权 | `oauth.rs::oauth_start/oauth_poll`; `variant.rs::oauth_platform` | frontend OAuth dialog → commands → core；POST state 后由用户扫码/授权，轮询 token 和账号 | 是插件式 state/token 流程，不能据此宣称标准 OAuth scopes/audience 已验证；需人工交互，不能绕过挑战 |
| Token 生命周期 | `refresh.rs::ensure_fresh_token/refresh_account_token`; `config.rs::norm_ts` | 到期时间归一为毫秒；刷新请求使用 refresh token 与 source=plugin；失败标记 needs_relogin | 部分写入错误被忽略；网络失败可被标为需重新登录，错误分类需细化；刷新/账号写入并发需统一锁 |
| 国内/国际版 | `variant.rs::WbVariant::{Cn,Ai}/auth_file_path/data_root/billing_paths/supports_checkin` | 账号自带 variant；API、platform、文件名、数据根分区；只有国内版支持签到 | 边界已有代码；不能因有国际版 billing fallback 推断国际版签到存在 |
| 进程与切换 | `process.rs::is_workbuddy_running/close_workbuddy/launch_workbuddy`; `switch.rs::switch_account` | commands → 阶段锁 → 关闭客户端 → 恢复/复制/同步 → 写认证 → 重开 | 涉及实际进程和官方认证文件，阶段 00 不执行；restart=false 拒绝会话写入意图；认证失败的全流程恢复仍需专项验证 |
| 认证文件 | `auth_file.rs::read_auth_file_at/backup_auth_file/write_account_to_auth_file`; `variant.rs::auth_file_path` | Windows 路径从注入 home 派生 `AppData/Local/CodeBuddyExtension/Data/Public/auth/`；原子写后按值比较 token | 支持 WorkBuddy 5.6 `$wbEncrypted` 信封保留；不可将官方信封当作本工具 DPAPI 密文；写权限错误仍有 macOS 专用提示 |
| 本地导入和导出 | `commands.rs::import_local/export_accounts`; `export_import.rs::select_export_records/export_accounts_to_path` | import_local 经 core account_meta 返回脱敏账号（阶段 02 复核纠正）；export_accounts 返回完整 records 给前端；导出文件含 token | 导出违反令牌不得返回前端/普通导出要求，接入真实账号前阻断 |
| 会话定位 | `session.rs::SessionPaths/workbuddy_db_path/find_project_jsonl/current_user_uid_at` | JSONL 正文与 sessions 表共同组成会话；数据根从 variant 派生；扫描最大版本 edge-sync-mapping 文件 | cid 到路径的输入边界、符号链接/重解析点需专项验证；不得读取真实目录做初始测试 |
| 会话复制 | `session.rs::copy_sessions_for_switch/copy_sessions_cross/run_copy` | commands → 同/跨区 operation locks → 恢复旧操作 → 新 UUID → 正文、数据库、关联登记 | 保留源会话；会话写入是多个文件与 SQLite 的阶段事务，非单一 ACID 事务 |
| 关联模型 | `session_link.rs::LinkStore/LinkGroup/LinkMember/PairBase/BaselineRecord/Operation` | session_links.json、基线、预览凭据与 operations 日志持久化；不同客户端 namespace 独立 | 可保留，不另建第二个会话关联系统 |
| 增量与冲突 | `session_link.rs::normalize_jsonl/decide_sync/SyncVerdict`; `session.rs::session_links_preview/sync_sessions_cross`; `session_groups.rs::preview_pair/sync_pair/sync_safe_batch` | 归一化内容 SHA256 与有序前缀、双方基线决定 unchanged/fast-forward/ahead/diverge；写入前重验证 preview token | 增量判断保留目标身份；分歧可显式覆盖；必须继续保障取消零写入，不将多重集相等当作内容相等 |
| 活跃写入门禁 | `session.rs::app_running_blocks_target_write` | 客户端运行且目标为当前账号时拦截；非当前账号可放行 | 比任务书更宽；复制对活动共享 DB 的 raw backup 不足以证明一致性，统一产品应先收紧 |
| SQLite / WAL | `session.rs::snapshot_workbuddy_db/verify_db_snapshot/update_target_session_row`; `session_backup.rs::ensure_full_synchronous` | 同步采用 SQLite Backup API，quick_check 后更新事务校验 owner/title；synchronous 至少 FULL | 同步备份有 WAL 一致性措施；复制的 `backup_workbuddy_db` 是依次拷贝主库/WAL/SHM + 长度校验，不能等同在线快照；未发现统一官方版本 allowlist 与完整 schema/外键门禁 |
| 备份与恢复 | `session_backup.rs::begin_operation/mark_protected/maintain/cleanup_after_success`; `session.rs::recover_pending_session_operations_at/run_sync_phases` | 阶段日志与唯一 UUID 支持中断恢复；失败保留证据 | 成功后会清理临时事务备份；这不是用户可长期恢复的备份功能。多文件恢复主要为继续完成/补偿，不是保证全部回滚 |
| 积分 | `credits.rs::get_credit_expiry`; `credit_usage.rs::get_statistics`; `official_usage.rs` | 资源 summary/paid/free 与旧接口回退；只展示摘要；套餐到期处理与缓存 | 私有/未公开接口与字段兼容风险；积分更新不等于签到到账；官方客户端标识和 UA 不应机械复用 |
| Token 统计 | `token_stats.rs::get_statistics` → 各来源解析器；`src/pages/TokenStatsPage.tsx` | 本地多来源日志/索引统计；保留已存在页面 | 测试解析器不代表本机真实日志验证；统计扫描需要可控数据根和权限 |
| 签到 | `checkin.rs::get_checkin_status/perform_checkin/checkin_account/run_checkin_all` | 已有 Rust 国内版 status → submit → log 流程；国际版直接 skipped | 无需再逐行翻译 Go；结果主要 success/already/error/skipped，缺任务书详细错误类型与取消；缺字段可被默认 false，存在误提交风险 |
| 调度 | `checkin.rs::date_str/next_cycle_delay/run_checkin_cycle`; `config.rs::default_checkin_config`; `src-tauri/src/lib.rs::spawn_background_loops` | 默认新安装关闭，历史配置可开启；Local 时区；随机窗口目标分钟或 30 分钟恢复周期 | 非固定北京时间 09:15；缺显式补执行开关与跨 host 持久幂等任务模型；进程内互斥不能覆盖不同 host |
| Tauri 暴露面 | `src-tauri/src/lib.rs::run`; `commands.rs`; `capabilities/default.json` | main window 可 invoke 注册命令，含导出、路径保存、切换、同步；opener/updater/dialog 权限；csp=null | 应验证每个 command 参数及授权，限制导出路径、拒绝任意文件读取；配置 capability 不自动收窄所有自定义 command |
| 自动更新/自启动 | `update_service.rs`; `tray.rs`; `lib.rs::run` | 上游更新签名公钥；单实例插件首先注册；autostart 插件使用 --hidden | Fork 需独立身份/更新链；不能让上游更新覆盖本产品；自启动必须用户显式开启，系统关闭/睡眠无执行保证 |
| 额外背景行为 | `lib.rs::spawn_background_loops`; `travel.rs`; `rate_limit_hook.rs`; `companion.rs` | 非截图模式会启动签到、旅行、轮换、保活与 hook 处理；内嵌独立 companion runtime | 用户排除两项目常驻互调，但上游已有辅助 runtime；可保留其功能，不能当作 Go Helper 桥接；需去掉/禁用未授权背景写入 |

## 3. Helper 入口与可复用边界

| 审查项 | 文件、函数/类型与调用关系 | 结论/风险 |
| --- | --- | --- |
| 可执行入口 | `cmd/workbuddy-helper/main.go::main`; `build.ps1` | flags → Store → 数据目录锁 → Service → 可选 HTTP server/scheduler。构建脚本 test/vet/build；不直接运行它连接真实数据 |
| 登录 | `internal/client/client.go::NewLoginSessionWithClient/LoginSession.Start/Poll`; `internal/service/service.go::StartLogin/PollLogin/commitLoginResult` | 国内使用 copilot.tencent.com + platform=CLI，Switch 国内使用 www.codebuddy.cn + platform=workbuddy；国际均有 workbuddy-ai；登录 URL 有白名单校验 |
| 唯一性 | `internal/model/model.go::Account.VersionMode`; `service.go::commitLoginResult`; `store/migrate.go::accountImportKey` | uid+版本列表区分，优于 Switch 跨区合并；不能仅按显示名匹配 |
| 国内签到 | `client.go::DailyCheckin` → `doEnvelope`; `service.go::Checkin` | POST codebuddy.cn/v2/billing/meter/daily-checkin；通过业务 code 判断结果；只允许 ModeCN；已有日完成状态跳过 |
| 状态检查 | `service.go::Checkin/isAlreadyMessage` | 主要依赖本地当天标记及重复业务码/消息；未找到等价独立服务端签到状态查询，不能用它替代 Switch status 流程 |
| 积分 | `client.go::Points/pointsPage/packageValues`; `service.go::Points/refreshPoints/RefreshAllPoints` | 分页与字段校验；签到后积分错误不等于签到失败；可参考解析和部分失败语义 |
| 服务端失败 | `client.go::Error/Kind/classifyHTTP/classifyBusiness/doEnvelope` | auth/rate/server/protocol/transport 等分类；响应大小受限；缺 code 的结构体零值可能被视为 code=0，需明确拒绝畸形成功响应 |
| 凭证刷新 | `client.go::Refresh`; `service.go::prepareAccount/refreshAccount` | 过期或鉴权失败刷新一次重试；X-Refresh-Token、X-Auth-Refresh-Source 头；需基于真实授权证据判断是否可共享 |
| 调度/重试 | `service.go::StartScheduler/runScheduledIfDue/runPendingRechecks` | 20 秒 tick，固定 UTC+8，默认 09:15；仅计划后 30 分钟窗口，不能满足全天启动补执行要求；国际 pending recheck 不迁移 |
| 幂等 | `service.go::accountLock/runScheduledIfDue`; `internal/instance/lock_windows.go::Acquire` | 账号 mutex、全局任务锁、当天持久状态、数据目录 Windows 独占文件；失败持久化只重写 marker 测试值得保留 |
| 日志 | `service.go::appendLogLocked/sanitize`; `model.go::LogEntry`; main 的 UTC log | 有脱敏和业务日志；UTC 输出与业务 UTC+8 分开。是否能覆盖未知异常格式需新增测试 |
| DPAPI | `internal/store/dpapi_windows.go::protectDPAPI/unprotectDPAPI`; `seal_default_windows.go`; `store.go::Save/Load` | Windows 默认 DPAPI，WBH1 格式；调用 CRYPTPROTECT_UI_FORBIDDEN，不使用机器级 flag。可参考设计，不能直接将其 state.bin 当 Switch JSON |
| 原子保存/恢复 | `store.go::writeRaw/inspectRegularFile/unmarshalState` | 备份回退、未来版本拒绝、目录/符号链接检查；并发 Load/Save 序列化 |
| 可移植导出 | `store/migrate.go::ExportPortableFrom/ImportInto`; `portable_cipher.go` | WBK1 AES-GCM + 同目录 key.bin；复制两者等同带走解密能力，不采用为本产品普通导出 |
| 单实例 | `instance/lock_windows.go::Acquire/Close` | CreateFile ShareMode=0，按 dataDir 隔离；与 Tauri 单实例不同维度，统一调度需数据根锁 |
| 服务端 | `internal/server/server.go::Handler/basicAuth/hostGuard/csrf/securityHeaders`; main 的监听配置 | 可选 BasicAuth、Host/CSRF 限制；统一桌面不迁移此端口，避免新增攻击面 |
| 国内/国际边界 | `service.go::Checkin/ActiveChat/RunAll`; `model.go::ModeCN/ModeIntl` | 国内真实签到与国际自动对话不是相同能力，不能混合 |
| 模拟客户端与私有接口 | `client.go::ClientUA/IntlClientUA/IntlClientName/IntlClientVer/machineID/ActiveChat/reportChatEvent/chatHeaders` | 有硬编码客户端版本、机器标识、growthEvent，目的是登记国际活跃；明确排除；国内签到及积分接口亦未找到公开第三方 API 契约 |
| 依赖 | `go.mod/go.sum` | Go 1.26.0，直接 golang.org/x/net v0.59.0，详见模块清单；只把必要行为重写进 Rust，不长期运行 Go Helper |

## 4. 授权兼容判断

两个国内流程的域名及 platform 不同。源码没有可据以证明受众、scope、签发方、不同能力授权复用的协议或声明。不得因为字段都叫 accessToken 就自动共享。官方客户端加密信封不透明，当前源码将其用于写回登录态；签到要求可用明文 token，信封返回需重新登录错误。真实凭证的 audience/scope/issuer 与刷新权属均未验证。

阶段 02 保留同一个账号目录下独立能力和 credential reference；只有得到允许且可验证的授权时才复用。本次未解析、复制或读取任何真实用户 Token。

## 5. Windows 历史问题与测试范围

源码 Git 历史证据：`dddcf91` 修复 Windows 备份目录 flush 的 os error 5，合并 PR #77；`9dbafec` 修复 Windows 失败用例；`53e7647`/`228e120` 修复 Windows npm shell 调用；`3af39c2`/PR #133 串行注册表探测并放宽测试侧超时。以上为历史修复，不宣称所有 Windows Issue 已关闭。

GitHub unauthenticated API 返回 rate-limit-exceeded，无法完整获取当前 Issue 列表；网页和本地历史只支持部分核对。此限制已记录，需后续补查。

已实际运行 core 719 单元测试 + 5 集成测试、server 9 测试、前端 24 测试，均无失败；fmt 检查通过。原版桌面测试编译报 E0425（tray.rs:1032，测试模块函数未限定），桌面用例未执行；这是已复现的 Windows 基线失败，阶段 01 在开发分支修复。Helper test/vet/build 结果见构建报告及 JSONL。不存在代码覆盖率测量结果，不能把用例通过数称作覆盖率。Windows 注册表探针属于临时测试键；进程相关只读/注入探针不等于真实切换验收。

## 6. 阶段结论

主项目足以作为主体，不需要把 Helper 整个客户端并入。源码证实基本会话算法与签到已有，但距任务书的凭证、安全门禁、时区、异常状态与备份产品仍有差距。风险阻止真实凭证接入和正式发布，不阻止隔离目录的原版构建。原版桌面启动仅在截图/虚构数据模式下评估，不允许常规启动触发真实背景功能。
