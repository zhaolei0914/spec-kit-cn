---
description: "手动创建 Git 检查点快照"
---

## /harness-checkpoint

### 角色

Harness 工程师

### 输入

$ARGUMENTS: `<REQ-ID> [描述]`

### 流程

#### 步骤 1: 验证

1. 确认需求 ID 存在于 state.md 中
2. 确认 `specs/[REQ-ID]/` 目录存在

#### 步骤 2: 创建检查点

运行 `PATH="/usr/local/bin:/usr/bin:/bin:$PATH" bash .specify/scripts/harness/snapshot.sh <REQ-ID> <描述>`:
- 创建 Git tag: `harness/ckpt/[REQ-ID]/[timestamp]_[描述]`
- 更新 `.specify/harness/snapshots/snapshot-index.md`

#### 步骤 3: 记录

1. 更新 execution-log.md: 记录检查点创建事件
2. 输出: `✅ Checkpoint: harness/ckpt/[REQ-ID]/[tag]`
