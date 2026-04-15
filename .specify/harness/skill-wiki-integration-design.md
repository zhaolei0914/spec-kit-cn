# Skill & Wiki 深度集成到 Harness 11 步工作流设计方案

> **版本**: 1.0.0  
> **日期**: 2026-04-14  
> **目标**: 让 LLM 在 Harness 工作流的每个阶段都能获取正确的上下文，写出符合业务和规范的代码

---

## 一、核心设计理念

### 🎯 **分层上下文加载策略**

```
┌─────────────────────────────────────────────────────────────┐
│                    上下文加载金字塔                           │
├─────────────────────────────────────────────────────────────┤
│  L1: 全局上下文 (所有阶段必读)                               │
│      - SKILL.md: 技术栈、规范、模式                          │
│      - Wiki Overview: 架构、模块关系、工作流                  │
├─────────────────────────────────────────────────────────────┤
│  L2: 角色上下文 (按角色加载)                                 │
│      - BA: Wiki Templates.md (需求模板)                      │
│      - Architect: Wiki CLI-Core.md (架构设计)                │
│      - Developer: Wiki Memory.md (编码规范)                  │
│      - QA: Wiki Documentation.md (测试文档)                  │
├─────────────────────────────────────────────────────────────┤
│  L3: 任务上下文 (按需加载)                                   │
│      - 需求分析: 归档需求摘要                                │
│      - 开发设计: 设计决策历史                                │
│      - 编写代码: 代码模式、已知陷阱                          │
│      - 测试验证: 测试策略、用例模板                          │
└─────────────────────────────────────────────────────────────┘
```

### 🔑 **三大原则**

1. **最小必要原则**: 只加载当前阶段需要的上下文，避免 token 浪费
2. **渐进增强原则**: 从全局 → 角色 → 任务，逐层细化上下文
3. **一致性原则**: 所有阶段都从同一套 Skill/Wiki 加载，确保规范统一

---

## 二、11 步工作流集成详细设计

### 📋 **工作流 → 上下文映射表**

| 工作流 | 角色 | L1 全局上下文 | L2 角色上下文 | L3 任务上下文 |
|--------|------|--------------|--------------|--------------|
| **/0-制定项目上下文** | System | - | - | - |
| **/1-需求分析** | BA/PM | SKILL.md<br>Wiki Overview | Wiki Templates.md<br>Wiki Command-Templates.md | 归档需求摘要<br>Memory/MEMORY.md |
| **/2-需求规范** | BA/PM | SKILL.md<br>Wiki Overview | Wiki Templates.md | 归档需求 FR 结构 |
| **/3-开发设计** | Architect | SKILL.md<br>Wiki Overview | Wiki CLI-Core.md<br>Wiki Project-Configuration.md | Memory 设计决策<br>Memory 代码模式 |
| **/4-实施步骤** | Architect | SKILL.md<br>Wiki Overview | Wiki CLI-Core.md | Design.md 脚手架 |
| **/5-实施前检测** | Architect | SKILL.md | - | Spec/Design/Tasks 制品 |
| **/6-编写代码** | Developer | SKILL.md<br>Wiki Overview | Wiki Memory.md<br>Wiki CLI-Core.md | Memory 编码规范<br>Memory 已知陷阱<br>代码模式 |
| **/8-生成测试用例** | QA | SKILL.md<br>Wiki Overview | Wiki Documentation.md | Memory 测试策略 |
| **/9-测试验证** | QA | SKILL.md | Wiki Documentation.md | Case.md 测试用例 |
| **/10-同步文档** | DocOps | SKILL.md | Wiki Documentation.md<br>Wiki Documentation-Configuration.md | Changelog 条目 |
| **/11-归档需求** | DocOps | SKILL.md | Wiki Memory.md | 需求完整制品 |

---

## 三、各工作流具体集成方案

### 🔹 **/1-需求分析** 集成方案

#### **修改位置**: `步骤 2.1 上下文检查`

**原代码**:
```bash
cat .windsurf/skills/project-context/SKILL.md  # 读取项目上下文
cat .specify/memory/index.md  # 读取项目记忆索引
```

**新增代码**:
```bash
# === L1: 全局上下文 (必读) ===
cat .windsurf/skills/project-context/SKILL.md  # 技术栈、规范、模式
cat .specify/wikis/[PROJECT_NAME]/overview.md  # 架构、模块关系、工作流

# === L2: 角色上下文 (BA/PM) ===
cat .specify/wikis/[PROJECT_NAME]/templates.md  # 需求模板系统设计
cat .specify/wikis/[PROJECT_NAME]/command-templates.md  # 命令模板规范

# === L3: 任务上下文 (需求分析) ===
cat .specify/memory/index.md  # 归档需求索引
# 如果发现相关归档需求，读取其 L1 摘要
```

#### **上下文使用指导**

在生成 `requirement.md` 时：
1. **从 SKILL.md 获取**：项目核心原则、业务领域、技术约束
2. **从 Wiki Overview 获取**：现有模块能力边界、工作流阶段
3. **从 Wiki Templates 获取**：需求文档结构、占位符规范、GWT 格式
4. **从 Memory 获取**：相关历史需求的 FR、约束、设计决策

---

### 🔹 **/2-需求规范** 集成方案

#### **修改位置**: `步骤 1. 加载上下文`

**原代码**:
```bash
cat .windsurf/skills/project-context/SKILL.md
cat .specify/memory/index.md
cat specs/[REQ_ID]/requirement.md
```

**新增代码**:
```bash
# === L1: 全局上下文 ===
cat .windsurf/skills/project-context/SKILL.md
cat .specify/wikis/[PROJECT_NAME]/overview.md

# === L2: 角色上下文 (BA/PM) ===
cat .specify/wikis/[PROJECT_NAME]/templates.md  # spec-template.md 设计理念

# === L3: 任务上下文 ===
cat .specify/memory/index.md  # 归档需求 FR 结构参考
cat specs/[REQ_ID]/requirement.md
```

#### **上下文使用指导**

在生成 `spec.md` 时：
1. **从 SKILL.md 获取**：API 规范、错误处理规范、命名规范
2. **从 Wiki Templates 获取**：FR 编号规则、验收场景 GWT 格式、优先级排序
3. **从归档需求获取**：类似需求的 FR 分组结构和编号风格

---

### 🔹 **/3-开发设计** 集成方案

#### **修改位置**: `步骤 2. 加载需求上下文` 之后

**新增代码**:
```bash
# === L1: 全局上下文 ===
cat .windsurf/skills/project-context/SKILL.md
cat .specify/wikis/[PROJECT_NAME]/overview.md

# === L2: 角色上下文 (Architect) ===
cat .specify/wikis/[PROJECT_NAME]/cli-core.md  # CLI 架构设计
cat .specify/wikis/[PROJECT_NAME]/project-configuration.md  # 项目配置规范

# === L3: 任务上下文 (架构设计) ===
cat .specify/memory/MEMORY.md  # 读取设计决策和代码模式
# 按 MEMORY.md 读取协议加载:
# - design-decisions.md: 历史架构决策
# - code-patterns.md: 可复用的代码模式
```

#### **上下文使用指导**

在生成 `design.md` 时：
1. **从 SKILL.md 获取**：技术栈版本、框架选择、设计模式
2. **从 Wiki Overview 获取**：模块协作方式、解耦策略
3. **从 Wiki CLI-Core 获取**：CLI 架构模式、命令式架构设计
4. **从 Memory 获取**：历史设计决策（避免重复踩坑）、可复用代码模式

---

### 🔹 **/4-实施步骤** 集成方案

#### **修改位置**: `步骤 1. 加载上下文` 

**新增代码**:
```bash
# === L1: 全局上下文 ===
cat .windsurf/skills/project-context/SKILL.md
cat .specify/wikis/[PROJECT_NAME]/overview.md

# === L2: 角色上下文 (Architect) ===
cat .specify/wikis/[PROJECT_NAME]/cli-core.md  # 执行流程设计

# === L3: 任务上下文 (任务分解) ===
cat specs/[REQ_ID]/design.md  # 提取代码脚手架
```

#### **上下文使用指导**

在生成 `tasks.md` 时：
1. **从 SKILL.md 获取**：命名规范、文件组织规范
2. **从 Wiki CLI-Core 获取**：命令式架构的任务分解模式
3. **从 Design.md 获取**：函数签名、接口定义、业务规则

---

### 🔹 **/6-编写代码** 集成方案（最关键！）

#### **修改位置**: `步骤 1. 加载和分析实施上下文`

**原代码**:
```bash
# 必需: 读取 .windsurf/skills/project-context/SKILL.md
# 必需: 读取 .specify/memory/MEMORY.md
```

**新增代码**:
```bash
# === L1: 全局上下文 (必读) ===
cat .windsurf/skills/project-context/SKILL.md  # 技术栈、规范、模式
cat .specify/wikis/[PROJECT_NAME]/overview.md  # 架构、模块关系

# === L2: 角色上下文 (Developer) ===
cat .specify/wikis/[PROJECT_NAME]/memory.md  # 编码规范详解
cat .specify/wikis/[PROJECT_NAME]/cli-core.md  # CLI 实现细节

# === L3: 任务上下文 (编码实现) ===
cat .specify/memory/MEMORY.md  # 按读取协议加载:
# - coding-standards.md: 编码规范（命名、格式、注释）
# - known-pitfalls.md: 已知陷阱和反模式
# - code-patterns.md: 可复用代码模式

cat specs/[REQ_ID]/tasks.md  # 任务列表、函数规格
cat specs/[REQ_ID]/design.md  # 设计文档、接口定义
```

#### **上下文使用指导**（最详细！）

在编写代码时，**严格按以下优先级使用上下文**：

**优先级 1: 接口定义和业务规则（来自 Design.md）**
- ✅ 函数签名、参数类型、返回值 → **必须完全一致**
- ✅ 数据库表结构、字段类型、约束 → **必须完全一致**
- ✅ API 路径、方法、参数、响应格式 → **必须完全一致**
- ✅ 业务流程、状态机、错误码 → **必须完全一致**

**优先级 2: 编码规范（来自 SKILL.md + Memory）**
- ✅ 命名规范：`snake_case` / `PascalCase` / `UPPER_SNAKE_CASE`
- ✅ 禁止规则：不用 `print()`，必须用 `console.print()`
- ✅ 错误处理：使用 `raise` / `try/except`，不用裸 `except`
- ✅ 导入规范：绝对导入，不用 `import *`
- ✅ 路径处理：使用 `Path` 对象，不用字符串拼接

**优先级 3: 架构模式（来自 Wiki Overview + CLI-Core）**
- ✅ 模块协作：通过文件系统，不用 Python 调用
- ✅ 命令模式：Typer 框架，`@app.command()`
- ✅ 配置驱动：使用 `AGENT_CONFIG` 字典，不硬编码

**优先级 4: 代码复用（来自 Memory Code-Patterns）**
- ✅ 搜索现有函数、模块、工具类
- ✅ 优先复用现有代码，而不是重新实现
- ✅ 如果现有代码不完整，完善而不是新建

**优先级 5: 避免陷阱（来自 Memory Known-Pitfalls）**
- ✅ 检查已知陷阱列表，避免重复踩坑
- ✅ 参考历史 Bug 修复记录

---

### 🔹 **/8-生成测试用例** 集成方案

#### **新增代码**:
```bash
# === L1: 全局上下文 ===
cat .windsurf/skills/project-context/SKILL.md
cat .specify/wikis/[PROJECT_NAME]/overview.md

# === L2: 角色上下文 (QA) ===
cat .specify/wikis/[PROJECT_NAME]/documentation.md  # 测试文档规范

# === L3: 任务上下文 (测试设计) ===
cat .specify/memory/MEMORY.md  # 读取测试策略
cat specs/[REQ_ID]/spec.md  # 验收场景 (GWT)
cat specs/[REQ_ID]/design.md  # 接口定义、错误码
```

#### **上下文使用指导**

在生成 `case.md` 时：
1. **从 Spec.md 获取**：验收场景（GWT 格式）→ 直接转为测试用例
2. **从 Design.md 获取**：接口定义 → 生成接口测试用例
3. **从 SKILL.md 获取**：测试规范（如果有 TODO 则参考建议）
4. **从 Memory 获取**：测试策略、Mock 策略

---

### 🔹 **/10-同步文档** 集成方案

#### **新增代码**:
```bash
# === L1: 全局上下文 ===
cat .windsurf/skills/project-context/SKILL.md

# === L2: 角色上下文 (DocOps) ===
cat .specify/wikis/[PROJECT_NAME]/documentation.md  # 文档组织方式
cat .specify/wikis/[PROJECT_NAME]/documentation-configuration.md  # DocFX 配置

# === L3: 任务上下文 ===
cat .ai-changelogs.md  # 未同步的 changelog 条目
```

---

### 🔹 **/11-归档需求** 集成方案

#### **新增代码**:
```bash
# === L1: 全局上下文 ===
cat .windsurf/skills/project-context/SKILL.md

# === L2: 角色上下文 (DocOps) ===
cat .specify/wikis/[PROJECT_NAME]/memory.md  # Memory 系统设计

# === L3: 任务上下文 ===
cat specs/[REQ_ID]/*.md  # 需求完整制品
```

---

## 四、实施步骤

### 📝 **阶段 1: 修改工作流文件（1-2 小时）**

1. **批量修改 11 个工作流文件**，在每个文件的"加载上下文"章节添加：
   ```bash
   # === L1: 全局上下文 (必读) ===
   cat .windsurf/skills/project-context/SKILL.md
   cat .specify/wikis/[PROJECT_NAME]/overview.md
   
   # === L2: 角色上下文 ([ROLE]) ===
   # (根据上表添加对应的 Wiki 文件)
   
   # === L3: 任务上下文 ([TASK]) ===
   # (根据上表添加对应的 Memory 和制品文件)
   ```

2. **添加上下文使用指导**：在每个工作流的"执行流程"章节前，添加：
   ```markdown
   ## 上下文使用指导
   
   在执行本工作流时，请按以下优先级使用上下文：
   1. **优先级 1**: [具体指导]
   2. **优先级 2**: [具体指导]
   ...
   ```

### 📝 **阶段 2: 创建 Wiki 快速索引（30 分钟）**

创建 `.specify/wikis/[PROJECT_NAME]/README.md`：

```markdown
# Wiki 快速索引

## 按角色查找

- **BA/PM**: templates.md, command-templates.md
- **Architect**: cli-core.md, project-configuration.md
- **Developer**: memory.md, cli-core.md
- **QA**: documentation.md
- **DocOps**: documentation.md, documentation-configuration.md

## 按任务查找

- **理解架构**: overview.md
- **需求模板**: templates.md
- **编码规范**: memory.md
- **测试规范**: documentation.md
- **文档配置**: documentation-configuration.md
```

### 📝 **阶段 3: 更新 SKILL.md（30 分钟）**

在 SKILL.md 末尾添加：

```markdown
## 附录：Wiki 文档导航

本项目的 Wiki 文档位于 `.specify/wikis/[PROJECT_NAME]/`，提供架构和流程的详细说明：

- **overview.md**: 项目全景、架构概览、端到端工作流
- **cli-core.md**: CLI 架构设计、命令式架构、执行流程
- **templates.md**: 需求模板系统、占位符规范、GWT 格式
- **memory.md**: Memory 系统设计、编码规范、已知陷阱
- **documentation.md**: 文档组织方式、测试文档规范
- **project-configuration.md**: 项目配置规范、依赖管理
- **command-templates.md**: 命令模板规范、生成逻辑
- **documentation-configuration.md**: DocFX 配置、文档站点构建

💡 **使用建议**：
- 编码前先读 SKILL.md（规范）+ overview.md（架构）
- 设计时参考 cli-core.md（架构模式）+ memory.md（历史决策）
- 测试时参考 documentation.md（测试规范）
```

### 📝 **阶段 4: 测试验证（1 小时）**

1. **运行 `/1-需求分析`**，检查是否正确加载 Wiki Templates.md
2. **运行 `/3-开发设计`**，检查是否正确加载 CLI-Core.md 和设计决策
3. **运行 `/6-编写代码`**，检查是否严格遵守 SKILL.md 规范和 Design.md 接口
4. **验证生成的代码**：
   - 命名规范是否符合 SKILL.md
   - 接口定义是否与 Design.md 一致
   - 是否复用了 Memory 中的代码模式
   - 是否避免了 Known-Pitfalls 中的陷阱

---

## 五、预期效果

### ✅ **需求分析阶段**
- LLM 理解项目架构边界，不提出超出能力的需求
- 需求文档结构符合 Wiki Templates 规范
- 自动参考归档需求的 FR 结构

### ✅ **开发设计阶段**
- 设计方案符合 Wiki Overview 的架构模式
- 复用 Memory 中的历史设计决策
- 避免重复踩坑

### ✅ **编写代码阶段（最关键！）**
- **100% 符合 SKILL.md 规范**：命名、格式、禁止规则
- **100% 符合 Design.md 接口**：函数签名、参数、返回值
- **优先复用现有代码**：减少重复实现
- **避免已知陷阱**：参考 Known-Pitfalls

### ✅ **测试验证阶段**
- 测试用例直接从 Spec.md 的 GWT 场景生成
- 测试策略符合 Memory 规范

---

## 六、维护建议

### 🔄 **定期更新 Skill/Wiki**

1. **代码变更后** → 重新运行 `/0-制定项目上下文` → 更新 SKILL.md
2. **架构演进后** → 手动更新 Wiki Overview.md
3. **新增设计决策** → 更新 Memory/design-decisions.md
4. **发现新陷阱** → 更新 Memory/known-pitfalls.md

### 📊 **质量监控**

在 `.specify/harness/execution-log.md` 中记录：
- 是否正确加载了所有必需的上下文文件
- 生成的代码是否符合 SKILL.md 规范
- 是否复用了 Memory 中的代码模式

---

## 七、总结

### 🎯 **核心价值**

通过将 Skill 和 Wiki 深度集成到 Harness 11 步工作流，实现：

1. **规范统一**：所有阶段都从同一套 Skill/Wiki 加载，确保规范一致
2. **上下文精准**：每个角色只加载需要的上下文，避免 token 浪费
3. **质量保障**：LLM 严格遵守 SKILL.md 规范和 Design.md 接口
4. **知识复用**：自动参考 Memory 中的历史决策和代码模式
5. **避免踩坑**：参考 Known-Pitfalls，减少重复错误

### 🚀 **下一步行动**

1. ✅ 批量修改 11 个工作流文件（优先 /1, /3, /6）
2. ✅ 创建 Wiki 快速索引
3. ✅ 更新 SKILL.md 添加 Wiki 导航
4. ✅ 测试验证（重点测试 /6-编写代码）
5. ✅ 记录执行日志，监控质量

**让 Skill 成为"规范之手"，Wiki 成为"架构之眼"，Memory 成为"经验之库"，三者协同指导 LLM 写出高质量代码！** 🎉
