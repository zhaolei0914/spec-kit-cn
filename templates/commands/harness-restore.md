---
description: "从 Git 检查点恢复制品"
---

## /harness-restore

### 角色

Harness 工程师

### 输入

$ARGUMENTS: `<REQ-ID> <tag名称|--latest>`

### 流程

#### 步骤 1: 列出可用检查点

读取 `.specify/harness/snapshots/snapshot-index.md`，列出该需求的所有检查点:

```
可用检查点:
  1. harness/ckpt/REQ-001/20260330-101500_post-spec
  2. harness/ckpt/REQ-001/20260330-103800_post-design
  3. harness/ckpt/REQ-001/20260330-115000_pre-implement (最新)
```

如果指定了 `--latest`，自动选择最新检查点。

#### 步骤 2: 确认恢复

⚠️ **人工确认**: 恢复操作会覆盖当前制品文件，确认继续？

#### 步骤 3: 执行恢复

运行 `PATH="/usr/local/bin:/usr/bin:/bin:$PATH" bash scripts/harness/restore.sh <REQ-ID> <tag>`:
- 自动 stash 当前修改
- 从检查点恢复 `specs/[REQ-ID]/` 目录

#### 步骤 4: 更新状态

1. 更新 state.md: 回退阶段进度到检查点对应的阶段
2. 更新 execution-log.md: 记录恢复事件
3. 输出: `✅ 已恢复到检查点: [tag]`
