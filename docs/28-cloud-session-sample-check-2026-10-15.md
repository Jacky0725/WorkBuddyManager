# 云会话样本与实现边界核对（2026-10-15）

本轮只读检查客户端元数据与安装包静态代码，未读取旧云会话正文，未创建云任务或提交任何云端迁移请求，未修改官方客户端配置和数据。

## 当前事实

- 国内版 5.8.2 主库仍只有 1 条云记录，不符合云活动查询所需的 `deleted_at=-1`；测试项目没有云记录，`projects/cloud` 没有本地云会话 JSONL。旧的非测试记录不用于验收。
- 安装包 `main/server.js` 的 `isDesktopCloudTaskEntryEnabled` 要求产品配置 `productFeatures.DesktopCloudTaskEntry` 严格为 `true`。本轮未核验运行时配置值，不能据此宣称所有桌面版本不支持云任务，也不修改开关来强行启用入口。
- `main/node.js` 的 `resolveCloudPersonalTranscriptPath` 使用 `projects/cloud/user-<conversationId>/<conversationId>.jsonl`，有独立序列化与远端请求对账流程。本地 JSONL 的存在本身不能证明云端任务已归属另一账号；不能仅修改本地 owner、transport 或映射后报告云迁移成功。
- 官方[小程序快速开始](https://www.workbuddy.cn/docs/workbuddymini/quick-start/Quickstart)说明：微信搜索“腾讯 WorkBuddy”，输入栏上方切换环境，“云端工作”在云端沙箱执行，“连接电脑”控制桌面端。该入口可用于创建明确的云样本；普通桌面本地任务不等同云任务。

只读结果见 `docs/evidence/phase28-cloud-readonly-check.json`。alpha.5 的附件、Buddy 和本地会话功能保持已发布状态；本轮没有必要的代码改动，也不为等待样本另发安装包。

## 继续验收所需的最小用户操作

在小程序中使用与已登记 A/B/C 之一相同的账号，选择“云端工作”，创建仅含虚构文字的任务，例如“云迁移验收 1015：请只回复测试成功，不访问网页、不读取文件、不调用工具”。只需告知所属测试账号和任务标题，无需凭据或正文。不能登录相同账号时直接说明，不要求新增账号或开发者接入。

取得样本后先确认任务身份、客户端可见性、正文及资源取得方式，再确定能否使用受支持方式创建目标账号自己的副本。现阶段没有已验证的云端历史导入/迁移路径，写入门禁继续关闭，不把样本创建或本地缓存写入记为迁移通过。
