# 签到与积分验证：接口、授权及替代路径

日期：2026-10-12。用户要求三账号验收通过，并要求持续解决签到与积分验证，可参考 GitHub 项目。验收结论必须来自实测，不能修改结果标记充当通过。任务书 [10.3 节](PROJECT_TASK_V1.md)要求三个获授权账号与真实查询/签到/积分结果；[12 节](PROJECT_TASK_V1.md)要求在真实 Token、授权边界、绕过安全验证等不明时停止相关高风险操作。

用户随后明确：目前取得的**仅为 A/B/C 账号持有人的测试授权**，没有腾讯／WorkBuddy 服务方对第三方接口或 UI 自动化的授权。因此可继续在限定测试账号和空白项目内做本地兼容性核对；不能据此开放私有签到、积分接口或自动点击官方客户端。

## 已核实的事实

1. 当前 Manager 只登记 A/B 两个国内版账号；C 尚未加入。详见 [当前测试范围核对](18-confirmed-test-scope-and-current-state.md)。因此三账号真实验收当前不能判定通过。
2. 历史 [401/404 记录](evidence/phase11-checkin-auth-probe.json)仅覆盖 `www.codebuddy.cn` 上的 `checkin-activity-status` 和 `user-resource` 两个 URL。记录没有请求头、响应完整信息或可复现的匿名测试材料；其中 `user-resource` 与当前源码所用的 `get-user-resource` 名称也不同。401/404 只证明那两次请求未成功，**不能证明**所有签到路径已失效，也不能证明必须使用私有签名。历史报告中的更强结论应撤回。
3. 当前**开发源码**的国内版签到基址为 `https://www.codebuddy.cn`，路径前缀 `/v2/billing/meter`；积分查询另有资源路径和回退。`Checkin`、`PointsRead` 能力仍为 `Unverified`，手动/批量签到与积分生产入口均会短路；每日计划 `production_enabled=false`。未读取真实 Token 或发起本轮 billing 请求。
4. [88lin/workbuddy-auto-signin](https://github.com/88lin/workbuddy-auto-signin) 自述使用 `https://copilot.tencent.com` 及从客户端逆向获得的私有签到路径；[sep1107/workbuddy-checkin](https://github.com/sep1107/workbuddy-checkin) 自述 Windows 使用 UI Automation 操作官方客户端签到控件。它们提供实现思路，不提供腾讯对本项目的接口/自动化授权，也未证明兼容 WorkBuddy 5.8.1。
5. [官方积分说明](https://www.codebuddy.cn/docs/workbuddy/Credits)描述产品内积分，不公布第三方签到或积分 API 授权。可找到的[腾讯云代码助手软件许可及服务协议](https://cloud.tencent.com/document/product/301/106125)第 8.2.1 条对未经授权的第三方接入和使用有明确限制；其第 2 节主要描述 IDE 插件，是否直接适用于当前 WorkBuddy 国内桌面版需服务方确认。国际版另有独立条款，不能替代国内版授权判断。
6. 当前正在运行的 `release/0.2.0-alpha.2/local-candidate/workbuddy-manager.exe` 对应 app 提交 `1333f84`。该提交的 `api_capability_error()` 对所有能力都返回 `None`，调度快照还错误报告 `production_enabled=true`，与后来的开发源码修复 `b15b00a` 不同。它的新版后台循环使用 `DisabledProductionAdapter`，且当前未找到旧版自动签到配置文件；但手动签到/积分旧入口缺少生产门禁。**不能以开发源码的门禁为正在运行或已上传的 alpha.2 二进制背书，也不应在该候选包点击签到或积分刷新。**
7. 在当前源码 `b15b00a` 上执行 `cargo test -p wb-switch-core --test account_security --test manager_scheduler`：授权/凭证安全 19 项和调度 6 项全部通过，包括“未验证签到/积分在刷新和请求前被阻断”以及“后台轮询与手动触发不能预留或发送签到”。这只证明源码在隔离测试中的门禁行为，不证明 alpha.2 二进制或真实服务验收通过。

## 可继续的验证路径

- **服务方授权的接口方案：**取得明确覆盖 WorkBuddy Manager 的第三方接口授权、正式基址及路径、OAuth/凭证用途与 scope/issuer/audience、调用频率和积分字段语义。随后用隔离测试账号先做只读状态查询，再对允许账号至多执行一次真实签到，分别核对服务端结果与官方客户端积分显示；失败不重试写请求，也不伪装官方客户端。
- **官方客户端人工方案：**用户可在官方 UI 手动签到并查看积分，记录截图或脱敏结果。这能验证账号当日权益，但不能作为 Manager 自动签到或积分适配器通过的证据。
- **界面自动化方案：**只有在服务方确认允许第三方自动化操作客户端且 5.8.1 控件行为被单独验证后，再设计用户会话内的可禁用适配器；GitHub 项目的早期控件定位不能直接照搬。

向服务方核实的具体问题：是否允许独立开源客户端管理三个自有账号的登录态、调用每日签到和积分查询；若允许，正式接口与授权流程是什么；是否允许在官方桌面端通过辅助功能自动点击签到按钮；适用版本、频率、幂等码及积分到账延迟如何定义。无需向本项目提交密码或 Token。

在上述授权和账号事实未补齐前，保持生产签到/积分适配器关闭，三账号及真实签到/积分验收分别标记为**未通过/未完成**。模拟通过、改写日志、换域名试探私有端点或复用真实 Token 都不能补齐证据。
