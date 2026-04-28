# AGENTS.md

<!-- gitnexus:start -->
# GitNexus — 代码智能

使用 GitNexus MCP 工具来理解代码、评估影响并安全导航。

> **注意**：本文档中的 GitNexus 工具名称使用 Windsurf 的命名约定（`mcp2_*` 前缀）。如果您使用其他 IDE（如 Claude Desktop、Cursor），工具名称可能不同（如 `query` 而不是 `mcp2_query`），请根据您的 IDE 调整工具名称。

> 如果任何 GitNexus 工具警告索引已过时，请联系管理员重新索引仓库。

## 必须做的

- **在编辑任何符号之前必须运行影响分析。** 在修改函数、类或方法之前，运行 `mcp2_impact({target: "symbolName", direction: "upstream", repo: "{{REPO_NAME}}"})` 并向用户报告爆炸半径（直接调用者、受影响的进程、风险级别）。
- **在提交之前必须运行 `mcp2_detect_changes()`** 以验证您的更改仅影响预期的符号和执行流。
- **如果影响分析返回高或严重风险，必须警告用户**，然后再继续编辑。
- 探索不熟悉的代码时，使用 `mcp2_query({repo: "{{REPO_NAME}}", query: "concept"})` 查找执行流，而不是 grep。它返回按相关性排名的进程分组结果。
- 当您需要特定符号的完整上下文——调用者、被调用者、它参与的执行流——使用 `mcp2_context({name: "symbolName", repo: "{{REPO_NAME}}"})`。

## 调试时

1. `mcp2_query({repo: "{{REPO_NAME}}", query: "<错误或症状>"})` — 查找与问题相关的执行流
2. `mcp2_context({name: "<可疑函数>", repo: "{{REPO_NAME}}"})` — 查看所有调用者、被调用者和进程参与
3. 使用 Cypher 查询深入分析：`mcp2_cypher({repo: "{{REPO_NAME}}", query: "MATCH (n) WHERE n.name = 'symbolName' RETURN n"})`
4. 对于回归：`mcp2_detect_changes({repo: "{{REPO_NAME}}"})` — 查看您的更改影响

## 重构时

- **重命名**：必须首先使用 `mcp2_rename({new_name: "newName", old_name: "oldName", repo: "{{REPO_NAME}}", dry_run: true})`。查看预览——图编辑是安全的，text_search 编辑需要手动审查。然后使用 `dry_run: false` 运行。
- **提取/拆分**：必须运行 `mcp2_context({name: "target", repo: "{{REPO_NAME}}"})` 以查看所有传入/传出引用，然后运行 `mcp2_impact({target: "target", direction: "upstream", repo: "{{REPO_NAME}}"})` 以在移动代码之前查找所有外部调用者。
- 任何重构后：运行 `mcp2_detect_changes({repo: "{{REPO_NAME}}"})` 以验证仅更改了预期的文件。

## 绝不做

- 绝不在不先对其运行 `mcp2_impact` 的情况下编辑函数、类或方法。
- 绝不忽略影响分析的高或严重风险警告。
- 绝不使用查找和替换重命名符号——使用理解调用图的 `mcp2_rename`。
- 绝不在不运行 `mcp2_detect_changes()` 检查受影响范围的情况下提交更改。

## 工具快速参考

| 工具 | 何时使用 | 命令 |
|------|---------|------|
| `mcp2_query` | 按概念查找代码 | `mcp2_query({repo: "{{REPO_NAME}}", query: "auth validation"})` |
| `mcp2_context` | 一个符号的 360 度视图 | `mcp2_context({name: "validateUser", repo: "{{REPO_NAME}}"})` |
| `mcp2_impact` | 编辑前的爆炸半径 | `mcp2_impact({target: "X", direction: "upstream", repo: "{{REPO_NAME}}"})` |
| `mcp2_detect_changes` | 提交前范围检查 | `mcp2_detect_changes({repo: "{{REPO_NAME}}"})` |
| `mcp2_rename` | 安全的多文件重命名 | `mcp2_rename({new_name: "new", old_name: "old", repo: "{{REPO_NAME}}", dry_run: true})` |
| `mcp2_cypher` | 自定义图查询 | `mcp2_cypher({repo: "{{REPO_NAME}}", query: "MATCH ..."})` |

## 影响风险级别

| 深度 | 含义 | 操作 |
|------|------|------|
| d=1 | 将会破坏——直接调用者/导入者 | 必须更新这些 |
| d=2 | 可能受影响——间接依赖 | 应该测试 |
| d=3 | 可能需要测试——传递性 | 如果是关键路径则测试 |

## 常用查询

| 用途 | MCP 工具调用 |
|------|-------------|
| 代码库概述，检查索引新鲜度 | `mcp2_get_context_files({repo_name: "{{REPO_NAME}}"})` |
| 查找所有功能区域 | `mcp2_query({repo: "{{REPO_NAME}}", query: "clusters"})` |
| 查看所有执行流 | `mcp2_query({repo: "{{REPO_NAME}}", query: "processes"})` |
| 追踪特定执行流 | `mcp2_context({name: "processName", repo: "{{REPO_NAME}}"})` |
| 列出所有已索引仓库 | `mcp2_list_repos()` |

## 完成前自检

在完成任何代码修改任务之前，验证：
1. 为所有修改的符号运行了 `mcp2_impact`
2. 没有忽略高/严重风险警告
3. `mcp2_detect_changes()` 确认更改与预期范围匹配
4. 所有 d=1（将会破坏）依赖项已更新

## 保持索引新鲜

提交代码更改后，GitNexus 索引变得过时。重新运行 analyze 以更新它：

```bash
npx gitnexus analyze
```

如果索引之前包含嵌入，请通过添加 `--embeddings` 来保留它们：

```bash
npx gitnexus analyze --embeddings
```

要检查嵌入是否存在，请检查 `.gitnexus/meta.json` — `stats.embeddings` 字段显示计数（0 表示没有嵌入）。**在没有 `--embeddings` 的情况下运行 analyze 将删除任何先前生成的嵌入。**

> Claude Code 用户：PostToolUse 钩子在 `git commit` 和 `git merge` 后自动处理此操作。

## CLI

| 任务 | 阅读此技能文件 |
|------|---------------|
| 理解架构 / "X 如何工作？" | `.windsurf/skills/gitnexus-exploring/SKILL.md` |
| 爆炸半径 / "如果我更改 X 会破坏什么？" | `.windsurf/skills/gitnexus-impact-analysis/SKILL.md` |
| 跟踪错误 / "为什么 X 失败？" | `.windsurf/skills/gitnexus-debugging/SKILL.md` |
| 重命名 / 提取 / 拆分 / 重构 | `.windsurf/skills/gitnexus-refactoring/SKILL.md` |
| 工具、资源、模式参考 | `.windsurf/skills/gitnexus-guide/SKILL.md` |
| 索引、状态、清理、wiki CLI 命令 | `.windsurf/skills/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
