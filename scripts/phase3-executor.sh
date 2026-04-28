#!/bin/bash
set -e  # 任何命令失败立即退出

echo "=== 阶段 3：初始化项目配置文件 ==="
echo ""

# 步骤 3.1：创建目录结构
echo "▶ 步骤 3.1：创建目录结构"
mkdir -p specs/archived/ docs/ memory/summaries .specify/memory/summaries
echo "✅ 完成"
echo ""

# 步骤 3.2：追加 SKILL.md 项目记忆引用
echo "▶ 步骤 3.2：追加 SKILL.md 项目记忆引用"
SKILL_FILE="__AGENT_SKILLS_DIR__/project-context/SKILL.md"
MARKER="## 项目记忆"

if ! grep -q "^$MARKER" "$SKILL_FILE"; then
  cat >> "$SKILL_FILE" << 'EOF'
---

## 项目记忆

项目开发记忆独立管理，入口文件：[`.specify/memory/MEMORY.md`](../../../.specify/memory/MEMORY.md)

**开发前必须先读取 `.specify/memory/MEMORY.md` 和 `.specify/memory/index.md`**，然后按 MEMORY.md 中的读取协议按需加载对应记忆文件。
EOF
  echo "✅ 已追加项目记忆章节"
else
  echo "⚠️  项目记忆章节已存在，跳过"
fi
echo ""

# 步骤 3.3：确定 CODE_DIRS 变量值
echo "▶ 步骤 3.3：确定 CODE_DIRS 变量值"
CODE_DIRS="src/, .specify/scripts/"
echo "CODE_DIRS=\"$CODE_DIRS\""
echo "✅ 完成"
echo ""

# 步骤 3.4：确保规则文件存在
echo "▶ 步骤 3.4：确保规则文件存在"
RULES_FILE="__AGENT_RULES_FILE__"
if [ ! -f "$RULES_FILE" ]; then
  touch "$RULES_FILE"
  echo "✅ 已创建 $RULES_FILE"
else
  echo "⚠️  $RULES_FILE 已存在"
fi
echo ""

# 步骤 3.5 & 3.6：读取模板并追加到规则文件
echo "▶ 步骤 3.5-3.6：填充模板并追加到规则文件"
TEMPLATE="__AGENT_TEMPLATES_DIR__/AGENT_RULES_FILE.md"
MARKER_RULES="## 语言规范（全局强制）"

if ! grep -q "$MARKER_RULES" "$RULES_FILE"; then
  # 添加分隔注释
  cat >> "$RULES_FILE" << 'EOF'

<!-- ========================================== -->
<!-- 以下内容由 /0-制定项目上下文 自动生成 -->
<!-- ========================================== -->

EOF

  # 替换变量并追加
  sed "s|{{CODE_DIRS}}|$CODE_DIRS|g" "$TEMPLATE" >> "$RULES_FILE"
  echo "✅ 已追加规则到 $RULES_FILE"
else
  echo "⚠️  规则内容已存在，跳过"
fi
echo ""

# 步骤 3.7：确保 .ai-changelogs.md 存在
echo "▶ 步骤 3.7：确保 .ai-changelogs.md 存在"
CHANGELOG_FILE=".ai-changelogs.md"
if [ ! -f "$CHANGELOG_FILE" ]; then
  cp __AGENT_TEMPLATES_DIR__/ai-changelogs.md "$CHANGELOG_FILE"
  echo "✅ 已创建 $CHANGELOG_FILE"
else
  echo "⚠️  $CHANGELOG_FILE 已存在"
fi
echo ""

# 步骤 3.8：确保记忆文件存在
echo "▶ 步骤 3.8：确保记忆文件存在"
test -f .specify/memory/MEMORY.md || cp memory/MEMORY.md .specify/memory/MEMORY.md
test -f .specify/memory/coding-standards.md || cp memory/coding-standards.md .specify/memory/coding-standards.md
test -f .specify/memory/code-patterns.md || cp memory/code-patterns.md .specify/memory/code-patterns.md
echo "✅ 完成"
echo ""
# 步骤 3.9：生成 AGENTS.md 到根目录
echo "▶ 步骤 3.9：生成 AGENTS.md 到根目录"
AGENTS_FILE="AGENTS.md"
AGENTS_TEMPLATE=".specify/templates/AGENTS.md"

if [ ! -f "$AGENTS_FILE" ]; then
  # 获取仓库名（从 git remote 或目录名）
  REPO_NAME=$(git remote get-url origin 2>/dev/null | sed -E 's|.*/([^/]+)(\.git)?$|\1|' || basename "$(pwd)")

  # 替换占位符并生成文件
  sed "s|{{REPO_NAME}}|$REPO_NAME|g" "$AGENTS_TEMPLATE" > "$AGENTS_FILE"
  echo "✅ 已生成 $AGENTS_FILE (仓库名: $REPO_NAME)"
else
  echo "⚠️  $AGENTS_FILE 已存在，跳过"
fi
echo ""

echo "=== 阶段 3 执行完成 ==="
