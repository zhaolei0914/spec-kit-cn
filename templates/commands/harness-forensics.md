---
description: "对失败或卡住的工作流进行事后调查"
---

## /harness-forensics

### 角色

Harness 工程师

### 输入

$ARGUMENTS: 需求 ID 或 "latest"

### 流程

#### 步骤 0: Harness 初始化

1. 读取 `.specify/harness/config.yml` 加载配置
2. 读取 `.specify/harness/state.md` 检查工作流状态
3. 解析参数: 如果是 "latest"，取最近一个有失败记录的需求
4. 在 execution-log.md 记录「⏳ Forensics 调查中」

#### 步骤 1: 收集证据

- 读取 execution-log.md 中该需求的所有执行记录
- 读取 audit-log.md 中的相关决策
- 读取 git log 中的相关提交 (`git log --oneline --grep="REQ-ID"`)
- 读取自愈循环的升级记录
- 读取测试报告中的失败用例 (result.md)

#### 步骤 2: 分析失败模式

- 哪个阶段失败最多？
- 自愈循环平均几轮？
- 哪类问题反复出现？
- 人工干预集中在哪？
- 上下文使用率是否接近上限？

#### 步骤 3: 根因分类

| 根因类别 | 建议改进 |
|---------|---------|
| 规范不清晰 | 改进 /2 模板，增加边界条件检查 |
| 设计不完整 | 改进 /3 模板，增加完整性检查项 |
| 任务粒度不当 | 调整 config.yml 任务阈值 |
| 测试覆盖不足 | 加强 /8 模板，增加覆盖率要求 |
| Harness 配置不当 | 调整 config.yml 参数 |
| 上下文溢出 | 调整 session_split.phase_groups |
| 自愈策略不匹配 | 调整 self_healing 轮次配置 |

#### 步骤 4: 输出改进建议

生成 `.specify/harness/forensics/[REQ_ID]-forensics.md`:

```markdown
# 事后调查报告: [REQ-ID]

## 时间线
| 时间 | 阶段 | 事件 | 结果 |
|------|------|------|------|

## 失败模式分析
- 失败集中阶段: ...
- 自愈平均轮次: ...
- 反复出现的问题: ...

## 根因分析
- 主要根因: ...
- 次要根因: ...

## 改进建议
1. [优先级高] ...
2. [优先级中] ...
3. [优先级低] ...

## 建议的配置调整
(config.yml diff)
```

#### 步骤 5: 更新 Harness (如适用)

将验证通过的改进建议应用到命令模板或配置，记录到 `.specify/templates/commands/CHANGELOG.md`

#### 步骤 N: Harness 收尾

1. 更新 execution-log.md (状态、耗时)
2. 更新 state.md (最后活动时间)
3. 输出 Back-Pressure 结果
