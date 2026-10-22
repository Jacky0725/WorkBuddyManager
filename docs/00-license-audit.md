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

补充 Windows desktop 目标的锁定 metadata 闭包：384 个节点，`evidence/windows-desktop-license-inventory.json`。其中 2 个未声明 license 的节点是本地 wb-switch-core / wb-switch-rust，需沿用上游根 MIT；5 个 MPL-2.0 节点为 cssparser-macros、cssparser、dtoa-short、option-ext、selectors。另含 Unicode-3.0、CDLA-Permissive-2.0 等声明，必须保留各自 notice。该清单包含构建期依赖，不能直接当成最终安装包逐文件合规证明。

## 未确定的素材

`src/assets/workbuddy-official-icon.png`、CodeBuddy 标识、截图、应用图标以及 companion 角色素材没有在本次审查中取得逐项独立授权证据。Fork 产品应替换自有标识或确认授权，MIT 仓库根文本不应被当作第三方商标许可证。涉及 AGENT companion 素材保留源 manifest `vendor/agent-companion.version.json` 与其来源 notice。

## 服务规则与授权

已检索官方文档，找到 [设置中的协议入口说明](https://www.codebuddy.cn/docs/workbuddyapp/Settings) 和 [官方自动化功能说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Automation-Guide)。官方的 Agent 定时任务说明不能证明第三方调用 billing 签到接口获准。

本次未获得明确许可第三方自动签到、插件 state/token 复用或硬编码客户端标识的服务条款证据。因此国内签到/积分标记为兼容性与授权边界待确认；测试只使用 Mock/虚构账户。Helper `ActiveChat` + `growthEvent` + IntlClientUA/Ver 路径明确排除，不能包装为国际版签到。

发布门禁：正式授权边界、素材和最终依赖 notice 未完成前，不发布宣称合规的安装包；不因工具测试通过就声称服务方允许自动签到。

阶段 07 补充：安装器使用自有 WM 几何标识，编译界面的第三方产品图标改为文字。Companion 素材/runtime 不作为安装器资源。Windows desktop 闭包与安装的非 dev npm 包共 502 项，许可文本、字体 OFL、Lucide ISC 和五个 MPL crate 的对应源已收集于 app/licenses；清单及来源见 phase07-release-license-inventory.json、phase07-license-text-provenance.json 和 app/THIRD_PARTY_NOTICES.md。该清单包含构建依赖，不是二进制符号链接审计。

react-remove-scroll-bar 2.3.8 的 npm 包未携带完整文本，registry 网络失败且 GitHub API 限流。已保留作者仓库固定 commit 8ca9ba5 的 MIT 文本，但该提交标为 2.3.7，发行版来源对应仍未确认，不将“文本已收集”写成“全部分发义务验证完成”。selectors 通用 MPL-2.0 全文从本机 cssparser 同许可证文件保留，原始源文件许可头一起保留。Tauri、WebView2、unic、defmt 等文本从固定 crate 上游 SHA 获取；victory-vendor 另保留固定 v36.9.2 根 MIT 及 vendored D3 ISC 文本。

最终字节交叉验证发现首次 Git 入库时 14 份许可文本发生换行转换，一份 MPL Cargo.lock 被嵌套忽略。已在 app `5c493712b9e6d381b67677dd565c45b9f257d4e0` 仅修正这些材料的入库字节；保留失败证据。新增材料应先确保 `licenses/** -text` 生效，并对已核对的许可目录使用显式 `git add -f licenses`，避免对应源被嵌套忽略。后续由候选校验脚本逐文件对照安装资源、源码 ZIP 和依赖清单。


## 2026-10-22 发行代码与许可对应补证

已重新取得官方 npm 的 react-remove-scroll-bar 2.3.8、2.3.7 元数据与原始 tarball，验证两包各自 SHA512 integrity；2.3.8 与锁文件一致，本机安装的 27 个文件与包内字节全部一致。两版本的 26 个非 manifest 文件逐字节一致，package.json 仅版本号与 react-style-singleton 范围变化。2.3.7 registry gitHead 为 29e9fcd1eecf7d3b77a767941c4a57fe461fc1e4；该提交到已保留许可的 8ca9ba5ea52de03308fe8ced94f7b159a44d28ff，Git 差异仅增加 LICENSE，源码未变，许可字节亦与本地保留件相同。因此该已发布代码的 MIT 许可对应问题已补证。

2.3.8 registry gitHead 仍不可获取（raw 404，git fetch not our ref），没有伪称验证该精确提交或可复现构建。证据见 evidence/phase48-license-correspondence.json 与 app/licenses/npm/react-remove-scroll-bar-2.3.8/PROVENANCE.json；本结论只关闭该依赖代码的许可对应项，不是服务方授权、所有素材权属或正式法律认证。旧包及其历史材料不覆盖改写，本次材料单独补充。
