# Templates

# Templates 模块文档

## 概述

`Templates` 模块是 **Speckit** 工程化工作流的核心基础设施，提供一套**语义化、上下文感知、可组合的 Markdown 模板系统**，用于自动生成项目规范（spec）、实施计划（plan）、任务清单（tasks）、检查清单（checklist）及开发指南（agent-file）等关键工程文档。

该模块不执行逻辑，而是作为**声明式文档骨架**，通过占位符（如 `[FEATURE]`、`[DATE]`、`[###-feature-name]`）与 Speckit CLI 命令（如 `/speckit.spec`、`/speckit.plan`）深度集成，在运行时被动态填充为结构清晰、领域一致、可追溯的工程资产。

> ✅ **核心价值**：消除文档与代码的割裂，确保需求 → 设计 → 实现 → 验收全程“单源事实”（Single Source of Truth），支持 MVP 增量交付与跨角色对齐（产品、开发、测试）。

---

## 模块结构

```bash
templates/
├── agent-file-template.md    # 全局开发指南（面向团队）
├── checklist-template.md     # 功能级检查清单（面向 QA/DevOps）
├── plan-template.md          # 技术实施计划（面向架构师/TL）
├── spec-template.md          # 功能规范（面向产品经理/用户）
├── tasks-template.md         # 可执行任务列表（面向开发者）
└── vscode-settings.json      # VS Code 插件配置（辅助编辑体验）
```

所有 `.md` 模板均采用 **GitHub Flavored Markdown (GFM)**，并严格遵循以下设计原则：

| 原则 | 说明 | 示例 |
|------|------|------|
| **语义占位符** | 使用 `[KEY]` 格式，明确表达其语义和来源，避免模糊变量（如 `$1`） | `[FEATURE NAME]`, `[NEEDS CLARIFICATION: ...]` |
| **上下文锚点** | 通过注释 `<!-- /speckit.XXX 命令必须... -->` 显式声明生成逻辑约束 | `<!-- /speckit.tasks 命令必须根据 spec.md 用户故事替换 -->` |
| **结构化分层** | 按“阶段”（Stage）、“类别”（Category）、“用户故事”（US）组织内容，支持增量交付 | `## 阶段 3: 用户故事 1 - [Title](优先级: P1)🎯 MVP` |
| **可追溯性标记** | 所有任务/检查项带唯一 ID（`T012`, `CHK004`）和归属标签（`[US1]`, `[P]`） | `- [ ] T012 [P] [US1] 在 src/models/user.py 中创建 User 模型` |
| **防御性注释** | 包含 `⚠️ 关键`、`⚠️ 如要求测试时` 等强提示，防止误用或遗漏 | `**⚠️ 关键**: 在此阶段完成之前, 无法开始任何用户故事工作` |

---

## 关键模板详解

### 1. `spec-template.md` —— 功能规范（Spec）

**定位**：需求入口，定义“做什么”与“为什么做”。  
**驱动命令**：`/speckit.spec`  
**核心机制**：
- **用户故事优先级排序**：强制按 `P1/P2/P3` 排序，每个故事必须满足 **独立可测试、可交付、可演示**（MVP 切片）。
- **验收场景 GWT 格式**：`给定-当-那么` 结构，直接映射到自动化测试用例。
- **需求标记化**：`FR-001`、`SC-001` 等编号 + `NEEDS CLARIFICATION` 占位符，显式暴露模糊点。

```mermaid
graph LR
  A[用户描述] --> B[/speckit.spec]
  B --> C[spec-template.md]
  C --> D[填充用户故事<br>验收场景<br>功能需求<br>成功标准]
  D --> E[输出: specs/xxx/spec.md]
```

### 2. `plan-template.md` —— 实施计划（Plan）

**定位**：技术翻译层，定义“怎么做”与“用什么做”。  
**驱动命令**：`/speckit.plan`  
**核心机制**：
- **技术背景结构化**：9 个必填维度（语言/依赖/存储/测试/平台等），拒绝模糊表述（如 `NEEDS CLARIFICATION`）。
- **章程检查门控**：显式列出合规性检查点（如安全、合规、性能），失败则阻断流程。
- **项目结构双视图**：同时定义 **文档结构**（`specs/xxx/`）与 **源码结构**（`src/`、`backend/`、`ios/`），支持多范式项目（单体/Web/移动）。

### 3. `tasks-template.md` —— 任务清单（Tasks）

**定位**：执行蓝图，定义“谁在何时做哪件事”。  
**驱动命令**：`/speckit.tasks`  
**核心机制**：
- **阶段化流水线**：`设置 → 基础 → US1 → US2 → ... → 完善`，每阶段含明确目的与检查点。
- **依赖关系显式建模**：通过 `依赖于...`、`阻塞...`、`可并行` 等文本声明，替代隐式依赖。
- **并行策略内建**：`[P]` 标签标识无文件冲突任务，支持团队并行开发；`[US1]` 标签保障可追溯性。
- **MVP 交付路径**：提供 `仅 MVP`、`增量交付`、`并行团队` 三种实施策略，开箱即用。

### 4. `checklist-template.md` —— 检查清单（Checklist）

**定位**：质量门禁，定义“是否做完”与“是否做对”。  
**驱动命令**：`/speckit.checklist`  
**核心机制**：
- **上下文驱动生成**：基于 `spec.md`（需求）、`plan.md`（技术）、`tasks.md`（实施）三重输入生成，非通用模板。
- **分类+编号体系**：`[类别 1]` 下 `CHK001` ~ `CHK003`，便于审计与工具解析。
- **操作导向语言**：每项以动词开头（“验证...”、“检查...”、“确认...”），杜绝模糊描述。

### 5. `agent-file-template.md` —— 开发指南（Agent File）

**定位**：团队知识中枢，定义“项目全景”与“如何上手”。  
**驱动命令**：由 `/speckit.plan` 或 `/speckit.tasks` 自动触发更新  
**核心机制**：
- **动态聚合**：从所有 `plan.md` 中提取活跃技术、项目结构、命令、代码风格、最近变更。
- **手动扩展区**：`<!-- 手动添加内容开始 -->` 提供人工补充入口，平衡自动化与灵活性。
- **时效性保障**：`最后更新时间: [DATE]` 强制刷新，避免过期指南。

### 6. `vscode-settings.json` —— IDE 集成

**定位**：提升模板编辑效率。  
**作用**：
- 启用 `chat.promptFilesRecommendations`，在 VS Code 聊天中智能推荐相关模板（如输入 `/speckit.plan` 时推荐 `plan-template.md`）。
- 配置 `chat.tools.terminal.autoApprove`，允许 `.specify/scripts/` 下脚本免确认执行，加速本地验证。

---

## 与其他模块的集成关系

`Templates` 模块本身无业务逻辑，其价值完全体现在与 Speckit CLI 命令链的协同中：

```mermaid
graph TD
  U[用户输入] --> S[/speckit.spec]
  S -->|填充| SPEC[spec-template.md]
  SPEC -->|输出| spec_md[specs/xxx/spec.md]

  spec_md --> P[/speckit.plan]
  P -->|填充| PLAN[plan-template.md]
  PLAN -->|输出| plan_md[specs/xxx/plan.md]

  plan_md & spec_md --> T[/speckit.tasks]
  T -->|填充| TASKS[tasks-template.md]
  TASKS -->|输出| tasks_md[specs/xxx/tasks.md]

  spec_md & plan_md & tasks_md --> C[/speckit.checklist]
  C -->|填充| CHECKLIST[checklist-template.md]
  CHECKLIST -->|输出| checklist_md[specs/xxx/checklist.md]

  plan_md & tasks_md --> A[/speckit.agentfile]
  A -->|聚合| AGENT[agent-file-template.md]
  AGENT -->|输出| agent_md[docs/agent.md]
```

- **输入依赖**：每个模板的生成严格依赖上游产物（如 `tasks.md` 必须有 `spec.md` 和 `plan.md`）。
- **输出契约**：所有生成文件遵循固定路径约定（`specs/[ID]/xxx.md`），供后续工具（如 CI 流水线、文档站点）消费。
- **双向反馈**：开发者可在 `NEEDS CLARIFICATION` 处手动填写，再通过 `/speckit.replan` 触发重新生成，形成闭环。

---

## 最佳实践

### ✅ 推荐做法
- **始终从 `/speckit.spec` 启动**：确保需求先行，避免技术方案漂移。
- **利用 `[P]` 标签并行开发**：同一用户故事内，模型、服务、端点可由不同成员并行实现。
- **在 `checklist.md` 中内联评论**：用 `<!-- COMMENT: ... -->` 记录阻塞原因或临时方案，保持可追溯。
- **定期运行 `/speckit.agentfile`**：确保团队共享的开发指南始终反映最新结构与命令。

### ❌ 应避免
- **手动编辑生成文件**：`spec.md`/`plan.md`/`tasks.md` 是机器生成物，修改应通过重运行命令或修正模板。
- **删除 `NEEDS CLARIFICATION` 占位符而不填写**：这会掩盖需求风险，导致后期返工。
- **忽略检查点（Checkpoints）**：如 `基础就绪`、`用户故事 1 应该完全功能化`，它们是质量门禁，不可跳过。
- **在 `agent-file-template.md` 中硬编码路径**：应依赖自动聚合，保证跨项目一致性。

---

## 扩展性说明

- **新增模板**：只需在 `templates/` 下添加 `xxx-template.md`，并在对应 CLI 命令中注册填充逻辑。
- **定制占位符**：支持嵌套占位符（如 `[SPEC.[FEATURE].P1_SCENARIO]`），需在命令实现中解析。
- **多语言支持**：模板本身为纯文本，可通过 `i18n/` 目录提供不同语言版本，CLI 根据环境变量选择。

> 📌 **一句话总结**：`Templates` 模块是 Speckit 的“文档 DNA”——它不写代码，但决定了每一行代码为何而写、如何被验证、以及最终交付何种价值。