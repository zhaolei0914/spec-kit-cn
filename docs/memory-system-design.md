# 记忆系统设计方案

## 一、背景与目标

### 1.1 现状

当前记忆以文件形式嵌套在 Skill 目录内：

```
__AGENT_SKILLS_DIR__/project-context/
├── SKILL.md                    # 项目概述（引用 memory/）
├── standards/*.md              # 编码规范 Skill
└── memory/                     # 记忆文件（嵌套在 Skill 内）
    ├── index.md
    ├── summaries/
    ├── coding-standards.md
    ├── known-pitfalls.md
    ├── design-decisions.md
    └── code-patterns.md
```

**问题**：

1. **职责混淆** — Skill 是"项目知识的静态提取"（由代码分析生成），memory 是"开发过程中动态积累的经验"，两者生命周期和更新频率完全不同，却混在同一目录
2. **无独立管控** — memory 没有自己的容量策略、版本控制、精炼机制，全靠各命令模板中的零散指令
3. **Agent 路径耦合** — memory 路径随 `__AGENT_SKILLS_DIR__` 变化，但记忆内容与 Agent 类型无关

### 1.2 设计目标

| 目标 | 说明 |
|------|------|
| **独立存放** | 记忆从 Skill 中分离，拥有独立目录和管理机制 |
| **单项目范围** | 不做跨项目复用，聚焦当前项目的开发经验 |
| **文件驱动** | 纯文件系统实现，无外部依赖（无数据库、无向量库） |
| **分层读取** | 不同阶段只读取需要的记忆层，控制 token 消耗 |
| **自动精炼** | 容量管控 + 过期淘汰 + 同类合并，防止记忆膨胀 |
| **Agent 无关** | 记忆目录路径固定，不随 Agent 类型变化 |

---

## 二、Skill vs 独立文件 — 方案对比

### 方案 A：做成独立 Skill（`memory-system/`）

```
__AGENT_SKILLS_DIR__/
├── project-context/          # 现有 Skill（代码分析产物）
│   └── SKILL.md
└── memory-system/            # 新增 Skill（记忆系统）
    └── SKILL.md              # 记忆系统入口
    └── ...
```

| 优点 | 缺点 |
|------|------|
| 复用 Skill 的按需加载机制 | 路径仍然绑定 `__AGENT_SKILLS_DIR__`，随 Agent 变化 |
| 符合现有 Skill 约定 | Skill 预期是"静态知识提取"，记忆是"动态积累"，语义不匹配 |
| 命令模板中已有 Skill 读取模式 | memory-system 的 SKILL.md 不是代码分析产物，破坏 Skill 一致性 |

### 方案 B：独立文件目录（`.specify/memory/`）

```
.specify/
└── memory/                   # 独立记忆目录（Agent 无关）
    ├── MEMORY.md             # 记忆系统入口 + 读取协议
    ├── index.md              # L0 极简索引
    ├── summaries/            # L1 需求摘要
    ├── coding-standards.md   # 编码规范
    ├── known-pitfalls.md     # 已知陷阱
    ├── design-decisions.md   # 设计决策
    └── code-patterns.md      # 代码模式
```

| 优点 | 缺点 |
|------|------|
| 路径固定 `.specify/memory/`，Agent 无关 | 命令模板中需要新增读取路径（不再复用 Skill 路径） |
| 语义清晰：`.specify/` = 项目元数据，memory = 开发记忆 | 需要独立的管理机制（不复用 Skill 生成器） |
| 独立管控生命周期、容量、精炼策略 | 与 SKILL.md 的关联需要重新设计 |
| 已有 `.specify/memory/constitution.md` 先例 | — |

### 结论：**方案 B — 独立文件目录**

理由：
1. 记忆是**动态积累**，Skill 是**静态提取**，放在一起违反单一职责
2. `.specify/memory/` 路径已存在（constitution.md），扩展自然
3. 路径固定后，命令模板中不需要 `__AGENT_SKILLS_DIR__` 占位符，简化模板
4. ECC 和 OmO 都将记忆与技能分开存储

---

## 三、记忆系统架构

### 3.1 目录结构

```
.specify/memory/
├── MEMORY.md                 # 🔑 记忆系统入口（读取协议 + 容量策略）
├── constitution.md           # 项目章程（现有，不变）
├── index.md                  # L0 极简索引（每需求1行，≤50行）
├── summaries/                # L1 需求摘要（每需求1文件，≤1K tokens）
│   ├── REQ-001.md
│   └── REQ-002.md
├── coding-standards.md       # 编码规范（≤30条）
├── known-pitfalls.md         # 已知陷阱（≤30条）
├── design-decisions.md       # 设计决策（≤30条）
└── code-patterns.md          # 代码模式（≤20条）
```

### 3.2 分层读取协议

参考 ECC 的分层记忆和 OmO 的按需加载，设计三层读取协议：

```
L0 索引层（始终读取）
│   index.md — 极简表格，1行/需求，≤50行
│   预算: ≤500 tokens
│
├── L1 摘要层（按需读取）
│   summaries/[ID].md — 需求摘要，≤1K tokens/个
│   读取时机: 需要了解某个需求的 FR 分组和约束时
│
└── L2 经验层（按角色读取）
    coding-standards.md  — 编写代码时必读
    known-pitfalls.md    — 修改已有模块时必读
    design-decisions.md  — 理解设计意图时读
    code-patterns.md     — 需要复用实现方式时读
    预算: 每个文件 ≤2K tokens
```

### 3.3 各阶段记忆读写矩阵

| SDD 阶段 | 读取 | 写入 |
|----------|------|------|
| `/0-制定项目上下文` | — | 初始化 MEMORY.md + 全部文件骨架 |
| `/1-需求分析` | index.md | — |
| `/2-需求规范` | index.md | — |
| `/3-开发设计` | index.md, design-decisions.md | — |
| `/4-实施步骤` | index.md | — |
| `/5-实施前检测` | index.md, coding-standards.md | — |
| `/6-编写代码` | coding-standards.md, known-pitfalls.md, code-patterns.md | coding-standards.md, known-pitfalls.md（步骤6记忆更新检查） |
| `/8-生成测试用例` | index.md | — |
| `/9-测试验证` | index.md, known-pitfalls.md | known-pitfalls.md（测试发现的陷阱） |
| `/10-同步文档` | index.md | — |
| `/11-归档需求` | 全部 | design-decisions.md, known-pitfalls.md, coding-standards.md, code-patterns.md, summaries/, index.md |

---

## 四、MEMORY.md 入口文件设计

`MEMORY.md` 是记忆系统的唯一入口，所有命令模板只需引用此文件，由它定义读取协议。

```markdown
# 项目记忆系统

## 读取协议

**开发前必读**: 本文件 + `index.md`

根据当前任务类型，按需读取对应记忆文件：

| 任务类型 | 必读文件 | 可选文件 |
|----------|---------|---------|
| 编写代码 | coding-standards.md | known-pitfalls.md, code-patterns.md |
| 修改已有模块 | known-pitfalls.md, coding-standards.md | code-patterns.md |
| 架构设计 | design-decisions.md | code-patterns.md |
| 复用实现模式 | code-patterns.md | — |
| 测试验证 | known-pitfalls.md | coding-standards.md |

## 写入规则

记忆写入仅在以下时机发生：
1. **`/6-编写代码` 步骤6** — 记忆更新检查（编码规范、已知陷阱）
2. **`/9-测试验证`** — 测试发现的陷阱
3. **`/11-归档需求`** — 全面精炼（设计决策、代码模式、摘要、索引）

写入条件（必须同时满足）：
- ✅ 可泛化（不是一次性的特殊情况）
- ✅ 非显而易见（有信息增量）
- ✅ 可操作（能指导后续开发行为）

## 容量策略

| 文件 | 条目上限 | 超限处理 |
|------|---------|---------|
| index.md | 50 行 | 归档最早的已完成需求 |
| coding-standards.md | 30 条 | 合并相似条目、泛化提升 |
| known-pitfalls.md | 30 条 | 合并同类、淘汰已被规范化的条目 |
| design-decisions.md | 30 条 | 合并同领域决策 |
| code-patterns.md | 20 条 | 合并相似模式、淘汰已过时的 |
| summaries/*.md | 每文件 ≤1K tokens | 压缩冗余描述 |

## 精炼机制

在 `/11-归档需求` 阶段执行记忆精炼：

1. **容量检查** — 超限文件触发精炼
2. **合并同类** — 语义相似的条目合并为一条
3. **泛化提升** — 具体案例提升为通用规则
4. **淘汰过期** — 已被编码规范覆盖的陷阱、已重构的代码模式
5. **置信度标记** — 被多次验证的记忆标记 `[高置信]`
```

---

## 五、与现有系统的关系

### 5.1 与 Skill 系统的关系

```
SKILL.md（项目知识入口）
├── 引用 standards/*.md（编码规范 Skill）
└── 引用 .specify/memory/MEMORY.md（记忆系统入口）
         └── 记忆系统自行管理读取协议

分工:
  Skill = 静态知识（代码分析产物，`/0-制定项目上下文` 生成）
  Memory = 动态经验（开发过程积累，`/6`、`/9`、`/11` 写入）
```

SKILL.md 末尾保留一个指向记忆系统的引用：

```markdown
## 项目记忆

项目开发记忆独立管理，入口文件：[`.specify/memory/MEMORY.md`](../../.specify/memory/MEMORY.md)
```

### 5.2 与 constitution.md 的关系

`constitution.md` 是项目章程（核心原则、治理规则），属于**项目级不变量**。它继续存放在 `.specify/memory/` 目录中，但不参与记忆的读写协议和容量管控——它是"宪法"，不是"经验"。

### 5.3 与 Agent 项目规则的关系

`__AGENT_RULES_FILE__`（如 `.windsurfrules`、`CLAUDE.md`）中写入的开发前置规则，引用路径从：
```
__AGENT_SKILLS_DIR__/project-context/memory/index.md
```
改为：
```
.specify/memory/MEMORY.md
```

---

## 六、参考系统对比

| 维度 | ECC 分层记忆 | OmO 分层上下文 | **本方案** |
|------|-------------|---------------|-----------|
| **存储** | SQLite + instinct 文件 | AGENTS.md 层级文件 | `.specify/memory/` 纯文件 |
| **自动提取** | Git 历史 + 会话自动提取 | ContextScout 自动扫描 | SDD 流程节点触发写入 |
| **容量管控** | `AUTOCOMPACT_PCT` 百分比 | 无显式管控 | 每文件条目上限 + 精炼机制 |
| **检索方式** | `instinct-status` 命令查询 | 按优先级自动加载 | 三层读取协议（L0→L1→L2） |
| **精炼** | `/evolve` 聚类为技能、`/prune` 清理 | 无显式精炼 | `/11-归档需求` 阶段统一精炼 |
| **置信度** | 置信度评分 | 无 | `[高置信]` 标记（多次验证） |
| **跨会话** | ✅ SQLite 持久化 | ✅ 文件持久化 | ✅ 文件持久化 |
| **跨项目** | ✅ 导入/导出 | ✅ 技能复用 | ❌ 不做（设计选择） |
| **外部依赖** | SQLite | 无 | 无 |

### 借鉴要点

- **来自 ECC**: 容量管控策略、置信度评分、精炼机制（合并/泛化/淘汰）
- **来自 OmO**: 零配置、自动注入（通过 SDD 流程节点自动触发）、分层按需加载

---

## 七、迁移计划

### 改动范围

| 类别 | 文件 | 改动 |
|------|------|------|
| **新增** | `.specify/memory/MEMORY.md` | 记忆系统入口文件模板 |
| **修改** | `templates/commands/0-制定项目上下文.md` | 阶段4：记忆初始化路径从 `__AGENT_SKILLS_DIR__/project-context/memory/` 改为 `.specify/memory/`；阶段5：SKILL.md 记忆章节改为引用 MEMORY.md |
| **修改** | `templates/commands/6-编写代码.md` | 步骤6 记忆更新检查路径改为 `.specify/memory/` |
| **修改** | `templates/commands/9-测试验证.md` | 记忆读取路径改为 `.specify/memory/` |
| **修改** | `templates/commands/11-归档需求.md` | 全部记忆路径改为 `.specify/memory/`；新增精炼机制详细步骤 |
| **修改** | `templates/commands/3-开发设计.md` | 记忆读取路径改为 `.specify/memory/` |
| **修改** | `create-release-packages.sh` | `.specify/memory/` 已在 build_variant 中复制，无需改动；移除旧 `__AGENT_SKILLS_DIR__/project-context/memory/` 初始化逻辑 |

### 向后兼容

- 对已使用旧路径的项目，`/0-制定项目上下文` 重新执行时检测旧路径，自动迁移到新位置
- SKILL.md 中的旧 `memory/` 引用在重新执行 `/0` 时更新

---

## 八、总结

| 决策 | 选择 | 理由 |
|------|------|------|
| Skill vs 独立文件 | **独立文件** | 记忆是动态经验，Skill 是静态知识，职责不同 |
| 存储位置 | **`.specify/memory/`** | Agent 无关、已有先例、语义清晰 |
| 入口文件 | **MEMORY.md** | 单一入口，自包含读取协议和容量策略 |
| 精炼时机 | **`/11-归档需求`** | SDD 流程自然节点，不增加额外操作 |
| 外部依赖 | **无** | 纯文件系统，零门槛 |
