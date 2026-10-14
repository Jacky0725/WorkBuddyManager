# 国内版积分查询验收（2026-10-14）

本次仅处理任务书要求的可用积分与套餐到期查询。没有扩大到国际版，也没有改动已通过跨日验收的签到调度。

WorkBuddy 5.8.2 客户端归档含 `get-user-resource-summary`、`get-user-resource-paid-packages` 和 `get-user-resource-free-packages` 三条资源路径。用已登记的国内版测试账号对固定官方主机做只读探测：`copilot.tencent.com` 的 summary 路径返回 404；`www.codebuddy.cn` 的 summary 路径返回 HTTP 200、`code=0`，`data.Packages` 为数组；携带官方客户端所用查询条件的 paid/free 路径均返回 HTTP 200、`code=0`，`data.Accounts` 为数组。探测没有输出令牌、余额或完整响应。

Manager 积分刷新现在要求独立的 `PointsRead` 授权标记。用户手动刷新尚未登记的账号时，先对固定 `www.codebuddy.cn` summary 路径进行限时、禁止重定向的只读验证；验证成功且账号 UID/令牌未在过程中变化，才把用途标记写入 DPAPI 凭证库。自动刷新不创建新授权。已登记账号复用标记，不重复探测。三路资源结果须全部有效才能作为总余额显示；任一路失败时只可使用完整的旧接口回退结果，不把部分资源相加显示为总额。

在 A/B/C 三个已登记国内版账号上，逐个完成用途验证及真实只读查询。三账号结果均 `ok=true`，含可解析的资源数组与到期字段；没有输出积分数值。`cargo test -p wb-switch-core credits::tests` 27 项、前端 Vitest 35 项通过；Rust server/Tauri `cargo check` 和 TypeScript 检查通过。此记录证明当前三个账号的读数链路可用，不保证未来令牌失效或服务端接口变更后仍可用。国际版 `PointsRead` 继续关闭。

优化构建与 NSIS 打包成功。本地候选位于 `release/0.2.0-alpha.3/points-candidate-20261014/`，哈希见该目录 `MANIFEST.md`；它尚未替换运行中的旧候选，也未上传 Releases。

会话写入未随本次积分改动开放。WorkBuddy 5.8.2 的测试会话含文件历史引用，现有算法只迁移 JSONL 和数据库行，无法无损迁移被引用文件；5.8.2 客户端指纹也尚未通过写后官方显示与恢复核验。官方客户端退出后，已在 `%USERPROFILE%\.workbuddy-manager\backups\acceptance-582-20261014` 保存独立主库、映射库、测试正文与历史文件备份，未修改官方会话库。
