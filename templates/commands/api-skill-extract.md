---
description: 从业务代码抽取对外 API 接口信息，生成供其他服务对接使用的 Skill 文档
---

## 用户输入

```text
$ARGUMENTS
```

**参数说明**（均为可选）：
- 第一个参数：服务源码目录（可选，自动检测 `src/` 下的服务目录）
- `--output` 或 `-o`：输出目录（可选，默认 `.windsurf/skills/api-external/`）
- `--service-name`：服务名称（可选，自动检测）
- `--base-url`：API 基础路径（可选，自动检测）

---

## 执行步骤

### 步骤 1：自动检测源码目录

如果用户未指定源码目录，自动检测：

1. 查找 `src/` 目录下包含 `urls.py` 的服务目录（Django）
2. 或查找包含 `@app.route` / `@app.get` 的目录（Flask/FastAPI）

```bash
# 查找 Django 服务目录
find src/ -name "urls.py" -type f 2>/dev/null | head -5

# 查找 Flask/FastAPI 服务目录
grep -rl "@app\.\(route\|get\|post\)" src/ --include="*.py" 2>/dev/null | head -5
```

从结果中确定 `SOURCE_DIR`（取包含路由文件的最上层服务目录）。

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

### 步骤 3：运行 API Skill 生成工具

// turbo
```bash
python .specify/scripts/python/main.py api-skill \
  --skeleton .specify/scripts/python/cache/project_skeleton.json \
  --output {OUTPUT_DIR}
```

**默认值**：
- `OUTPUT_DIR`：`.windsurf/skills/api-external/`

**可选参数**：
- 如果用户指定了服务名称：添加 `--service-name "{SERVICE_NAME}"`
- 如果用户指定了基础路径：添加 `--base-url "{BASE_URL}"`

### 步骤 4：验证输出

检查生成的文件结构：
```
{OUTPUT_DIR}/
├── SKILL.md              (符合 Anthropic Agent Skills 最佳实践)
├── api-spec.json         (结构化 API 规范)
└── endpoints/            (每个接口一个文件)
    ├── get_upgrade_v1_jobs.md
    └── ...
```

### 步骤 4：输出摘要

向用户报告：
- 检测到的框架
- 发现的 API 端点数量
- 生成的文件总数
- SKILL.md 符合 Anthropic Agent Skills 最佳实践

---

## 生成的 Skill 特点

符合 **Anthropic Agent Skills 最佳实践**：

| 最佳实践 | 实现 |
|----------|------|
| **name** (64字符限制) | 服务名称转小写连字符 |
| **description** (200字符限制) | 说明何时使用此 Skill |
| **Keep it focused** | 每个接口一个独立文件 |
| **Use examples** | 包含使用示例 |
| **When to Apply** | "何时使用"章节 |
| **Progressive disclosure** | SKILL.md → endpoints/*.md |

---

## 输出文件说明

### SKILL.md

API Skill 主文档，包含：
- **何时使用**章节
- 服务概述
- 认证方式
- API 分组导航
- **使用示例**

### api-spec.json

结构化 API 规范，可用于：
- 自动生成客户端代码
- API 测试工具导入
- 服务间对接

### endpoints/*.md

按模块分组的 API 详情，包含：
- 请求参数表格
- 响应结构
- 源码位置

---

## 支持的框架

| 框架 | 路由检测 | Handler 检测 |
|------|----------|-------------|
| **Django** | `url()`, `path()` | View 类 |
| **Flask** | `@app.route()` | 函数 |
| **FastAPI** | `@app.get()` 等 | 函数 |

---

## 使用示例

### 基本用法

```
/api-skill-extract src/v7tov8Service
```

### 指定输出目录

```
/api-skill-extract src/v7tov8Service --output .windsurf/skills/upgrade-api/
```

### 指定服务名称

```
/api-skill-extract src/v7tov8Service --service-name "升级服务"
```

---

## 其他服务对接

生成 API Skill 后，其他服务开发时可以这样使用：

```
请帮我调用 v7tov8Service 的"查看作业列表"接口，
参考 .windsurf/skills/api-external/SKILL.md
```

AI 将自动读取 API Skill 并生成符合规范的调用代码。
