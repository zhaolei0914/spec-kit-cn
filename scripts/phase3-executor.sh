#!/bin/bash
set -e  # 任何命令失败立即退出

echo "=== 阶段 3：初始化项目配置文件 ==="
echo ""

# 步骤 3.0：前置检查与文件复制（从阶段 1 步骤 5 移入）
echo "▶ 步骤 3.0：前置检查与文件复制"

# 检测 .specify/skills/ 下是否有项目 SKILL.md
if [ -d ".specify/skills" ]; then
  # 查找第一个 SKILL.md 文件
  SKILL_SOURCE=$(find .specify/skills -name "SKILL.md" -type f | head -1)

  if [ -n "$SKILL_SOURCE" ]; then
    echo "  发现源文件: $SKILL_SOURCE"

    # 创建目标目录
    mkdir -p __AGENT_SKILLS_DIR__/project-context

    # 复制 SKILL.md
    cp "$SKILL_SOURCE" __AGENT_SKILLS_DIR__/project-context/SKILL.md
    echo "  ✅ 已复制到 __AGENT_SKILLS_DIR__/project-context/SKILL.md"

    # 修改 name 字段为 project-context
    sed -i '1,10s/^name: .*/name: project-context/' __AGENT_SKILLS_DIR__/project-context/SKILL.md
    echo "  ✅ 已修改 name 字段"

    # 删除临时目录
    rm -rf .specify/skills
    echo "  ✅ 已清理临时目录"
  else
    echo "  ⚠️  .specify/skills/ 目录存在但未找到 SKILL.md，跳过复制"
  fi
else
  echo "  ℹ️  .specify/skills/ 不存在，跳过复制（可能已在之前执行过）"
fi

# 验证 SKILL.md 是否存在
if [ ! -f "__AGENT_SKILLS_DIR__/project-context/SKILL.md" ]; then
  echo ""
  echo "❌ 错误：SKILL.md 文件不存在"
  echo "   期望位置: __AGENT_SKILLS_DIR__/project-context/SKILL.md"
  echo ""
  echo "可能原因："
  echo "  1. 阶段 1 的 GitNexus 分析未成功生成 SKILL.md"
  echo "  2. fetch_context.py 下载失败"
  echo "  3. 文件已被手动删除"
  echo ""
  echo "解决方案："
  echo "  请重新执行 /0-制定项目上下文1 命令的阶段 1"
  exit 1
fi

echo "  ✅ 验证通过: SKILL.md 文件存在"
echo "✅ 完成"
echo ""

# 步骤 3.1：创建目录结构
echo "▶ 步骤 3.1：创建目录结构"
mkdir -p specs/archived/ docs/ .specify/memory/summaries
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
