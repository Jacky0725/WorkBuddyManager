# WorkBuddy Manager

按 [项目总任务 V1.0](docs/PROJECT_TASK_V1.md) 开发 Windows 多账号桌面管理器。

工作根目录：`D:\codex\WorkBuddyManager`。前一轮准备文档归档在 `docs/pre-migration-preparation/`。

工程最初位于 `D:\codexs\WorkBuddyManager`，随后迁至 `D:\codex\WorkBuddyManage`；现已整体迁入上述工作根目录，包含 Git 历史、三个子模块、工具、测试缓存和构建产物。历史任务书和构建日志中的原路径保留，用于追溯当时的执行环境；后续命令均在当前工作根目录执行。

## 当前进度

- 已获取两个上游完整 Git 仓库，并以 Git submodule 固定版本。
- 阶段 00：五份审查报告与基线证据已建立，真实授权/分发边界未验证的事项已标明。
- 阶段 01：Windows 桌面测试入口最小修复，34 个用例通过；原版 x64 NSIS 基线构建成功，未签名、未安装、未做真实 UI 验收。
- 阶段 02：账号按提供方/区域隔离；后台凭证使用当前用户 DPAPI；公开导出仅含资料。19 个新增安全测试及全工程回归通过。
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
- [测试记录](docs/06-testing.md)
- [已知限制与阶段门禁](docs/11-known-limitations.md)
- [相对上游的改动](docs/12-upstream-differences.md)

## 获取源码与复查证据

```powershell
git submodule update --init -- upstream/workbuddy-switch upstream/workbuddy-helper
python scripts/collect-audit-evidence.py
```

`app` 的本地开发提交尚未推送到上游远端，不能依靠原作者仓库获取 `7c4c0cc`。本地已保存完整 checkout；另提供 `docs/evidence/app-development.bundle`，可在克隆固定基线后恢复开发提交：

```powershell
git clone https://github.com/changexbc/workbuddy-switch.git app
git -C app fetch ../docs/evidence/app-development.bundle develop/workbuddy-manager
git -C app checkout -b develop/workbuddy-manager FETCH_HEAD
```

以上恢复命令仅适用于尚无 app 目录的新 checkout，已有目录不得覆盖。

工具下载、测试数据及构建缓存仅存放在忽略目录。不得直接运行原版客户端连接真实账号；真实账号验收需要另行明确授权。
