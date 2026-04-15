---
version: 1.0.0
updated: YYYY-MM-DD
---

# 项目上下文

> 本文档由 `/0-制定项目上下文` 自动生成，作为 AI 开发代理的项目知识库。

## 项目概述

**项目名称**：{{PROJECT_NAME}}

**项目描述**：{{PROJECT_DESCRIPTION}}
<!-- 填充指导: 一句话描述项目目标和用途（20-50字） -->

**项目类型**：{{PROJECT_TYPE}}

---

## 技术栈

### 编程语言

{{LLM_LANGUAGE}}
<!-- 填充指导: 从 .context-facts.json 的 project_facts.language 读取，或从代码文件扩展名推断 -->

### 框架与库

{{LLM_FRAMEWORKS}}
<!-- 填充指导: 读取 .context-facts.json 中 project_facts.frameworks；如为空，抽样读取核心文件的 import 语句识别框架 -->

### 数据库与中间件

{{LLM_MIDDLEWARE}}
<!-- 填充指导: 读取 project_facts.middleware；如为空，检查配置文件中的数据库/缓存/消息队列连接配置 -->

### 版本信息

{{LLM_VERSIONS}}
<!-- 填充指导: 读取 project_facts.versions；如为空，检查 Dockerfile、CI 配置中的版本信息 -->

---

## 架构

{{LLM_ARCHITECTURE}}
<!-- 填充指导: 判断整体架构类型：微服务/单体/前后端分离/monorepo/CLI/库，加 1-2 句描述 -->

{{LLM_ARCHITECTURE_DETAIL}}
<!-- 填充指导: 补充分层方式和模块职责描述（1-2 句）。无补充则删除此占位符 -->

### 目录结构

{{LLM_DIRECTORY_STRUCTURE}}
<!-- 填充指导: 列出核心目录及其职责，格式：`dir/` — 职责说明 -->

---

## 核心入口点

| 入口 | 类型 | 描述 |
|------|------|------|
| {{LLM_ENTRY_POINTS}} | | |
<!-- 填充指导: 从 .context-facts.json 的 entry_points 读取，或从 main()、路由配置等识别。格式：每行一个入口 -->

---

## 业务流程

{{LLM_BUSINESS_FLOWS}}
<!-- 填充指导: 选取 top 3-5 入口函数，读取源代码，用自然语言描述核心业务流程（格式：步骤A → 步骤B → 步骤C） -->

---

## 设计模式

{{LLM_DESIGN_PATTERNS}}
<!-- 填充指导: 从 code_patterns.naming.class_examples 识别模式类名（Factory、Strategy、Handler、Observer 等），列出设计模式 + 具体类名 -->

---

## 核心原则

{{LLM_CORE_PRINCIPLES}}
<!-- 填充指导: 新项目 → 引导用户填写；已有代码 → 从代码推断隐含原则（测试风格、模块组织、错误处理方式等）。格式：1. **原则名**: 描述 -->

---

## 开发规范

### 命名规范

{{LLM_NAMING_CONVENTIONS}}
<!-- 填充指导: 抽样读取 5-10 个核心文件，提炼函数/变量/类名/文件名/常量的命名风格，给出具体示例 -->

{{LLM_NAMING_EXTRA}}
<!-- 填充指导: 补充遗漏：API 路径前缀、数据库表名规范、CLI 命令名规范等。无遗漏则删除此占位符 -->

### 代码风格

{{LLM_CODE_STYLE}}
<!-- 填充指导: 从代码和配置中提炼：缩进、注释格式、异常处理、日志规范、导入顺序 -->

{{LLM_CODE_STYLE_EXTRA}}
<!-- 填充指导: 补充遗漏：行长度限制、引号风格、末尾逗号规范等。无遗漏则删除此占位符 -->

### 禁止规则

{{LLM_FORBIDDEN_RULES}}
<!-- 填充指导: 从反模式检测和最佳实践推理：print调试、裸except、硬编码密钥、import *、SQL拼接等 -->

{{LLM_FORBIDDEN_EXTRA}}
<!-- 填充指导: 基于项目类型补充通用禁止规则。无补充则删除此占位符 -->

### 错误处理

{{LLM_ERROR_HANDLING}}
<!-- 填充指导: 从代码中提炼错误处理方式：异常类型、错误码、日志记录、用户提示 -->

---

## API 规范

{{LLM_API_SPEC}}
<!-- 填充指导: 从路由和接口定义中提炼：URL风格、请求/响应格式、认证方式、版本控制 -->

---

## 测试规范

{{LLM_TEST_SPEC}}
<!-- 填充指导: 从测试代码中提炼：测试框架、覆盖率要求、测试命名、mock策略 -->

---

## 环境部署

### 部署方式

{{LLM_DEPLOYMENT}}
<!-- 填充指导: 读取 Dockerfile、docker-compose.yml、CI 配置和 README 中的部署说明，总结为 3-5 行部署步骤 -->

### 环境变量

{{LLM_ENV_VARIABLES}}
<!-- 填充指导: 读取 .env 文件内容（脱敏），列出关键变量及其用途说明 -->

---

## 项目记忆

项目开发记忆独立管理，入口文件：[`.specify/memory/MEMORY.md`](../../../.specify/memory/MEMORY.md)

**开发前必须先读取 `.specify/memory/MEMORY.md` 和 `.specify/memory/index.md`**，然后按 MEMORY.md 中的读取协议按需加载对应记忆文件。
