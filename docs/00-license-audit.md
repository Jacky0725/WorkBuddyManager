# 阶段 00：许可证审查

日期：2026-10-08。此报告为源码/元数据核对与分发准备，不声称已完成全依赖法律审核。

## 已核对的上游文本

| 来源 | 文件 | 许可与版权 |
| --- | --- | --- |
| Switch 固定提交 | `upstream/workbuddy-switch/LICENSE` | MIT，Copyright (c) 2026 wb-switch |
| Helper 固定提交 | `upstream/workbuddy-helper/LICENSE` | MIT，Copyright (c) 2026 autumnsentiment |
| Agent Companion 快照 | `upstream/workbuddy-switch/vendor/agent-companion/LICENSE` | 保留快照自带 MIT 文本，详见该文件 |
| patched indexmap | `upstream/workbuddy-switch/vendor-patched/indexmap/LICENSE-MIT`、`LICENSE-APACHE` | MIT / Apache-2.0 双许可，保留本地修改来源 |
| Helper lucide | `upstream/workbuddy-helper/cmd/workbuddy-helper/web/lucide-LICENSE.txt` | 单独素材 notice，复制素材时必须随分发保留 |
| Go x/net 0.59.0 | 下载模块 LICENSE | BSD-3-Clause，Copyright 2009 The Go Authors；见 `evidence/go-x-net-LICENSE.txt` |

两上游 MIT 文本允许使用、修改、合并和分发，但须保留版权与许可声明。源码许可不授予腾讯商标、官网图标、服务访问或客户端身份使用权限。

## 依赖盘点与待完成边界

`scripts/collect-audit-evidence.py` 依据根和 companion 的 package-lock/Cargo.lock 生成 `evidence/npm-license-inventory.json` 和 `evidence/rust-license-inventory.json`。包括开发、可选及跨平台依赖，不是最终 Windows 二进制实际链接清单。Rust 尚未下载的目标依赖明确标为 unavailable；local crates 需读取对应 LICENSE，不能因没有 registry manifest 就判定无许可证。

npm 锁文件共 613 个条目（跨两份 lock，存在重复）。许可表达式包括 MIT、Apache-2.0、ISC、BSD、0BSD、BlueOak-1.0.0、OFL-1.1、CC-BY-4.0、MPL-2.0 等。MPL-2.0 需保留对应文件源码与修改义务，不能直接称全部为 MIT。`evidence/helper-modules.jsonl` 含直接 x/net 与间接 module 图；Go 主程序实际只使用 x/net/proxy，间接图的文本许可仍需补全。

发布前必须把 SPDX 元数据转换为按实际分发内容的 NOTICE 文本清单；保留字体 OFL、图标署名及 CC-BY、MPL notices；对本地 patched/vendor crate 单独标明修改。不存在“全部第三方依赖已确认可无条件分发”的结论。

## 未确定的素材

`src/assets/workbuddy-official-icon.png`、CodeBuddy 标识、截图、应用图标以及 companion 角色素材没有在本次审查中取得逐项独立授权证据。Fork 产品应替换自有标识或确认授权，MIT 仓库根文本不应被当作第三方商标许可证。涉及 AGENT companion 素材保留源 manifest `vendor/agent-companion.version.json` 与其来源 notice。

## 服务规则与授权

已检索官方文档，找到 [设置中的协议入口说明](https://www.codebuddy.cn/docs/workbuddyapp/Settings) 和 [官方自动化功能说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Automation-Guide)。官方的 Agent 定时任务说明不能证明第三方调用 billing 签到接口获准。

本次未获得明确许可第三方自动签到、插件 state/token 复用或硬编码客户端标识的服务条款证据。因此国内签到/积分标记为兼容性与授权边界待确认；测试只使用 Mock/虚构账户。Helper `ActiveChat` + `growthEvent` + IntlClientUA/Ver 路径明确排除，不能包装为国际版签到。

发布门禁：正式授权边界、素材和最终依赖 notice 未完成前，不发布宣称合规的安装包；不因工具测试通过就声称服务方允许自动签到。
