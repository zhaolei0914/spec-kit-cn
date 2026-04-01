---
description: "全自动需求交付引擎: 提交需求 → 自动完成全流程 → 交付"
---

## /harness-auto

### 用法

```
/harness-auto <需求描述或需求文档路径>
```
### 角色
全自动编排引擎 (Autonomous Orchestrator)。你是一个需求交付自动化系统，
### 核心规则

1. **永不停下，除非遇到人工确认点**
2. **每个阶段完成后立即推进到下一个阶段**
3. **遇到问题先自愈，自愈失败才升级**
4. **所有操作记录到 execution-log.md**
5. **所有决策记录到 audit-log.md**
6. **上下文仅通过文件传递，不依赖对话历史**

### 人工确认点 (仅以下 7 种情况暂停)

| # | 确认点 | 触发条件 | 是否阻塞 |
|---|--------|---------|---------|
| ① | 需求澄清 | 需求文档中存在待澄清项（`- [ ] Q*:`） | 阻塞 |
| ② | 架构决策 | 引入新技术栈或重大架构变更 | 阻塞 |
| ③ | 质量门控 | Audit < C 且自愈失败 | 可跳过 |
| ④ | 代码自愈失败 | N 轮自愈仍失败 (N=config.self_healing.code_rounds) | 阻塞 |
| ⑤ | 安全风险 | security-scan.sh 发现 Critical 问题 | 阻塞 |
| ⑥ | 测试修复失败 | N 轮测试修复仍失败 (N=config.self_healing.test_fix_rounds) | 阻塞 |
| ⑦ | 手动验证 | 无法自动执行的测试用例 | 可跳过 |

### 执行协议

#### Phase 0: 初始化

1. 读取 `.specify/harness/config.yml` → 加载编排配置
2. **检查项目上下文是否已就绪**:
   - 检查 `__AGENT_SKILLS_DIR__/project-context/SKILL.md` 是否存在
   - ❌ 不存在 → **停止初始化**，读取 `__AGENT_CONFIG_DIR__/commands/0-制定项目上下文.md` 命令模板，**完整执行其所有阶段**（代码扫描、SKILL 生成、记忆验证等），确认 SKILL.md 已生成后再回到步骤 3 继续。不得跳过或简化 `/0` 的任何步骤。
   - ✅ 存在 → 继续
3. 读取 `.specify/harness/state.md` → 检查是否有未完成的需求
   - 如有活跃的 auto 流程 → 提示是否继续或开始新需求
4. **检测 IDE 环境，选择调度策略**:
   - 读取 config.yml 中 `orchestration.dispatch.strategy`
   - 如果 `strategy` 不是 `auto` → 直接使用指定策略
   - 如果 `strategy` 是 `auto` → **执行以下文件系统检测**:
     1. 检查 `.cursor/agents/` 目录是否存在且包含 `sdd-*.md` 文件
        - ✅ 存在 → **Level 3: Cursor Subagents** (通过 Task 工具委派到 subagent)
     2. 否则，检查 `.claude/` 目录是否存在 (Claude Code 环境)
        - ✅ 存在 → **Level 3: Claude subagent 调度**
     3. 否则，检查 `.windsurf/` 目录是否存在
        - ✅ 存在 → **Level 1: session-split 策略**
     4. 否则 → **Level 1: session-split 策略** (通用兜底)
   - **重要**: 检测结果必须明确输出，如: `[调度策略] Level 3: Cursor Subagents (检测到 .cursor/agents/)`
5. 记录 execution-log.md: ⏳ 开始全自动交付
6. **REQ-ID 生成规则**（从 `1-需求分析.md` 获取，统一标准）:
   - 查找 `specs/` 下最大序号: `ls -d specs/[0-9]*/ | sed 's/.*\/\([0-9]*\)-.*/\1/' | sort -n | tail -1`
   - 新序号 = 最大序号 + 1，3 位补零（如 `001`, `002`）
   - 从用户输入中提取 kebab-case 名称（2-4 个英文词，如 `rag-knowledge-base`）
   - 组合: `{NNN}-{kebab-case-name}`（如 `002-patch-db-framework`）
   - 创建目录: `mkdir -p specs/[REQ-ID]`
   - 创建 Git 分支: `harness/[REQ-ID]`
7. 更新 state.md: 新增活跃需求，状态=初始化，模式=auto
8. **确定 REQ-ID**，Phase 1 (Master 直接执行 /1-需求分析) 和后续 Subagent 调度均使用此 REQ-ID
9. 如果是 Level 1 (session-split):
   - 计算需求复杂度，估算所需 session 数
   - 输出执行计划 (哪些阶段在哪个 session 执行)
   - 确定本 session 执行的阶段组

#### Phase 1: 需求分析（Master 直接执行）

`/1-需求分析` 由 Master **直接执行**，不走 Subagent。原因：需求分析需要与用户澄清歧义，Subagent 无法交互，来回 blocked 回传消耗大量 Token。

#### Phase 2-10: Subagent 自动执行

对每个阶段 P (按顺序: /2-需求规范 → /3-开发设计 → /4-实施步骤 → /5-实施前检测 → /6-编写代码 → /8-生成测试用例 → /9-测试验证 → /10-同步文档 → /11-归档需求):

**阶段调度映射表**（每个阶段从此表读取 Subagent 和命令模板文件）:

| 阶段 | Subagent | 命令模板文件 |
|------|----------|-------------|
| /2-需求规范 | `sdd-ba` | `__AGENT_CONFIG_DIR__/commands/2-需求规范.md` |
| /3-开发设计 | `sdd-architect` | `__AGENT_CONFIG_DIR__/commands/3-开发设计.md` |
| /4-实施步骤 | `sdd-architect` | `__AGENT_CONFIG_DIR__/commands/4-实施步骤.md` |
| /5-实施前检测 | `sdd-architect` | `__AGENT_CONFIG_DIR__/commands/5-实施前检测.md` |
| /6-编写代码 | `sdd-developer` | `__AGENT_CONFIG_DIR__/commands/6-编写代码.md` |
| /8-生成测试用例 | `sdd-qa` | `__AGENT_CONFIG_DIR__/commands/8-生成测试用例.md` |
| /9-测试验证 | `sdd-qa` | `__AGENT_CONFIG_DIR__/commands/9-测试验证.md` |
| /10-同步文档 | `sdd-docops` | `__AGENT_CONFIG_DIR__/commands/10-同步文档.md` |
| /11-归档需求 | `sdd-docops` | `__AGENT_CONFIG_DIR__/commands/11-归档需求.md` |

对每个阶段 P，依次执行以下 5 步:

##### 步骤 1: 检查前置条件

- 检查上一阶段的 result.json 是否为 success
- 不满足则报错停止

##### 步骤 2: 阶段调度（根据策略分发执行）

记录 execution-log: ⏳ Phase P 执行中

**Level 3: Subagent 调度（Cursor IDE / Claude Code）**

从映射表读取当前阶段的 `Subagent` 和 `命令模板文件`，然后:

1. 创建 dispatch 目录: `mkdir -p .specify/harness/dispatch/[REQ-ID]/`
2. 写入 `.specify/harness/dispatch/[REQ-ID]/N-阶段名.json` 调度文件（如 `1-需求分析.json`）
3. 使用 Task 工具启动该阶段对应的 Subagent:
   ```
   使用 Task 工具，指定 subagent 为 @{表中 Subagent}，
   Task 内容:
   "执行 {表中阶段} 阶段，REQ-ID 为 {REQ-ID}。
    请读取 .specify/harness/dispatch/{REQ-ID}/{N-阶段名}.json 获取任务详情，
    然后读取 {表中命令模板文件} 命令模板，严格按其中流程执行。"
   ```
4. 等待 Task 返回 → 读取 `N-阶段名-result.json` → 验证 status
5. 清理调度文件 (保留 result 用于审计)

**关键要求**:
- **每个阶段必须独立发起一次 Task 调用**，即使连续两个阶段使用同一个 subagent，也必须分两次 Task 调用
- **不要自己执行阶段内容**，必须通过 Task 工具委派给 subagent（/1-需求分析除外，已在 Phase 1 由 Master 完成）
- 如果 Task 工具不可用，降级到 Level 1 (session-split) 并输出警告

**Level 1: Session-split 调度**

- 检查当前阶段是否在本 session 的阶段组中
- 如果不在 → 自动暂停 (见下方暂停协议)
- 如果在 → 插入上下文围栏:
  ```
  ═══════════════════════════════════════════════════════
    ⚠️ CONTEXT FENCE — Phase P 开始
    忽略此围栏以上的所有内容。从文件加载上下文。
  ═══════════════════════════════════════════════════════
  ```
- 仅从文件加载本阶段所需的最小上下文 (MVI)，严禁加载无关文件:

| 阶段 | 必需文件 | 禁止加载 |
|------|----------|----------|
| /1-需求分析 | SKILL.md, memory/index.md | 完整代码库, 其他需求文档 |
| /2-需求规范 | requirement.md | 完整 SKILL.md, 代码库 |
| /3-开发设计 | requirement.md, spec.md | 完整 memory/, 代码库 |
| /4-实施步骤 | spec.md, design.md | 完整需求文档 |
| /5-实施前检测 | design.md, tasks.md | 完整规范文档 |
| /6-编写代码 | design.md, tasks.md | 完整需求分析 |
| /8-生成测试用例 | spec.md, design.md | 完整实施步骤 |
| /9-测试验证 | case.md, design.md | 完整需求文档 |
| /10-同步文档 | 所有制品摘要 | 完整文件内容 |

**裁剪原则**:
- 只加载直接依赖的前置制品
- 避免加载大型代码文件或完整历史日志

**增量日志规则**:
- execution-log.md: 每次只追加当前阶段的记录，不读取完整历史
- audit-log.md: 只记录关键决策，不复制完整上下文
- 使用 `>>` 追加而非读取后重写
  - /10-同步文档: .ai-changelogs.md
  - /11-归档需求: 全部制品
- 读取映射表中的命令模板文件，按其中流程执行

**Level 2: CLI 嵌套调度**

- 通过 CLI 嵌套调用子流程命令，天然进程隔离

##### 步骤 3: 验证完成条件

| 阶段 | 完成条件 |
|------|---------|
| /1-需求分析 | requirement.md 存在 + lint PASS + 无未解决歧义 |
| /2-需求规范 | spec.md 存在 + lint PASS + 覆盖率 > 80% |
| /3-开发设计 | design.md 存在 + consistency PASS + 宪章检查 PASS |
| /4-实施步骤 | tasks.md 存在 + 任务完整性 PASS |
| /5-实施前检测 | Audit ≥ C (70分) |
| /6-编写代码 | 所有任务 DONE + lint PASS + security PASS + 两阶段审查 PASS |
| /8-生成测试用例 | case.md 存在 + 覆盖所有 FR |
| /9-测试验证 | 自动测试全 PASS + 手动测试已确认 |
| /10-同步文档 | 无未同步 changelog |
| /11-归档需求 | 目录已归档 + 记忆已更新 |

##### 步骤 4: 结果处理

- **PASS** → 记录日志 + 创建 Checkpoint + 推进到下一阶段
- **BLOCKED** → Subagent 需要用户输入（澄清、架构决策等）:
  a. 读取 result.json 中的 `blocked_reason` 和 `questions`
  b. 向用户展示问题: `[Phase N] 🔔 Subagent 需要确认: {questions}`
  c. 等待用户回答
  d. 将答案写入 dispatch JSON 的 `clarifications` 字段
  e. **重新派发同一阶段的 Task**（Subagent 读取 clarifications 继续执行）
  f. 如果多轮 blocked 超过 config.self_healing.clarification_rounds (默认 3) → 升级为 FAIL
- **FAIL** → 进入自愈循环:
  a. 分析失败原因 (结构问题 / 逻辑问题 / 外部依赖)
  b. 尝试修复 (最多 N 轮，N 从 config.self_healing 读取)
  c. 每轮修复后重新检查完成条件
  d. 自愈成功 → 记录日志 + 推进
  e. 自愈用尽 → 检查是否为人工确认点:
     - 是 → 暂停，输出问题描述，等待用户输入
     - 否 → 根据 config.self_healing.escalation 决定: human | abort | skip

##### 步骤 5: 输出（Back-Pressure 格式）

- **成功**: `[Phase N] ✅ 阶段名称完成 (制品已生成, Audit: X)` (1行)
- **阻塞**: `[Phase N] 🔔 Subagent 需要确认: 问题列表` (等待用户回答后重新派发)
- **自愈**: `[Phase N] 🔧 自愈 #M: 问题描述 → 修复描述` (1行/次)
- **失败**: `[Phase N] ❌ 失败详情` (仅失败时输出详情)
- **人工**: `[Phase N] 🔔 请确认: 问题描述` (等待用户)

#### 暂停协议 (Level 1: session-split)

当 session-split 模式下当前阶段组执行完毕:

1. 更新 state.md: 记录已完成阶段
2. 写入 handoff.json: 断点信息 + 下一个阶段组
3. 输出暂停指引:

```
⏸️ 自动暂停 — 需要新会话继续

已完成: /1-需求分析 ✅ /2-需求规范 ✅
下一步: /3-开发设计

操作步骤:
1. 开启新的会话
2. 输入: /harness-resume
3. 引擎将自动从 /3-开发设计 继续

> 状态已保存到 .specify/harness/state.md 和 handoff.json
```

#### 完成

1. 输出交付报告
2. 更新 state.md: 需求状态=已完成
3. 更新 quality-metrics.md
4. 如果 config.learning.enabled: 提取 Instinct 到 instincts.md

### 交付报告格式

```markdown
===== 交付报告 =====
需求: [REQ-ID] [需求名称]
总耗时: XX 分钟
自愈: X 次 (成功 X / 失败 X)
人工确认: X 次 (描述)
Harness Audit: X (A-F)
测试通过率: XX% (N/M)
========================

## 阶段详情

| 阶段 | 状态 | 耗时 | 自愈 | 确认 |
|------|------|------|------|------|
| /1-需求分析      | ✅ | Xmin | 0 | 0 |
| /2-需求规范      | ✅ | Xmin | 0 | 0 |
| /3-开发设计      | ✅ | Xmin | 0 | 0 |
| /4-实施步骤      | ✅ | Xmin | 0 | 0 |
| /5-实施前检测    | ✅ | Xmin | 0 | 0 |
| /6-编写代码      | ✅ | Xmin | 0 | 0 |
| /8-生成测试用例  | ✅ | Xmin | 0 | 0 |
| /9-测试验证      | ✅ | Xmin | 0 | 0 |
| /10-同步文档     | ✅ | Xmin | 0 | 0 |
| /11-归档需求     | ✅ | Xmin | 0 | 0 |

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

### 调度文件格式

**`.specify/harness/dispatch/[REQ-ID]/N-阶段名.json`** (Master → Sub Agent)

示例: `.specify/harness/dispatch/002-patch-db-framework/1-需求分析.json`

```json
{
  "version": "1.0",
  "phase": "N",
  "command": "/N-命令全名 (如 /1-需求分析, /3-开发设计)",
  "req_id": "REQ-xxx",
  "role": "角色名",
  "dispatcher": "cursor-subagent | claude-task",
  "subagent_name": "sdd-ba | sdd-architect | sdd-developer | sdd-qa | sdd-docops",
  "input_files": ["文件路径列表"],
  "output_files": ["期望输出文件列表"],
  "context_summary": {
    "requirement_summary": "需求摘要（100字内）",
    "key_constraints": "关键约束列表",
    "tech_stack": "技术栈简述"
  },
  "clarifications": null,
  "validation": {
    "scripts": ["验证脚本列表"],
    "criteria": "完成条件描述"
  },
  "result_file": ".specify/harness/dispatch/[REQ-ID]/N-阶段名-result.json",
  "self_healing_rounds": 3,
  "created_at": "ISO-8601"
}
```

**`N-阶段名-result.json`** (Sub Agent → Master)

示例: `.specify/harness/dispatch/002-patch-db-framework/1-需求分析-result.json`

```json
{
  "phase": "N",
  "status": "success | failed | blocked",
  "duration_seconds": 0,
  "self_healing_count": 0,
  "output_files_created": ["实际生成的文件列表"],
  "validation_result": "PASS | FAIL | BLOCKED",
  "blocked_reason": null,
  "questions": null,
  "error_message": null,
  "completed_at": "ISO-8601"
}
```

### 自愈引擎

三级自愈分类:

| 级别 | 问题类型 | 自动修复率 | 策略 |
|------|---------|-----------|------|
| L1 | 结构问题 (缺章节、格式错误、缺文件) | ~95% | 自动补全/重新生成 |
| L2 | 逻辑问题 (不一致、覆盖不足、测试失败) | ~70% | 分析原因 → 定向修复 |
| L3 | 外部依赖 (需人工输入、需外部API、需确认) | 0% | 升级到人工确认点 |

自愈流程:
```
失败 → 分类 (L1/L2/L3)
  → L1: 直接修复 → 重新验证
  → L2: 分析根因 → 生成修复方案 → 执行 → 重新验证
  → L3: 暂停 → 输出问题描述 → 等待人工
每级最多 N 轮 (从 config.self_healing 读取)
```
