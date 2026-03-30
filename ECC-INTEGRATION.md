# Everything Claude Code (ECC) 集成说明

本文档详细说明了 Spec Kit 如何集成 [everything-claude-code](https://github.com/affaan-m/everything-claude-code) 项目的核心组件。

## 📋 集成概览

### 集成范围

Spec Kit 完整集成了 ECC 的以下组件，用于增强 **Claude Code、Windsurf、Codex** 三个 AI 工具：

| 组件 | Claude Code | Windsurf | Codex | 数量 |
|------|-------------|----------|-------|------|
| **Agents** | ✅ | ❌ | ❌ | 12 个 |
| **Commands** | ✅ | ✅ | ✅ | 15 个 |
| **Skills** | ✅ | ✅ | ✅ | 8 个目录 |
| **Rules** | ✅ | ✅ | ✅ | 13 种语言 |
| **Hooks** | ✅ | ❌ | ❌ | 1 个示例 |

### 为什么集成 ECC？

1. **生产级实践**: ECC 在多个生产应用中经过实战测试
2. **完整工作流**: 提供从规划到测试的完整开发工作流
3. **跨工具兼容**: Skills 遵循标准，可在三个工具间共享
4. **持续更新**: 活跃维护，持续改进

## 🎯 集成的组件详解

### 1. Agents（代理）- 仅 Claude Code

**12 个专业代理**，用于委托特定领域的任务：

#### 核心代理（8个）
- **planner** - 实现规划：分析需求，制定实施计划
- **architect** - 系统设计：架构决策，可扩展性设计
- **tdd-guide** - TDD 指导：测试驱动开发工作流
- **code-reviewer** - 代码审查：质量、可维护性审查
- **security-reviewer** - 安全审查：漏洞检测，安全最佳实践
- **build-error-resolver** - 构建修复：解决编译和类型错误
- **doc-updater** - 文档更新：同步代码和文档
- **refactor-cleaner** - 重构清理：移除死代码，优化结构

#### 语言特定代理（4个）
- **typescript-reviewer** - TypeScript/JavaScript 代码审查
- **python-reviewer** - Python 代码审查
- **go-reviewer** - Go 代码审查
- **database-reviewer** - 数据库设计和查询优化

**使用方式**:
```bash
# Claude Code 中使用
/plan "添加用户认证功能"
# 自动调用 planner 代理

/code-review
# 自动调用 code-reviewer 代理
```

---

### 2. Commands（命令）- 三个工具都支持

**15 个核心命令**，提供快速执行的开发任务：

#### 基础工作流（8个）
- **plan** - 功能规划：分析需求，制定实施步骤
- **tdd** - TDD 工作流：编写测试，实现代码，重构
- **code-review** - 代码审查：检查质量、安全、可维护性
- **build-fix** - 修复构建：解决编译错误
- **refactor-clean** - 重构清理：移除死代码
- **docs** - 生成文档：自动生成 API 文档
- **update-docs** - 更新文档：同步代码变更
- **setup-pm** - 配置包管理器：设置 npm/pnpm/yarn/bun

#### 高级功能（7个）
- **e2e** - E2E 测试：生成 Playwright 测试
- **skill-create** - 技能创建：从 git 历史生成技能
- **save-session** - 保存会话：保存当前工作状态
- **resume-session** - 恢复会话：恢复之前的工作
- **learn** - 持续学习：从会话中提取模式
- **checkpoint** - 检查点：保存验证状态
- **verify** - 验证循环：运行验证流程

**使用方式**:
```bash
# Claude Code
/plan "实现用户登录"
/tdd "编写登录测试"

# Windsurf
/plan "实现用户登录"
/tdd "编写登录测试"

# Codex
/plan "实现用户登录"
/tdd "编写登录测试"
```

**与 SDD 命令的关系**:
- **SDD 命令**: 中文名称，专注于规范驱动开发（需求分析、规范编写等）
- **ECC 命令**: 英文名称，专注于代码实现和质量保证
- **无冲突**: 两套命令互补，可同时使用

---

### 3. Skills（技能）- 三个工具都支持

**8 个核心技能目录**，遵循 [Agent Skills 标准](https://agentskills.io)：

#### 开发标准（3个）
- **coding-standards** - 编码标准：不可变性、文件组织、命名规范
- **tdd-workflow** - TDD 方法论：红-绿-重构循环
- **security-review** - 安全检查清单：输入验证、密钥管理

#### 架构模式（2个）
- **backend-patterns** - 后端模式：API 设计、数据库模式、缓存策略
- **frontend-patterns** - 前端模式：React、Next.js 最佳实践

#### 语言特定（2个）
- **golang-patterns** - Go 惯用语和最佳实践
- **golang-testing** - Go 测试模式、基准测试

#### 高级功能（1个）
- **iterative-retrieval** - 渐进式上下文检索：子代理的上下文细化

**Skills 的优势**:
- **标准格式**: 遵循 agentskills.io 标准
- **跨工具兼容**: Claude、Windsurf、Codex 都支持
- **渐进式加载**: 只加载 name/description，完整内容按需加载
- **可扩展**: 可以添加自定义技能

**使用方式**:
```bash
# Claude Code
@coding-standards
@tdd-workflow

# Windsurf
@coding-standards
@tdd-workflow

# Codex
$skill-installer coding-standards
```

---

### 4. Rules（规则）- 三个工具都支持

**13 种语言的规则**，始终遵循的开发指南：

#### 通用规则（common/）- 7 个文件
- **coding-style.md** - 编码风格：不可变性、文件组织、错误处理
- **git-workflow.md** - Git 工作流：提交格式、PR 流程
- **testing.md** - 测试要求：80% 覆盖率、TDD 工作流
- **performance.md** - 性能优化：模型选择、上下文管理
- **patterns.md** - 设计模式：API 响应格式、仓储模式
- **security.md** - 安全检查：密钥管理、输入验证
- **agents.md** - 代理编排：何时委托给子代理

#### 语言特定规则 - 12 种语言
- **typescript/** - TypeScript/JavaScript
- **python/** - Python
- **golang/** - Go
- **cpp/** - C++
- **csharp/** - C#
- **java/** - Java
- **kotlin/** - Kotlin
- **perl/** - Perl
- **php/** - PHP
- **rust/** - Rust
- **swift/** - Swift

每种语言包含 5 个规则文件：
- `coding-style.md` - 语言特定编码风格
- `testing.md` - 测试框架和模式
- `patterns.md` - 语言惯用语和设计模式
- `tools.md` - 推荐工具和库
- `performance.md` - 性能优化技巧

**Rules 的作用**:
- **始终生效**: 在所有对话中自动应用
- **一致性**: 确保代码风格和质量标准统一
- **最佳实践**: 编码、测试、安全的最佳实践

---

### 5. Hooks（钩子）- 仅 Claude Code

**hooks.json** - 基于触发器的自动化配置示例

**功能**:
- 工具事件触发（读取、编辑、运行命令等）
- 自动化检查（console.log 警告、格式化等）
- 会话生命周期管理

**注意**: 作为示例提供，需要手动配置到 `~/.claude/settings.json`

---

## 🏗️ 构建流程

### 构建时集成

在运行 `create-release-packages.sh` 时，ECC 组件会自动集成到对应的 AI 工具包中：

```bash
# 构建所有工具的包
.github/workflows/scripts/create-release-packages.sh v1.5.0

# 只构建特定工具
AGENTS="claude,windsurf,codex" SCRIPTS=sh ./create-release-packages.sh v1.5.0
```

### 生成的包结构

#### Claude Code 包
```
spec-kit-template-claude-sh-1.5.0.zip
├── .specify/
│   ├── memory/
│   ├── scripts/
│   └── templates/
└── .claude/
    ├── agents/              # 🆕 12 个 ECC 代理
    ├── commands/            # SDD 命令 + 15 个 ECC 命令
    ├── skills/              # 🆕 8 个 ECC 技能目录
    ├── rules/               # 🆕 13 种语言的 ECC 规则
    └── hooks-example.json   # 🆕 ECC hooks 示例
```

#### Windsurf 包
```
spec-kit-template-windsurf-sh-1.5.0.zip
├── .specify/
│   ├── memory/
│   ├── scripts/
│   └── templates/
└── .windsurf/
    ├── workflows/           # SDD workflows + 15 个 ECC 命令
    ├── skills/              # 🆕 8 个 ECC 技能目录
    └── rules/               # 🆕 13 种语言的 ECC 规则
```

#### Codex 包
```
spec-kit-template-codex-sh-1.5.0.zip
├── .specify/
│   ├── memory/
│   ├── scripts/
│   └── templates/
└── .codex/
    ├── prompts/             # SDD prompts + 15 个 ECC 命令
    ├── skills/              # 🆕 8 个 ECC 技能目录
    └── rules/               # 🆕 13 种语言的 ECC 规则
```

---

## 📖 使用指南

### 推荐工作流

#### 1. 规范驱动开发（SDD）阶段
使用 Spec Kit 的 SDD 命令：

```bash
/speckit.constitution  # 建立项目原则
/speckit.specify       # 创建基线规范
/speckit.plan          # 创建实施计划
/speckit.tasks         # 生成可执行任务
```

#### 2. 代码实现阶段
使用 ECC 命令：

```bash
/plan "实现用户认证"    # ECC 规划
/tdd "编写登录测试"     # ECC TDD
/code-review           # ECC 代码审查
/build-fix             # ECC 构建修复
```

#### 3. 质量保证阶段
结合使用：

```bash
/speckit.analyze       # SDD 一致性检查
/e2e                   # ECC E2E 测试
/verify                # ECC 验证循环
```

### 技能使用

在需要参考最佳实践时，@mention 技能：

```bash
# 开发前参考
@coding-standards
@tdd-workflow

# 实现时参考
@backend-patterns
@frontend-patterns

# 特定语言
@golang-patterns
```

### 规则应用

规则自动应用，无需手动调用。但可以查看规则文件了解标准：

```bash
# 查看通用规则
cat .claude/rules/common/coding-style.md
cat .claude/rules/common/testing.md

# 查看语言特定规则
cat .claude/rules/typescript/patterns.md
cat .claude/rules/python/testing.md
```

---

## 🔄 维护和更新

### 同步 ECC 更新

建议每季度同步一次 everything-claude-code 的更新：

```bash
# 1. 更新 everything-claude-code
cd /path/to/everything-claude-code
git pull origin main

# 2. 复制更新到 spec-kit-cn
cd /path/to/spec-kit-cn

# 复制 agents
cp /path/to/everything-claude-code/agents/*.md ecc-components/agents/

# 复制 commands
cp /path/to/everything-claude-code/commands/*.md ecc-components/commands/

# 复制 skills
cp -r /path/to/everything-claude-code/skills/* ecc-components/skills/

# 复制 rules
cp -r /path/to/everything-claude-code/rules/* ecc-components/rules/

# 复制 hooks
cp /path/to/everything-claude-code/hooks/hooks.json ecc-components/hooks/

# 3. 重新构建包
.github/workflows/scripts/create-release-packages.sh v1.5.1
```

### 版本追踪

在 `ecc-components/README.md` 中记录：
- ECC 版本号
- 集成日期
- 下次同步日期

---

## 📊 集成统计

### 文件数量
- **Agents**: 12 个文件
- **Commands**: 15 个文件
- **Skills**: 8 个目录（每个包含 SKILL.md + 支持文件）
- **Rules**: 65 个文件（common + 12 种语言）
- **Hooks**: 1 个文件

### 包大小影响
- **Claude Code 包**: 增加约 2-3 MB
- **Windsurf 包**: 增加约 1.5-2 MB
- **Codex 包**: 增加约 1.5-2 MB

---

## 🔗 相关资源

### ECC 项目
- **GitHub**: https://github.com/affaan-m/everything-claude-code
- **精简指南**: https://x.com/affaanmustafa/status/2012378465664745795
- **详细指南**: https://x.com/affaanmustafa/status/2014040193557471352

### Agent Skills 标准
- **官网**: https://agentskills.io
- **规范**: https://agentskills.io/spec

### Spec Kit
- **GitHub**: https://github.com/zhaolei0914/spec-kit-cn
- **文档**: README.md

---

## ⚠️ 注意事项

1. **Agents 限制**: 仅 Claude Code 支持 agents，Windsurf 和 Codex 不支持
2. **命名冲突**: ECC 命令使用英文名，与 SDD 中文命令无冲突
3. **Skills 兼容性**: 三个工具都遵循 Agent Skills 标准，可以共享
4. **Hooks 可选**: Hooks 作为示例提供，需要手动配置
5. **许可证**: ECC 使用 MIT 许可证，与 Spec Kit 兼容

---

## 🎓 学习路径

### 初学者
1. 阅读 ECC 精简指南
2. 尝试基础命令：`/plan`, `/tdd`, `/code-review`
3. 查看 `coding-standards` 技能
4. 阅读 `common/` 规则

### 进阶用户
1. 使用高级命令：`/e2e`, `/save-session`, `/learn`
2. 探索语言特定技能和规则
3. 配置 hooks（Claude Code）
4. 自定义技能

### 团队使用
1. 统一使用 ECC 规则确保代码一致性
2. 共享自定义技能
3. 建立团队级 hooks
4. 定期同步 ECC 更新

---

**集成完成日期**: 2026-03-23  
**ECC 版本**: v1.9.0  
**Spec Kit 版本**: v1.5.0+
