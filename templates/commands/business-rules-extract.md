---
description: 从业务代码抽取业务规则，生成业务规则 Skill 文档
---

## 用户输入

```text
$ARGUMENTS
```

**参数说明**（均为可选）：
- 第一个参数：服务源码目录（可选，自动检测 `src/` 下的服务目录）
- `--output` 或 `-o`：输出目录（可选，默认 `__AGENT_SKILLS_DIR__/business-rules/`）

---

## 执行步骤

### 步骤 1：自动检测源码目录

如果用户未指定源码目录，自动检测：

```bash
# 查找包含 models.py 的服务目录
find src/ -name "models.py" -type f 2>/dev/null | head -5
```

从结果中确定 `SOURCE_DIR`（取包含 models.py 的最上层服务目录）。

### 步骤 2：确保骨架数据存在

首先检查骨架数据是否存在，如果不存在则先生成：

```bash
# 检查骨架数据是否存在
if [ ! -f ".specify/scripts/python/cache/project_skeleton.json" ]; then
  echo "骨架数据不存在，先运行 analyze 命令..."
fi
```

如果骨架数据不存在，运行：

// turbo
```bash
python .specify/scripts/python/main.py analyze \
  --source {SOURCE_DIR} \
  --output .specify/scripts/python/cache/project_skeleton.json
```

### 步骤 3：运行业务规则生成工具

// turbo
```bash
python .specify/scripts/python/main.py business-rules \
  --skeleton .specify/scripts/python/cache/project_skeleton.json \
  --output {OUTPUT_DIR}
```

**默认值**：
- `OUTPUT_DIR`：`__AGENT_SKILLS_DIR__/business-rules/`

### 步骤 4：验证输出

检查生成的文件结构：
```
{OUTPUT_DIR}/
├── SKILL.md              (符合 Anthropic Agent Skills 最佳实践)
├── BUSINESS_RULES.md     (入口索引)
├── api/                  (每个 API 一个文件)
│   ├── job_list_view.md
│   └── ...
└── handler/              (每个 Handler 一个文件)
    ├── data_for_a_m_s_handler_base.md
    └── ...
```

### 步骤 4：输出摘要

向用户报告：
- 发现的 API 入口数量
- 发现的 Handler 入口数量
- 生成的文件总数
- SKILL.md 符合 Anthropic Agent Skills 最佳实践

---

## 生成的 Skill 特点

符合 **Anthropic Agent Skills 最佳实践**：

| 最佳实践 | 实现 |
|----------|------|
| **name** (64字符限制) | "business-rules" |
| **description** (200字符限制) | 说明何时使用此 Skill |
| **Keep it focused** | 每个入口一个独立文件 |
| **Use examples** | 包含使用示例 |
| **When to Apply** | "何时使用"章节 |
| **Progressive disclosure** | SKILL.md → BUSINESS_RULES.md → 单文件 |
