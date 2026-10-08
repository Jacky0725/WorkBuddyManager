# WorkBuddy Manager

按 [项目总任务 V1.0](docs/PROJECT_TASK_V1.md) 开发 Windows 多账号桌面管理器。

工作根目录：`D:\codexs\WorkBuddyManager`。前一轮 `D:\codex\WorkBuddyManager` 的准备文档保留。

## 当前进度

- 已获取两个上游完整 Git 仓库，并以 Git submodule 固定版本。
- 阶段 00：源码、许可证、兼容性及集成决策报告已建立，测试证据见 `docs/evidence/`。
- 功能开发、真实账号测试与产品发布尚未完成；原版构建不等于统一产品交付。

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

## 获取源码与复查证据

```powershell
git submodule update --init
python scripts/collect-audit-evidence.py
```

工具下载、测试数据及构建缓存仅存放在忽略目录。不得直接运行原版客户端连接真实账号；真实账号验收需要另行明确授权。
