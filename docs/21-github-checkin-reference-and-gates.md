# GitHub 签到实现参考与当前门禁核对

日期：2026-10-13。此文区分开源项目的自述、当前开发源码和本机运行的 `0.2.0-alpha.3` 候选包。开源项目的接口路径与成功声明仅作实现线索，本机验收以 A/B/C 的实际状态和 Manager 调度记录为准。

## 可借鉴的设计

| 项目 | 可借鉴之处 | 当前工程不能直接照搬的部分 |
| --- | --- | --- |
| [SIMON-WORLD/workbuddy-daily-credit](https://github.com/SIMON-WORLD/workbuddy-daily-credit) | 状态查询 → 可领取才提交 → 提交后复核；限制目标 HTTPS 域名；只读本机登录态 | 该仓库自述使用未公开的客户端接口，并建议个人单账号使用；其默认域名为 `copilot.tencent.com`，与当前工程的 `www.codebuddy.cn` 不同 |
| [88lin/workbuddy-auto-signin](https://github.com/88lin/workbuddy-auto-signin) | 区分网络、鉴权、业务错误与已签到；离线凭据格式诊断；给定运行时间预算 | 其端点与凭据解密实现来自客户端逆向，且对部分响应形态有项目特定假设；不可把示例返回值直接当成当前版本合同 |
| [autumnsentiment/workbuddy-helper](https://github.com/autumnsentiment/workbuddy-helper) | 多账号串行、北京时间判重、单实例锁、令牌加密存储和逐账号日志 | 它有独立登录和存储体系；不能把它的账号令牌迁移到 Manager 的 `DesktopSwitch` 用途，也不能借其仓库声称真实账号已通过 |

三个项目都以 HTTP 接口为主要签到路径，不能证明“成长计划”浏览器页或 WorkBuddy 5.8.1 原生 UI 有稳定签到按钮。Manager 应继续保留 UI 与 HTTP 两个适配方向，但选择真实生产适配器前须核对官方页面/端点、账号身份、凭证用途、响应语义和当前版本。不得把仓库自述当作本机实测。

本机 5.8.1 的 `D:\Program Files\WorkBuddy\resources\app.asar` 只读静态核对（SHA256 `d2644ce221ed2da7a6f71ac1e469557b20cc07d8a2636dc44ff04e212af4e6d4`）在偏移约 92454856/92455380 的客户端逻辑中看到：状态与领取分别向 `productManager.getEndpoint()` 下的 `/v2/billing/meter/checkin-activity-status`、`/v2/billing/meter/daily-checkin` 发 POST，调用 `buildHeadersWithTuringToken(session)`，成功按 HTTP 200 且响应 `code=0`、`data` 存在判断。这与简单 Bearer 请求不同；不能仅换域名或照搬 GitHub 脚本就开放生产门禁。这里仅记录成员名和调用关系，没有执行归档代码或读取/输出令牌。

2026-10-13 在用户已授权的当前 A 测试登录态上，临时取得 `88lin/workbuddy-auto-signin` 的 `signin.py`（下载内容 SHA256 `a5aa672b340a0c7a7d4ffd589471528e28198480d7d9838e30e0ea7da591ec44`），先核查 `doctor/status/claim` 代码路径，并将认证端点严格限定为 `https://copilot.tencent.com`。离线 `doctor` 返回 `AUTH_READY`；只读状态请求返回 HTTP 200、`code=0`、`active=true`、`today_checked_in=false`。随后使用同一已验证账号执行**一次** `daily-checkin` POST（不重试），回执 HTTP 200、`code=0` 且含 `data`；再次只读查询返回 `today_checked_in=true`。输出仅保留状态码和字段结构，未打印令牌或积分数值。

同日，在官方客户端关闭状态下通过 Manager 的普通账号切换路径转到已登记的 B，确认当前认证身份为 B 后，使用同一限定端点执行状态 → **一次**领取 → 状态复核：三次请求均为 HTTP 200、`code=0`，状态由 `active=true, today_checked_in=false` 变为 `today_checked_in=true`。随后切回 A，并核对当前认证文件的账号 UID 与操作前备份一致。A/B 真实请求证明该参考路径在这两个登录态的当日签到可用。

用户确认 C 已登记并登录后，核对 Manager 索引有三条互不相同的 UID，当前官方认证文件 UID 与第三条一致。重新下载同一 SHA256 的参考脚本，只执行固定 `https://copilot.tencent.com` 状态查询；HTTP 200、`code=0`、`active=true`、`today_checked_in=true`，故**没有重复提交**领取请求。第二次只读状态查询确认 `today_credit`、`daily_credit`、`total_credits` 字段存在且为非负数值；此处只验证状态接口的积分字段结构与当日累计数据，不等同于可用余额、到期时间或积分入账流水，也未输出任何实际数值。临时脚本已移除。

随后用 Manager 已保存且受 DPAPI 保护的 A/B/C 三份账号令牌分别对固定官方状态端点做只读查询；三个账号均返回 HTTP 200、`code=0`、`active=true`、`today_checked_in=true`，`total_credits` 为数值。三个独立的 `Checkin` 用途授权记录在各账号状态核验通过后写入 DPAPI 凭证库，公开账号索引只含用途引用而无明文令牌。`OfficialCheckinAdapter` 使用固定 HTTPS 主机、禁止重定向、逐账号授权标记与严格响应解析；旧 `checkin`/`credits` 入口仍关闭。运行真实每日调度一次，2026-10-13 三个账号分别记录 `AlreadyCompleted`，没有提交领取；在最终桌面候选版中点击“全部立即签到”后各账号仍只有一次尝试和一条事件。**这是已签到日的状态/幂等验收，不是未签到日通过 Manager 自动领取的实测。** 隔天领取、令牌更新与 Turing 风控仍需验收。

新适配器按明确的布尔状态判定：`true` 视为已签，`false` 才允许提交；缺字段、非布尔值或互相矛盾的字段一律停止。提交后必须重新查询，只有确认服务端已签才记录成功。401/403/429/5xx 不降级或重发领取。凭证不写入日志，也不因拥有 `DesktopSwitch` 凭证而自动获得 `Checkin` 或 `PointsRead` 权限。

## 当前开发源码的门禁

| 能力 | 状态 | 代码依据 |
| --- | --- | --- |
| 桌面账号切换 | 开放，受账号有效性、客户端关闭和操作锁等检查约束 | `account_repository::api_capability_error(DesktopSwitch)` 返回 `None`；`switch::switch_account` 获取 `ClientOperationLease` |
| 旧 HTTP 签到：状态查询、单账号、批量 | 关闭 | `api_capability_error(Checkin)` 返回错误；`checkin_account` 在刷新凭证和请求前短路 |
| 官方积分资源查询 | 关闭 | `api_capability_error(PointsRead)` 返回错误；`credits::get_credit_expiry` 在网络请求前短路 |
| Manager 每日签到与“立即签到” | `0.2.0-alpha.3` 本机候选包已开放 A/B/C；已签到日的状态核验和去重通过，隔天首次领取待验收 | `manager_scheduler` 使用 `OfficialCheckinAdapter`、北京时间持久化任务日志和独立账号凭证；无授权或凭证不可用时关闭 |
| UI 签到 | 未接入生产，视为关闭 | 只有 `ui_checkin` 状态机及隔离测试，尚无真实驱动、身份/结果验收或前端入口 |
| WorkBuddy 国内版本地会话复制、同步、恢复写入 | 精确指纹候选仅匹配 5.8.1；本机已更新为 5.8.2，当前全部拒绝写入 | `session_safety::require_verified_local_client()`、逐行本地类型检查、进程与操作锁 |
| 云会话、Buddy 绑定、官方分组、附件及跨档会话写入 | 关闭 | 云端删除标记、引用目标和附件资源没有完整迁移/回滚契约；`require_verified_client()` 及逐行检查继续阻断 |
| 只读调查、Mock/单元测试、本地构建与配置编辑 | 开放 | 这些操作不改变上述生产门禁 |

本机 `daily_scheduler_config.json` 的 `enabled=true`、北京时间 09:15 已由 `0.2.0-alpha.3` 候选包接管。桌面自动签到页面显示“后台已接入”、A/B/C 2026-10-13 各一条“已完成”，下一次预计执行为 10/14 09:15。Windows 当前用户登录自启动已通过应用开关开启并回读：`Run` 指向该候选包的 `workbuddy-manager.exe --hidden`，`StartupApproved` 为启用状态。候选包位于 `release/0.2.0-alpha.3/local-candidate/`，app 源码提交 `975226e`。该目录里的安装包未作数字签名，尚未上传 GitHub Releases。

## 下一步

2026-10-14 北京时间 00:35 的跨日预检通过固定官方端点只读查得 A/B/C 均未签到，调度日志无当天任务；这是计划时间前的预期状态。09:20 后复查，Manager `0.2.0-alpha.3` 进程仍运行且 Windows 登录自启动注册仍启用。持久化调度日志显示三账号分别于 09:15:38、09:15:41、09:15:44 执行，均为 `Finished(Success)`、一次尝试、一条事件、`may_have_completed=false`。随后同一固定端点对三个账号分别只读查询，均返回 `today_checked_in=true`。因此，**A/B/C 在未签到日经 Manager 自动执行的状态→领取→复核链路已通过一次跨日实测**；不据此推断长期令牌刷新、所有风控情形或积分可用余额。专项 09:20 复核自动化已暂停。

1. 在后续令牌刷新及网络/鉴权/限流异常时继续观察逐账号调度与去重；若服务端要求额外 Turing 验证，应停用并记录，不尝试绕过。
2. 验证官方登录态刷新后逐账号凭证更新及计划调度；确认网络失败、401/403/429、重启和重复触发都不会重复领取。
3. 查询可用积分余额、到期时间需要独立的 `PointsRead` 用途适配器；当前仅验证签到状态接口中的累计积分字段。
4. 保持当前候选程序运行至 10/14 09:15（或在当天重新登录 Windows 后由自启动唤起），再核对 A/B/C 三条隔天任务和服务端状态；当前 10/13 已签到记录不能代替此项。

用户要求会话所有类型开放；当前源代码只支持本地行。云会话按官方客户端观察使用不同删除语义，Buddy/分组含跨行引用，附件还需确认资源文件与引用的复制、冲突和恢复规则。不能凭 SQLite 列名相同便放开这些类型。2026-10-13 复查发现官方客户端已更新为 5.8.2（EXE SHA256 `ffbcf6d43caed2868ce876948bf63e78fa244109282681fb6a1f9f534d717552`）；主库 schema_version 58 和两库结构摘要仍与 5.8.1 指纹一致，但客户端二进制变化，源码按设计拒绝会话写入。需先核验 5.8.2 的正文/资源/写后官方显示与回滚，不能仅凭结构摘要放开。
