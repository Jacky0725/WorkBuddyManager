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

额外数据库版本/schema 门禁、调度 host/UI 接入与新增 UI 测试尚未验收。现有上游相近用例不能代替这些新增验收。账号与凭证测试见阶段 02，签到 Mock 测试见阶段 03，固定北京时间调度核心与持久幂等见阶段 04；真实数据迁移仍未执行。

三账号真实登录、A→B→C→A、真实签到/积分、生产会话迁移、真实应用 UI、安装/卸载/重装、Windows 10 与 11 双系统验收全部未执行。未提供或读取真实测试账号；不得宣称这些操作成功。

## 环境与隔离

core/server/app test 使用独立 WB_SWITCH_HOME、APPDATA、LOCALAPPDATA。Helper 用例创建临时目录和 httptest server，不调用生产服务。自动构建的可执行文件没有运行或安装到用户生产环境。可视验收另行安排，不用进程存在替代 UI 正常的结论。

## 2026-10-09：阶段 02 最终回归

最终代码的 Rust 验证见 `evidence/phase02-workspace-final-test.log`：core 719 单元 + 19 新增安全集成 + 5 原集成，桌面 34，HTTP host 9，合计 786 passed，0 failed/ignored。前端 24 passed、TypeScript/Vite 构建成功，见 `phase02-frontend-final-test.log` 与 `phase02-frontend-final-build.log`。本轮合计 810 passed，未重复计算阶段 00 的 Go 测试。

使用 `cargo test --locked -p wb-switch-core -p wb-switch-server -p wb-switch-rust`；WB_SWITCH_HOME/APPDATA/LOCALAPPDATA 指向 phase02 fixture，CARGO_TARGET_DIR 指向项目测试缓存。安全测试均用随机临时目录和虚构凭证。可用 `scripts/Test-Development.ps1 -Target All` 复查；该脚本不会启动 GUI 或安装应用。

保存了两次中间回归失败日志：旧测试仍要求普通导出保留 token 和导入替换本地 id，已改为新安全契约；信封短路的原有错误语义已恢复。迁移遗留的 Tauri permissions/native 输出引用旧路径，首次桌面编译失败；仅清理本工程缓存内受影响包后，完整编译与桌面测试通过。无依赖版本升级，Cargo.lock 只给 core 增加已锁定 fs2 依赖。

## 2026-10-09：阶段 03 核心回归

`phase03-core-test.log` 记录 719 单元 + 19 账号安全 + 12 Mock HTTP + 5 既有集成，755 passed，0 failed/ignored。Mock 用例使用本地 HTTP server 覆盖状态矩阵、批量、重复、取消、限速间隔和超时恢复；未调用生产服务。前端/host 未改动，不将之前阶段的检查重复计入本轮新增验收。

## 2026-10-09：阶段 04 全工程回归

`development-all.log`：719 core 单元 + 19 账号安全 + 13 Mock HTTP + 5 CLI 集成 + 18 调度 + 34 桌面 + 9 HTTP host，共 817 passed，0 failed/ignored。前端 24 passed、构建成功，本轮合计 841。新的 HTTP 用例覆盖持久调度与真实回环 HTTP 引擎组合、重启不重复。18 调度用例包括注入时钟、持久恢复与 Windows 子进程文件锁。没有注册自启动、读取生产凭证或运行 GUI。

完整测试命令成功，外层环境检查发现脚本把未设置变量恢复为空字符串。修复 wrapper 后重跑 18 项调度测试，五个环境变量均恢复原值或原先不存在状态；见 `phase04-wrapper-environment.json`。保留第一次错误检查的记录，重复测试不加入 841。Vite 仍有既有的大 chunk 提示。
