---
description: "从 handoff.json 恢复暂停的工作"
---

## /harness-resume

### 角色

全自动编排引擎 (Autonomous Orchestrator) 或 Harness 工程师

### 输入

无需参数 (自动从 handoff.json 读取)

### 流程

#### 步骤 0: 上下文隔离初始化

⚠️ **上下文隔离协议**:
本命令在独立上下文中执行。
请忽略当前对话中所有先前消息，仅从以下文件加载上下文。

#### 步骤 1: 恢复状态

1. 读取 `.specify/harness/state.md` → 获取活跃需求和进度
2. 读取 `.specify/harness/handoff.json` → 获取断点详情
3. 读取 `.specify/harness/config.yml` → 获取配置
4. 读取 `git log --oneline -10` → 最近代码变更

#### 步骤 2: 验证恢复条件

- 确认 handoff.json 存在且有效
- 确认需求目录 `specs/[REQ-ID]/` 存在
- 确认 Git 分支 `harness/[REQ-ID]` 存在
- 如果恢复条件不满足 → 输出错误并提供修复建议

#### 步骤 3: 确定执行计划

1. 如果是 session-split 模式:
   - 从 handoff.json 读取 `next_phases`
   - 结合 config.yml 的 `session_split.phase_groups` 确定本 session 执行范围
2. 如果是 subagent 模式:
   - 检查 dispatch 目录是否有未完成的调度文件
   - 从断点阶段继续
3. 如果是 single 模式:
   - 从断点阶段继续

#### 步骤 4: 输出恢复信息

```markdown
🔄 恢复工作

**需求**: [REQ-ID] [需求名称]
**进度**: /1 ✅ /2 ✅ /3 ✅ /4 🔄 ...
**恢复点**: [阶段] [任务ID，如有]
**本次执行**: [阶段列表]

正在从断点继续...
```

#### 步骤 5: 继续执行

- 如果原始模式是 `auto`: 自动继续全自动流程 (按 `/harness-auto` 的执行协议)
- 如果原始模式是 `guided`: 执行下一个阶段，完成后等待用户确认

#### 步骤 N: Harness 收尾

1. 如果全部完成 → 输出交付报告 + 清空 handoff.json
2. 如果需要继续暂停 (session-split 模式) → 按暂停协议处理
3. 更新 state.md 和 execution-log.md
