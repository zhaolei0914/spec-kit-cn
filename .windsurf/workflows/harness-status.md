---
description: "显示当前 Harness 工作流状态和下一步操作建议"
---

## /harness-status

### 角色

Harness 工程师

### 输入

无需参数

### 流程

#### 步骤 1: 加载状态

1. 读取 `.specify/harness/config.yml` → 当前配置
2. 读取 `.specify/harness/state.md` → 活跃需求和进度
3. 读取 `.specify/harness/handoff.json` → 是否有暂停的工作
4. 读取 `.specify/harness/execution-log.md` → 最近执行记录 (最后 5 条)

#### 步骤 2: 输出状态报告

```markdown
# Harness 状态

**Profile**: [当前 profile]
**活跃需求**: N 个
**调度策略**: [auto/subagent/session-split/single]

## 活跃需求

### REQ-xxx: [需求标题]
- 状态: [当前状态]
- 进度: /1 ✅ /2 ✅ /3 🔄 /4 ⏳ ...
- 模式: [auto/guided]
- 下一步: [建议操作]

## 最近活动
| 时间 | 命令 | 需求 | 结果 |
|------|------|------|------|

## 建议操作
- [具体建议，如 "继续执行 /3-开发设计 REQ-001"]
```

如果有暂停的工作 (handoff.json 不为空):

```markdown
⚠️ 发现暂停的工作:
- 需求: [REQ-ID]
- 暂停原因: [原因]
- 恢复指令: /harness-resume
```
