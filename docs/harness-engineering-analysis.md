# Harness Engineering 符合度分析报告

> **项目**: Spec Kit CN (spec-kit-cn)
> **分析日期**: 2026-03-30
> **分析范围**: `templates/commands/` 工作流命令、项目架构、记忆系统、质量门控

---

## 一、什么是 Harness Engineering

Harness Engineering（驾驭工程）是由 OpenAI 在其 Codex 团队实践中提出的概念，随后被 Martin Fowler、Anthropic、LangChain 等进一步阐述。其核心思想是：

> **AI 模型是马，Harness 是缰绳和马具，工程师是骑手。**

Harness 不是 Agent 本身，而是围绕 Agent 的**完整基础设施**——工具编排、安全护栏、反馈回路、可观测性和人机协作检查点。

### Harness Engineering 五大支柱

| 支柱 | 定义 | 来源 |
|------|------|------|
| **1. 工具编排 (Tool Orchestration)** | 定义 Agent 可访问的工具、调用方式和权限边界 | NxCode, OpenAI |
| **2. 护栏与安全约束 (Guardrails)** | 确定性规则防止 Agent 采取有害行动：权限边界、验证检查、架构约束、速率限制 | OpenAI Codex |
| **3. 错误恢复与反馈回路 (Feedback Loops)** | 自动重试、自验证循环、回滚机制、循环检测 | LangChain, Anthropic |
| **4. 可观测性 (Observability)** | 记录每个 Agent 动作、追踪 Token 使用、记录决策点、发现异常 | NxCode |
| **5. 人机协作检查点 (Human-in-the-Loop)** | 在高杠杆决策点放置人工审批门控 | Anthropic |

### OpenAI Codex 团队的三类 Harness 组件

| 类别 | 描述 |
|------|------|
| **上下文工程** | 代码库中持续增强的知识库 + Agent 可访问的动态上下文（可观测性数据、浏览器导航等） |
| **架构约束** | 不仅由 LLM Agent 监控，还有确定性的自定义 Linter 和结构化测试 |
| **"垃圾回收"** | 定期运行的 Agent，发现文档不一致或架构约束违规，对抗熵增和衰退 |

### 关键引用

- **OpenAI**: _"When the agent struggles, we treat it as a signal: identify what is missing — tools, guardrails, documentation — and feed it back into the repository."_
- **Martin Fowler**: _"Increasing trust and reliability required constraining the solution space: specific architectural patterns, enforced boundaries, standardized structures."_
- **LangChain**: 仅通过改变 Harness（不换模型），Agent 在 Terminal Bench 2.0 上从 52.8% 跃升到 66.5%。

---

## 二、当前项目现状总览

### 2.1 工作流命令矩阵

| 编号 | 命令 | 角色 | 功能 | Harness 相关能力 |
|------|------|------|------|-----------------|
| 0 | `/0-制定项目上下文` | 系统 | 自动分析代码生成 Skill + 项目记忆初始化 | 上下文工程 ✅ |
| 1 | `/1-需求分析` | BA/PM | 创建/导入/修订需求文档 | 工具编排 ✅ |
| 2 | `/2-需求规范` | BA/PM | 生成功能规范 + 10 类覆盖扫描 | 护栏 ✅ |
| 3 | `/3-开发设计` | Architect | 生成开发设计文档 + 多维检测 | 护栏 ✅ |
| 4 | `/4-实施步骤` | Architect | 生成任务列表 tasks.md | 工具编排 ✅ |
| 5 | `/5-实施前检测` | Architect | 跨制品一致性分析（只读） | 护栏 ✅ |
| 6 | `/6-编写代码` | Developer | 按任务编码 + 自愈循环 | 反馈回路 ✅ |
| 7 | *(已内嵌到 /6)* | - | 实现后检测 | 反馈回路 ✅ |
| 8 | `/8-生成测试用例` | QA | 基于 spec+design 生成测试用例 | 护栏 ✅ |
| 9 | `/9-测试验证` | QA | 执行测试 + 缺陷跟踪 + 发布建议 | 人机协作 ✅ |
| 10 | `/10-同步文档` | DocOps | 批量同步未同步的变更到文档 | 上下文工程 ✅ |
| 11 | `/11-归档需求` | DocOps | 归档 + 精炼长期记忆 | 上下文工程 ✅ |
| - | `/api-skill-extract` | 工具 | 提取 API 接口生成 Skill 文档 | 上下文工程 ✅ |
| - | `/business-rules-extract` | 工具 | 提取业务规则生成 Skill 文档 | 上下文工程 ✅ |

### 2.2 角色与交接体系

```
BA/PM ──→ Architect ──→ Developer ──→ QA ──→ DocOps
 /1 /2      /3 /4 /5       /6          /8 /9    /10 /11
    ↑                                    ↑
    └─── 需求变更反馈 ←── 缺陷修复 ←──┘
```

**交接协议**: 每个命令末尾均包含结构化的交接指引，明确当前角色、下一角色、交接物和上下文切换建议。

### 2.3 记忆系统

```
三层读取协议:
L0 index.md        ← 每需求1行，快速判断相关性
L1 summaries/       ← 每需求≤1K tokens 的摘要
L2 specs/archived/  ← 完整归档原文

辅助记忆文件:
├── coding-standards.md   (≤30条)
├── known-pitfalls.md     (≤30条)
├── design-decisions.md   (≤30条)
└── code-patterns.md      (≤20条)
```

### 2.4 ECC 集成

已集成 Everything Claude Code 的 Agents(12)、Commands(15)、Skills(8)、Rules(13种语言)、Hooks(示例)。

---

## 三、Harness Engineering 五大支柱逐项评估

### 3.1 工具编排 (Tool Orchestration)

| 评估项 | 现状 | 评分 |
|--------|------|------|
| Agent 可访问的工具是否明确定义 | ✅ 每个命令明确定义了文件读取、脚本执行、模板引用的范围 | ⭐⭐⭐⭐ |
| 工具权限边界是否清晰 | ⚠️ `/5-实施前检测` 严格只读，但其他命令无明确的权限声明 | ⭐⭐⭐ |
| 工具调用是否有标准化接口 | ⚠️ 各命令通过 bash 代码块调用工具，但无统一的工具注册/发现机制 | ⭐⭐ |
| 多 Agent 并行协调 | ❌ 无并行 Agent 协调机制，所有命令串行执行 | ⭐ |

**总评**: ⭐⭐⭐ (3/5) — 工具访问范围定义良好，但缺乏统一的权限模型和工具注册机制。

### 3.2 护栏与安全约束 (Guardrails)

| 评估项 | 现状 | 评分 |
|--------|------|------|
| 架构约束执行 | ✅ 项目章程(constitution) + SKILL.md 章程检查 + 阶段关卡 | ⭐⭐⭐⭐ |
| 输出验证 | ✅ 10类覆盖扫描(/2)、多维设计检测(/3)、跨制品一致性(/5)、自愈循环(/6) | ⭐⭐⭐⭐⭐ |
| 模糊性检测 | ✅ 禁止模糊词汇列表、`[NEEDS CLARIFICATION]` 标记、占位符检测 | ⭐⭐⭐⭐ |
| 确定性 Linter/结构化测试 | ❌ 无自定义 Linter 脚本、无结构化架构测试(如 ArchUnit) | ⭐ |
| 速率限制/循环检测 | ❌ 自愈循环限制3轮，但无通用的循环检测或 Token 预算管理 | ⭐⭐ |

**总评**: ⭐⭐⭐⭐ (4/5) — LLM 层面的护栏非常强大，但缺乏确定性（非 LLM）的自动化验证工具。

### 3.3 错误恢复与反馈回路 (Feedback Loops)

| 评估项 | 现状 | 评分 |
|--------|------|------|
| 自验证循环 | ✅ `/6-编写代码` 内嵌自愈循环（最多3轮自动修复） | ⭐⭐⭐⭐ |
| 测试驱动反馈 | ✅ 任务配对测试、层级测试模式、测试脚本自动生成(/9) | ⭐⭐⭐⭐ |
| 回滚机制 | ⚠️ Git 分支管理作为隐式回滚，但无 Agent 级别的快照/回滚 | ⭐⭐ |
| 循环检测 | ⚠️ 仅自愈循环有3轮限制和升级机制，无通用的无限循环检测 | ⭐⭐ |
| 跨阶段反馈 | ✅ 代码→文档同步规则(.windsurfrules)、changelog 驱动的回溯更新 | ⭐⭐⭐⭐ |

**总评**: ⭐⭐⭐⭐ (3.5/5) — 自愈和测试反馈出色，但缺乏系统级的回滚和循环检测。

### 3.4 可观测性 (Observability)

| 评估项 | 现状 | 评分 |
|--------|------|------|
| Agent 动作日志 | ⚠️ `.ai-changelogs.md` 记录代码变更，但不记录 Agent 决策过程 | ⭐⭐ |
| 执行历史追踪 | ⚠️ 实施报告和测试报告提供事后总结，但无实时执行追踪 | ⭐⭐ |
| Token 使用追踪 | ❌ 无 Token 消耗监控和预算管理 | ⭐ |
| 决策点记录 | ⚠️ 覆盖报告、一致性报告记录了部分决策，但不系统 | ⭐⭐ |
| 质量指标仪表板 | ❌ 无聚合的质量指标视图、无历史趋势追踪 | ⭐ |
| 异常检测 | ⚠️ 各检测命令发现问题，但无主动的异常告警机制 | ⭐⭐ |

**总评**: ⭐⭐ (2/5) — **这是最大的短板**。可观测性基本停留在报告级别，缺乏系统化的日志、指标和追踪。

### 3.5 人机协作检查点 (Human-in-the-Loop)

| 评估项 | 现状 | 评分 |
|--------|------|------|
| 审批门控 | ✅ `/9-测试验证` 是明确的人工审核节点（发布决策） | ⭐⭐⭐ |
| 高风险操作确认 | ✅ `/6-编写代码` 步骤4 design.md 一致性预检查需用户确认 | ⭐⭐⭐ |
| 需求澄清交互 | ✅ `/1-需求分析` 交互式问答、`/9` 人工验证用例收集反馈 | ⭐⭐⭐⭐ |
| 升级机制 | ✅ 自愈循环3轮后升级人工、自动执行失败转人工验证 | ⭐⭐⭐ |
| 决策日志 | ❌ 人工决策未系统记录（为什么批准、为什么拒绝） | ⭐ |

**总评**: ⭐⭐⭐ (3/5) — 有人工检查点，但缺乏系统化的决策记录和灵活的门控配置。

---

## 四、综合评估矩阵

| Harness 支柱 | 评分 | 现状总结 |
|-------------|------|---------|
| 1. 工具编排 | ⭐⭐⭐ (3/5) | 命令范围清晰，缺统一权限模型和工具注册 |
| 2. 护栏与安全约束 | ⭐⭐⭐⭐ (4/5) | LLM 护栏极强，缺确定性自动化验证 |
| 3. 错误恢复与反馈 | ⭐⭐⭐½ (3.5/5) | 自愈循环优秀，缺系统级回滚和循环检测 |
| 4. 可观测性 | ⭐⭐ (2/5) | **最大短板**，缺日志/指标/追踪体系 |
| 5. 人机协作 | ⭐⭐⭐ (3/5) | 有检查点，缺决策记录和灵活配置 |
| **综合** | **⭐⭐⭐ (3.1/5)** | **已具备 Harness Engineering 的核心骨架，但在可观测性、确定性验证和系统化方面存在显著差距** |

---

## 五、已有优势（对标行业最佳实践）

### 5.1 业界领先的方面

| 优势 | 描述 | 对标 |
|------|------|------|
| **结构化工作流链** | 0→11 完整的编号工作流，覆盖从上下文建立到需求归档的全生命周期 | 超越 OpenAI Codex 的无序 Agent 模式 |
| **角色专业化 + 交接协议** | 5 种角色（BA/PM、Architect、Developer、QA、DocOps）+ 结构化交接 | 接近 Anthropic 的 multi-agent orchestration |
| **三层记忆系统** | L0→L1→L2 渐进式读取 + 容量约束 + 自动归档 | 超越大多数项目的 CLAUDE.md 单文件记忆 |
| **多层次护栏** | 10类覆盖扫描 + 4维设计检测 + 跨制品一致性 + 自愈循环 | 护栏层次比 OpenAI 描述的更丰富 |
| **文档-代码同步** | changelog 驱动的变更追踪 + 自动文档同步规则 | 对应 OpenAI 的 "垃圾回收" Agent |
| **知识蒸馏** | /11 归档时精炼设计决策、经验教训、代码模式 | 先进的长期学习机制 |

### 5.2 对 OpenAI 三类 Harness 组件的覆盖

| OpenAI 组件 | 项目覆盖 | 覆盖度 |
|------------|---------|--------|
| 上下文工程 | SKILL.md + 三层记忆 + constitution + Confluence MCP 搜索 | ✅✅✅ 优秀 |
| 架构约束 | 项目章程 + 阶段关卡 + 模板约束 + 禁止模糊词 | ✅✅ 良好（缺确定性 Linter） |
| "垃圾回收" | changelog 驱动的文档同步 + 容量检查 + 记忆精炼 | ✅✅✅ 优秀 |

---

## 六、差距分析：缺失的 Harness 组件

### 6.1 严重缺失 (Critical Gaps)

#### GAP-C1: 确定性验证工具缺失

**现状**: 所有验证依赖 LLM 判断（10类扫描、设计检测、一致性分析），无确定性脚本。

**风险**: LLM 可能遗漏、误判或不一致地应用规则。OpenAI 团队明确指出：_"architectural constraints monitored not only by LLM-based agents, but also deterministic custom linters and structural tests."_

**缺失项**:
- 自定义 Linter 脚本（验证文档结构、命名规范、追溯标记）
- 结构化测试（验证 spec↔design↔tasks↔code 的引用完整性）
- CI 集成 Hook（在提交时自动运行验证）

#### GAP-C2: 可观测性体系缺失

**现状**: 仅有事后报告（实施报告、测试报告），无实时日志和指标。

**风险**: 无法回答关键问题：Agent 在哪个阶段花费了最多时间？哪类任务失败率最高？质量趋势如何？

**缺失项**:
- 工作流执行日志（开始时间、结束时间、步骤耗时）
- 质量指标聚合（覆盖率趋势、缺陷密度、自愈成功率）
- Token 消耗追踪和预算管理
- 决策审计日志

#### GAP-C3: Harness 配置层缺失

**现状**: 工作流规则、质量阈值、角色权限散布在各个命令文件中，无集中配置。

**风险**: 无法快速调整 Harness 参数（如自愈轮次上限、覆盖率阈值、Token 预算），也无法在不同项目间复用配置。

**缺失项**:
- 集中式 Harness 配置文件（`harness.yml` 或类似）
- 可配置的质量门控阈值
- 环境特定配置（开发/测试/生产）

### 6.2 显著缺失 (Major Gaps)

#### GAP-M1: 工作流编排引擎缺失

**现状**: 命令之间的编排依赖交接协议文本描述，无自动化执行链。

**缺失项**:
- 工作流状态机（定义合法的命令转换路径）
- 前置条件自动检查（不仅在命令内部，还在编排层）
- 工作流进度持久化（跨会话恢复）

#### GAP-M2: Agent 快照/回滚机制缺失

**现状**: 依赖 Git 进行代码回滚，但无 Agent 工作状态的快照。

**缺失项**:
- 制品快照（在关键检查点保存 specs/ 目录状态）
- 回滚命令（恢复到某个检查点的制品状态）
- 变更影响分析（回滚时评估影响范围）

#### GAP-M3: Prompt 版本管理缺失

**现状**: 命令模板作为普通 Markdown 文件管理，无版本追踪和效果评估。

**缺失项**:
- 命令模板变更日志
- Prompt 效果对比测试框架
- Prompt 回归测试

#### GAP-M4: 安全 Harness 缺失

**现状**: 无针对 Agent 输出的安全检查。

**缺失项**:
- Agent 输出中的敏感信息检测（API Key、密码、Token 泄露）
- 文件系统访问白名单
- 危险命令拦截（rm -rf、DROP TABLE 等）
- Agent 动作审计追踪

### 6.3 改进空间 (Improvement Opportunities)

#### GAP-I1: 并行执行支持不足

**现状**: tasks.md 标记了 `[并行]` 任务，但工作流命令串行执行。

#### GAP-I2: 跨项目学习机制缺失

**现状**: 记忆系统限于单项目，无跨项目的最佳实践共享。

#### GAP-I3: 人工决策未系统记录

**现状**: 人工审核结果（批准/拒绝/修改）未持久化记录。

#### GAP-I4: 缺乏 Dry-run 模式

**现状**: 每个命令都会产生实际制品，无法进行无副作用的预演。

---

## 七、与行业实践的对标

### 7.1 OpenAI Codex 团队对标

| OpenAI 实践 | 本项目状态 | 差距 |
|------------|-----------|------|
| AGENTS.md 机器可读指令 | ✅ SKILL.md + 项目章程 + 各模板 | 无显著差距 |
| 可复现的开发环境 | ⚠️ 有 .devcontainer 但未与 Harness 集成 | 需要加强环境隔离 |
| CI 中的机械不变量 | ❌ 无确定性 CI 验证 | **关键差距** |
| 每个 PR 有 Agent 驱动的代码审查 | ⚠️ /6 自愈循环有审查，但非 PR 级别 | 需要 CI/CD 集成 |
| 定期运行的"垃圾回收" Agent | ✅ /10 /11 文档同步和归档 | 需要自动化定期触发 |

### 7.2 Anthropic Claude Code 对标

| Anthropic 实践 | 本项目状态 | 差距 |
|---------------|-----------|------|
| 权限模型（默认只读） | ⚠️ /5 只读，其他命令无明确权限声明 | 需要统一权限模型 |
| Hooks 系统（生命周期注入） | ⚠️ ECC 集成了示例 Hooks，但 SDD 流程无 Hooks | 需要为 SDD 命令添加 Hook 点 |
| CLAUDE.md 持久化上下文 | ✅ SKILL.md + 三层记忆 + .windsurfrules | 优于单文件 |
| 自动快照和可逆编辑 | ❌ 无 Agent 级别快照 | 需要添加 |
| progress.txt 跨窗口状态 | ⚠️ tasks.md 复选框是隐式进度，但无标准进度文件 | 需要标准化 |

### 7.3 LangChain 自验证循环对标

| LangChain 实践 | 本项目状态 | 差距 |
|---------------|-----------|------|
| 自验证循环 | ✅ /6 自愈循环（3轮自动修复 + 人工升级） | 匹配 |
| 循环检测 | ⚠️ 仅轮次限制，无行为模式循环检测 | 可改进 |
| 反馈到 Harness 的改进 | ⚠️ /11 归档精炼经验，但不自动改进命令模板 | 需要闭环 |

---

## 八、结论

### 整体评价

本项目在 Harness Engineering 方面已经建立了**坚实的骨架**，特别是在以下方面表现突出：

1. **结构化工作流链**是业内少见的完整度
2. **多层护栏体系**（模板约束 → 覆盖扫描 → 一致性检测 → 自愈循环）层次丰富
3. **三层记忆系统**和知识蒸馏机制超越了大多数同类项目
4. **角色专业化 + 交接协议**体现了成熟的工程思维

### 关键改进方向（优先级排序）

| 优先级 | 方向 | 预期影响 |
|--------|------|---------|
| **P0** | 添加确定性验证工具（自定义 Linter + 结构化测试） | 从"LLM 说了算"进化到"LLM + 确定性双重验证" |
| **P0** | 建立可观测性体系（执行日志 + 质量指标 + 审计追踪） | 使 Harness 效果可量化、可改进 |
| **P1** | 引入 Harness 配置层（集中配置 + 质量阈值 + 环境适配） | 使 Harness 可配置、可复用 |
| **P1** | 工作流编排引擎（状态机 + 进度持久化 + 自动前置检查） | 提升工作流的自动化和可靠性 |
| **P2** | 安全 Harness（敏感信息检测 + 权限白名单 + 危险命令拦截） | 降低 Agent 自主操作的安全风险 |
| **P2** | Agent 快照/回滚机制 | 支持安全实验和错误恢复 |
| **P3** | Prompt 版本管理和效果评估 | 持续优化命令模板质量 |
| **P3** | 跨项目学习和 Dry-run 模式 | 提升整体效率 |

详细的解决方案请参见 [harness-engineering-solution.md](./harness-engineering-solution.md)。

---

## 参考文献

1. [OpenAI - Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)
2. [Martin Fowler - Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)
3. [Anthropic - Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
4. [NxCode - What Is Harness Engineering? Complete Guide (2026)](https://www.nxcode.io/resources/news/what-is-harness-engineering-complete-guide-2026)
5. [HumanLayer - Skill Issue: Harness Engineering for Coding Agents](https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents)
6. [LangChain - Improving Deep Agents with Harness Engineering](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)
