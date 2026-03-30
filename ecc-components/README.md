# Everything Claude Code (ECC) 集成组件

本目录包含从 [everything-claude-code](https://github.com/affaan-m/everything-claude-code) 项目集成的核心组件，用于增强 Spec Kit 的 AI 辅助开发能力。

## 📦 组件概览

### Agents（代理）- 仅 Claude Code
专业子代理，用于委托特定任务：

- `planner.md` - 功能实现规划
- `architect.md` - 系统设计决策
- `tdd-guide.md` - 测试驱动开发
- `code-reviewer.md` - 代码质量审查
- `security-reviewer.md` - 安全漏洞检测
- `build-error-resolver.md` - 构建错误修复
- `doc-updater.md` - 文档更新
- `refactor-cleaner.md` - 代码重构清理
- `typescript-reviewer.md` - TypeScript 代码审查
- `python-reviewer.md` - Python 代码审查
- `go-reviewer.md` - Go 代码审查
- `database-reviewer.md` - 数据库设计审查

### Commands（命令）- Claude / Windsurf / Codex
快速执行的斜杠命令：

**开发工作流**:
- `plan.md` - 功能规划
- `tdd.md` - TDD 工作流
- `code-review.md` - 代码审查
- `build-fix.md` - 修复构建错误
- `refactor-clean.md` - 重构清理
- `docs.md` - 文档生成
- `update-docs.md` - 更新文档
- `setup-pm.md` - 包管理器配置

**高级功能**:
- `e2e.md` - E2E 测试生成
- `skill-create.md` - 技能创建
- `save-session.md` - 保存会话
- `resume-session.md` - 恢复会话
- `learn.md` - 持续学习
- `checkpoint.md` - 检查点
- `verify.md` - 验证循环

### Skills（技能）- Claude / Windsurf / Codex
多步骤工作流定义（遵循 [agentskills.io](https://agentskills.io) 标准）：

- `coding-standards/` - 编码标准和最佳实践
- `tdd-workflow/` - TDD 方法论
- `security-review/` - 安全检查清单
- `backend-patterns/` - 后端模式（API、数据库）
- `frontend-patterns/` - 前端模式（React、Next.js）
- `golang-patterns/` - Go 惯用语和模式
- `golang-testing/` - Go 测试模式
- `iterative-retrieval/` - 渐进式上下文检索

### Rules（规则）- Claude / Windsurf / Codex
始终遵循的开发指南：

**通用规则（common/）**:
- `coding-style.md` - 编码风格（不可变性、文件组织）
- `git-workflow.md` - Git 工作流和提交规范
- `testing.md` - 测试要求（80% 覆盖率）
- `performance.md` - 性能优化
- `patterns.md` - 设计模式
- `security.md` - 安全检查
- `agents.md` - 代理编排

**语言特定规则**:
- `typescript/` - TypeScript/JavaScript
- `python/` - Python
- `golang/` - Go
- `cpp/` - C++
- `csharp/` - C#
- `java/` - Java
- `kotlin/` - Kotlin
- `perl/` - Perl
- `php/` - PHP
- `rust/` - Rust
- `swift/` - Swift

### Hooks（钩子）- 仅 Claude Code
基于触发器的自动化：

- `hooks.json` - Claude Code hooks 配置示例

## 🎯 集成方式

### 构建时集成
这些组件在构建 Spec Kit 模板包时自动集成到对应的 AI 工具目录中：

**Claude Code**:
```
.claude/
├── agents/          ← ECC agents
├── commands/        ← SDD commands + ECC commands
├── skills/          ← ECC skills
├── rules/           ← ECC rules
└── hooks-example.json  ← ECC hooks 示例
```

**Windsurf**:
```
.windsurf/
├── workflows/       ← SDD workflows + ECC commands
├── skills/          ← ECC skills
└── rules/           ← ECC rules
```

**Codex**:
```
.codex/
├── prompts/         ← SDD prompts + ECC commands
├── skills/          ← ECC skills
└── rules/           ← ECC rules
```

## 📚 使用说明

### Claude Code
```bash
# 使用代理
/plan "添加用户认证功能"
/tdd "实现登录接口"
/code-review

# 查看技能
@coding-standards
@tdd-workflow
```

### Windsurf
```bash
# 使用 workflows
/plan "添加用户认证功能"
/tdd "实现登录接口"

# 使用技能
@coding-standards
@tdd-workflow
```

### Codex
```bash
# 使用 prompts
/plan "添加用户认证功能"
/tdd "实现登录接口"

# 使用技能
$skill-installer coding-standards
```

## 🔄 更新维护

### 同步 ECC 更新
定期从 everything-claude-code 同步更新：

```bash
# 1. 进入 everything-claude-code 目录
cd /path/to/everything-claude-code
git pull

# 2. 复制更新的组件到 spec-kit-cn
cp agents/*.md /path/to/spec-kit-cn/ecc-components/agents/
cp commands/*.md /path/to/spec-kit-cn/ecc-components/commands/
cp -r skills/* /path/to/spec-kit-cn/ecc-components/skills/
cp -r rules/* /path/to/spec-kit-cn/ecc-components/rules/
```

### 版本管理
- ECC 组件版本: 基于 everything-claude-code v1.9.0
- 集成日期: 2026-03-23
- 下次同步: 建议每季度同步一次

## 📄 许可证

这些组件来自 [everything-claude-code](https://github.com/affaan-m/everything-claude-code)，遵循 MIT 许可证。

## 🔗 相关链接

- **ECC 项目**: https://github.com/affaan-m/everything-claude-code
- **Agent Skills 标准**: https://agentskills.io
- **ECC 精简指南**: https://x.com/affaanmustafa/status/2012378465664745795
- **ECC 详细指南**: https://x.com/affaanmustafa/status/2014040193557471352

## ⚠️ 注意事项

1. **Agents 仅限 Claude Code**: Windsurf 和 Codex 不支持 agents 概念
2. **Skills 跨工具兼容**: 三个工具都遵循 Agent Skills 标准
3. **命令名称**: ECC 命令使用英文名，与 SDD 中文命令无冲突
4. **Hooks 可选**: 仅 Claude Code 和 Windsurf 支持 hooks

## 🎓 学习资源

建议按以下顺序学习 ECC 组件：

1. **阅读 ECC 精简指南** - 了解核心概念
2. **尝试基础命令** - `/plan`, `/tdd`, `/code-review`
3. **探索技能库** - `@coding-standards`, `@tdd-workflow`
4. **应用规则** - 查看 `rules/common/` 了解开发原则
5. **使用代理**（Claude）- 委托复杂任务给专业代理
