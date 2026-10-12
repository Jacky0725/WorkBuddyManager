# 签到与积分验证：接口、授权及替代路径

日期：2026-10-12。用户要求三账号验收通过，并要求持续解决签到与积分验证，可参考 GitHub 项目。验收结论必须来自实测，不能修改结果标记充当通过。任务书 [10.3 节](PROJECT_TASK_V1.md)要求三个获授权账号与真实查询/签到/积分结果；[12 节](PROJECT_TASK_V1.md)要求在真实 Token、授权边界、绕过安全验证等不明时停止相关高风险操作。

用户随后先明确只有 A/B/C 账号持有人的测试授权，又提供一张显示为“WorkBuddy 官方支持团队”于 2026-10-12 10:28 回复的截图。截图文字表示允许使用官方 API 调用签到、查询积分，适用于正常注册的个人和企业账号、Windows 客户端 v3.0 及以上；要求使用官方鉴权且不得用于非法用途，也提及不经接口的客户端自动化。截图是重要的授权线索，但目前缺少工单编号、原始链接/发送方域名和配套 API 文档，无法独立核验来源或确定准确接口与权限。已向用户索取非敏感出处，不需要密码、Token 或 Client Secret。

## 已核实的事实

1. 当前 Manager 只登记 A/B 两个国内版账号；C 尚未加入。详见 [当前测试范围核对](18-confirmed-test-scope-and-current-state.md)。因此三账号真实验收当前不能判定通过。
2. 历史 [401/404 记录](evidence/phase11-checkin-auth-probe.json)仅覆盖 `www.codebuddy.cn` 上的 `checkin-activity-status` 和 `user-resource` 两个 URL。记录没有请求头、响应完整信息或可复现的匿名测试材料；其中 `user-resource` 与当前源码所用的 `get-user-resource` 名称也不同。401/404 只证明那两次请求未成功，**不能证明**所有签到路径已失效，也不能证明必须使用私有签名。历史报告中的更强结论应撤回。
3. 当前**开发源码**的国内版签到基址为 `https://www.codebuddy.cn`，路径前缀 `/v2/billing/meter`；积分查询另有资源路径和回退。`Checkin`、`PointsRead` 能力仍为 `Unverified`，手动/批量签到与积分生产入口均会短路；每日计划 `production_enabled=false`。未读取真实 Token 或发起本轮 billing 请求。
4. [88lin/workbuddy-auto-signin](https://github.com/88lin/workbuddy-auto-signin) 自述使用 `https://copilot.tencent.com` 及从客户端逆向获得的私有签到路径；[sep1107/workbuddy-checkin](https://github.com/sep1107/workbuddy-checkin) 自述 Windows 使用 UI Automation 操作官方客户端签到控件。它们提供实现思路，不提供腾讯对本项目的接口/自动化授权，也未证明兼容 WorkBuddy 5.8.1。
5. [官方积分说明](https://www.codebuddy.cn/docs/workbuddy/Credits)描述产品内积分，不公布第三方签到或积分 API 授权。可找到的[腾讯云代码助手软件许可及服务协议](https://cloud.tencent.com/document/product/301/106125)第 8.2.1 条对未经授权的第三方接入和使用有明确限制；其第 2 节主要描述 IDE 插件，是否直接适用于当前 WorkBuddy 国内桌面版需服务方确认。国际版另有独立条款，不能替代国内版授权判断。
6. 当前正在运行的 `release/0.2.0-alpha.2/local-candidate/workbuddy-manager.exe` 对应 app 提交 `1333f84`。该提交的 `api_capability_error()` 对所有能力都返回 `None`，调度快照还错误报告 `production_enabled=true`，与后来的开发源码修复 `b15b00a` 不同。它的新版后台循环使用 `DisabledProductionAdapter`，且当前未找到旧版自动签到配置文件；但手动签到/积分旧入口缺少生产门禁。**不能以开发源码的门禁为正在运行或已上传的 alpha.2 二进制背书，也不应在该候选包点击签到或积分刷新。**
7. 在当前源码 `b15b00a` 上执行 `cargo test -p wb-switch-core --test account_security --test manager_scheduler`：授权/凭证安全 19 项和调度 6 项全部通过，包括“未验证签到/积分在刷新和请求前被阻断”以及“后台轮询与手动触发不能预留或发送签到”。这只证明源码在隔离测试中的门禁行为，不证明 alpha.2 二进制或真实服务验收通过。
8. [官方 CodeBuddy 开放平台手册](https://www.codebuddy.cn/apiDocs/open-platform.html)提供第三方应用创建和 OAuth 2.0 授权流程；其 [OpenAPI 规范](https://www.codebuddy.cn/apiDocs/api.yaml)截至本次核对没有签到路径，也没有个人积分余额接口。规范内的企业资源积分接口用于企业额度查询，不能当成 A/B/C 的个人签到与积分接口。手册与截图给出的“官方 API”说法之间还缺少可执行的端点、scope 和字段合同。
9. 用户要求暂时使用“官方客户端的签到接口”。当前源码的 `/v2/billing/meter/checkin-activity-status`、`checkin-status` 与 `daily-checkin` 是既有客户端兼容路径，使用账号库 `access_token` 组装 Bearer 请求；尚未证明该 Token 对签到 API 的 issuer/audience/scope 合格，也未证明这些路径属于开放平台文档的第三方接口。已修正状态查询：仅首选路径明确 404 才回退旧路径，401/403/429/500 直接返回，避免用额外请求掩盖鉴权和限速问题。针对该判定的隔离单测通过，生产门禁保持关闭。
10. 只读检查 Manager 当前账号索引：A/B 各只有 `DesktopSwitch` 凭证引用，没有独立 `Checkin` 或 `PointsRead` 凭证引用；未读取任何凭证值。因此不能将桌面切换登录态直接当作截图所称的“官方鉴权方式”。

## 可继续的验证路径

- **服务方授权的接口方案：**取得明确覆盖 WorkBuddy Manager 的第三方接口授权、正式基址及路径、OAuth/凭证用途与 scope/issuer/audience、调用频率和积分字段语义。随后用隔离测试账号先做只读状态查询，再对允许账号至多执行一次真实签到，分别核对服务端结果与官方客户端积分显示；失败不重试写请求，也不伪装官方客户端。
- **官方客户端人工方案：**用户可在官方 UI 手动签到并查看积分，记录截图或脱敏结果。这能验证账号当日权益，但不能作为 Manager 自动签到或积分适配器通过的证据。
- **界面自动化方案：**只有在服务方确认允许第三方自动化操作客户端且 5.8.1 控件行为被单独验证后，再设计用户会话内的可禁用适配器；GitHub 项目的早期控件定位不能直接照搬。

向服务方核实的具体问题：是否允许独立开源客户端管理三个自有账号的登录态、调用每日签到和积分查询；若允许，正式接口与授权流程是什么；是否允许在官方桌面端通过辅助功能自动点击签到按钮；适用版本、频率、幂等码及积分到账延迟如何定义。无需向本项目提交密码或 Token。

在截图出处、正式接口合同和账号事实未补齐前，保持生产签到/积分适配器关闭，三账号及真实签到/积分验收分别标记为**未通过/未完成**。模拟通过、改写日志、换域名试探私有端点或复用真实 Token 都不能补齐证据。
