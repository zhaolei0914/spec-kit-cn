# Skill & Wiki 上下文加载快速参考

> **一页纸速查手册** - 打印或保存到桌面，随时查阅

---

## 📚 三层上下文加载模型

```
┌─────────────────────────────────────────────┐
│ L1: 全局上下文 (所有阶段必读)               │
│     SKILL.md + Wiki Overview.md             │
├─────────────────────────────────────────────┤
│ L2: 角色上下文 (按角色加载)                 │
│     BA → Templates | Architect → CLI-Core  │
│     Developer → Memory | QA → Documentation │
├─────────────────────────────────────────────┤
│ L3: 任务上下文 (按需加载)                   │
│     需求摘要 | 设计决策 | 代码模式 | 测试策略│
└─────────────────────────────────────────────┘
```

---

## 🗺️ 工作流 → 上下文映射速查表

| 工作流 | L1 全局 | L2 角色 | L3 任务 |
|--------|---------|---------|---------|
| `/1-需求分析` | SKILL<br>Overview | Templates<br>Command-Templates | 归档需求<br>MEMORY |
| `/2-需求规范` | SKILL<br>Overview | Templates | 归档 FR 结构 |
| `/3-开发设计` | SKILL<br>Overview | CLI-Core<br>Project-Config | 设计决策<br>代码模式 |
| `/4-实施步骤` | SKILL<br>Overview | CLI-Core | Design 脚手架 |
| `/5-实施前检测` | SKILL | - | 制品文件 |
| `/6-编写代码` | SKILL<br>Overview | Memory<br>CLI-Core | 编码规范<br>已知陷阱<br>代码模式 |
| `/8-生成测试用例` | SKILL<br>Overview | Documentation | 测试策略 |
| `/9-测试验证` | SKILL | Documentation | 测试用例 |
| `/10-同步文档` | SKILL | Documentation<br>Doc-Config | Changelog |
| `/11-归档需求` | SKILL | Memory | 需求制品 |

---

## 📂 文件路径速查

### Skill 文件
```
.windsurf/skills/project-context/
├── SKILL.md                    # 技术栈、规范、模式
└── .context-facts.json         # 代码事实数据
```

### Wiki 文件
```
.specify/wikis/[PROJECT_NAME]/
├── overview.md                 # 架构、模块关系、工作流
├── cli-core.md                 # CLI 架构设计
├── templates.md                # 需求模板系统
├── command-templates.md        # 命令模板规范
├── memory.md                   # Memory 系统设计
├── documentation.md            # 文档组织方式
├── project-configuration.md    # 项目配置规范
└── documentation-configuration.md  # DocFX 配置
```

### Memory 文件
```
.specify/memory/
├── MEMORY.md                   # Memory 索引（读取协议）
├── index.md                    # 归档需求索引
├── summaries/[ID].md           # 需求摘要（L1）
├── coding-standards.md         # 编码规范
├── known-pitfalls.md           # 已知陷阱
├── code-patterns.md            # 代码模式
└── design-decisions.md         # 设计决策
```

---

## 🎯 按角色查找上下文

### BA/PM（需求分析师）
```bash
# L1
cat .windsurf/skills/project-context/SKILL.md
cat .specify/wikis/[PROJECT_NAME]/overview.md

# L2
cat .specify/wikis/[PROJECT_NAME]/templates.md
cat .specify/wikis/[PROJECT_NAME]/command-templates.md

# L3
cat .specify/memory/index.md
cat .specify/memory/summaries/[ID].md  # 如果相关
```

### Architect（架构设计师）
```bash
# L1
cat .windsurf/skills/project-context/SKILL.md
cat .specify/wikis/[PROJECT_NAME]/overview.md

# L2
cat .specify/wikis/[PROJECT_NAME]/cli-core.md
cat .specify/wikis/[PROJECT_NAME]/project-configuration.md

# L3
cat .specify/memory/MEMORY.md
cat .specify/memory/design-decisions.md
cat .specify/memory/code-patterns.md
```

### Developer（开发工程师）
```bash
# L1
cat .windsurf/skills/project-context/SKILL.md
cat .specify/wikis/[PROJECT_NAME]/overview.md

# L2
cat .specify/wikis/[PROJECT_NAME]/memory.md
cat .specify/wikis/[PROJECT_NAME]/cli-core.md

# L3
cat .specify/memory/MEMORY.md
cat .specify/memory/coding-standards.md
cat .specify/memory/known-pitfalls.md
cat .specify/memory/code-patterns.md
cat specs/[REQ_ID]/tasks.md
cat specs/[REQ_ID]/design.md
```

### QA（测试工程师）
```bash
# L1
cat .windsurf/skills/project-context/SKILL.md
cat .specify/wikis/[PROJECT_NAME]/overview.md

# L2
cat .specify/wikis/[PROJECT_NAME]/documentation.md

# L3
cat .specify/memory/MEMORY.md
cat specs/[REQ_ID]/spec.md
cat specs/[REQ_ID]/design.md
```

---

## 🔍 按任务查找上下文

### 理解项目架构
```bash
cat .specify/wikis/[PROJECT_NAME]/overview.md  # 架构概览
cat .specify/wikis/[PROJECT_NAME]/cli-core.md  # CLI 架构
cat .windsurf/skills/project-context/SKILL.md  # 技术栈
```

### 编写需求文档
```bash
cat .specify/wikis/[PROJECT_NAME]/templates.md  # 模板规范
cat .specify/memory/index.md                    # 归档需求参考
```

### 设计技术方案
```bash
cat .specify/wikis/[PROJECT_NAME]/cli-core.md        # 架构模式
cat .specify/memory/design-decisions.md              # 历史决策
cat .specify/memory/code-patterns.md                 # 代码模式
```

### 编写代码
```bash
cat .windsurf/skills/project-context/SKILL.md        # 编码规范
cat .specify/memory/coding-standards.md              # 详细规范
cat .specify/memory/known-pitfalls.md                # 已知陷阱
cat specs/[REQ_ID]/design.md                         # 接口定义
```

### 编写测试
```bash
cat .specify/wikis/[PROJECT_NAME]/documentation.md   # 测试规范
cat specs/[REQ_ID]/spec.md                           # 验收场景
```

---

## ⚡ 编码时的 5 大优先级

### 优先级 1: 接口定义（来自 Design.md）
- ✅ 函数签名、参数、返回值 → **必须完全一致**
- ✅ 数据库表结构、字段、约束 → **必须完全一致**
- ✅ API 路径、方法、参数、响应 → **必须完全一致**

### 优先级 2: 编码规范（来自 SKILL.md）
- ✅ 命名：`snake_case` / `PascalCase` / `UPPER_SNAKE_CASE`
- ✅ 禁止：`print()` → 用 `console.print()`
- ✅ 禁止：字符串拼接路径 → 用 `Path` 对象
- ✅ 禁止：裸 `except` → 捕获具体异常

### 优先级 3: 架构模式（来自 Wiki）
- ✅ 模块协作：文件系统，不用 Python 调用
- ✅ 命令模式：Typer `@app.command()`
- ✅ 配置驱动：`AGENT_CONFIG` 字典

### 优先级 4: 代码复用（来自 Memory）
- ✅ 搜索现有函数、模块
- ✅ 优先复用，而非重新实现
- ✅ 不完整则完善，而非新建

### 优先级 5: 避免陷阱（来自 Memory）
- ✅ 检查 `known-pitfalls.md`
- ✅ 参考历史 Bug 修复

---

## 🚨 常见错误和解决方案

### ❌ 错误 1: 没有加载 SKILL.md
**症状**: 生成的代码使用 `print()` 而非 `console.print()`  
**解决**: 在工作流开头添加 `cat .windsurf/skills/project-context/SKILL.md`

### ❌ 错误 2: 没有参考 Design.md
**症状**: 函数签名与设计文档不一致  
**解决**: 在编码前先读取 `specs/[REQ_ID]/design.md`，提取接口定义

### ❌ 错误 3: 没有复用现有代码
**症状**: 重新实现了已存在的函数  
**解决**: 在编码前扫描代码库，搜索可复用的函数

### ❌ 错误 4: 重复踩坑
**症状**: 遇到了 `known-pitfalls.md` 中已记录的陷阱  
**解决**: 在编码前读取 `.specify/memory/known-pitfalls.md`

---

## 📊 质量检查清单

### 编码完成后，检查以下项目：

- [ ] **命名规范**: 函数用 `snake_case`，类用 `PascalCase`
- [ ] **输出规范**: 使用 `console.print()` 而非 `print()`
- [ ] **路径处理**: 使用 `Path` 对象而非字符串拼接
- [ ] **错误处理**: 捕获具体异常，不用裸 `except`
- [ ] **接口一致**: 函数签名与 `design.md` 完全一致
- [ ] **代码复用**: 优先复用现有代码
- [ ] **避免陷阱**: 没有触发 `known-pitfalls.md` 中的陷阱
- [ ] **追溯注释**: 添加 `# FR-xxx, design.md X.X` 注释

---

## 🔧 故障排查

### 问题: 找不到 Wiki 文件
```bash
# 检查项目名称
ls -la .specify/wikis/

# 如果不存在，运行 /0-制定项目上下文
# 这会自动下载 Wiki 文件
```

### 问题: SKILL.md 内容过时
```bash
# 重新生成 SKILL.md
# 运行 /0-制定项目上下文
```

### 问题: Memory 文件缺失
```bash
# 检查 Memory 目录
ls -la .specify/memory/

# 如果缺失，手动创建或从模板复制
```

---

## 💡 最佳实践

1. **编码前三步走**:
   - 第 1 步: 读 SKILL.md（规范）
   - 第 2 步: 读 Wiki Overview（架构）
   - 第 3 步: 读 Design.md（接口）

2. **设计前三步走**:
   - 第 1 步: 读 Wiki CLI-Core（架构模式）
   - 第 2 步: 读 Memory 设计决策（历史经验）
   - 第 3 步: 读 Spec.md（需求）

3. **需求分析前三步走**:
   - 第 1 步: 读 Wiki Overview（能力边界）
   - 第 2 步: 读 Wiki Templates（模板规范）
   - 第 3 步: 读 Memory 归档需求（历史参考）

---

## 📞 获取帮助

- **详细设计方案**: `.specify/harness/skill-wiki-integration-design.md`
- **实施检查清单**: `.specify/harness/skill-wiki-integration-checklist.md`
- **问题反馈**: 记录到 `.specify/harness/issues.md`

---

**记住：Skill 是规范，Wiki 是架构，Memory 是经验，三者协同才能写出高质量代码！** 🚀
