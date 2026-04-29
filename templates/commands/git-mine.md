---
description: "从 Git 历史中深度提取编码规范、设计决策、已知陷阱等知识到 Memory 文件"
---

## Git 历史知识挖掘

**前置条件**：项目必须已执行 `/0-制定项目上下文1` 命令的阶段 4。

---

## 步骤 1：查看提交摘要

```bash
cat .specify/memory/git-commits/summary.md
```

这个文件包含：
- 所有提交的优先级排序表格
- 高/中/低优先级统计
- 分析建议

---

## 步骤 2：分析高优先级提交

根据摘要表格，找到所有 🔴 高优先级提交，逐个打开详情文件：

```bash
cat .specify/memory/git-commits/details/commit-<hash>.md
```

每个详情文件包含：
- 基本信息（hash, author, date, message）
- 统计信息（文件数、行数）
- 修改的文件列表
- Diff（限制 200 行）
- 分析建议模板

---

## 步骤 3：提取知识到 Memory 文件

对于每个值得提取的提交，根据分类追加到对应的 Memory 文件：

### 编码规范类 → `.specify/memory/coding-standards.md`

```markdown
## 从 Git 历史中提取的编码规范

### CS-{commit_hash}: {summary}
- **来源**: Commit {commit_hash} by {author}
- **日期**: {date}
- **类别**: {category}
- **说明**: {details}
- **相关文件**: {changed_files}

---
```

### 设计决策类 → `.specify/memory/design-decisions.md`

```markdown
## 从 Git 历史中提取的设计决策

### DD-{commit_hash}: {title}
- **来源**: Commit {commit_hash} by {author}
- **日期**: {date}
- **做了什么**: {what}
- **为什么**: {why}
- **替代方案**: {alternatives}
- **选择理由**: {rationale}
- **相关文件**: {changed_files}

---
```

### Bug 修复类 → `.specify/memory/known-pitfalls.md`

```markdown
## 从 Git 历史中提取的已知陷阱

### KP-{commit_hash}: {title}
- **来源**: Commit {commit_hash} by {author}
- **日期**: {date}
- **根本原因**: {root_cause}
- **解决方案**: {solution}
- **如何避免**: {prevention}
- **相关文件**: {changed_files}

---
```

---

## 步骤 4：输出统计

完成后输出统计信息：

```
✅ Git 历史记忆提取完成！

📊 提取统计：
  - 编码规范: X 条 → .specify/memory/coding-standards.md
  - 设计决策: X 条 → .specify/memory/design-decisions.md
  - 已知陷阱: X 条 → .specify/memory/known-pitfalls.md

💡 建议：
  - 人工审核提取的知识，补充缺失的上下文
  - 定期运行 /git-mine 保持 Memory 最新
```

---

## 分析提示

**高优先级提交**（🔴）：
- 大型重构（文件数 ≥ 5 或行数 ≥ 100）
- 包含关键词：refactor, 重构, 架构, architecture, breaking

**中优先级提交**（🟡）：
- 重要功能或 Bug 修复（文件数 ≥ 3 或行数 ≥ 50）
- 包含关键词：fix, 修复, bug, feature, 功能

**低优先级提交**（⚪）：
- 小改动、文档更新、配置调整
- 可以跳过

---

## 注意事项

1. **优先分析高优先级**：工具已经预筛选出重要提交
2. **Diff 已限制长度**：每个提交最多显示 200 行 diff
3. **文件已准备好**：不需要执行 git 命令，直接读取文件即可
4. **可以分批处理**：不需要一次性分析所有提交
