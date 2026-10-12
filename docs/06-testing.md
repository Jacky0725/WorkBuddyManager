# 测试记录

## 2026-10-08：上游审查与基线

| 范围 | 通过 | 失败 | 跳过 | 证据 |
| --- | ---: | ---: | ---: | --- |
| Switch core 单元测试 | 719 | 0 | 0 | evidence/switch-core-test.log |
| Switch core CLI 认证同步 fixture 集成 | 5 | 0 | 0 | 同上 |
| Switch HTTP host | 9 | 0 | 0 | evidence/switch-server-test.log |
| Switch 前端纯逻辑 | 24 | 0 | 0 | evidence/switch-frontend-test.log |
| Helper Go | 135 | 0 | 4 | evidence/helper-test.jsonl |
| 原版 Windows 桌面 | 未执行 | 编译失败 E0425 | 未执行 | evidence/switch-desktop-test.log |
| app 单行测试入口修复后 Windows 桌面 | 34 | 0 | 0 | evidence/app-desktop-test.log |

成功执行的用例共 926，另有 Helper 4 skip。该数是两个上游及最小基线修复的结果，不是统一产品新功能验收，也不是代码覆盖率。

已执行 npm 锁文件安装、TypeScript/Vite 构建、companion runtime 构建、fmt、Go vet 与 Windows Go exe 构建。npm audit 有 1 high 告警，未自动修复；源码符号/测试/依赖 license 清单在 evidence。

原版 Windows x64 NSIS debug 基线打包成功，退出码为 0；安装器、主程序和 companion runtime 的 SHA256、大小及 NotSigned 状态见 `evidence/windows-baseline-artifacts.json`。产物仅留存用于回归比较，没有安装或启动。

原版桌面测试错误的修复不改变运行时行为。保留原版 failure 与 app pass 两份证据。没有用 mock sidecar 冒充 runtime。

## 尚未执行

官方完整数据库版本/schema 白名单、调度实际生产执行与完整桌面 UI 尚未验收；阶段 06 已接入配置服务与只读演示页面检查。现有上游相近用例不能代替这些新增验收。账号与凭证测试见阶段 02，签到 Mock 测试见阶段 03，调度核心与持久幂等见阶段 04，会话安全加固见阶段 05；真实数据迁移仍未执行。

三账号真实登录、A→B→C→A、真实签到/积分、生产会话迁移、Windows 10 与 11 双系统验收未执行。阶段 07 已验证正常 Manager UI 与虚构资料，见下面的新增记录；安装验收按最终记录单独判断。

## 环境与隔离

core/server/app test 使用独立 WB_SWITCH_HOME、APPDATA、LOCALAPPDATA。Helper 用例创建临时目录和 httptest server，不调用生产服务。阶段 07 仅安装/启动自有 Manager 的隔离候选，官方生产账号与会话未操作；可视验收证据见后续记录，不用进程存在替代 UI 正常的结论。

## 2026-10-09：阶段 02 最终回归

最终代码的 Rust 验证见 `evidence/phase02-workspace-final-test.log`：core 719 单元 + 19 新增安全集成 + 5 原集成，桌面 34，HTTP host 9，合计 786 passed，0 failed/ignored。前端 24 passed、TypeScript/Vite 构建成功，见 `phase02-frontend-final-test.log` 与 `phase02-frontend-final-build.log`。本轮合计 810 passed，未重复计算阶段 00 的 Go 测试。

使用 `cargo test --locked -p wb-switch-core -p wb-switch-server -p wb-switch-rust`；WB_SWITCH_HOME/APPDATA/LOCALAPPDATA 指向 phase02 fixture，CARGO_TARGET_DIR 指向项目测试缓存。安全测试均用随机临时目录和虚构凭证。可用 `scripts/Test-Development.ps1 -Target All` 复查；该脚本不会启动 GUI 或安装应用。

保存了两次中间回归失败日志：旧测试仍要求普通导出保留 token 和导入替换本地 id，已改为新安全契约；信封短路的原有错误语义已恢复。迁移遗留的 Tauri permissions/native 输出引用旧路径，首次桌面编译失败；仅清理本工程缓存内受影响包后，完整编译与桌面测试通过。无依赖版本升级，Cargo.lock 只给 core 增加已锁定 fs2 依赖。

## 2026-10-09：阶段 03 核心回归

`phase03-core-test.log` 记录 719 单元 + 19 账号安全 + 12 Mock HTTP + 5 既有集成，755 passed，0 failed/ignored。Mock 用例使用本地 HTTP server 覆盖状态矩阵、批量、重复、取消、限速间隔和超时恢复；未调用生产服务。前端/host 未改动，不将之前阶段的检查重复计入本轮新增验收。

## 2026-10-09：阶段 04 全工程回归

`phase04-workspace-test.log`：719 core 单元 + 19 账号安全 + 13 Mock HTTP + 5 CLI 集成 + 18 调度 + 34 桌面 + 9 HTTP host，共 817 passed，0 failed/ignored。前端 24 passed、构建成功，本轮合计 841。新的 HTTP 用例覆盖持久调度与真实回环 HTTP 引擎组合、重启不重复。18 调度用例包括注入时钟、持久恢复与 Windows 子进程文件锁。没有注册自启动、读取生产凭证或运行 GUI。

完整测试命令成功，外层环境检查发现脚本把未设置变量恢复为空字符串。修复 wrapper 后重跑 18 项调度测试，五个环境变量均恢复原值或原先不存在状态；见 `phase04-wrapper-environment.json`。保留第一次错误检查的记录，重复测试不加入 841。Vite 仍有既有的大 chunk 提示。

## 2026-10-09：阶段 05 会话安全回归

`phase05-workspace-test.log`：723 core 单元 + 19 账号安全 + 13 Mock HTTP + 5 CLI 集成 + 18 调度 + 8 会话安全 + 34 桌面 + 9 HTTP host，共 829 Rust passed，0 failed/ignored。前端 24 passed、构建成功，本轮共 853。新增 4 个 core 及 8 个会话安全集成用例，保留复制/同步/分歧/恢复的既有回归。

首轮 2 个失败及中间通过日志均保留：旧跨档运行门禁断言已更新；新 WAL 用例发现备份继承 WAL 模式，已修复。生产会话入口禁用、没有实际关闭/启动官方客户端、没有生产数据库操作。详细边界见 `05-session-safety.md`。


## 2026-10-09：阶段 06 每日计划与配置服务

`phase06-workspace-test.log`：723 core 单元 + 19 账号安全 + 13 Mock HTTP + 5 CLI + 6 配置服务 + 18 调度 + 8 会话安全 + 34 桌面 + 13 HTTP host，共 839 Rust passed，0 failed/ignored。最终前端 33 passed，构建成功，共 872；未把首次前端 32 passed 或之前阶段重复计入。

新增配置服务覆盖只读首次加载、保存与旧版本冲突、非法参数、坏记录保留、跨进程锁及生产门禁先于账号访问。HTTP 路由测试验证真实请求/响应结构、来源限制与旧入口拒绝；前端规则测试覆盖未知结果、日期与区域隔离、北京时间、暂停计划和重试预算。完整日志见 phase06；Vite 大 chunk 提示及上游 Rust warnings 保留。

仅启动 VITE_DEMO_MODE=1 前端服务，浏览器可访问性树确认签到页、设置跳转与账号卡片状态。两次截图超时，未完成像素布局和窄屏验收，未启动正常后端/GUI。正常模式保存的完整浏览器交互、自启动、真实账号与生产执行尚未验收。详情见 `06-manager-ui.md`。

## 阶段 07：安全与产品候选

最终回归：core 726 单元 + 19 账号安全 + 13 Mock HTTP + 5 CLI + 4 加密备份 + 6 配置服务 + 18 调度 + 8 会话安全 + 34 桌面 + 15 HTTP host，共 **848 Rust passed**，0 failed/ignored。前端 **35 passed**、TypeScript/Vite 构建成功，本轮总计 883。证据为 `phase07-all-tests.log`、`phase07-frontend-final-tests.log`、`phase07-manager-release-build.log`（最终 TypeScript/Vite 和优化构建）。没有将早期重复运行加入数量。

新增用例验证加密备份与恢复、损坏/无确认/过期预览/并发锁/提交失败保留原索引、认证文件写入锁、Bearer/引号空格脱敏、本机会话与跨站/旧 cookie 拒绝。首轮日期边界失败和旧 CLI fixture 目录失败分别通过注入固定时钟与更新隔离目录修复；失败日志原样保留。

2026-10-10 正常模式启动自有 workbuddy-manager.exe，WB_SWITCH_HOME/APPDATA/LOCALAPPDATA 使用独立桌面 fixture；三条资料无真实 token。不是 VITE_DEMO_MODE，没有启动真实官方登录流程。CSP 下 WebView2 与 Tauri IPC 正常，账号列表显示三条；启用计划并保存后磁盘配置一致，实际签到仍暂停，没有执行任务记录。

桌面创建加密备份并预览确认恢复；恢复后三账号 id 不变，索引升级为 storage_version=1，回滚备份出现，每日计划 SHA256 不变。加密文件不包含虚构昵称或 UID 明文，凭证保密另外由 Rust 虚构凭证测试验证。操作日志显示成功结果；截图和文本在 evidence/manager-ui/，结构记录在 phase07-desktop-*.json。

关闭主窗口后原进程仍在；第二次启动打开原窗口，只存在一个主进程。停止测试进程后带精确 --hidden 参数启动，没有可见主窗口，后台进程存在。没有注册 HKCU 自启动，也未执行真实 Windows 登录测试。证据为 phase07-single-instance.json 与 phase07-hidden-start.json。

debug x64 NSIS 候选生成成功，完整 log 为 phase07-manager-debug-build.log。优化构建成功，最终日志为 phase07-manager-release-build.log；首次完整优化构建日志单独保留，没有用 debug 构建替代优化版本。

### 2026-10-10：优化产物与安装循环

实际系统是 Windows 11 家庭中文版 **25H2 / 10.0.26200 / x64**，来自本机 OS 元数据，见 phase07-test-os.json。用户此前报告的 22H2 是目标信息，未在该版本上验收；Windows 10 亦未验收。WorkBuddy 国内版 v5.7.7 只来自用户报告，未读取本机官方安装或账号数据确认。

NSIS 当前用户隔离循环：debug 安装 → 正常 UI → 卸载 → 优化版安装 → 正常 UI → 卸载。安装器与卸载器退出码均为 0；优化版运行截图为 manager-ui/optimized-installed-accounts.png。最后停止的只是路径核对后的自有测试进程，未停止官方客户端。卸载后应用和本轮新增卸载注册项不存在，全部 11 个 fixture 文件 SHA256 不变，三条虚构账号、两份加密备份与计划保留；见 phase07-manager-release-install.json、phase07-manager-release-uninstall.json。没有注册真实登录自启动，也没有验证 Windows 用户登录/系统重启。

功能 app 提交：`0cd8baa4383efe20f0a342dc1c4534443968697a`；初始许可材料提交：`77360f2558769f954225025e7299fbcf1853dda1`。首轮优化安装器大小 6,168,329 字节，SHA256 `CC6ABE1D29B4EE0A000D6487854FA345AED836EC9966041BA21E6C381012B0AE`，签名状态 NotSigned；其安装后主程序 23,792,640 字节，SHA256 `6203D4321C899B014558115A6814F01A4C2D35636A392EE282E2EC8E81696D07`。首轮材料保留在 release/0.2.0-alpha.1/before-source-byte-fix，不作最终交付。Tauri 为 NSIS 修改 bundle type 标记，构建缓存的原始 exe 与安装后的 exe 不保证哈希相同；交付的单文件 exe 取自实际安装版本，见 phase07-installed-package-check.json。

完整工程保留于当前工作根目录。候选目录提供源码 ZIP、开发历史 bundle、LICENSE、THIRD_PARTY_NOTICES、502 项依赖许可清单和 MPL 对应源；逐文件校验包含许可与对应源。校验只能确认材料与构建留存一致，不能替代许可分发审查或官方业务兼容性结论。

候选初次逐文件清单核对通过；进一步对照源码 ZIP 时，发现 14 份许可文件的 Git 入库换行转换及一份被嵌套 .gitignore 忽略的 MPL Cargo.lock。完整失败清单保留在 phase07-candidate-first-failed-verification.json；后续提交 `5c493712b9e6d381b67677dd565c45b9f257d4e0` 仅修正这 15 份许可/对应源入库字节，业务源码不变，重新构建并收集最终候选。最终字节核验结果以 evidence/manager-candidate-verification.json 为准；这不是生产兼容、代码覆盖率或许可合法性的认证。

最终提交重新优化构建成功（phase07-manager-release-build.log）；安装器 6,162,963 字节，SHA256 `30A93E5E0BE8E2F431967D8025EC7D83F4C4E0888F184E30F4A69A751EFEB700`，安装后 exe 23,792,640 字节，SHA256 `0674557F6F90B66680C7F009ADBFFB3924E5356E34C666CB0590F9878CE051A4`。再次隔离安装退出码 0，正常窗口显示三条虚构资料及生产接口禁用提示；截图为 manager-ui/final-installed-accounts.png，安装记录为 phase07-final-install.json，代码与测试提交关系见 phase07-final-build-source.json。

最终隔离卸载退出码 0，主程序与本轮卸载注册项已移除，11 份 fixture 文件哈希全部不变，三条虚构资料和两份备份保留（phase07-final-uninstall.json）。最终候选字节核验通过：全部载荷与 SHA256SUMS 一致，827 份许可文本对照依赖清单，五份 MPL crate 对应源存在；安装依赖许可/对应源与源码 ZIP 一致，ZIP 重新导出与最终 Git 提交一致，开发 bundle 有效。详见 manager-candidate-verification.json。

## 2026-10-10：阶段 08 国内版 5.7.7 结构与隔离写入核验

已收到“授权读写兼容核验”。PE FileVersion 实测 5.7.7；只读采集主库和 edge v4 结构，重建空库及虚构会话后运行实际算法，未读取凭证/真实业务记录、未关闭官方进程、未写官方库。

app `5c1e50fcbab4aeaa86d90d3ca27ea3cb178b7cbf` 仅测试改动。`Test-Development.ps1 -Target Core`：731 单元 + 73 集成 = 804 passed，0 failed/ignored；Python 探针保护测试 3 passed。新增 5 个结构用例验证复制、FastForward、WAL 快照、事务失败回滚及云字段现状。云绑定原样复制和 deleted_at=-1/NULL 条件差异是未解决发现，不代表云会话兼容通过。未改 host/前端，未重复全工程测试。

初次探针 LIKE 被权限保护拒绝，改为 Python 名称过滤；初次 Python 测试因 Windows 未关闭 SQLite 连接导致清理失败，明确关闭连接后通过。失败与成功日志均保留。两份 fixture 的 sqlite_schema DDL 与实际观察对应一致；证据汇总为 phase08-compatibility-results.json，核心日志为 phase08-core-tests.log。完整范围见 14-workbuddy-577-compatibility.md。

阶段 07 候选冻结于 `5c49371`，当前根开发 bundle 推进至 `5c1e50f`。候选校验按其历史提交而非最新 HEAD 比较；官方请求、官方数据库写入和正式发布均未放行。

## 2026-10-10：阶段 09 本地迁移类型与恢复保护

静态读取安装包的三个程序文本成员，确认本地 NULL / 云 -1 活动条件以及 Buddy 快照引用校验。未执行官方代码、读取用户数据或修改官方数据库。程序事实证据为 phase09-installed-code-facts.json。

app `ad17460db9b587ba9fd5090987ad37415d6c94db` 新增复制/同步/预览/恢复的迁移类型拒绝规则，并在读取元数据失败时停止，不把错误替换成 NULL。新增 3 个结构回归用例，原云字段现状用例改为 11 种不支持输入的拒绝检查；当前 5.7.7 结构用例共 8 个。同步恢复用例证明 cloud/-1 不再被误作本地删除而还原正文。

完整 `Test-Development.ps1 -Target All`：core 807 + Tauri 34 + server 15 = **856 Rust passed**，前端 **35 passed**，前端生产构建成功；失败/跳过均为零。保留上游 warnings 和 chunk 提示。两次早期新测试错误（文件列表误与整数比较导致编译失败、预览 groups 字段误写为 items 导致断言失败）已修正，失败日志为 phase09-core-first-failed-build.log 和 phase09-core-first-failed-tests.log。最终日志为 phase09-workspace-tests.log、phase09-frontend-tests.log 和 phase09-frontend-build.log，汇总及哈希为 phase09-transfer-policy-results.json。

生成的 vendor permissions 已还原。没有新 GUI、NSIS 安装/卸载、官方正文显示或接管验收，不能声称新运行时已交付安装器；阶段 07 候选仍固定于 `5c49371`，根开发 bundle 推进至 `ad17460`。复核历史候选载荷/许可文本/源码及 bundle 校验继续通过。范围与后续空白项目清单见 15-local-session-transfer-policy.md。

## 2026-10-12：审查问题修复回归

独立审查发现四个生产门禁和接口返回值问题。开发源码恢复 Checkin/PointsRead 的未验证授权拒绝、每日计划 `production_enabled=false` 与 `run_now()` 的明确暂停结果，以及官方会话写入 `require_verified_client()` 拒绝；服务端手动签到路由按 `Result` 分支返回，避免成功值触发 `unwrap_err()` panic。普通账号切换仍可进行，会话写入请求在读取路径或凭证前被拒绝。

修复前 `Test-Development.ps1 -Target Core` 在账号安全用例 `unverified_checkin_and_points_are_gated_before_refresh_or_request` 失败，原始记录为 `phase11-core-first-failed-tests.log`。修复后完整 `Test-Development.ps1 -Target All`：**858 Rust passed**、**35 前端 passed**，前端生产构建成功；相关路由和账号安全测试均通过。日志分别为 `phase11-all-tests.log`、`phase11-frontend-tests.log`、`phase11-frontend-build.log`。测试使用隔离 fixture，未执行官方签到、积分请求或会话数据库写入。

同时开发源码对 Windows 客户端关闭失败显示残留 PID，并在强制关闭后重新核对是否还有新进程。用户自行关闭官方进程、重试切换后反馈成功；该反馈未经本轮独立采集业务验收证据。本轮没有自动关闭用户官方进程。GitHub 上已上传的 `v0.2.0-alpha.2` 安装包早于这次源码修复，不能用上述新测试结果为该已上传二进制背书。
