# A. Specify CLI 架构与代码解读

本文只讲 Spec Kit 仓库中的 Python CLI（`specify`）：它如何下载模板、合并到目标目录、以及如何做环境检查。

## 1. 入口与打包

- 包名：`specify-cli`
- Python 版本：`>=3.11`
- 入口命令：
  - `pyproject.toml`：`specify = "specify_cli:main"`

代码位置：

- `src/specify_cli/__init__.py`

## 2. 命令列表（Typer）

- `specify init`
  - 初始化（下载 release 模板 zip + 解压/合并 + 可选 git init）

- `specify check`
  - 检测系统工具与 agent 工具是否存在

- `specify version`
  - 输出版本与系统信息

## 3. init 的主流程（从输入到落盘）

### 3.1 参数与分支

- `project_name` + `--here` 互斥
- `project_name = "."` 等价于 `--here`
- `--force`：当 `--here` 目录非空时跳过确认

### 3.2 选择 agent（`AGENT_CONFIG`）

`AGENT_CONFIG` 定义：

- `name`：展示名
- `folder`：该 agent 在用户项目里的目录前缀
- `install_url`：若需要 CLI 工具，指向安装说明
- `requires_cli`：是否必须检测本地是否安装了该 CLI

`--ai` 未提供时会进入交互选择（readchar + Rich Live）。

### 3.3 选择脚本类型（sh/ps）

- 未指定时默认：Windows -> `ps`，其它 -> `sh`
- 该选择会影响下载哪个 release asset：
  - `spec-kit-template-{ai_assistant}-{script_type}.zip`

### 3.4 GitHub release 拉取与下载

关键函数：

- `download_template_from_github(...)`
  - 调 GitHub API：`/releases/latest`
  - 查找匹配 asset
  - 下载 zip
  - 处理 rate limit（解析 header 并构造更友好错误提示）

- TLS：使用 `truststore` 构建 `ssl_context`。

### 3.5 解压与合并

关键函数：

- `download_and_extract_template(...)`

两种模式：

- 新目录：直接解压到目标目录
- 当前目录（`--here` 或 `.`）：
  - 解压到临时目录
  - 遍历复制/合并到当前目录
  - `.vscode/settings.json` 特殊：走 JSON deep merge

### 3.6 `.vscode/settings.json` 合并策略

关键函数：

- `handle_vscode_settings(...)`
- `merge_json_files(...)`

策略要点：

- 递归合并 dict
- list 与普通值直接替换

此策略与 `templates/vscode-settings.json` 配套，用于把推荐的 prompt files/自动批准脚本写进用户的 VSCode settings。

### 3.7 脚本执行位修复（POSIX）

函数：`ensure_executable_scripts(project_path)`

- 只对 `.specify/scripts/**/*.sh` 生效
- 只给带 shebang 的脚本加执行位
- Windows 下直接跳过

### 3.8 git 初始化

函数：`init_git_repo(project_path)`

- `git init` -> `git add .` -> `git commit ...`
- 若 `--no-git` 或系统无 git，则跳过

## 4. check 命令的定位

`specify check` 主要用于：

- 快速确认 git 是否存在
- 快速确认某些 agent CLI 是否存在（由 `AGENT_CONFIG.requires_cli` 决定）

## 5. 维护建议（针对当前实现形态）

- `src/specify_cli/__init__.py` 是单文件集中式实现，修改前建议：
  - 先写清楚变更会影响哪些外部行为（尤其是 init 的落盘结构与覆盖策略）
  - 避免引入“兼容垫片”式逻辑，优先修正调用点（保持结构清晰）

- 对于依赖 GitHub API 的行为：
  - 企业网络/共享 CI 场景容易触发 rate limit
  - `--github-token` 是推荐的稳定路径
