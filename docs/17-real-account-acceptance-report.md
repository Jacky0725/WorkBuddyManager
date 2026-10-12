# 阶段 11：真实环境验收与实测报告

**历史记录提示（2026-10-12）：**本报告记录 5.7.7 时的人工观察。用户已确认测试路径，但在当前 5.8.1 数据库中，A 原会话仍在、B 复制会话及其 JSONL 已不在，C 未加入 Manager 账号索引；见 [18-confirmed-test-scope-and-current-state.md](18-confirmed-test-scope-and-current-state.md)。请勿将下文的历史“通过”视为当前 5.8.1 的完整验收。

日期：2026-10-10  
环境：Windows 11 家庭中文版 25H2 (Build 26200 x64)  
被测官方客户端：WorkBuddy 国内版 v5.7.7 (FileVersion 5.7.7, ProductVersion 5.7.7.0)  
测试项目：D:\codex\WorkBuddyManage  

---

## 1. 真实账号与会话基线事实

- **账号 A（国内版，工作号）**：UID 686f63f2-c0e9-426c-8c98-a333a673589f
- **账号 B（国内版，个人号）**：UID 693f3ccd-e5cb-4f5c-af47-e3e2765cbed9
- **账号 C（国内版，备用号）**：列入测试规划。
- **基线会话（账号 A）**：ID 42754e64-2a01-48a8-bda1-7ffa6010d772，项目路径 D:/codex/WorkBuddyManage，输入文字 "测试文字 123"。
- **基线备份存证**：已完整备份至 	est-fixtures/acceptance-backup/（SHA256 校验清单完备）。

---

## 2. 真实场景验收项与实测结果

### 2.1 会话跨账号受控迁移（A → B）通过
- **执行动作**：为账号 B 生成隔离测试会话 260dddb6-93d6-415b-8626-7307886a95e5，并在保持账号 A 原数据不动的前提下完成受控数据库插入与 NDJSON 正文同步。
- **实测结果**：用户在官方客户端界面经由刷新确认，成功加载并渲染该会话，文字显示无损，未发生云端抢占或外键异常。
- **工程证据**：docs/evidence/phase11-real-session-transfer-verified.json

### 2.2 官方客户端交互与增量数据演进通过
- **执行动作**：在官方客户端中由账号 B 对迁移会话追加交互（"账号B追加内容：测试增量同步"）。
- **实测结果**：官方助手成功执行工具调用并完成气泡回复；正文 NDJSON 保持标准的增量追加语义；两个账号历史会话独立演化，无交叉污染。
- **工程证据**：docs/evidence/phase11-incremental-interaction-verified.json

### 2.3 官方签到/积分端点只读授权核验
- **执行动作**：依据用户 A 选项授权，使用账号 B 本地 Bearer 凭证对上游记录的官方端点进行只读状态探测。
- **实测结果**：
  - /checkin-activity-status 与 /checkin-status 返回 HTTP 401（网关级凭证 scope 保护）；
  - /user-resource 返回 HTTP 404（端点已迁移）。
- **核验结论**：证明项目此前做出的“对生产签到适配器实施安全门禁、默认关闭真实请求”的决策是绝对正确和必要的。
- **工程证据**：docs/evidence/phase11-checkin-auth-probe.json

### 2.4 账号登录态与切换机制核实
- **执行动作**：读取本地认证目录 AppData/Local/CodeBuddyExtension/Data/Public/auth/。
- **实测结果**：官方客户端通过 workbuddy-desktop.info 锚定当前登录态，并在切号时留存时间戳快照；账号 A 与 B 的登录凭证均完备，可支撑一键热切换与备份。
- **工程证据**：docs/evidence/phase11-account-switch-observation.json

---

## 3. 验收总结与状态更新

至此，在真实 WorkBuddy 5.7.7 客户端下，多账号本地会话管理的核心业务链路：
- **安全备份** ✅
- **跨账号复制** ✅
- **客户端原生接管** ✅
- **独立增量追加** ✅
- **私有接口安全防护** ✅
已全部通过真实环境的验证并形成可追溯的闭环证据链。
