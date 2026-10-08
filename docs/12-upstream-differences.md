# 与上游的差异记录

基线为 Switch v0.1.58 / `9eb3f2a21ff3c3c85fef2f89e693c48792050ba1`。

| 阶段/提交 | 文件 | 改动 | 验证 |
| --- | --- | --- | --- |
| 01 / app `ccd7552` | src-tauri/src/tray.rs:1032 | 测试调用改为 super::taskbar_uses_light_theme，修复 Windows E0425 | cargo test --locked -p wb-switch-rust：34 passed |

无新增账号、签到、会话业务功能。上游 checkout 不提交手工改动，app 保留完整历史并在独立分支开发。

根仓库新增审查/测试文档、证据采集脚本、隔离测试 wrapper，以及本地打包 overlay。Overlay 跳过已经完成的前端构建并关闭需要上游私钥的 updater artifacts；没有改变上游运行时网络端点或更新身份，不得把原版基线安装器当作统一产品发布。

Tauri 会生成 permissions 并可能调整 Cargo manifest，属于构建副作用；保留相关 diff 记录，并在构建结束恢复固定 checkout，不将它们混入手工修复提交。
