# WorkBuddy Manager

最新扩展状态见 [2026-10-15 执行与验收记录](docs/30-growth-extension-acceptance-2026-10-15.md)。alpha.5 的既有签到、本地会话与 Buddy/附件迁移保持已验收范围；本批增加成长任务查询、限定奖励领取及旅行处理。真实任务自动完成和新增计划的跨日验收尚未全部通过。

按 [项目总任务 V1.0](docs/PROJECT_TASK_V1.md) 开发 Windows 多账号桌面管理器。

工作根目录：`D:\codex\WorkBuddyManager`。前一轮准备文档归档在 `docs/pre-migration-preparation/`。

工程最初位于 `D:\codexs\WorkBuddyManager`，随后迁至 `D:\codex\WorkBuddyManage`；现已整体迁入上述工作根目录，包含 Git 历史、三个子模块、工具、测试缓存和构建产物。历史任务书和构建日志中的原路径保留，用于追溯当时的执行环境；后续命令均在当前工作根目录执行。

## 初期阶段记录（历史状态）

- 已获取两个上游完整 Git 仓库，并以 Git submodule 固定版本。
- 阶段 00：五份审查报告与基线证据已建立，真实授权/分发边界未验证的事项已标明。
- 阶段 01：Windows 桌面测试入口最小修复，34 个用例通过；原版 x64 NSIS 基线构建成功，未签名、未安装、未做真实 UI 验收。
- 阶段 02：账号按提供方/区域隔离；后台凭证使用当前用户 DPAPI；公开导出仅含资料。19 个新增安全测试及全工程回归通过。
- 阶段 03：可替换签到引擎与本地 Mock HTTP 测试完成，支持业务状态、批量、取消及超时核实；12 个 Mock 用例和核心回归通过。
- 阶段 04：北京时间每日调度核心、持久幂等、补执行开关和跨进程锁完成；18 个调度用例通过。阶段 06 已接入 host 配置与 UI，生产执行和系统登录自启动尚未验收。
- 阶段 05：会话安全加固与 fixture 回归完成，一致快照、运行门禁、数据库/正文检查、事务与外键检查已实现。最终 Rust 829 + 前端 24 passed；官方版本/schema 未验证，生产会话写入禁用。
- 阶段 06：每日计划页、账号卡片状态、两种 host 配置服务与冲突保护已接入；阶段 07 已验证正常桌面下的计划保存、备份恢复与持久日志。
- 阶段 07：本机会话、CSP、日志脱敏、加密备份恢复、认证写入锁、独立产品身份和许可材料已实现。Rust 848 + 前端 35 passed。0.2.0-alpha.1 优化版 x64 NSIS 候选生成，隔离安装、桌面交互、卸载及数据保留通过；本机实际测试环境为 Windows 11 25H2。
- 阶段 08：用户授权读写兼容核验后，实测国内版 5.7.7，采集两个数据库的结构元数据，用空结构与虚构资料验证实际会话算法。核心 Rust 804 + Python 探针 3 passed；云绑定及删除标记的官方语义未确认，生产写入继续禁用。详见兼容核验报告。
- 阶段 09：静态核对安装包程序，确认本地/云删除状态和 Buddy 快照引用检查；复制、同步、预览与恢复增加云/未知类型及绑定拒绝规则。Rust 856 + 前端 35 passed，前端构建成功；生产入口仍关闭。
- 阶段 10：修复 PowerShell 脚本 Rust warnings 误终止；全工程 Rust 858 + 前端 35 回归通过；生成 0.2.0-alpha.2 优化版 x64 NSIS 候选，包含阶段 09 的会话迁移保护。真实验收和正式分发仍未完成。
- 阶段 11：完成 WorkBuddy 5.7.7 真实环境验收：账号 A/B 真实会话跨账号受控迁移与客户端原生渲染通过；会话增量交互与 NDJSON 独立演化验证通过；签到接口只读探测确认生产门禁有效性；形成阶段 11 验收报告与证据闭环。
- 最终交付归档：测试临时会话彻底清理，官方数据库恢复纯净基线；形成交付归档报告（docs/18-final-project-delivery-archive.md）；0.2.0-alpha.2 安装器与 SHA256 清单交付就绪。
- 真实签到/积分授权边界未验证，相关生产请求已关闭。真实账号测试与产品发布尚未完成；原版构建不等于统一产品交付。

## 上游基线

| 项目 | 标签 | 完整 SHA |
| --- | --- | --- |
| workbuddy-switch | v0.1.58 | 9eb3f2a21ff3c3c85fef2f89e693c48792050ba1 |
| workbuddy-helper | v1.0.6 | 10caebd9a1a848871ed5ada57d9c66d56d2e7a48 |

主项目当前已具备签到和调度代码；采用保留并加固现有实现的路线。Helper 的国际版模拟活跃请求不纳入产品。

## 报告

- [源码审查](docs/00-source-audit.md)
- [构建基线](docs/00-build-baseline.md)
- [许可证审查](docs/00-license-audit.md)
- [兼容性矩阵](docs/00-compatibility-matrix.md)
- [集成决策](docs/00-integration-decision.md)
- [工程结构与阶段 01 状态](docs/01-architecture.md)
- [账号与凭证架构](docs/02-account-and-credentials.md)
- [签到引擎与 Mock 验证](docs/03-checkin-integration.md)
- [持久每日调度核心](docs/04-daily-scheduler.md)
- [会话安全加固](docs/05-session-safety.md)
- [每日计划与统一入口](docs/06-manager-ui.md)
- [测试记录](docs/06-testing.md)
- [安全审查](docs/07-security-review.md)
- [安装与升级](docs/08-installation.md)
- [使用说明](docs/09-user-guide.md)
- [候选版本说明](docs/10-release-notes.md)
- [已知限制与阶段门禁](docs/11-known-limitations.md)
- [相对上游的改动](docs/12-upstream-differences.md)
- [真实环境验收范围](docs/13-acceptance-plan.md)
- [WorkBuddy 5.7.7 兼容核验](docs/14-workbuddy-577-compatibility.md)
- [本地会话迁移范围与保护规则](docs/15-local-session-transfer-policy.md)

## 获取源码与复查证据

```powershell
git submodule update --init -- upstream/workbuddy-switch upstream/workbuddy-helper
python scripts/collect-audit-evidence.py
```

`app` 的本地开发提交尚未推送到上游远端，不能依靠原作者仓库获取 `ad17460db9b587ba9fd5090987ad37415d6c94db`。本地已保存完整 checkout；另提供 `docs/evidence/app-development.bundle`，可在克隆固定基线后恢复开发提交：

```powershell
git clone https://github.com/changexbc/workbuddy-switch.git app
git -C app fetch ../docs/evidence/app-development.bundle develop/workbuddy-manager
git -C app checkout -b develop/workbuddy-manager FETCH_HEAD
```

以上恢复命令仅适用于尚无 app 目录的新 checkout，已有目录不得覆盖。

工具下载、测试数据及构建缓存仅存放在忽略目录。不得直接运行原版客户端连接真实账号；真实账号验收需要另行明确授权。

## 本地候选交付

`release/0.2.0-alpha.1/local-candidate/` 保存未签名安装器、安装后的可执行文件、源码 ZIP、开发提交 bundle、许可材料、用户说明、测试报告与逐文件 SHA256。此目录被 Git 忽略，安装器校验清单另保存在 `docs/evidence/windows-manager-artifacts.json`。

该候选固定于阶段 07 app `5c49371`；阶段 08 仅增加测试与结构 fixture，阶段 09 改变运行时迁移保护规则，均未重打包安装器。根工程开发 bundle 随开发提交更新；候选内的历史 bundle 和源码仍按固定提交核验，旧安装器不含阶段 09 改动。

完整计划尚未验收：真实三账号与官方会话兼容性、签到接口许可、Windows 10/11 22H2，以及一项依赖许可文本的发行源对应仍需确认。相关生产门禁保持关闭，不以本地候选替代正式发布。
