---
description: "对当前 Harness 配置和制品进行全面审计评分"
---

## /harness-audit

### 角色

Harness 工程师

### 输入

$ARGUMENTS: 需求 ID 或留空扫描全部活跃需求

### 流程

#### 步骤 0: Harness 初始化

1. 读取 `.specify/harness/config.yml` 加载配置
2. 读取 `.specify/harness/state.md` 获取活跃需求列表
3. 如果指定了需求 ID，仅审计该需求；否则审计全部活跃需求
4. 在 execution-log.md 记录「⏳ Harness Audit 执行中」

#### 步骤 1: 制品完整性扫描

对每个目标需求运行 `scripts/harness/lint-specs.sh`:
- 检查必需文件是否存在
- 检查必需章节是否完整
- 记录评分 (0-20 分)

#### 步骤 2: 跨制品一致性检查

对每个目标需求运行 `scripts/harness/consistency-check.sh`:
- FR 追溯覆盖 (spec → design → tasks)
- 术语一致性
- 任务依赖完整性
- 记录评分 (0-20 分)

#### 步骤 3: 安全扫描

运行 `scripts/harness/security-scan.sh`:
- 敏感信息泄露检查
- 危险命令检查
- 环境文件检查
- 私钥文件检查
- 记录评分 (0-20 分)

#### 步骤 4: 追溯完整性

对每个目标需求检查:
- requirement.md → spec.md FR 引用
- spec.md → design.md 模块映射
- design.md → tasks.md 任务分解
- tasks.md → 代码文件追溯注释
- 记录评分 (0-20 分)

#### 步骤 5: 文档同步检查

检查 `.ai-changelogs.md`:
- 是否有未同步的变更记录
- changelog 条目与制品版本一致性
- 记录评分 (0-20 分)

#### 步骤 6: 综合评分

总分 = 制品完整性 + 一致性 + 安全 + 追溯 + 文档同步 (0-100 分)

评级:
- **A** (90-100): 优秀 — Harness 完全合规
- **B** (80-89): 良好 — 小幅改进即可
- **C** (70-79): 合格 — 需关注部分问题
- **D** (60-69): 需改进 — 多个维度有缺陷
- **F** (<60): 不合格 — 需要全面整改

#### 步骤 7: 输出报告

生成 `.specify/harness/audit-report.md`:

```markdown
# Harness Audit 报告

**生成时间**: [时间戳]
**Profile**: [当前 profile]
**审计范围**: [需求 ID 列表]

## 综合评分: [等级] ([分数]分)

| 维度 | 得分 | 满分 | 详情 |
|------|------|------|------|
| 制品完整性 | X | 20 | ... |
| 跨制品一致性 | X | 20 | ... |
| 安全 | X | 20 | ... |
| 追溯完整性 | X | 20 | ... |
| 文档同步 | X | 20 | ... |
| **总计** | **X** | **100** | |

## 问题清单

### 严重 (必须修复)
- ...

### 警告 (建议修复)
- ...

## 改进建议
- ...
```

#### 步骤 N: Harness 收尾

1. 更新 execution-log.md (状态、耗时、评分)
2. 更新 quality-metrics.md 的 Audit 评分趋势
3. 更新 state.md (最后活动时间)
4. 输出 Back-Pressure 结果:
   - 成功: `✅ Harness Audit: [等级] ([分数]分) — [需求ID]`
   - 问题: 输出问题摘要
