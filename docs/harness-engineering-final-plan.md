# Harness Engineering 最终实施方案

> **项目**: Spec Kit CN (spec-kit-cn)
> **编写日期**: 2026-03-30
> **综合来源**: [分析报告](./harness-engineering-analysis.md) | [初版方案](./harness-engineering-solution.md) | [同类产品](./harness-engineering-similar-products.md)
> **新增参考**: Everything Claude Code (ECC) · Oh My OpenAgent (OmO) · Get Shit Done (GSD) · OpenAgentsControl (OAC) · Ruflo · Superpowers
> **目标**: 实现完美 Harness Engineering 能力，全自动端到端流程，综合评分从 ⭐⭐⭐ (3.1/5) 提升至 ⭐⭐⭐⭐⭐ (5/5)

---

## 目录

- [一、新增参考工具能力提炼](#一新增参考工具能力提炼)
- [二、完美 Harness Engineering 能力模型](#二完美-harness-engineering-能力模型)
- [三、最终架构设计](#三最终架构设计)
- [四、十大核心模块详细设计](#四十大核心模块详细设计)
- [**五、全自动编排引擎 (核心)**](#五全自动编排引擎-核心)
  - [5.10 上下文隔离与 Agent 调度架构](#510-上下文隔离与-agent-调度架构)
  - [5.11 Level 3: 多 Agent 调度 (Cursor/Claude Code)](#511-level-3-策略-原生多-agent-调度-cursor--claude-code)
  - [5.12 Level 1: 单 Agent 管理 (Windsurf)](#512-level-1-策略-单-agent-上下文管理-windsurf)
  - [5.13 调度配置](#513-configyml-完整调度配置)
  - [5.14 调度文件协议](#514-调度文件协议)
- [六、命令模板改造方案](#六命令模板改造方案)
- [七、实施路线图（8周）](#七实施路线图8周)
- [八、目录结构总览](#八目录结构总览)
- [九、预期成效与验收标准](#九预期成效与验收标准)

---

## 一、新增参考工具能力提炼

### 1.1 六大工具核心能力总结

| 工具 | 定位 | 核心 Harness 创新 | Stars |
|------|------|-------------------|-------|
| **Everything Claude Code (ECC)** | Agent Harness 性能优化系统 | AgentShield 安全审计、Harness Audit 评分、Hook Runtime 控制、持续学习系统、跨 Harness 一致性 | 50K+ |
| **Oh My OpenAgent (OmO)** | 最佳 Agent Harness | Hash-Anchored 编辑、分层 AGENTS.md (`/init-deep`)、Discipline Agents 角色模型、Skill-Embedded MCP | 活跃 |
| **Get Shit Done (GSD)** | 上下文工程驱动的全流程框架 | STATE.md 跨会话记忆、HANDOFF.json 暂停/恢复、多 Agent 并行 Wave 执行、XML 结构化任务、`/gsd:forensics` 事后调查 | 活跃 |
| **OpenAgentsControl (OAC)** | 模式驱动的 Agent 控制框架 | ContextScout 智能模式发现、MVI 原则(Token 效率 80% 降低)、ExternalScout 实时文档、审批门控 | 活跃 |
| **Ruflo** | Agent 编排平台 | 分布式 Swarm 智能、RAG 集成、企业级编排架构 | 活跃 |
| **Superpowers** | Agentic Skills 框架 | Subagent-Driven Development、两阶段审查(规范合规+代码质量)、强制 TDD RED-GREEN-REFACTOR、Git Worktree 隔离 | 活跃 |

### 1.2 关键创新点 → GAP 映射

| 创新点 | 来源 | 对应 GAP | 复用优先级 |
|--------|------|----------|-----------|
| **AgentShield 安全审计** (A-F 评级、红蓝对抗、CI 集成) | ECC | GAP-M4 安全 | P0 |
| **Harness Audit 确定性评分** | ECC | GAP-C1 确定性验证 | P0 |
| **Hook Runtime 控制** (`ECC_HOOK_PROFILE=minimal\|standard\|strict`) | ECC | GAP-C3 配置层 | P1 |
| **持续学习 v2** (Instinct 置信度评分 + 聚类进化) | ECC | GAP-I2 跨项目学习 | P2 |
| **Hash-Anchored 编辑** (行级哈希锚定) | OmO | 反馈回路-编辑可靠性 | P2 |
| **分层 AGENTS.md** (`/init-deep` 层级上下文) | OmO | 上下文工程 | P1 |
| **STATE.md 跨会话记忆** | GSD | GAP-M1 工作流编排 | P0 |
| **HANDOFF.json 暂停/恢复** | GSD | GAP-M1 进度持久化 | P0 |
| **多 Agent Wave 并行执行** | GSD | GAP-I1 并行执行 | P1 |
| **XML 结构化任务** (内建验证步骤) | GSD | 护栏-任务精确度 | P1 |
| **`/gsd:forensics` 事后调查** | GSD | GAP-C2 可观测性 | P1 |
| **ContextScout 智能模式发现** | OAC | 上下文工程 | P2 |
| **MVI 原则** (Minimum Viable Information) | OAC | Token 效率 | P1 |
| **审批门控** (所有写操作需人工确认) | OAC | GAP 人机协作 | P1 |
| **Subagent-Driven Development + 两阶段审查** | Superpowers | 反馈回路 | P0 |
| **强制 TDD RED-GREEN-REFACTOR** | Superpowers | 护栏-测试纪律 | P1 |
| **Git Worktree 隔离** | Superpowers/GSD | GAP-M2 快照/回滚 | P1 |

---

## 二、完美 Harness Engineering 能力模型

### 2.1 五大支柱 → 十大模块

基于所有参考工具的最佳实践，将 Harness Engineering 五大支柱细化为十大可实施模块：

```
+-------------------------------------------------------------+
|              完美 Harness Engineering 能力模型                 |
+-------------------------------------------------------------+
|                                                               |
|  支柱1: 工具编排          支柱2: 护栏与安全                    |
|  +-------------------+   +-------------------+               |
|  | M1 配置中心        |   | M3 确定性验证引擎  |               |
|  | M2 工作流状态机     |   | M4 安全审计系统    |               |
|  +-------------------+   +-------------------+               |
|                                                               |
|  支柱3: 反馈回路          支柱4: 可观测性                      |
|  +-------------------+   +-------------------+               |
|  | M5 自愈+两阶段审查  |   | M7 执行日志+指标   |               |
|  | M6 快照/回滚/恢复   |   | M8 事后调查+审计   |               |
|  +-------------------+   +-------------------+               |
|                                                               |
|  支柱5: 人机协作          横切关注点                           |
|  +-------------------+   +-------------------+               |
|  | M9 审批门控+决策记录 |   | M10 持续学习引擎   |               |
|  +-------------------+   +-------------------+               |
|                                                               |
+-------------------------------------------------------------+
```

### 2.2 十大模块能力定义

| 模块 | 名称 | 能力定义 | 主要参考 |
|------|------|---------|---------|
| **M1** | 配置中心 | 集中配置、多 Profile、Hook Runtime 控制、环境适配 | ECC + OAC + OpenSpec |
| **M2** | 工作流状态机 | 状态持久化、跨会话恢复、暂停/交接、前置条件验证 | GSD + Anthropic |
| **M3** | 确定性验证引擎 | 制品 Linter、一致性测试、Harness Audit 评分、CI Hook | ECC + OpenAI + HumanLayer |
| **M4** | 安全审计系统 | 敏感信息检测、权限模型、危险命令拦截、安全评分 | ECC AgentShield + OpenDev |
| **M5** | 增强反馈回路 | 自愈循环+两阶段审查、Back-Pressure、TDD 纪律 | Superpowers + HumanLayer |
| **M6** | 快照/回滚/恢复 | Git Checkpoint、Worktree 隔离、制品快照 | FSPEC + GSD + Superpowers |
| **M7** | 执行日志+指标 | 执行追踪、质量指标仪表板、Token 成本追踪 | Spec Kitty + GSD |
| **M8** | 事后调查+审计 | 决策审计、失败事后分析、Forensics 命令 | GSD + OpenAI |
| **M9** | 审批门控+决策记录 | 可配置审批点、决策持久化、升级机制 | OAC + Superpowers |
| **M10** | 持续学习引擎 | Instinct 学习、模式提取、Skill 进化 | ECC CL-v2 + OmO |

---

## 三、最终架构设计

### 3.1 整体架构

```
+================================================================+
||                    用户 / AI Agent                             ||
+================================================================+
      |                                                    ^
      v                                                    |
+-----+----------------------------------------------------+-----+
|                     M9 审批门控 + 决策记录                       |
|  (所有写操作需确认 · 决策持久化 · 升级机制)                      |
+-----+----------------------------------------------------+-----+
      |                                                    ^
      v                                                    |
+-----+----------------------------------------------------+-----+
|                     M1 配置中心                                 |
|  config.yml · Profile · Hook Runtime · 环境适配                 |
+-----+----------------------------------------------------+-----+
      |
      v
+-----+----------------------------------------------------+------+
|                     M2 工作流状态机                              |
|  progress.md · HANDOFF.json · 前置条件 · 状态转换               |
+-+----------+-----------+-----------+----------+-----------+-----+
  |          |           |           |          |           |
  v          v           v           v          v           v
+----+   +----+   +-----+   +------+   +------+   +------+
| /0 |   | /1 |   | /2  |   | /3-5 |   | /6   |   | /8-11|
|制定 |-->|需求 |-->|规范  |-->|设计   |-->|编码   |-->|测试   |
|上下 |   |分析 |   |      |   |实施   |   |      |   |归档   |
|文   |   |    |   |      |   |检测   |   |      |   |      |
+--+-+   +--+-+   +--+--+   +--+---+   +--+---+   +--+---+
   |        |        |         |          |           |
   +--------+--------+---------+----------+-----------+
   |                                                  |
   v                                                  v
+--+--------------------------------------------------+---+
|              M3 确定性验证引擎 (每个阶段触发)               |
|  lint-specs.sh · consistency-check.sh · harness-audit   |
+--+--------------------------------------------------+---+
   |                                                  |
   v                                                  v
+--+--------------------------------------------------+---+
|              M4 安全审计系统 (持续运行)                     |
|  security-scan.sh · 权限白名单 · 危险命令拦截              |
+--+--------------------------------------------------+---+
   |                                                  |
   v                                                  v
+--+--------------------------------------------------+---+
|              M5 增强反馈回路                                |
|  自愈循环 · 两阶段审查 · Back-Pressure · TDD 纪律          |
+--+--------------------------------------------------+---+
   |                                                  |
   v                                                  v
+--+-----------+--+--+-----------+--+-+---------------+---+
| M6 快照/回滚  |  | M7 执行日志  |  | M8 事后调查+审计   |
| Git Checkpoint|  | 质量指标     |  | Forensics        |
| Worktree     |  | Token 追踪   |  | 决策日志          |
+--------------+  +--------------+  +------------------+
                                           |
                                           v
                                    +------+------+
                                    | M10 持续学习 |
                                    | Instinct    |
                                    | Skill 进化   |
                                    +-------------+
```

### 3.2 核心设计原则

| 原则 | 来源 | 说明 |
|------|------|------|
| **失败即信号** | OpenAI | Agent 失败时改进 Harness，而非简单重试 |
| **Back-Pressure** | HumanLayer | 成功静默、失败详输出，保护上下文窗口 |
| **MVI** | OAC | 最小可用信息原则，按需加载上下文 |
| **渐进增强** | 通用 | 在现有命令上叠加能力，不破坏已有流程 |
| **确定性优先** | OpenAI | 能用脚本验证的不依赖 LLM |
| **两阶段审查** | Superpowers | 先查规范合规，再查代码质量 |
| **原子提交** | GSD | 每个任务一个提交，可精确回滚 |

---

## 四、十大核心模块详细设计

### M1: 配置中心

**参考**: ECC Hook Runtime + OAC Context System + OpenSpec Profile

**文件**: `.specify/harness/config.yml`

```yaml
harness:
  version: "2.0"
  project_name: ""

# === Profile 系统 (参考 GSD/OAC) ===
profile: "standard"  # minimal | standard | strict
profiles:
  minimal:
    quality_gates: { min_coverage: 70, max_clarifications: 5, self_healing_rounds: 2 }
    security: { enabled: false }
    observability: { execution_log: true, quality_metrics: false, audit_log: false }
  standard:
    quality_gates: { min_coverage: 85, max_clarifications: 3, self_healing_rounds: 3 }
    security: { enabled: true, scan_on_commit: true }
    observability: { execution_log: true, quality_metrics: true, audit_log: true }
  strict:
    quality_gates: { min_coverage: 95, max_clarifications: 1, self_healing_rounds: 5 }
    security: { enabled: true, scan_on_commit: true, block_on_critical: true }
    observability: { execution_log: true, quality_metrics: true, audit_log: true }

# === Hook Runtime 控制 (参考 ECC) ===
hooks:
  profile: "standard"  # minimal | standard | strict
  disabled: []         # 禁用特定 Hook, 如 ["security-scan", "lint"]

# === 工作流编排 (参考 GSD) ===
orchestration:
  auto_advance: false          # 自动串联命令
  parallel_execution: true     # 允许并行任务
  require_approval: true       # 写操作需审批
  commit_strategy: "atomic"    # atomic | phase | milestone
  branch_strategy: "phase"     # none | phase | milestone

# === 安全 (参考 ECC AgentShield + GSD) ===
security:
  sensitive_patterns:
    - '(password|secret|api_key|token)\s*[:=]\s*["\x27][^"\x27]{8,}'
    - 'BEGIN.*PRIVATE KEY'
    - 'AKIA[0-9A-Z]{16}'
  dangerous_commands: ["rm -rf /", "DROP TABLE", "DROP DATABASE"]
  file_access:
    allow: ["specs/", "src/", ".specify/", ".windsurf/"]
    deny: [".env", ".env.*", "**/*.pem", "**/*.key"]

# === 可观测性 ===
observability:
  execution_log: { max_entries: 100 }
  quality_metrics: { update_on: ["/9", "/11"] }
  audit_log: { retention_days: 90 }

# === 持续学习 (参考 ECC CL-v2) ===
learning:
  enabled: true
  instinct_confidence_threshold: 0.7
  max_instincts: 50
  auto_evolve: false
```

### M2: 工作流状态机

**参考**: GSD STATE.md + HANDOFF.json + Anthropic progress.txt

**文件**: `.specify/harness/state.md`

```markdown
# 工作流状态

<!-- 跨会话状态追踪。每次命令执行时读取和更新。 -->
<!-- 新对话开始时 Agent 必须首先读取此文件。 -->

## 全局状态

| 属性 | 值 |
|------|------|
| **Profile** | standard |
| **活跃需求数** | 2 |
| **最后活动** | 2026-03-30T10:15:00 |

## 活跃需求

### REQ-001: 用户认证模块

- **状态**: 实施中
- **当前阶段**: /6-编写代码
- **进度**: /1 ✅ /2 ✅ /3 ✅ /4 ✅ /5 ✅ /6 🔄 /8 ⏳ /9 ⏳ /11 ⏳
- **最后执行**: 2026-03-30T10:15:00
- **下一步**: 继续 `/6-编写代码 REQ-001`（任务 T015 起）
- **阻塞项**: 无
- **决策记录**: 选择 JWT 而非 Session（见 design.md 3.2 节）
```

**文件**: `.specify/harness/handoff.json` (参考 GSD)

```json
{
  "version": "1.0",
  "created_at": "2026-03-30T10:15:00Z",
  "reason": "会话暂停 - 等待外部 API 文档",
  "active_requirement": "REQ-001",
  "current_command": "/6-编写代码",
  "current_task": "T015",
  "context_summary": "已完成数据库表创建和用户注册接口，正在实施登录接口",
  "pending_decisions": ["OAuth2 provider 选择"],
  "files_in_progress": ["src/auth/login.py", "tests/test_login.py"],
  "resume_instructions": "读取 state.md → 加载 specs/REQ-001/tasks.md → 从 T015 继续"
}
```

**恢复协议** (新对话第一步):

```
1. 读取 .specify/harness/state.md        → 全局状态和活跃需求
2. 检查 .specify/harness/handoff.json     → 是否有暂停的工作
3. 读取 git log --oneline -20             → 最近代码变更
4. 加载 .specify/harness/config.yml       → Harness 配置
5. 根据状态建议下一步操作
```

### M3: 确定性验证引擎

**参考**: ECC Harness Audit + OpenAI CI 不变量 + HumanLayer Back-Pressure

#### 3a. 制品 Linter (`lint-specs.sh`)

与初版方案一致，增加以下来自 ECC 的增强：

- **Harness Audit 评分**: 运行完毕输出 A-F 等级评分（参考 ECC AgentShield）
- **Back-Pressure 输出**: 通过时仅输出一行 `✅ Lint PASS (A)`；失败时输出详细问题列表

#### 3b. 跨制品一致性检查 (`consistency-check.sh`)

与初版方案一致。

#### 3c. Harness Audit 命令 (新增，参考 ECC `/harness-audit`)

**文件**: `templates/commands/harness-audit.md`

```markdown
---
description: "对当前 Harness 配置和制品进行全面审计评分"
---

## /harness-audit

### 角色
Harness 工程师

### 输入
无需参数，自动扫描全部活跃需求

### 流程

1. **加载配置**: 读取 config.yml, state.md
2. **扫描制品完整性**: 对每个活跃需求运行 lint-specs.sh
3. **检查一致性**: 对每个活跃需求运行 consistency-check.sh
4. **安全扫描**: 运行 security-scan.sh
5. **评分**: 按以下维度评分 (每项 0-20 分，总分 0-100)
   - 制品完整性 (必需文件、必需章节)
   - 追溯完整性 (FR 覆盖、代码追溯)
   - 一致性 (跨制品引用)
   - 安全 (敏感信息、权限)
   - 文档同步 (changelog 未同步数)
6. **输出评级**:
   - A (90-100): 优秀
   - B (80-89): 良好
   - C (70-79): 合格
   - D (60-69): 需改进
   - F (<60): 不合格

### 输出
`.specify/harness/audit-report.md` - 最新审计报告
```

### M4: 安全审计系统

**参考**: ECC AgentShield (红蓝对抗 + A-F 评级 + CI 集成) + OpenDev 五层安全 + GSD deny list

#### 4a. 安全扫描 (`security-scan.sh`)

与初版方案一致，增加来自 ECC 的 A-F 安全评级输出。

#### 4b. 权限模型 (参考 OAC + GSD)

每个命令模板开头声明权限，且从 `config.yml` 的 `security.file_access` 读取白名单。

```markdown
### 权限声明 (从 config.yml 加载)

| 权限 | 范围 | 来源 |
|------|------|------|
| **读取** | config.security.file_access.allow | 配置文件 |
| **写入** | specs/[当前需求ID]/ | 动态限定 |
| **禁止** | config.security.file_access.deny | 配置文件 |
| **禁止命令** | config.security.dangerous_commands | 配置文件 |
```

#### 4c. 五层安全模型 (参考 OpenDev)

| 层 | 实现 | 检查时机 |
|----|------|---------|
| L1 Prompt 约束 | 命令模板中的权限声明 + 禁止列表 | 命令加载时 |
| L2 制品门控 | `/5-实施前检测` 只读模式 | 阶段转换时 |
| L3 文件权限 | config.yml 白名单/黑名单 | 每次文件操作 |
| L4 运行时监控 | security-scan.sh + pre-commit hook | 提交时 |
| L5 会话隔离 | 交接协议 + 角色分离 + Worktree | 角色切换时 |

### M5: 增强反馈回路

**参考**: Superpowers 两阶段审查 + HumanLayer Back-Pressure + ECC 验证循环

#### 5a. 两阶段审查 (参考 Superpowers)

在 `/6-编写代码` 的自愈循环中，将单一检查拆为两阶段：

```
阶段 1: 规范合规审查 (Spec Compliance)
  - tasks.md 任务是否完成
  - design.md 约束是否满足
  - FR 追溯是否完整
  → 不合规项必须修复后才进入阶段 2

阶段 2: 代码质量审查 (Code Quality)
  - 编码标准合规
  - 设计模式一致
  - 测试覆盖
  → 质量问题记录但不阻塞（除非是 Critical）
```

#### 5b. Back-Pressure 输出协议

所有验证脚本遵循统一的 Back-Pressure 输出协议：

```
成功: 仅输出 "✅ [检查名] PASS" (1行，最小上下文消耗)
失败: 输出 "❌ [检查名] FAIL" + 失败项详情 (仅失败项)
永远不输出: 通过的详细信息、进度条、装饰文本
```

#### 5c. TDD 纪律强化 (参考 Superpowers)

在 `/6-编写代码` 中嵌入 TDD 强制规则：

```
对每个任务:
1. RED   - 先写失败测试
2. GREEN - 写最小实现代码通过测试
3. REFACTOR - 重构，测试仍需通过
4. 如果发现代码先于测试编写 → 删除代码，从 RED 重新开始
```

### M6: 快照/回滚/恢复

**参考**: FSPEC Checkpoint + GSD Worktree + Superpowers Git Worktree + GSD 原子提交

#### 6a. Git Checkpoint (参考 FSPEC)

```bash
# snapshot.sh - 基于 git tag 的检查点
#!/bin/bash
REQ_ID="$1"; DESC="${2:-checkpoint}"
TAG="harness/ckpt/${REQ_ID}/$(date +%Y%m%d-%H%M%S)_${DESC}"
git tag "$TAG" -m "Harness checkpoint: ${REQ_ID} - ${DESC}"
echo "✅ Checkpoint: ${TAG}"
```

```bash
# restore.sh - 从检查点恢复
#!/bin/bash
REQ_ID="$1"; TAG="$2"
git stash push -m "pre-restore-$(date +%s)"
git checkout "$TAG" -- "specs/${REQ_ID}/"
echo "✅ Restored: ${TAG}"
```

#### 6b. 原子提交策略 (参考 GSD)

每个 tasks.md 任务完成后立即提交：

```
格式: <type>(<req-id>-<task-id>): <description>
示例: feat(REQ-001-T015): implement login endpoint
      test(REQ-001-T015): add login endpoint tests
```

**好处** (GSD 验证): `git bisect` 可精确定位故障任务；每个任务可单独回滚。

#### 6c. 自动快照时机

| 命令 | 快照时机 | 标签描述 |
|------|---------|---------|
| `/2` 完成后 | spec.md 生成 | `post-spec` |
| `/3` 完成后 | design.md 生成 | `post-design` |
| `/4` 完成后 | tasks.md 生成 | `post-tasks` |
| `/5` 通过后 | 一致性验证通过 | `pre-implement` |
| `/6` 完成后 | 代码实现完成 | `post-implement` |

### M7: 执行日志 + 指标

**参考**: Spec Kitty 仪表板 + GSD progress 命令

#### 7a. 执行日志 (`.specify/harness/execution-log.md`)

与初版方案一致。

#### 7b. 质量指标仪表板 (`.specify/harness/quality-metrics.md`)

与初版方案一致，增加来自 ECC 的 Harness Audit 评分趋势。

#### 7c. Token 成本追踪 (参考 ECC)

在执行日志中增加估算 Token 消耗字段，便于优化：

```markdown
| 属性 | 值 |
|------|------|
| **估算 Token** | ~15K input + ~5K output |
| **上下文使用率** | 35% (70K/200K) |
```

### M8: 事后调查 + 审计

**参考**: GSD `/gsd:forensics` + OpenAI "失败即信号"

#### 8a. Forensics 命令 (新增)

**文件**: `templates/commands/harness-forensics.md`

```markdown
---
description: "对失败或卡住的工作流进行事后调查"
---

## /harness-forensics

### 角色
Harness 工程师

### 输入
$ARGUMENTS: 需求 ID 或 "latest"

### 流程

1. **收集证据**:
   - 读取 execution-log.md 中该需求的所有执行记录
   - 读取 audit-log.md 中的相关决策
   - 读取 git log 中的相关提交
   - 读取自愈循环的升级记录
   - 读取测试报告中的失败用例

2. **分析失败模式**:
   - 哪个阶段失败最多？
   - 自愈循环平均几轮？
   - 哪类问题反复出现？
   - 人工干预集中在哪？

3. **根因分类**:
   - 规范不清晰 → 建议改进 /2 模板
   - 设计不完整 → 建议改进 /3 模板
   - 任务粒度不当 → 建议调整 config.yml 阈值
   - 测试覆盖不足 → 建议加强 /8 模板
   - Harness 配置不当 → 建议调整 config.yml

4. **输出改进建议**:
   生成 `.specify/harness/forensics/[REQ_ID]-forensics.md`
   包含: 时间线、失败模式、根因、改进建议

5. **更新 Harness** (如适用):
   将验证通过的改进建议应用到命令模板或配置
   记录到 templates/commands/CHANGELOG.md
```

#### 8b. 决策审计日志

与初版方案一致。

### M9: 审批门控 + 决策记录

**参考**: OAC 审批门控 + Superpowers human checkpoints

#### 9a. 可配置审批点

从 `config.yml` 的 `orchestration.require_approval` 控制：

| 严格度 | 审批范围 |
|--------|---------|
| `minimal` | 仅 `/6` 代码写入和 `/9` 发布决策 |
| `standard` | 阶段转换 + 代码写入 + 发布决策 |
| `strict` | 所有文件写入 + 命令执行 + 阶段转换 |

#### 9b. 决策持久化

每次人工决策自动追加到 `.specify/harness/audit-log.md`:

```markdown
### [时间戳] [决策类型]
- **需求**: REQ-ID
- **决策者**: 用户
- **选择**: [选项A / 选项B / 自定义]
- **理由**: [用户提供的理由，如有]
- **影响**: [受影响的制品/文件]
```

### M10: 持续学习引擎

**参考**: ECC Continuous Learning v2 + OmO `/init-deep`

#### 10a. Instinct 学习 (参考 ECC)

在 `/11-归档需求` 时，从完成的需求中提取 Instinct:

```markdown
# .specify/harness/instincts.md

## 已验证 Instinct (置信度 > 0.7)

### INST-001: JWT 优于 Session [置信度: 0.9]
- **来源**: REQ-001
- **场景**: 需要无状态认证时
- **规则**: 选择 JWT + httpOnly Cookie
- **验证**: 3 个需求中验证通过

### INST-002: 数据库迁移先于接口开发 [置信度: 0.8]
- **来源**: REQ-001, REQ-003
- **场景**: 涉及新表创建时
- **规则**: tasks.md 中数据库任务必须在接口任务之前
```

#### 10b. Skill 进化 (参考 ECC `/evolve`)

当相关 Instinct 达到 5 条以上且置信度均 > 0.8 时，自动聚类为新的 Skill 文件:

```
Instinct 积累 → 聚类相关模式 → 生成 SKILL.md → 加入项目记忆
```

---

## 五、全自动编排引擎 (核心)

> **目标**: 提交一个需求，全自动完成 `/1` → `/2` → `/3` → `/4` → `/5` → `/6` → `/8` → `/9` → `/10` → `/11` 全流程。
> 中间自愈，除非遇到必须人工确认的决策点才暂停。
> **参考**: GSD `auto_advance` + `/gsd:execute-phase` + ECC `/loop-start` + Superpowers subagent-driven-development + OmO Sisyphus

### 5.1 全自动入口命令: `/harness-auto`

```markdown
---
description: "全自动需求交付: 从需求提交到归档，一键完成"
---

## /harness-auto

### 用法

/harness-auto <需求描述或需求文档路径> [--mode=auto|guided] [--profile=strict]

### 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| mode | auto | auto=全自动, guided=每阶段确认 |
| profile | 从 config.yml | 覆盖 Harness profile |
| skip-discuss | false | 跳过澄清阶段，使用推断默认值 |
| dry-run | false | 仅生成计划，不执行代码 |
```

### 5.2 全流程状态机

```
                        /harness-auto <需求>
                              |
                              v
+====================================================================+
||                     Phase 0: 初始化                               ||
||  创建需求目录 · 初始化 state.md · 加载 config.yml · 创建分支      ||
+============================+=======================================+
                              |
                              v
+--------------------------------------------------------------------+
|  Phase 1: 需求分析 (/1)                                            |
|  自动解析需求 → 生成 requirement.md                                 |
|  ┌──────────────────────────────┐                                  |
|  │ 澄清循环 (最多 N 轮):       │                                  |
|  │  有歧义项? ──是──> 尝试自动推断                                  |
|  │      │              │                                           |
|  │      │         推断失败?──是──> [人工确认点①] 请用户澄清         |
|  │      │              │                                           |
|  │      否             否(推断成功)                                 |
|  │      │              │                                           |
|  │      v              v                                           |
|  │    完成 <──────── 继续                                          |
|  └──────────────────────────────┘                                  |
|  完成条件: requirement.md 存在 且 无 P0 歧义项                      |
+============================+=======================================+
                              |
                              v
+--------------------------------------------------------------------+
|  Phase 2: 需求规范 (/2)                                            |
|  自动生成 spec.md → 10类覆盖扫描 → lint-specs.sh                   |
|  ┌──────────────────────────────┐                                  |
|  │ 自愈循环 (最多 3 轮):        │                                  |
|  │  lint 失败? ──是──> 自动修复                                     |
|  │      │                                                          |
|  │      否                                                         |
|  │      v                                                          |
|  │  覆盖扫描 < 90%? ──是──> 自动补充                               |
|  │      │                                                          |
|  │      否                                                         |
|  │      v                                                          |
|  │    通过                                                         |
|  └──────────────────────────────┘                                  |
|  完成条件: spec.md lint PASS 且 覆盖率 >= 90%                       |
|  Checkpoint: git tag harness/ckpt/REQ-xxx/post-spec                |
+============================+=======================================+
                              |
                              v
+--------------------------------------------------------------------+
|  Phase 3: 开发设计 (/3)                                            |
|  加载项目记忆 → 生成 design.md → consistency-check.sh              |
|  ┌──────────────────────────────┐                                  |
|  │ 自愈循环 (最多 3 轮):        │                                  |
|  │  一致性检查失败? ──是──> 自动修复                                |
|  │      │                                                          |
|  │      否                                                         |
|  │      v                                                          |
|  │  宪章检查失败? ──是──> 自动调整                                  |
|  │      │                                                          |
|  │      否                                                         |
|  │      v                                                          |
|  │    通过                                                         |
|  └──────────────────────────────┘                                  |
|  ⚠️ 架构决策涉及新技术栈? ──是──> [人工确认点②]                    |
|  完成条件: design.md 通过一致性 + 宪章检查                          |
|  Checkpoint: git tag harness/ckpt/REQ-xxx/post-design              |
+============================+=======================================+
                              |
                              v
+--------------------------------------------------------------------+
|  Phase 4: 实施步骤 (/4)                                            |
|  生成 tasks.md (XML 结构化, 每个任务含验证步骤)                     |
|  完成条件: tasks.md 通过完整性检查                                  |
|  Checkpoint: git tag harness/ckpt/REQ-xxx/post-tasks               |
+============================+=======================================+
                              |
                              v
+--------------------------------------------------------------------+
|  Phase 5: 实施前检测 (/5) — 质量门控                                |
|  只读非破坏性检查: spec + design + tasks 一致性                     |
|  Harness Audit 评分                                                 |
|  ┌──────────────────────────────┐                                  |
|  │ 评分 < C (70分)?             │                                  |
|  │   是 → 自动回退修复 (最多2轮)                                    |
|  │   仍然 < C → [人工确认点③] 是否继续?                             |
|  │   否 → 通过，进入实施                                           |
|  └──────────────────────────────┘                                  |
|  完成条件: Harness Audit >= C                                       |
|  Checkpoint: git tag harness/ckpt/REQ-xxx/pre-implement            |
+============================+=======================================+
                              |
                              v
+--------------------------------------------------------------------+
|  Phase 6: 编写代码 (/6) — 核心实施                                  |
|  按 tasks.md 顺序执行每个任务                                       |
|  ┌──────────────────────────────────────────────────┐              |
|  │ 对每个任务 T:                                     │              |
|  │  1. TDD RED: 写失败测试                           │              |
|  │  2. TDD GREEN: 写最小实现                         │              |
|  │  3. TDD REFACTOR: 重构                            │              |
|  │  4. 原子提交: feat(REQ-xxx-Txxx): ...             │              |
|  │  5. 两阶段审查:                                   │              |
|  │     阶段1 规范合规 → 不通过 → 自愈修复 (最多3轮)   │              |
|  │     阶段2 代码质量 → Critical → 自愈; 非Critical记录│             |
|  │  6. 自愈失败 → [人工确认点④]                       │              |
|  │                                                    │              |
|  │ 所有任务完成后:                                    │              |
|  │  全量 lint + consistency + security 扫描            │              |
|  │  安全扫描发现 Critical → [人工确认点⑤]             │              |
|  └──────────────────────────────────────────────────┘              |
|  完成条件: 所有任务 DONE + 全量检查 PASS                            |
|  Checkpoint: git tag harness/ckpt/REQ-xxx/post-implement           |
+============================+=======================================+
                              |
                              v
+--------------------------------------------------------------------+
|  Phase 7: 生成测试用例 (/8)                                         |
|  基于 spec.md + design.md 生成 case.md                              |
|  完成条件: case.md 覆盖所有用户故事                                  |
+============================+=======================================+
                              |
                              v
+--------------------------------------------------------------------+
|  Phase 8: 测试验证 (/9)                                             |
|  执行 case.md 中的测试用例                                          |
|  ┌──────────────────────────────────────────────────┐              |
|  │ 自动可执行测试: 直接运行                          │              |
|  │ 手动验证测试: 标记为需人工验证                     │              |
|  │                                                    │              |
|  │ 测试失败?                                         │              |
|  │   是 → 自动缺陷修复循环 (最多 3 轮):              │              |
|  │        定位失败原因 → 修复代码 → 重跑测试           │              |
|  │        仍然失败 → [人工确认点⑥]                    │              |
|  │   否 → 通过                                       │              |
|  │                                                    │              |
|  │ 有手动验证项? ──是──> [人工确认点⑦] 请用户验证     │              |
|  └──────────────────────────────────────────────────┘              |
|  完成条件: 自动测试全 PASS + 手动测试已确认                          |
|  更新: quality-metrics.md                                           |
+============================+=======================================+
                              |
                              v
+--------------------------------------------------------------------+
|  Phase 9: 同步文档 (/10)                                            |
|  自动同步 .ai-changelogs.md → spec/design/tasks                    |
|  完成条件: 无未同步的 changelog 条目                                 |
+============================+=======================================+
                              |
                              v
+--------------------------------------------------------------------+
|  Phase 10: 归档需求 (/11)                                           |
|  归档 → 提取 Instinct → 更新项目记忆 → Forensics 分析              |
|  完成条件: 需求目录已移至 archived/                                  |
+============================+=======================================+
                              |
                              v
                      ✅ 需求交付完成
                    更新 state.md: DONE
                    输出交付报告
```

### 5.3 人工确认点定义

全流程中仅以下 7 个场景需要人工介入，其余全部自动完成：

| 确认点 | 触发条件 | 阻塞级别 | 超时处理 |
|--------|---------|---------|---------|
| **①** 需求澄清 | 存在无法自动推断的歧义项 | **阻塞** | 无（必须等待用户） |
| **②** 架构决策 | 引入新技术栈或架构范式 | **阻塞** | 无（必须等待用户） |
| **③** 质量门控 | Harness Audit < C 且自愈失败 | **可跳过** | 用户可选"继续"或"停止" |
| **④** 代码自愈失败 | 单任务自愈 3 轮仍失败 | **阻塞** | 输出问题描述等待用户指导 |
| **⑤** 安全风险 | 安全扫描发现 Critical 级别问题 | **阻塞** | 无（必须等待用户） |
| **⑥** 测试修复失败 | 自动缺陷修复 3 轮仍失败 | **阻塞** | 输出失败详情等待用户 |
| **⑦** 手动验证 | 存在无法自动执行的测试用例 | **可跳过** | 用户可选"跳过"或"验证" |

**设计原则**:
- 默认全自动，仅在**不确定性高**或**风险高**时暂停
- 所有确认点均记录到 `audit-log.md`
- `--mode=guided` 可在每个阶段转换时额外确认

### 5.4 自愈引擎详细设计

```
                    自愈引擎 (Self-Healing Engine)
                    ============================

  检测到问题 (lint失败 / 一致性失败 / 测试失败 / 审查不通过)
         |
         v
  +------+------+
  | 分类问题类型 |
  +------+------+
         |
    +----+----+----+----+
    |         |         |
    v         v         v
  结构问题  逻辑问题  外部依赖
  (格式/   (代码/    (API/
   缺失)    设计)     环境)
    |         |         |
    v         v         v
  自动修复  分析根因  标记为
  成功率    尝试修复  人工处理
  ~95%     ~70%      →确认点
    |         |
    v         v
  重新验证  重新验证
    |         |
  通过?     通过?
  是→继续   是→继续
  否→再来   否→再来
    |         |
  超过N轮?  超过N轮?
  是→升级   是→升级
  到人工     到人工
```

**自愈轮次配置** (从 config.yml 读取):

| Profile | 制品自愈轮次 | 代码自愈轮次 | 测试修复轮次 |
|---------|------------|------------|------------|
| minimal | 2 | 2 | 1 |
| standard | 3 | 3 | 3 |
| strict | 5 | 5 | 5 |

**自愈日志**: 每次自愈尝试记录到 `execution-log.md`:

```markdown
#### 自愈记录 #003
- **阶段**: /6-编写代码 T015
- **问题类型**: 测试失败 (TypeError: undefined is not a function)
- **轮次**: 2/3
- **修复动作**: 添加空值检查 + 更新类型定义
- **结果**: ✅ 修复成功，测试通过
```

### 5.5 自动推进条件 (Auto-Advance Criteria)

每个阶段的完成条件明确定义，编排引擎据此自动推进：

| 阶段 | 完成条件 (全部满足才推进) | 失败处理 |
|------|-------------------------|---------|
| `/1` 需求分析 | requirement.md 存在 + 无 P0 歧义 + lint PASS | 澄清循环 / 人工①  |
| `/2` 需求规范 | spec.md lint PASS + 覆盖率 ≥ 90% | 自愈 → 人工 |
| `/3` 开发设计 | design.md 一致性 PASS + 宪章 PASS | 自愈 → 人工② |
| `/4` 实施步骤 | tasks.md 完整性 PASS + 任务数 > 0 | 自愈 |
| `/5` 实施前检测 | Harness Audit ≥ C (70分) | 自愈 → 人工③ |
| `/6` 编写代码 | 所有任务 DONE + lint PASS + security PASS | 自愈 → 人工④⑤ |
| `/8` 测试用例 | case.md 存在 + 覆盖所有用户故事 | 自愈 |
| `/9` 测试验证 | 自动测试全 PASS + 手动已确认 | 自愈 → 人工⑥⑦ |
| `/10` 同步文档 | 无未同步 changelog | 自动 |
| `/11` 归档 | 目录已归档 + 记忆已更新 | 自动 |

### 5.6 编排引擎在 config.yml 中的配置

```yaml
# === 全自动编排 (新增) ===
orchestration:
  auto_advance: true             # 核心开关: 启用全自动推进
  mode: "auto"                   # auto | guided
  parallel_execution: true       # 允许并行任务 (如 /6 中的独立任务)
  commit_strategy: "atomic"      # atomic | phase | milestone
  branch_strategy: "phase"       # none | phase | milestone

  # 人工确认策略
  approval:
    ambiguity_resolution: "auto-infer"   # auto-infer | always-ask
    architecture_decisions: "ask"         # ask | auto (新技术栈时)
    quality_gate_bypass: "ask"           # ask | block | skip
    security_critical: "block"           # block (永远阻塞)
    manual_tests: "ask"                  # ask | skip

  # 自愈配置
  self_healing:
    spec_rounds: 3           # 制品自愈最大轮次
    code_rounds: 3           # 代码自愈最大轮次
    test_fix_rounds: 3       # 测试修复最大轮次
    escalation: "human"      # human | abort | skip

  # 自动推进超时
  timeouts:
    per_phase_minutes: 30    # 单阶段超时
    total_minutes: 240       # 全流程超时
    human_wait_minutes: 0    # 0=无限等待人工

  # 澄清策略
  clarification:
    max_rounds: 5            # 最大澄清轮次
    auto_infer: true         # 尝试自动推断模糊项
    infer_confidence: 0.8    # 自动推断置信度阈值
    record_inferences: true  # 记录所有自动推断到 audit-log
```

### 5.7 `/harness-auto` 命令模板完整设计

**文件**: `templates/commands/harness-auto.md`

```markdown
---
description: "全自动需求交付引擎: 提交需求 → 自动完成全流程 → 交付"
---

## 角色

全自动编排引擎 (Autonomous Orchestrator)。你是一个需求交付自动化系统，
职责是驱动需求从提交到归档的全流程自动完成。

## 核心规则

1. **永不停下，除非遇到人工确认点**
2. **每个阶段完成后立即推进到下一个阶段**
3. **遇到问题先自愈，自愈失败才升级**
4. **所有操作记录到 execution-log.md**
5. **所有决策记录到 audit-log.md**

## 执行协议

### Phase 0: 初始化

1. 读取 `.specify/harness/config.yml` → 加载编排配置
2. 读取 `.specify/harness/state.md` → 检查是否有未完成的需求
3. 为新需求生成 REQ-ID，创建 `specs/[REQ-ID]/` 目录
4. 创建 Git 分支: `harness/[REQ-ID]`
5. 更新 state.md: 新增活跃需求，状态=初始化
6. 记录 execution-log.md: ⏳ 开始全自动交付

### Phase 1-10: 自动执行

对每个阶段 P (从 /1 到 /11):
  1. 检查前置条件 → 不满足则报错停止
  2. 记录 execution-log: ⏳ Phase P 执行中
  3. 调用对应命令模板执行
  4. 检查完成条件:
     - PASS → 记录日志 + 创建 Checkpoint + 推进到 P+1
     - FAIL → 进入自愈循环:
       - 分析失败原因
       - 尝试修复 (最多 N 轮，N 从 config 读取)
       - 每轮修复后重新检查完成条件
       - 自愈成功 → 记录日志 + 推进
       - 自愈用尽 → 检查是否为人工确认点:
         - 是 → 暂停，输出问题描述，等待用户
         - 否 → 记录失败，abort 或 skip (从 config 读取)

### 完成

1. 输出交付报告 (requirement → spec → design → tasks → code → test → archive)
2. 更新 state.md: 需求状态=DONE
3. 更新 quality-metrics.md
4. 如果 config.learning.enabled: 提取 Instinct

## 交付报告格式

    # 需求交付报告: [REQ-ID] [需求名称]

    ## 执行摘要
    - 总耗时: XX 分钟
    - 自愈次数: X 次 (成功 X / 失败 X)
    - 人工确认: X 次
    - Harness Audit 评分: X (A-F)
    - 测试通过率: XX%

    ## 阶段详情
    | 阶段 | 状态 | 耗时 | 自愈 | 确认 |
    |------|------|------|------|------|
    | /1   | ✅   | 3min | 0    | 0    |
    | /2   | ✅   | 5min | 1    | 0    |
    | ...  | ...  | ...  | ...  | ...  |

    ## 产出制品
    - specs/[REQ-ID]/requirement.md
    - specs/[REQ-ID]/spec.md
    - specs/[REQ-ID]/design.md
    - specs/[REQ-ID]/tasks.md
    - specs/[REQ-ID]/case.md
    - specs/[REQ-ID]/result.md

    ## 学习 (Instinct)
    - INST-xxx: [提取的模式]
```

### 5.8 跨会话自动恢复

全自动流程可能跨越多个 AI 对话窗口。恢复协议：

```
新对话开始:
  1. 读取 state.md → 发现活跃的 auto 流程
  2. 读取 handoff.json → 获取断点信息
  3. 读取 execution-log.md → 获取最后成功阶段
  4. 自动从断点阶段继续执行
  5. 无需用户手动指令
```

**state.md 中的 auto 模式标记**:

```markdown
### REQ-001: 用户认证模块

- **状态**: 自动执行中
- **模式**: auto (全自动)
- **当前阶段**: /6-编写代码
- **进度**: /1 ✅ /2 ✅ /3 ✅ /4 ✅ /5 ✅ /6 🔄(T015) /8 ⏳ /9 ⏳ /11 ⏳
- **自愈统计**: 总计 4 次 (成功 3 / 失败 1)
- **人工确认**: 1 次 (①需求澄清: 用户确认使用 JWT)
- **下一步**: 自动继续 /6 T015
```

### 5.9 典型全自动执行流程示例

```
用户: /harness-auto 实现用户注册和登录功能，支持邮箱验证

[Phase 0] ⏳ 初始化...
  → 生成 REQ-007, 创建 specs/REQ-007/, 分支 harness/REQ-007
  → ✅ 初始化完成 (2s)

[Phase 1] ⏳ 需求分析...
  → 解析需求，发现 2 个歧义项:
    - 邮箱验证方式: 验证码 or 链接? → 自动推断: 链接 (置信度 0.85) ✅
    - 密码强度要求? → 无法推断 (置信度 0.4) → ⚠️ 人工确认点①
  → 🔔 请确认: 密码强度要求是什么?

用户: 至少8位，含大小写和数字

  → ✅ requirement.md 生成完成, lint PASS (45s)
  → 📝 audit-log: 用户确认密码强度要求

[Phase 2] ⏳ 需求规范...
  → spec.md 生成完成
  → lint-specs.sh: ❌ FAIL (缺少边界条件: 邮箱格式验证)
  → 自愈 #1: 补充邮箱格式验证边界条件
  → lint-specs.sh: ✅ PASS, 覆盖率 94%
  → Checkpoint: harness/ckpt/REQ-007/post-spec (52s)

[Phase 3] ⏳ 开发设计...
  → design.md 生成完成
  → consistency-check.sh: ✅ PASS
  → 宪章检查: ✅ PASS
  → Checkpoint: harness/ckpt/REQ-007/post-design (38s)

[Phase 4] ⏳ 实施步骤...
  → tasks.md 生成: 12 个任务, 3 个执行 wave
  → 完整性检查: ✅ PASS
  → Checkpoint: harness/ckpt/REQ-007/post-tasks (25s)

[Phase 5] ⏳ 实施前检测...
  → Harness Audit: B (83分) ✅
  → Checkpoint: harness/ckpt/REQ-007/pre-implement (15s)

[Phase 6] ⏳ 编写代码...
  → T001: 数据库迁移 → RED→GREEN→REFACTOR → ✅ → commit
  → T002: 用户模型 → RED→GREEN→REFACTOR → ✅ → commit
  → T003: 注册接口 → RED→GREEN → 阶段1审查失败(缺少输入验证)
    → 自愈 #2: 添加 Pydantic schema → ✅
  → T004-T012: ... 全部完成
  → 全量检查: lint ✅ consistency ✅ security ✅
  → Checkpoint: harness/ckpt/REQ-007/post-implement (12min)

[Phase 7] ⏳ 生成测试用例...
  → case.md: 28 个用例 (24 自动 + 4 手动)
  → ✅ 完成 (30s)

[Phase 8] ⏳ 测试验证...
  → 自动测试: 22/24 PASS, 2 FAIL
  → 自愈 #3: 修复 token 过期时间配置 → 重跑 → 24/24 PASS ✅
  → 手动验证: 4 项 → ⚠️ 人工确认点⑦
  → 🔔 请验证以下 4 项:
    - [ ] 注册邮件收到验证链接
    - [ ] 点击链接后账号激活
    - [ ] 过期链接显示错误信息
    - [ ] 重复注册被拒绝

用户: 全部验证通过

  → ✅ 测试全部通过, quality-metrics 已更新 (8min)

[Phase 9] ⏳ 同步文档... → ✅ 完成 (5s)

[Phase 10] ⏳ 归档需求...
  → 归档到 specs/archived/REQ-007/
  → 提取 Instinct: INST-012 "邮箱验证使用链接而非验证码"
  → 更新项目记忆
  → ✅ 完成 (15s)

===== 交付报告 =====
需求: REQ-007 用户注册和登录功能
总耗时: 22 分钟
自愈: 3 次 (全部成功)
人工确认: 2 次 (需求澄清 + 手动测试)
Harness Audit: B (83分)
测试通过率: 100% (28/28)
========================
```

### 5.10 上下文隔离与 Agent 调度架构

> **核心问题**: 全自动流程中，主流程 (`/harness-auto`) 编排 10+ 个子流程，
> 如果全部在同一会话中执行，上下文窗口会被子流程的中间产物污染，
> 导致后续子流程质量下降甚至失败。
>
> **设计原则**: **文件是唯一的上下文传递通道，会话不是记忆层。**

#### 5.10.1 主/子流程架构模型

```
+=============================================================+
||              主流程 (Master Orchestrator)                    ||
||  职责: 调度 · 监控 · 决策 · 人工交互                         ||
||  上下文: 仅保留 state.md + config.yml + 当前阶段元信息        ||
+=============================================================+
     |          |           |           |          |
     | dispatch | dispatch  | dispatch  | dispatch | ...
     v          v           v           v          v
  +------+  +------+  +--------+  +------+  +------+
  | /1   |  | /2   |  | /3     |  | /6   |  | /9   |
  | 子流程|  | 子流程|  | 子流程  |  | 子流程|  | 子流程|
  +--+---+  +--+---+  +--+-----+  +--+---+  +--+---+
     |          |           |           |          |
     v          v           v           v          v
  [文件写入] [文件写入]  [文件写入]  [文件写入] [文件写入]
     |          |           |           |          |
     +----------+-----------+-----------+----------+
                            |
                            v
              .specify/harness/state.md  (状态汇总)
              specs/REQ-xxx/*.md         (制品文件)
              .specify/harness/*.md      (日志/指标)
```

**关键规则**:
1. **子流程只从文件读取输入**，不依赖会话中的对话历史
2. **子流程只向文件写入输出**，主流程通过读取文件获取结果
3. **主流程不传递大段文本给子流程**，只传递文件路径和阶段指令
4. **每个子流程的 Prompt 开头强制声明**: "忽略所有先前对话，仅从以下文件加载上下文"

#### 5.10.2 子流程 Prompt 标准模板 (上下文隔离协议)

每个命令模板的「步骤 0: Harness 初始化」改为 **上下文隔离版本**:

```markdown
### 步骤 0: 上下文隔离初始化

⚠️ **上下文隔离协议**:
本子流程在独立上下文中执行。
请忽略当前对话中所有先前消息，仅从以下文件加载上下文:

1. 读取 `.specify/harness/config.yml` → Harness 配置
2. 读取 `.specify/harness/state.md` → 找到当前需求和阶段
3. 读取 `specs/[REQ-ID]/` 下的相关制品文件 (仅本阶段需要的):
   - /1 需要: 无前置制品
   - /2 需要: requirement.md
   - /3 需要: requirement.md + spec.md
   - /4 需要: spec.md + design.md
   - /5 需要: spec.md + design.md + tasks.md
   - /6 需要: design.md + tasks.md
   - /8 需要: spec.md + design.md
   - /9 需要: case.md + design.md
   - /10 需要: .ai-changelogs.md
   - /11 需要: 全部制品

4. 读取 `.windsurf/skills/SKILL.md` → 项目宪章 (如存在)
5. 更新 execution-log.md: ⏳ 子流程启动

完成初始化后，从此步骤开始执行，不要回顾任何对话历史。
```

#### 5.10.3 IDE 适配策略 — 三级调度模型

根据 IDE 对多 Agent 的支持程度，采用三种不同的调度策略:

```
+-------------------------------------------------------------------+
|                  IDE 能力矩阵与调度策略                             |
+-------------------------------------------------------------------+
|                                                                     |
|  Level 3: 原生多 Agent (最优)                                       |
|  +---------------------------+                                      |
|  | Claude Code (Task 工具)    |  主流程 spawn 子 Agent              |
|  | Cursor (Background Agent) |  每个子流程 = 独立 Agent             |
|  | Codex (子进程)            |  天然上下文隔离                       |
|  +---------------------------+                                      |
|                                                                     |
|  Level 2: 有限多 Agent / 命令链                                     |
|  +---------------------------+                                      |
|  | Gemini CLI (嵌套调用)      |  主流程通过 CLI 调用子流程           |
|  | Amazon Q (prompt chaining) |  文件传递 + 命令返回                 |
|  +---------------------------+                                      |
|                                                                     |
|  Level 1: 单 Agent (需特殊处理)                                     |
|  +---------------------------+                                      |
|  | Windsurf (单会话)          |  上下文预算管理 + 分段执行           |
|  | Kilo Code (单会话)        |  自动暂停/恢复                       |
|  +---------------------------+                                      |
|                                                                     |
+-------------------------------------------------------------------+
```

### 5.11 Level 3 策略: 原生多 Agent 调度 (Cursor / Claude Code)

#### Cursor 实现

Cursor 支持 Background Agent，主流程可以派发独立 Agent 执行子流程:

```
主流程 (用户会话中的 /harness-auto):

  Phase N 开始:
    1. 写入 .specify/harness/dispatch/phase-N.json:
       {
         "phase": N,
         "command": "/2-需求规范",
         "req_id": "REQ-007",
         "input_files": ["specs/REQ-007/requirement.md"],
         "output_files": ["specs/REQ-007/spec.md"],
         "completion_signal": ".specify/harness/dispatch/phase-N.done"
       }

    2. 派发 Background Agent:
       → Prompt: "读取 .specify/harness/dispatch/phase-N.json，
                  执行指定命令，完成后创建 .done 信号文件"

    3. 主流程轮询 .done 文件:
       → 存在 → 读取输出文件 → 验证完成条件 → 推进
       → 超时 → 检查日志 → 自愈或升级

  Phase N 完成:
    → 删除 dispatch/phase-N.json 和 .done
    → 更新 state.md
    → 进入 Phase N+1
```

**优势**:
- 每个子流程获得**完全干净的上下文**
- 主流程上下文**只保留调度元信息**，不会膨胀
- 子流程失败不污染主流程上下文
- 可并行执行独立子流程 (如 /6 中的独立任务)

#### Claude Code 实现

Claude Code 原生支持 `Task` 工具派发子 Agent:

```
主流程:

  Phase N:
    Task(prompt="
      你是 [角色名]。
      读取 .specify/harness/dispatch/phase-N.json 获取任务指令。
      严格按照 templates/commands/[命令].md 执行。
      完成后更新 state.md 和 execution-log.md。
      创建 .specify/harness/dispatch/phase-N.done 信号文件。
    ")

    → Task 返回结果
    → 主流程验证完成条件
    → 推进或自愈
```

### 5.12 Level 1 策略: 单 Agent 上下文管理 (Windsurf)

Windsurf 不支持多 Agent，无法清理上下文。需要特殊策略:

#### 5.12.1 核心挑战

```
问题: 单会话执行 10 个阶段

  /1 需求分析 → 输出 ~5K tokens 到上下文
  /2 需求规范 → 输出 ~8K tokens (读 requirement.md + 生成 spec.md)
  /3 开发设计 → 输出 ~10K tokens
  ...
  /6 编写代码 → 输出 ~50K+ tokens (代码 + 测试 + 审查)

  到 /6 时，上下文已消耗 ~80K tokens
  后续阶段质量严重下降，甚至无法正常运行
```

#### 5.12.2 解决方案: 分段执行 + 自动暂停/恢复

**核心思路**: 不试图在一个会话中完成全部流程，而是**智能分段**，每段结束时自动暂停并指引用户开新会话。

```
+---------------------------------------------+
|  Windsurf 分段执行策略                        |
+---------------------------------------------+
|                                               |
|  Session 1: 规划阶段 (上下文轻量)              |
|  ┌───────────────────────────┐               |
|  │ Phase 0: 初始化            │               |
|  │ Phase 1: 需求分析 (/1)     │   ~15K tokens |
|  │ Phase 2: 需求规范 (/2)     │               |
|  │ → 自动暂停 + 写 handoff    │               |
|  └───────────────────────────┘               |
|         ↓ (用户开新会话)                       |
|  Session 2: 设计阶段                          |
|  ┌───────────────────────────┐               |
|  │ 自动恢复 (读 handoff)      │               |
|  │ Phase 3: 开发设计 (/3)     │   ~20K tokens |
|  │ Phase 4: 实施步骤 (/4)     │               |
|  │ Phase 5: 实施前检测 (/5)   │               |
|  │ → 自动暂停 + 写 handoff    │               |
|  └───────────────────────────┘               |
|         ↓ (用户开新会话)                       |
|  Session 3: 实施阶段 (上下文最重)              |
|  ┌───────────────────────────┐               |
|  │ 自动恢复 (读 handoff)      │               |
|  │ Phase 6: 编写代码 (/6)     │   ~60K tokens |
|  │ → 如果任务过多，中途再分段   │               |
|  │ → 自动暂停 + 写 handoff    │               |
|  └───────────────────────────┘               |
|         ↓ (用户开新会话)                       |
|  Session 4: 验证阶段                          |
|  ┌───────────────────────────┐               |
|  │ 自动恢复 (读 handoff)      │               |
|  │ Phase 7: 测试用例 (/8)     │   ~25K tokens |
|  │ Phase 8: 测试验证 (/9)     │               |
|  │ Phase 9: 同步文档 (/10)    │               |
|  │ Phase 10: 归档 (/11)       │               |
|  │ → 完成，输出交付报告        │               |
|  └───────────────────────────┘               |
|                                               |
+---------------------------------------------+
```

#### 5.12.3 自动暂停触发条件

```yaml
# config.yml 新增
orchestration:
  context_management:
    strategy: "auto"               # auto | manual | none
    # auto: 根据 IDE 能力自动选择策略
    # manual: 用户手动控制暂停点
    # none: 尝试单会话完成 (不推荐)

    windsurf:
      session_budget_tokens: 60000   # 单会话 token 预算
      pause_threshold: 0.7           # 达到预算 70% 时自动暂停
      phase_groups:                   # 分段策略
        session_1: ["/1", "/2"]          # 规划
        session_2: ["/3", "/4", "/5"]    # 设计
        session_3: ["/6"]                # 实施 (可能需要多个 session)
        session_4: ["/8", "/9", "/10", "/11"]  # 验证+归档
      code_phase_task_limit: 8       # /6 单 session 最多执行 8 个任务
```

#### 5.12.4 Windsurf 自动暂停/恢复协议

**自动暂停** (每个 session 结束时):

```markdown
## ⏸️ 自动暂停 — 需要新会话继续

当前阶段组已完成，为保证后续阶段质量，请开启新会话继续。

**已完成**: /1 ✅ /2 ✅
**下一步**: /3-开发设计

### 操作步骤:
1. 开启新的 Windsurf 会话
2. 输入: `/harness-resume`
3. 引擎将自动从 /3 继续

> 状态已保存到 .specify/harness/state.md 和 handoff.json
```

**自动恢复** (新会话第一步):

```markdown
### /harness-resume 恢复协议

1. 读取 `.specify/harness/state.md` → 获取当前进度
2. 读取 `.specify/harness/handoff.json` → 获取断点详情
3. 确定当前 session 应执行的阶段组 (从 config.yml 读取)
4. 从断点阶段开始执行
5. 本 session 的阶段组执行完毕后:
   - 如果还有后续阶段 → 自动暂停
   - 如果全部完成 → 输出交付报告
```

#### 5.12.5 Windsurf 上下文压缩技术

在单 session 内，进一步减少上下文消耗:

| 技术 | 实现 | 效果 |
|------|------|------|
| **Back-Pressure 输出** | 成功仅输出 1 行，失败才输出详情 | ~60% token 节省 |
| **文件优先** | 所有生成内容直接写入文件，不在对话中展示 | ~40% token 节省 |
| **上下文围栏** | 阶段切换时插入 `---CONTEXT FENCE---` 标记，指示 Agent 忽略围栏前内容 | 逻辑隔离 |
| **MVI 加载** | 每阶段仅读取必需的文件 (见 5.10.2 的文件清单) | 按需加载 |
| **摘要压缩** | 阶段完成后，将该阶段全部输出替换为 1 行摘要写入 state.md | 事后压缩 |

**上下文围栏示例**:

```
═══════════════════════════════════════════════════════
  ⚠️ CONTEXT FENCE — Phase 2 完成
  以下是 Phase 3 的独立上下文，忽略此围栏以上的所有内容。
  从文件加载上下文: state.md → specs/REQ-007/spec.md
═══════════════════════════════════════════════════════
```

### 5.13 config.yml 完整调度配置

```yaml
# === 调度与上下文管理 (新增) ===
orchestration:
  auto_advance: true
  mode: "auto"

  # Agent 调度策略 (根据 IDE 自动检测或手动指定)
  dispatch:
    strategy: "auto"    # auto | subagent | session-split | single
    # auto:          自动检测 IDE 能力，选择最优策略
    # subagent:      强制使用子 Agent 模式 (需 IDE 支持)
    # session-split: 强制分段执行 (适用于所有 IDE)
    # single:        强制单会话执行 (不推荐，仅用于小需求)

  # 子 Agent 配置 (Level 3 IDE)
  subagent:
    dispatch_dir: ".specify/harness/dispatch/"  # 调度文件目录
    poll_interval_seconds: 5     # 轮询完成信号间隔
    timeout_minutes: 30          # 单子流程超时
    max_parallel: 1              # 最大并行子流程数 (1=串行)

  # 分段执行配置 (Level 1 IDE: Windsurf)
  session_split:
    session_budget_tokens: 60000
    pause_threshold: 0.7
    phase_groups:
      - ["/1", "/2"]
      - ["/3", "/4", "/5"]
      - ["/6"]
      - ["/8", "/9", "/10", "/11"]
    code_phase_task_limit: 8
    auto_pause_message: true       # 自动输出暂停指引
    auto_resume_on_start: true     # 新会话自动检测并恢复

  # 通用上下文管理
  context:
    file_only: true                # 上下文仅通过文件传递
    context_fence: true            # 启用上下文围栏
    back_pressure: true            # 启用 Back-Pressure 输出
    mvi_loading: true              # 最小可用信息加载
```

### 5.14 调度文件协议

**调度目录**: `.specify/harness/dispatch/`

**阶段调度文件** (`phase-N.json`):

```json
{
  "version": "1.0",
  "phase": 3,
  "command": "/3-开发设计",
  "req_id": "REQ-007",
  "role": "高级架构师",
  "input_files": [
    "specs/REQ-007/requirement.md",
    "specs/REQ-007/spec.md",
    ".windsurf/skills/SKILL.md"
  ],
  "output_files": [
    "specs/REQ-007/design.md"
  ],
  "validation": {
    "scripts": ["consistency-check.sh"],
    "criteria": "design.md 通过一致性 + 宪章检查"
  },
  "completion_signal": ".specify/harness/dispatch/phase-3.done",
  "self_healing_rounds": 3,
  "created_at": "2026-03-30T10:15:00Z"
}
```

**完成信号文件** (`phase-N.done`):

```json
{
  "phase": 3,
  "status": "success",
  "duration_seconds": 38,
  "self_healing_count": 0,
  "output_files_created": ["specs/REQ-007/design.md"],
  "validation_result": "PASS",
  "completed_at": "2026-03-30T10:15:38Z"
}
```

**调度文件生命周期**:

```
主流程创建 phase-N.json
    → 子流程/新session 读取 phase-N.json
    → 子流程执行命令
    → 子流程创建 phase-N.done
    → 主流程读取 phase-N.done
    → 主流程删除 phase-N.json + phase-N.done
    → 主流程创建 phase-(N+1).json
    → ...
```

### 5.15 IDE 适配总结

| 特性 | Windsurf (L1) | Gemini CLI (L2) | Cursor (L3) | Claude Code (L3) |
|------|--------------|-----------------|-------------|-----------------|
| **调度方式** | 分段+新会话 | CLI 嵌套调用 | Background Agent | Task 工具 |
| **上下文隔离** | 通过新会话实现 | 通过新进程实现 | 天然隔离 | 天然隔离 |
| **自动恢复** | `/harness-resume` | 自动 | 自动 | 自动 |
| **并行执行** | ❌ 不支持 | ❌ 不支持 | ✅ 支持 | ✅ 支持 |
| **人工确认** | 在当前 session | 在当前 session | 主流程转发 | 主流程转发 |
| **预计 session 数** | 4-6 个 | 1 个 | 1 个 | 1 个 |
| **用户体验** | 需手动开新会话 | 全自动 | 全自动 | 全自动 |

**自动检测逻辑** (在 `/harness-auto` 初始化阶段):

```
检测当前 IDE 环境:
  1. 检查 config.yml 中 dispatch.strategy 是否手动指定
     → 是 → 使用指定策略
     → 否 → 自动检测:

  2. 检查是否有 Task/subagent 能力 (Claude Code / Cursor):
     → 是 → 使用 Level 3: subagent 策略

  3. 检查是否是 CLI 环境 (可 fork 进程):
     → 是 → 使用 Level 2: CLI 嵌套策略

  4. 否则 (Windsurf / 其他单 Agent IDE):
     → 使用 Level 1: session-split 策略
     → 计算当前需求复杂度，估算所需 session 数
     → 输出执行计划给用户
```

### 5.16 Windsurf 全自动流程用户体验示例

```
===== Session 1 =====

用户: /harness-auto 实现用户注册和登录功能，支持邮箱验证

[检测] 当前环境: Windsurf (单 Agent)
[策略] 分段执行模式，预计 4 个 session
[计划]
  Session 1: /1 需求分析 + /2 需求规范
  Session 2: /3 开发设计 + /4 实施步骤 + /5 实施前检测
  Session 3: /6 编写代码
  Session 4: /8 测试用例 + /9 测试验证 + /10 同步 + /11 归档

[Phase 0] ✅ 初始化完成
[Phase 1] ✅ 需求分析完成 (requirement.md 已生成)
[Phase 2] ✅ 需求规范完成 (spec.md 已生成, Audit: B)

⏸️ Session 1 完成。已完成: /1 ✅ /2 ✅
   请开启新会话，输入: /harness-resume

===== Session 2 (新会话) =====

用户: /harness-resume

[恢复] 从 state.md 读取进度: /1 ✅ /2 ✅
[恢复] 本 session 执行: /3, /4, /5
════════════════════════════════════════════
  CONTEXT FENCE — 新 session，忽略先前对话
  从文件加载: state.md → spec.md
════════════════════════════════════════════

[Phase 3] ✅ 开发设计完成 (design.md 已生成)
[Phase 4] ✅ 实施步骤完成 (tasks.md: 12 任务)
[Phase 5] ✅ 实施前检测通过 (Audit: B, 83分)

⏸️ Session 2 完成。已完成: /1-/5 全部 ✅
   请开启新会话，输入: /harness-resume

===== Session 3 (新会话) =====

用户: /harness-resume

[恢复] 本 session 执行: /6 编写代码 (12 任务)
════════════════════════════════════════════
  CONTEXT FENCE — 从文件加载: tasks.md → design.md
════════════════════════════════════════════

[Phase 6] T001-T008: ✅ (上下文预算 68%)
[Phase 6] T009-T012: ✅
[Phase 6] 全量检查: lint ✅ security ✅

⏸️ Session 3 完成。已完成: /1-/6 全部 ✅
   请开启新会话，输入: /harness-resume

===== Session 4 (新会话) =====

用户: /harness-resume

[恢复] 本 session 执行: /8, /9, /10, /11

[Phase 7] ✅ 测试用例生成 (28 用例)
[Phase 8] ✅ 测试验证通过 (28/28 PASS)
[Phase 9] ✅ 文档同步完成
[Phase 10] ✅ 归档完成

===== 交付报告 =====
总 session 数: 4
总耗时: ~25 分钟 (不含用户开新会话时间)
========================
```

### 5.17 Cursor 全自动流程用户体验示例

```
用户: /harness-auto 实现用户注册和登录功能，支持邮箱验证

[检测] 当前环境: Cursor (支持 Background Agent)
[策略] 子 Agent 调度模式，单 session 全自动完成

[Phase 0] ✅ 初始化完成

[Phase 1] → 派发子 Agent: /1-需求分析
  ↳ 子 Agent 完成, requirement.md 已生成 ✅

[Phase 2] → 派发子 Agent: /2-需求规范
  ↳ 子 Agent 完成, spec.md 已生成, lint PASS ✅

[Phase 3] → 派发子 Agent: /3-开发设计
  ↳ 子 Agent 完成, design.md 已生成 ✅

... (后续阶段同理，每个阶段独立子 Agent) ...

[Phase 10] → 派发子 Agent: /11-归档需求
  ↳ 子 Agent 完成, 已归档 ✅

===== 交付报告 =====
总耗时: 22 分钟 (全自动，零中断)
人工确认: 0 次
========================
```

---

## 六、命令模板改造方案

### 6.1 通用改造 (所有命令)

每个命令模板增加以下标准步骤：

```markdown
### 步骤 0: Harness 初始化 (自动)

1. 读取 `.specify/harness/config.yml` 加载配置
2. 读取 `.specify/harness/state.md` 检查工作流状态
3. 验证当前命令是合法的下一步（工作流状态机）
4. 在 execution-log.md 记录「⏳ 执行中」
5. 验证权限声明

### [... 命令主体不变 ...]

### 步骤 N: Harness 收尾 (自动)

1. 运行确定性验证 (lint + consistency，Back-Pressure 输出)
2. 如检测到安全问题，运行 security-scan.sh
3. 更新 state.md (阶段进度、下一步)
4. 更新 execution-log.md (状态、耗时、质量指标)
5. 如果是阶段完成点，自动创建 Git Checkpoint
6. 输出交接指引
```

### 6.2 特定命令增强

| 命令 | 增强内容 | 参考来源 |
|------|---------|---------|
| `/0-制定项目上下文` | 初始化 Harness 全套文件(config.yml, state.md 等) | GSD `/gsd:new-project` |
| `/1-需求分析` | 决策记录到 audit-log.md | OAC 审批门控 |
| `/2-需求规范` | 步骤3后运行 lint-specs.sh | ECC harness-audit |
| `/3-开发设计` | 步骤后运行 consistency-check.sh | OpenAI CI 不变量 |
| `/4-实施步骤` | 生成 XML 结构化任务(含内建验证步骤) | GSD XML 任务 |
| `/5-实施前检测` | 输出 Harness Audit 评分 | ECC `/harness-audit` |
| `/6-编写代码` | 两阶段审查 + TDD 纪律 + 原子提交 | Superpowers + GSD |
| `/8-生成测试用例` | 强制 RED-GREEN-REFACTOR 模式 | Superpowers TDD |
| `/9-测试验证` | 更新 quality-metrics.md | Spec Kitty |
| `/11-归档需求` | Instinct 提取 + Forensics 分析 | ECC CL-v2 + GSD |

### 6.3 新增命令

| 命令 | 功能 | 参考来源 |
|------|------|---------|
| **`/harness-auto`** | **全自动需求交付 (核心入口)** | **GSD + ECC + Superpowers** |
| `/harness-audit` | 全面审计评分 (A-F) | ECC |
| `/harness-forensics` | 失败事后调查 | GSD `/gsd:forensics` |
| `/harness-status` | 显示当前状态和下一步 | GSD `/gsd:progress` |
| `/harness-pause` | 暂停工作，生成 handoff.json | GSD `/gsd:pause-work` |
| `/harness-resume` | 从 handoff.json 恢复 | GSD `/gsd:resume-work` |
| `/harness-checkpoint` | 手动创建检查点 | FSPEC checkpoint |
| `/harness-restore` | 从检查点恢复 | FSPEC restore |

---

## 七、实施路线图（8周）

### Phase 1: 基础设施 (Week 1-2)

| 任务 | 产出 | 参考 | 工作量 |
|------|------|------|--------|
| M1 配置中心 | config.yml + Profile 系统 | ECC/OAC/GSD | 1天 |
| M2 状态机 | state.md + handoff.json + 恢复协议 | GSD/Anthropic | 1天 |
| M3 确定性验证 | lint-specs.sh + consistency-check.sh | ECC/OpenAI | 2天 |
| M3 Harness Audit | harness-audit.md 命令模板 | ECC | 1天 |
| 通用改造 | 所有命令添加步骤0和步骤N | 全部 | 2天 |
| **全自动编排引擎** | **harness-auto.md + 状态机 + 自愈引擎** | **GSD/ECC/Superpowers** | **3天** |
| Pre-commit Hook | pre-commit-hook.sh | HumanLayer | 0.5天 |
| 新命令: harness-status | 状态查看命令 | GSD | 0.5天 |
| 新命令: harness-pause/resume | 暂停恢复命令 | GSD | 0.5天 |

### Phase 2: 安全 + 反馈 (Week 3-4)

| 任务 | 产出 | 参考 | 工作量 |
|------|------|------|--------|
| M4 安全扫描 | security-scan.sh + 安全评级 | ECC AgentShield | 1天 |
| M4 权限模型 | 命令模板权限声明 | OAC/GSD | 0.5天 |
| M5 两阶段审查 | /6 命令模板改造 | Superpowers | 1天 |
| M5 Back-Pressure | 验证脚本输出协议统一 | HumanLayer | 0.5天 |
| M5 TDD 纪律 | /6 + /8 命令模板改造 | Superpowers | 1天 |
| M6 Git Checkpoint | snapshot.sh + restore.sh | FSPEC | 0.5天 |
| M6 原子提交 | /6 命令模板改造 | GSD | 0.5天 |
| 新命令: harness-checkpoint/restore | 快照命令 | FSPEC | 0.5天 |

### Phase 3: 可观测性 (Week 5-6)

| 任务 | 产出 | 参考 | 工作量 |
|------|------|------|--------|
| M7 执行日志 | execution-log.md 模板 + 集成 | GSD | 1天 |
| M7 质量指标 | quality-metrics.md + 自动更新 | Spec Kitty | 1天 |
| M7 Token 追踪 | 执行日志增加 Token 字段 | ECC | 0.5天 |
| M8 Forensics | harness-forensics.md 命令模板 | GSD | 1天 |
| M8 审计日志 | audit-log.md + 自动记录 | OAC | 0.5天 |
| M9 审批门控 | 可配置审批 + 决策持久化 | OAC/Superpowers | 1天 |

### Phase 4: 学习 + 优化 (Week 7-8)

| 任务 | 产出 | 参考 | 工作量 |
|------|------|------|--------|
| M10 Instinct 学习 | instincts.md + /11 集成 | ECC CL-v2 | 1天 |
| M10 Skill 进化 | 聚类机制 + 自动生成 SKILL.md | ECC /evolve | 1天 |
| /4 XML 结构化任务 | tasks.md XML 格式增强 | GSD | 1天 |
| 命令模板 CHANGELOG | 版本管理 | 通用 | 0.5天 |
| Dry-run 模式 | config.yml 增加 dry_run | OpenSpec | 0.5天 |
| 整体集成测试 | 全流程端到端验证 | - | 2天 |

---

## 八、目录结构总览

```
.specify/
├── harness/                              # Harness Engineering 核心
│   ├── config.yml                        # M1 集中配置 + Profile
│   ├── state.md                          # M2 工作流状态
│   ├── handoff.json                      # M2 暂停/恢复交接
│   ├── execution-log.md                  # M7 执行日志
│   ├── quality-metrics.md                # M7 质量指标仪表板
│   ├── audit-log.md                      # M8 决策审计日志
│   ├── audit-report.md                   # M3 最新 Harness Audit 报告
│   ├── instincts.md                      # M10 已学习的 Instinct
│   ├── forensics/                        # M8 事后调查报告
│   │   └── [REQ_ID]-forensics.md
│   ├── dispatch/                         # 调度文件 (子 Agent 通信)
│   │   ├── phase-N.json                  # 阶段调度指令
│   │   └── phase-N.done                  # 完成信号
│   └── snapshots/                        # M6 快照记录 (git tag 索引)
│       └── snapshot-index.md
├── scripts/
│   └── harness/                          # Harness 验证脚本
│       ├── lint-specs.sh                 # M3 制品结构 Linter
│       ├── consistency-check.sh          # M3 跨制品一致性
│       ├── security-scan.sh              # M4 安全扫描
│       ├── pre-commit-hook.sh            # M3+M4 Git Hook
│       ├── snapshot.sh                   # M6 创建检查点
│       └── restore.sh                    # M6 恢复检查点
└── templates/
    └── commands/
        ├── CHANGELOG.md                  # 命令模板变更日志
        ├── harness-auto.md               # 新: 全自动需求交付 (核心入口)
        ├── harness-audit.md              # 新: Harness 审计
        ├── harness-forensics.md          # 新: 事后调查
        ├── harness-status.md             # 新: 状态查看
        ├── harness-pause.md              # 新: 暂停工作
        ├── harness-resume.md             # 新: 恢复工作
        ├── harness-checkpoint.md         # 新: 创建检查点
        └── harness-restore.md            # 新: 恢复检查点
```

---

## 九、预期成效与验收标准

### 9.1 五大支柱最终评分

| 支柱 | 当前 | 初版目标 | **最终目标** | 关键增强 |
|------|------|---------|-------------|---------|
| 工具编排 | ⭐⭐⭐ | ⭐⭐⭐⭐ | **⭐⭐⭐⭐⭐** | +M1 配置中心 +M2 状态机 +Hook Runtime |
| 护栏与安全 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **⭐⭐⭐⭐⭐** | +M3 Audit 评分 +M4 AgentShield 五层安全 |
| 反馈回路 | ⭐⭐⭐½ | ⭐⭐⭐⭐½ | **⭐⭐⭐⭐⭐** | +M5 两阶段审查 +TDD +原子提交 +Back-Pressure |
| 可观测性 | ⭐⭐ | ⭐⭐⭐⭐ | **⭐⭐⭐⭐⭐** | +M7 日志+指标+Token +M8 Forensics+审计 |
| 人机协作 | ⭐⭐⭐ | ⭐⭐⭐⭐ | **⭐⭐⭐⭐⭐** | +M9 可配置门控+决策记录 +M10 持续学习 |

### 9.2 量化验收标准

| 指标 | 当前 | 验收标准 |
|------|------|---------|
| Harness Audit 评分 | N/A | 活跃需求均 ≥ B (80分) |
| 确定性验证覆盖 | 0% | ≥ 90% 的检查项有确定性脚本 |
| 跨会话恢复时间 | ~10min 手动 | < 1min 自动 |
| 安全扫描覆盖 | 无 | 每次提交自动扫描 |
| 自愈成功率 | ~70% | ≥ 90% (两阶段审查后) |
| 决策可追溯性 | 无 | 100% 关键决策有审计记录 |
| 原子提交率 | 低 | ≥ 95% 任务有独立提交 |
| Instinct 积累 | 0 | ≥ 20 条已验证 Instinct |
| **全自动完成率** | **0%** | **≥ 80% 需求可全自动交付 (≤2次人工确认)** |
| **端到端平均耗时** | **手动数小时** | **< 30min (中等复杂度需求)** |
| **人工介入次数** | **每阶段** | **≤ 2次/需求 (仅澄清+验证)** |

### 9.3 对标行业最佳实践

| 实践 | OpenAI Codex | 本项目(实施后) | 差距 |
|------|-------------|---------------|------|
| AGENTS.md / SKILL.md | ✅ | ✅ | 无 |
| CI 机械不变量 | ✅ | ✅ (lint + consistency + security) | 无 |
| 可复现环境 | ✅ | ✅ (.devcontainer + config.yml) | 无 |
| "垃圾回收" Agent | ✅ | ✅ (/10 + /11 + harness-audit) | 无 |
| 持续学习 | ❓ | ✅ (Instinct + Skill 进化) | **我们领先** |
| 跨会话恢复 | ✅ | ✅ (state.md + handoff.json) | 无 |
| 事后调查 | ❓ | ✅ (harness-forensics) | **我们领先** |
| **全自动端到端交付** | ❌ | ✅ (/harness-auto + 自愈 + 自动推进) | **我们领先** |

---

## 参考文献

### 初版参考
1. [OpenAI - Harness Engineering](https://openai.com/index/harness-engineering/)
2. [Martin Fowler - Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)
3. [Anthropic - Effective Harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
4. [HumanLayer - Skill Issue: Harness Engineering](https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents)
5. [12-Factor Agents](https://www.humanlayer.dev/blog/12-factor-agents)
6. [LangChain - Improving Deep Agents](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)
7. [Spec Kitty](https://github.com/Priivacy-ai/spec-kitty)
8. [OpenSpec](https://github.com/Fission-AI/OpenSpec)
9. [FSPEC](https://github.com/sengac/fspec)
10. [OpenDev](https://github.com/opendev-to/opendev)

### 新增参考
11. [Everything Claude Code (ECC)](https://github.com/affaan-m/everything-claude-code) — AgentShield、Harness Audit、持续学习 v2、Hook Runtime 控制
12. [Oh My OpenAgent (OmO)](https://github.com/code-yeongyu/oh-my-openagent) — Hash-Anchored 编辑、分层 AGENTS.md、Discipline Agents
13. [Get Shit Done (GSD)](https://github.com/gsd-build/get-shit-done) — STATE.md、HANDOFF.json、Wave 并行、XML 任务、Forensics
14. [OpenAgentsControl (OAC)](https://github.com/darrenhinde/OpenAgentsControl) — ContextScout、MVI 原则、审批门控
15. [Ruflo](https://github.com/ruvnet/ruflo) — 分布式 Swarm 编排、RAG 集成
16. [Superpowers](https://github.com/obra/superpowers) — 两阶段审查、TDD 纪律、Subagent-Driven Development
