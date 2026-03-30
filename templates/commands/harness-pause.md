---
description: "暂停当前工作，生成 handoff.json 交接文件"
---

## /harness-pause

### 角色

Harness 工程师

### 输入

$ARGUMENTS: 暂停原因 (可选)

### 流程

#### 步骤 1: 收集当前状态

1. 读取 `.specify/harness/state.md` → 获取活跃需求
2. 读取 `.specify/harness/execution-log.md` → 获取最后执行记录
3. 确定当前进行中的需求、阶段、任务

#### 步骤 2: 生成交接文件

写入 `.specify/harness/handoff.json`:

```json
{
  "version": "1.0",
  "created_at": "[ISO-8601]",
  "reason": "[用户提供的原因 或 '用户手动暂停']",
  "active_requirement": "[REQ-ID]",
  "current_command": "[当前命令]",
  "current_task": "[当前任务ID，如有]",
  "context_summary": "[当前工作摘要]",
  "pending_decisions": ["待决策项列表"],
  "files_in_progress": ["正在修改的文件列表"],
  "resume_instructions": "[恢复指令]",
  "session_group": "[当前 session 组编号，如适用]",
  "completed_phases": ["已完成的阶段列表"],
  "next_phases": ["待执行的阶段列表"]
}
```

#### 步骤 3: 更新状态

1. 更新 state.md: 标记需求状态为「已暂停」
2. 更新 execution-log.md: 记录暂停事件

#### 步骤 4: 输出暂停信息

```markdown
⏸️ 工作已暂停

**需求**: [REQ-ID] [需求名称]
**当前阶段**: [阶段名]
**原因**: [原因]

恢复方式:
1. 开启新会话 (推荐，保持上下文干净)
2. 输入: /harness-resume
3. 引擎将自动从断点继续

> 状态已保存到 .specify/harness/state.md 和 handoff.json
```
