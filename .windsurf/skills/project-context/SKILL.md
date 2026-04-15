---
name: specify-cn-cli-context
description: specify-cn-cli 项目的技术栈、结构、方案、规范和环境上下文
version: 1.1.0
updated: 2026-04-14
---

# specify-cn-cli 项目上下文

> <div align="center"> <img src="./media/logo_small.webp" alt="Spec Kit Logo"/> <h1>🌱 Spec Kit CN</h1> <h3><em>更快地构建高质量软件. </em></h3> </div>

---

## 一、技术栈上下文（用什么技术？）

### 编程语言

| 语言 | 文件数 | 占比 |
|------|--------|------|
| **Shell/Bash** | 12 | 67% |
| **PowerShell** | 5 | 28% |
| **Python** | 1 | 6% |

### 框架

- **CLI 框架**: Typer (命令行接口)
- **UI 框架**: Rich (终端 UI 和格式化输出)
- **HTTP 客户端**: httpx (支持 SOCKS 代理)

### 中间件与数据存储

- **无持久化存储**: 项目为 CLI 工具，不依赖数据库或缓存
- **文件系统**: 使用 platformdirs 管理跨平台配置目录
- **TLS/SSL**: truststore (>=0.10.4) 用于安全 HTTPS 连接

### 构建与工具链

- **构建**: Python, Hatch, pip
- **CI/CD**: GitHub Actions

### 版本约束

- **Python**: `>=3.11`
- **项目版本**: `0.0.92`

---

## 二、项目结构上下文（代码怎么组织？）

### 整体架构

**架构类型**: CLI 工具 / 库

单体 CLI 应用，核心逻辑集中在 `src/specify_cli/__init__.py`。通过 Typer 框架提供命令行接口，使用 Rich 进行终端交互和输出格式化。项目采用脚本驱动架构，Shell/PowerShell 脚本负责项目初始化和模板生成，Python CLI 作为统一入口点。

### 目录结构

```
specify-cn-cli/
├── AGENTS.md
├── CHANGELOG.md
├── CLAUDE.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── SECURITY.md
├── SUPPORT.md
├── TERMINOLOGY.md
├── TRANSLATION_STANDARDS.md
├── pyproject.toml
├── spec-driven.md
├── docs/              # 文档
├── media/             # 媒体资源
├── memory/            # 项目记忆
├── scripts/           # 分析/生成脚本
├── src/               # 核心源代码
├── templates/         # 模板文件
```

### 功能模块映射

物理目录与功能职责的对应关系：

| 目录 | 功能聚类 | 核心职责 | 文件数 |
|------|----------|----------|--------|
| `src/` | specify-cli | Specify_cli | 1 |

> 注：聚类名（如 Analyzer, Generator）是 GitNexus 根据代码调用关系自动识别的功能模块，详见各模块详情文件（`analyzer.md`, `generator.md` 等）

---

## 三、技术方案上下文（业务怎么实现？）

技术方案详情见各模块文件（入口点、执行流、关键符号）：

- `specify-cli.md` — Specify_cli — 5 入口点, 11 执行流

### 核心业务流程

**项目初始化流程** (`init` 命令):
1. 检查 Git 仓库状态 (`is_git_repo`) → 如无则初始化 (`init_git_repo`)
2. AI 助手选择 → 交互式选择面板 (`create_selection_panel` + `get_key`)
3. 下载模板 (`download_and_extract_template`) → 检查 GitHub API 速率限制 (`_parse_rate_limit_headers`)
4. 生成 Agent 特定文件 → 处理 VS Code 设置 (`handle_vscode_settings` + `deep_merge`)
5. 设置脚本可执行权限 (`ensure_executable_scripts`)
6. 刷新上下文 (`_maybe_refresh`)

**版本检查流程** (`version` 命令):
1. 获取 GitHub Token (`_github_token`)
2. 查询最新版本 → 比较本地版本
3. 显示更新提示

### 设计模式与架构决策

- **命令模式**: Typer 框架实现 CLI 子命令 (`init`, `check`, `version`, `add`)
- **模板方法模式**: 多 Agent 支持通过统一模板生成不同格式的命令文件
- **策略模式**: 根据 Agent 类型 (Claude, Gemini, Copilot 等) 选择不同的文件生成策略
- **工具类模式**: `StepTracker` 和 `BannerGroup` 提供可复用的 UI 组件
- **配置驱动**: `AGENT_CONFIG` 字典作为单一数据源，消除硬编码

---

## 四、开发规范上下文（代码怎么写才合规？）

### 项目核心原则

1. **多 Agent 支持**: 支持 15+ AI 编码助手，统一工作流，灵活选择工具
2. **规范驱动开发 (SDD)**: 先写规范后编码，通过模板和工作流引导团队
3. **CLI 优先**: 所有功能通过命令行暴露，支持自动化和脚本集成
4. **跨平台兼容**: 同时提供 Bash 和 PowerShell 脚本，支持 Linux/macOS/Windows
5. **用户体验**: 使用 Rich 提供美观的终端 UI，交互式选择面板提升易用性
6. **配置即代码**: 使用 `AGENT_CONFIG` 作为单一数据源，避免特殊情况映射

### 命名规范

- **函数/方法**: `snake_case`
  — 如 `get_key`, `select_with_arrows`, `show_banner`, `callback`, `run_command`
- **类名**: `PascalCase`
  — 如 `StepTracker`, `BannerGroup`
- **文件名**: `kebab-case`
- **常量**: `UPPER_SNAKE_CASE`

- **脚本文件**: `kebab-case.sh` / `kebab-case.ps1`
- **模板目录**: `.agent-name/` (小写，带点前缀)
- **环境变量**: `UPPER_SNAKE_CASE` (如 `GH_TOKEN`, `GITHUB_TOKEN`)

### 代码风格

- **缩进**: 4 空格缩进
- **文档注释**: Google 风格
- **导入**: 绝对导入为主
- **日志**: `console.*()`
- **错误处理**: `raise` (5处), `try/except` (4处)

- **终端输出**: 使用 `console.print()` 而非 `print()`，支持 Rich 格式化
- **路径处理**: 使用 `Path` 对象而非字符串拼接
- **类型提示**: 函数参数使用类型注解 (Typer 要求)
- **字符串**: 优先使用 f-string 格式化

### 禁止规则

- ❌ **禁止使用 `print()`**: 必须使用 `console.print()` 以保持输出格式一致
- ❌ **禁止硬编码 Agent 映射**: 使用 `AGENT_CONFIG` 字典，避免特殊情况逻辑
- ❌ **禁止裸 `except`**: 必须捕获具体异常类型
- ❌ **禁止 `import *`**: 必须显式导入
- ❌ **禁止硬编码路径**: 使用 `platformdirs` 获取跨平台配置目录

### 错误处理

- **异常传播**: 使用 `raise` (5 处) 向上传播错误
- **异常捕获**: 使用 `try/except` (4 处) 处理可恢复错误
- **用户友好提示**: 错误信息使用 Rich 格式化 (`[red]Error:[/red]`)
- **退出码**: CLI 命令失败时返回非零退出码
- **网络错误**: HTTP 请求失败时显示详细错误信息和重试建议

---

## API 规范

**外部 API 调用**:

- **GitHub API**: 用于下载模板和检查版本
  - 认证: `GH_TOKEN` 或 `GITHUB_TOKEN` 环境变量
  - 速率限制: 自动检测并显示剩余配额
  - 端点: `https://api.github.com/repos/{owner}/{repo}/releases`

**CLI 接口**:

- **命令格式**: `specify-cn <command> [options]`
- **子命令**: `init`, `check`, `version`, `add`
- **选项**: 使用 `--` 前缀 (如 `--ai`, `--path`)

## 测试规范

TODO(LLM_TEST_SPEC): 项目当前无测试代码，建议添加：
- 测试框架: pytest
- 单元测试: 测试核心函数 (如 `is_git_repo`, `check_tool`)
- 集成测试: 测试完整 CLI 命令流程
- Mock 策略: Mock GitHub API 调用和文件系统操作

---

## 五、环境与配置上下文（运行依赖什么？）

### 配置文件

- `pyproject.toml`

### 环境变量

**代码中使用的环境变量**:

- `AGENTS`
- `GH_TOKEN`
- `GITHUB_TOKEN`
- `SCRIPTS`
- `SPECIFY_FEATURE`
- `exit_code`


### 部署方式

- **CI/CD**: GitHub Actions

**安装方式**:
```bash
pip install specify-cn-cli
```

**运行命令**:
```bash
specify-cn init --ai <agent-name>
specify-cn check
specify-cn version
specify-cn add <feature-name>
```

**发布流程**:
1. 更新 `pyproject.toml` 版本号
2. 更新 `CHANGELOG.md`
3. GitHub Actions 自动构建和发布到 PyPI
4. 生成多 Agent 模板包 (ZIP 格式)

---

## 附录：模块详情导航

GitNexus 已识别出 1 个功能模块（如 specify-cli, ...），
详见 `index.yaml` 或各模块 `.md` 文件（入口点、执行流、关键符号等详情）。
