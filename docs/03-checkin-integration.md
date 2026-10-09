# 阶段 03：可替换签到引擎与 Mock HTTP

日期：2026-10-09。阶段 02 之后的独立开发提交；生产请求保持关闭。

## 源码依据与实现决策

对照 Helper `internal/client/client.go::DailyCheckin/classifyHTTP/classifyBusiness` 和 `internal/service/service.go::Checkin/isAlreadyMessage`，保留国内签到、失效/限速/服务器错误分类、按账号串行与已完成跳过的语义。不移植国际模拟活跃、机器身份派生、growthEvent 或仿客户端 User-Agent。

改进原版响应缺字段默认成功、状态缺布尔值视为未签到、过宽 already 判定和授权失效后跨用途刷新。新引擎 `checkin_service.rs` 接受可替换 CheckinAdapter，包含单账号、顺序批量、状态查询和内存历史。CheckinResultStatus 区分任务书要求的九种状态，另有 Cancelled 和 InProgress；固定结果文案不回显原始 body、令牌或服务端消息。

## 验证边界

DisabledProductionAdapter 不构造网络请求。LoopbackCheckinAdapter 只允许 http + literal loopback IP + explicit port + 根路径，拒绝 URL 凭证、查询参数和其他主机；关闭代理和重定向，响应最大 64 KiB。只发送 fixture 账号标识，不持有真实令牌。该适配器未注册为桌面/HTTP IPC 接口。

`/status` 与 `/submit` 是本地测试协议，不能据此声称已经确认官方生产协议。status 的 code 必须为整数且显式成功，data 必须为对象，today_checked_in/todayCheckedIn 必须为布尔值，双字段不得矛盾；不符合时不提交。submit 要求显式成功业务码与对象 data。另保留 Helper 测试中 HTTP 400 + code 10001 + 明确“今天已签到”文案的重复完成语义，401/429/5xx 不会被文案覆盖。

同一账号+业务日期只能有一个运行任务；成功后重复触发只返回 AlreadyCompleted。批量并发度为 1，所有请求共用间隔门禁；单账号失败不停止其他账号。授权失效、人工处理或限速后停止该日自动尝试。

POST 超时/网络异常后只查询一次状态，不重发 POST；确认已完成返回 AlreadyCompleted，否则保留 Unknown + may_have_completed。后续触发遇到不确定任务只查询，不能自动重提。取消会中断等待和在途 HTTP；取消 POST 保留不确定状态。成功文案说明积分到账需要另行查询，签到响应不等于积分到账。

日期必须为规范 YYYY-MM-DD；北京时间生成日期、跨重启幂等和持久日志属于阶段 04。当前历史是进程内记录，不能代替持久审计。新引擎尚未接入生产授权或原 UI，UI 接入在阶段 06；原真实签到/积分入口继续由阶段 02 门禁关闭。

## 测试结果

`phase03-core-test.log`：719 单元 + 19 账号安全 + 12 Mock HTTP + 5 既有集成，共 755 passed，0 failed/ignored。12 个 Mock 用例内部包含多种状态矩阵：成功、已完成、401、403/428、429、500、404、业务码失效、缺 code/data、字段改型/改名/矛盾、并发重复、三账号部分成功、取消、请求间隔、超时核实、不确定结果不重提、能力禁用与重定向拒绝。

HTTP 仅发往临时本地 TcpListener。首轮因 Windows accepted socket 继承 nonblocking 导致 fixture 提前关闭，失败记录保留；设置 accepted stream 为 blocking 后全部通过。未发送生产请求，未做压力测试，未读取真实 Token。完整 workspace 回归将在后续 host 改动或接入时执行；本阶段未修改 host API。
