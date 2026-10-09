# 阶段 02：账号与凭证

开发日期：2026-10-08 至 2026-10-09。开发根目录：`D:\codex\WorkBuddyManager`。

## 实施范围

沿用 `account.rs` 作为账号服务，新增 `AccountRepository` 与 `CredentialStore`，不重写现有切换/会话内核。后台读取时解密到既有 `serde_json::Value` 对象；普通磁盘索引、列表和导出采用公开字段白名单。

账号身份为 provider + region + external_uid。历史 provider 缺省为 workbuddy，region 使用现有 cn/ai 档位。uid 缺失时只在同 provider/region 内使用真实邮箱兜底；显示名、备注与手机号不能合并账号。对外查找只接受本地 id，不再用裸 uid 选取凭证。同身份导入保留本地 id；新身份携带冲突 id 时生成新 id，保护会话引用。

字段映射：internal_id→id、external_uid→uid、display_name→nickname/email、remark→note、created_at→createdAt、updated_at→updatedAt；凭证刷新仍单独记录 refreshedAt。status 区分停用、需要授权与桌面可用。is_enabled 可通过现有展示字段服务以严格布尔值修改，前端入口待阶段 06；停用账号在桌面切换前拒绝。未凭空增加与上游重复的 AccountService 层。

## 存储与迁移

- `accounts.json` 保留数组外形，每项 storage_version=1，仅保存标量元数据及 CredentialReference。凭证引用包含 account_id、capability_type、随机 secure_storage_key、expires_at 与 credential_version。
- access/refresh token、auth_raw、profile_raw、官方加密信封和未知非公开字段均进入 `credentials/<随机 UUID>.dpapi`。不同用途分别生成不可变 blob。
- 使用 Windows 当前用户 DPAPI；不开启 LOCAL_MACHINE，不保存自建硬编码密钥，不提供非 Windows 明文降级。
- 附加 entropy 和加密载荷同时绑定本地 id、提供方、区域、external_uid 及授权用途。改 UID、跨区域或交换用途会导致读取失败。
- 首次写旧库前先把原始文件字节保存为 DPAPI 加密备份，并实际解密比对；通过后才创建凭证 blob，最后原子替换元数据索引。写入先 sync_all，再 rename。失败不覆盖旧索引。
- 旧库只读不会自动改写。仅在已授权的应用写操作中迁移；本轮迁移测试全部针对临时 fixture，未读取或迁移用户真实账号。
- 密文不可读取时返回 CredentialUnavailable 与重新授权提示，隐藏已部分解密的令牌。展示字段修改保留原引用；同身份重新授权可替换损坏凭证。旧密文版本保留用于恢复，垃圾收集与完整备份 UI 待后续阶段。
- 损坏索引、未知版本、重复安全索引 id、索引夹带非公开字段均拒绝写入；桌面与 HTTP 列表命令返回固定错误。

正常账号修改在同一数据目录的 accounts.lock 排他锁内完成读取、修改和发布；跨宿主争抢返回可重试错误。异步刷新写回还比较旧凭证引用，拒绝覆盖更新后的凭证；未提交成功的刷新不会同步写入 CLI 认证文件。公开 save 是完整索引替换接口，仅供内部初始化/fixture，常规命令使用带锁 update。

DPAPI 是同一 Windows 用户的保护边界，不能隔离同用户恶意进程；不同用户/设备迁移需要额外导出机制。本轮未进行跨 Windows 用户验证。实现依据 [Microsoft CryptProtectData](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata) 与 [CryptUnprotectData](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptunprotectdata)。

## 授权用途与界面契约

DesktopSwitch、Checkin、PointsRead 使用独立引用。既有桌面凭证只归入 DesktopSwitch；Checkin 与 PointsRead 即使有独立凭证，也保持 Unverified，不能以字符串存在代替 scope/audience/issuer 验证。

真实签到/积分查询在网络请求及令牌刷新之前被关闭，返回 authorization_unverified。国际版签到保持跳过。后续阶段可开发 Mock 适配器；没有授权边界证据不得打开真实适配器。

account_meta、导出响应与文件均不含原始授权响应、凭证引用、未知字段或登录令牌。needsReloginReason 使用固定提示，避免服务端回显令牌。普通 JSON 导出只保存账号资料，不能恢复登录；前端说明已同步修改。官方不透明信封只作为密文载荷保留，没有解密或把它当成签到凭证。

纠正阶段 00 审查：固定上游的 import_local 本来就调用 account_meta 返回脱敏数据，之前“import_local 返回完整账号”的判断不准确；本轮未声称修复这个不存在的泄漏。

## 验证与剩余范围

测试证据位于 docs/evidence/phase02-*.log。新增安全测试覆盖实际 DPAPI 往返、索引不含明文、旧库加密备份恢复、未知版本/损坏数据、账号/区域/用途/UID 绑定、重授权、同名 CRUD、导出白名单、并发锁、过期/停用凭证及陈旧刷新拒绝。核心、桌面、HTTP host 与前端回归分别记录；测试数以最终日志为准。

未验证真实三账号切换、生产凭证迁移、跨用户 DPAPI、真实签到/积分、安装和桌面可视操作。上游其他命令/日志的全面安全审查在阶段 07；不得据本阶段测试宣称整个应用已经达到发布安全标准。
