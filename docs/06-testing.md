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

WorkBuddy Manager 统一账号/capability、安全凭证迁移、签到完整 Mock HTTP 状态矩阵、固定北京时间调度与持久幂等、额外数据库版本/schema 门禁以及新增 UI 测试尚未开发/执行。现有上游相近用例不能代替这些新增验收。

三账号真实登录、A→B→C→A、真实签到/积分、生产会话迁移、真实应用 UI、安装/卸载/重装、Windows 10 与 11 双系统验收全部未执行。未提供或读取真实测试账号；不得宣称这些操作成功。

## 环境与隔离

core/server/app test 使用独立 WB_SWITCH_HOME、APPDATA、LOCALAPPDATA。Helper 用例创建临时目录和 httptest server，不调用生产服务。自动构建的可执行文件没有运行或安装到用户生产环境。可视验收另行安排，不用进程存在替代 UI 正常的结论。
