# GitHub 签到实现参考与当前门禁核对

日期：2026-10-13。此文区分开源项目的自述、当前开发源码和本机运行中的旧候选包。开源项目的接口路径与成功声明仅作实现线索，不构成 WorkBuddy 5.8.1、A/B/C 或第三方授权的验收证据。

## 可借鉴的设计

| 项目 | 可借鉴之处 | 当前工程不能直接照搬的部分 |
| --- | --- | --- |
| [SIMON-WORLD/workbuddy-daily-credit](https://github.com/SIMON-WORLD/workbuddy-daily-credit) | 状态查询 → 可领取才提交 → 提交后复核；限制目标 HTTPS 域名；只读本机登录态 | 该仓库自述使用未公开的客户端接口，并建议个人单账号使用；其默认域名为 `copilot.tencent.com`，与当前工程的 `www.codebuddy.cn` 不同 |
| [88lin/workbuddy-auto-signin](https://github.com/88lin/workbuddy-auto-signin) | 区分网络、鉴权、业务错误与已签到；离线凭据格式诊断；给定运行时间预算 | 其端点与凭据解密实现来自客户端逆向，且对部分响应形态有项目特定假设；不可把示例返回值直接当成当前版本合同 |
| [autumnsentiment/workbuddy-helper](https://github.com/autumnsentiment/workbuddy-helper) | 多账号串行、北京时间判重、单实例锁、令牌加密存储和逐账号日志 | 它有独立登录和存储体系；不能把它的账号令牌迁移到 Manager 的 `DesktopSwitch` 用途，也不能借其仓库声称真实账号已通过 |

三个项目都以 HTTP 接口为主要签到路径，不能证明“成长计划”浏览器页或 WorkBuddy 5.8.1 原生 UI 有稳定签到按钮。Manager 应继续保留 UI 与 HTTP 两个适配方向，但选择真实生产适配器前须核对官方页面/端点、账号身份、凭证用途、响应语义和当前版本。不得把仓库自述当作本机实测。

现有 HTTP 路径未来若获验证，应按明确的布尔状态判定：`true` 视为已签，`false` 才允许提交；缺字段、非布尔值或互相矛盾的字段一律停止。只有明确 404 才尝试兼容路径；401/403/429/5xx 不降级。提交后应重新查询或取得等价官方回执，按账号和北京时间业务日期记录。凭证不写入日志，不把 `DesktopSwitch` 凭证自动升级为 `Checkin` 或 `PointsRead` 权限。

## 当前开发源码的门禁

| 能力 | 状态 | 代码依据 |
| --- | --- | --- |
| 桌面账号切换 | 开放，受账号有效性、客户端关闭和操作锁等检查约束 | `account_repository::api_capability_error(DesktopSwitch)` 返回 `None`；`switch::switch_account` 获取 `ClientOperationLease` |
| HTTP 签到：状态查询、单账号、批量 | 关闭 | `api_capability_error(Checkin)` 返回错误；`checkin_account` 在刷新凭证和请求前短路 |
| 官方积分资源查询 | 关闭 | `api_capability_error(PointsRead)` 返回错误；`credits::get_credit_expiry` 在网络请求前短路 |
| Manager 每日签到与“立即签到” | 关闭 | `manager_scheduler` 使用 `DisabledProductionAdapter`，快照 `production_enabled=false`，`run_now()` 返回阻断原因；可保存配置但不执行 |
| UI 签到 | 未接入生产，视为关闭 | 只有 `ui_checkin` 状态机及隔离测试，尚无真实驱动、身份/结果验收或前端入口 |
| WorkBuddy 会话复制、同步、恢复写入 | 关闭 | `session_safety::require_verified_client()` 固定返回错误；纯切号可通过 `preflight_switch(..., false)` |
| 只读调查、Mock/单元测试、本地构建与配置编辑 | 开放 | 这些操作不改变上述生产门禁 |

本机 `daily_scheduler_config.json` 的 `enabled=true`、北京时间 09:15 是**已保存偏好**，不是生产签到已启动：开发源码的 `production_enabled` 仍固定为 `false`。当前运行的 `release/0.2.0-alpha.2/local-candidate/workbuddy-manager.exe` 则对应旧 app 提交 `1333f84`：该版本 `api_capability_error()` 对所有能力返回 `None`，且快照报告 `production_enabled=true`。虽然其新版后台循环仍使用禁用适配器，旧候选包的手动签到和积分入口缺少现有门禁；不能用开发源码的安全状态推断已安装包安全，旧包不应执行真实签到或积分刷新。

## 下一步

1. 在不暴露令牌的前提下取得可核验的当前版本接口/页面契约；先做单账号只读状态和身份验证，不试探多个候选域名。
2. 对照 A/B/C 分别验证凭证用途和账号隔离。当前 Manager 仅登记 A/B；C 未登记，不能声称三账号验收完成。
3. 完成经验证的单账号适配器与真实回执，再逐级开放人工触发、多账号串行和每日计划；每一阶段单独验收。
4. 以新版本构建包含门禁修复的测试包，替换旧 `alpha.2` 候选后再做真实客户端验收。
