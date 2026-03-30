# 项目上下文模板（已废弃）

> **注意**：此模板已被 Agent Skills 动态生成方式替代。
>
> 新的项目上下文生成方式请参考：
> - Workflow: `.windsurf/workflows/0-制定项目上下文与章程.md`
> - 生成目录: `.specify/skills/project-context/`
>
> Skills 文件基于项目实际代码动态生成，不使用预置模板。

---

## 旧模板内容（仅供参考）

以下内容已废弃，保留仅供参考历史格式。

### 目的

> **AI 提取指令**：从 README.md 或项目文档中提取项目目标和愿景

[AI_EXTRACT: 从 README.md 或项目文档提取项目目标和愿景]

### 技术栈

> **AI 提取指令**：
> 1. 从依赖文件（package.json、pyproject.toml、go.mod 等）识别语言和框架
> 2. 从 settings.py 或配置文件识别数据库
> 3. 从 Dockerfile、docker-compose.yml 等识别基础设施

- **语言**: [AI_EXTRACT: 从依赖文件和源代码识别]
- **框架**: [AI_EXTRACT: 从依赖文件识别]
- **数据库**: [AI_EXTRACT: 从配置文件识别]
- **基础设施**: [AI_EXTRACT: 从部署配置识别]

## 项目约定

### 代码风格

> **AI 提取指令**：检查 linter 配置（ESLint、Prettier、Black、isort 等）

[AI_EXTRACT: 从 linter 配置和现有代码提取代码风格规范]

### 架构模式

> **AI 提取指令**：分析目录结构和代码组织

[AI_EXTRACT: 从目录结构和代码组织分析架构模式]

## 领域上下文

> 本章节定义业务领域的核心概念、术语和实体关系。
> AI 助手在每次交互中会自动加载这些约束，确保生成的代码符合业务规则。

> **AI 提取指令**：
> 1. 从 README、代码注释、模型定义中提取业务概念
> 2. 从模型关系中提取实体关系
> 3. 从业务逻辑代码中提取业务规则

### 核心业务概念

| 术语 | 定义 | AI 必须遵守的规则 |
|------|------|--------------------|
| [AI_EXTRACT] | [AI_EXTRACT] | [AI_EXTRACT] |

### 关键实体关系

```mermaid
[AI_EXTRACT: 从模型定义提取实体关系图]
```

### 业务规则约束

> AI 助手在生成代码时必须自动检查这些规则

- [AI_EXTRACT: 从业务逻辑代码提取业务规则]

## 重要约束

> **AI 提取指令**：从文档和代码中识别技术/业务/合规约束

[AI_EXTRACT: 从项目文档和代码提取重要约束]

## 外部依赖

> **AI 提取指令**：
> 1. **RPC 依赖**：搜索 `grep -r "ThriftClient\|thrift_client" --include="*.py"` 提取 Thrift 调用
> 2. **HTTP 依赖**：搜索 `grep -r "requests\.\|httpx\.\|urllib" --include="*.py"` 提取 HTTP 调用
> 3. **数据库依赖**：分析 settings.py 中的 DATABASES 配置
> 4. **中间件依赖**：搜索 Redis、etcd、MQ 等关键词

### RPC 服务依赖

| 服务名 | 服务类型 | 调用方法 | 用途 |
|--------|----------|----------|------|
| [AI_EXTRACT] | [AI_EXTRACT] | [AI_EXTRACT] | [AI_EXTRACT] |

### HTTP API 依赖

| 服务/URL | 方法 | 用途 |
|----------|------|------|
| [AI_EXTRACT] | [AI_EXTRACT] | [AI_EXTRACT] |

### 数据库依赖

| 数据库别名 | 类型 | 用途 |
|------------|------|------|
| default | [AI_EXTRACT] | 主数据库 |
| [AI_EXTRACT] | [AI_EXTRACT] | [AI_EXTRACT] |

### 中间件依赖

| 中间件 | 用途 |
|--------|------|
| [AI_EXTRACT] | [AI_EXTRACT] |

---

## 部署与运维

> **AI 提取指令**：
> 1. 搜索 `find . -name "*.service" -o -name "Dockerfile*"` 找到部署配置
> 2. 分析 src/etc/ 目录下的配置文件
> 3. 从 settings.py 提取端口和数据库配置

### 服务运行

| 项目 | 值 |
|------|----|
| **运行模式** | [AI_EXTRACT: 从部署配置识别] |
| **服务名称** | [AI_EXTRACT: 从 .service 文件提取] |
| **运行用户** | [AI_EXTRACT: 从部署配置提取] |
| **服务模板** | [AI_EXTRACT: 从 src/etc/ 目录提取] |

### 配置文件

| 文件 | 用途 |
|------|------|
| [AI_EXTRACT] | [AI_EXTRACT] |

### 关键配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| [AI_EXTRACT] | [AI_EXTRACT] | [AI_EXTRACT] |

### 端口

| 类型 | 端口 | 说明 |
|------|------|------|
| [AI_EXTRACT] | [AI_EXTRACT] | [AI_EXTRACT] |

### 数据库

| 项目 | 值 |
|------|----|
| **类型** | [AI_EXTRACT: 从 settings.py 提取] |
| **名称** | [AI_EXTRACT: 从 settings.py 提取] |
| **迁移命令** | [AI_EXTRACT: 从项目提取] |

---

## 代码实现规范

> **AI 提取指令**：从现有服务代码中提取实际的实现模式和规范

### 目录结构

> **AI 提取指令**：分析现有服务的目录组织

```
[AI_EXTRACT: 从现有服务提取实际目录结构]
```

### 错误码/事件/资源定义

> **AI 提取指令**：
> 1. 搜索 `find . -name "*_errorcode.py" | head -1` 找到现有错误码文件
> 2. 分析文件内容，提取项目前缀、命名格式、JSON 文档注释格式
> 3. 将提取的实际格式填充到下方

**位置**: `exception/[SERVICE_NAME]_errorcode.py`、`_event.py`、`_resource.py`

| 类型 | 格式 | 示例 |
|------|------|------|
| 错误码 | `[PROJECT_PREFIX].[MODULE].[ERROR]` | [AI_EXTRACT: 从现有代码提取] |
| 事件 | `[PROJECT_PREFIX].[EVENT_NAME]` | [AI_EXTRACT: 从现有代码提取] |
| 资源 | `[PROJECT_PREFIX].[TYPE].[NAME]` | [AI_EXTRACT: 从现有代码提取] |

**错误码完整格式**（从现有代码提取）:

```python
[AI_EXTRACT: 从 exception/*_errorcode.py 提取完整格式，包括 JSON 文档注释和变量定义]
```

**变量命名规则**: [AI_EXTRACT: 从现有代码提取命名规则]

### 模型定义

> **AI 提取指令**：
> 1. 搜索 `find . -name "models.py" | head -3` 找到现有模型文件
> 2. 分析模型基类、字段定义规范、Meta 类规范
> 3. 提取一个实际模型作为示例

**要求**: [AI_EXTRACT: 从现有模型提取规范，如基类、字段属性、Meta 定义等]

**示例**（从现有代码提取）:
```python
[AI_EXTRACT: 从 models.py 提取一个实际模型定义]
```

### 服务层

> **AI 提取指令**：
> 1. 搜索 `find . -type d -name "service"` 找到服务层目录
> 2. 分析服务类的方法结构和调用流程
> 3. 提取实际的服务层代码模式

**要求**: [AI_EXTRACT: 从现有服务层代码提取方法流程规范]

**示例**（从现有代码提取）:
```python
[AI_EXTRACT: 从 service/ 目录提取一个实际服务方法]
```

### Web 层

> **AI 提取指令**：
> 1. 搜索 `find . -type d -name "web"` 找到 Web 层目录
> 2. 分析请求处理模式、响应格式、异常处理
> 3. 提取实际的 Web 层代码模式

**要求**: [AI_EXTRACT: 从现有 Web 层代码提取请求处理规范]

**示例**（从现有代码提取）:
```python
[AI_EXTRACT: 从 web/ 目录提取一个实际请求处理方法]
```

### API 响应格式

> **AI 提取指令**：
> 1. 分析现有 Web 层代码中的响应格式
> 2. 提取成功、列表、错误三种响应的实际格式

| 类型 | 格式 |
|------|------|
| 成功 | [AI_EXTRACT: 从现有代码提取] |
| 列表 | [AI_EXTRACT: 从现有代码提取] |
| 错误 | [AI_EXTRACT: 从现有代码提取] |

### 日志级别

| 级别 | 场景 |
|------|------|
| DEBUG | 调试信息 |
| INFO | 正常业务流程 |
| WARNING | 可恢复异常 |
| ERROR | 不可恢复异常 |

### 设计追溯

代码注释标注需求编号: `设计追溯: FR-020, FR-021`

---

## Common 库使用规范

> Common 库是项目的公共能力层。所有新服务必须遵循以下规范使用 Common 库。

> **AI 提取指令**：
> 1. 搜索 `find . -type d -name "Common" | head -1` 找到 Common 库目录
> 2. 分析 Common 库的目录结构和提供的能力
> 3. 提取模型基类、异常处理、工具函数、装饰器等的使用方式

### Common 库目录结构

```
[AI_EXTRACT: 从项目中提取 Common 库的实际目录结构]
```

### 模型基类使用

> **AI 提取指令**：分析 `Common/models.py`，提取模型基类及其能力

**模型基类**: [AI_EXTRACT: 从 Common/models.py 提取基类名称和导入方式]

**使用示例**:
```python
[AI_EXTRACT: 从现有业务代码中提取模型基类的实际使用方式]
```

### 异常处理规范

> **AI 提取指令**：分析 `Common/exception/` 目录，提取异常类和使用方式

**异常类型**:
| 异常类 | 用途 |
|--------|------|
| [AI_EXTRACT] | [AI_EXTRACT] |

**使用示例**:
```python
[AI_EXTRACT: 从现有业务代码中提取异常处理的实际使用方式]
```

### 工具函数使用

> **AI 提取指令**：分析 `Common/utils/` 目录，提取常用工具函数

**常用工具函数**:
```python
[AI_EXTRACT: 从 Common/utils/ 提取常用工具函数的导入方式]
```

### Web 层装饰器

> **AI 提取指令**：分析 `Common/web/` 目录，提取装饰器使用方式

**装饰器列表**:
| 装饰器 | 用途 |
|--------|------|
| [AI_EXTRACT] | [AI_EXTRACT] |

**使用示例**:
```python
[AI_EXTRACT: 从现有业务代码中提取装饰器的实际使用方式]
```

### 配置读取

> **AI 提取指令**：分析 `Common/appconfig.py` 和 `Common/settings.py`

**配置模块**:
```python
[AI_EXTRACT: 从 Common/appconfig.py 和 Common/settings.py 提取配置读取方式]
```

---

## Thrift RPC 使用规范

> 项目使用 Thrift 作为服务间 RPC 通信协议。所有 Thrift 相关代码必须遵循以下规范。

> **AI 提取指令**：
> 1. 搜索 `find . -type d -name "thrift"` 找到 Thrift 相关目录
> 2. 分析 `Common/thrift/` 目录，提取客户端和服务端的使用方式
> 3. 从现有业务代码中提取 Thrift 调用的实际示例

### Thrift 客户端调用

> **AI 提取指令**：分析 `Common/thrift/client.py`，提取 ThriftClient 的使用方式

**ThriftClient 导入和参数**:
```python
[AI_EXTRACT: 从 Common/thrift/client.py 提取 ThriftClient 的导入和参数说明]
```

**使用示例**（从现有业务代码提取）:
```python
[AI_EXTRACT: 从现有业务代码中提取 ThriftClient 的实际调用方式]
```

### Thrift 服务端实现

> **AI 提取指令**：分析 `Common/thrift/server.py` 和现有 Processor 实现

**Processor 实现模式**:
```python
[AI_EXTRACT: 从现有 thriftor/processor.py 提取 Processor 实现模式]
```

### Thrift 接口装饰器

> **AI 提取指令**：分析 `Common/thrift/wrappers.py`

**装饰器列表**:
| 装饰器 | 用途 |
|--------|------|
| [AI_EXTRACT] | [AI_EXTRACT] |

**异常处理规则**: [AI_EXTRACT: 从 Common/thrift/wrappers.py 提取异常处理规则]

### Thrift 类型定义

> **AI 提取指令**：搜索 `find . -name "ttypes.py" | head -5` 找到 Thrift 类型文件

**Thrift 类型文件位置**: [AI_EXTRACT: 从项目中提取 Thrift 类型文件的实际位置]

**常用 Thrift 类型导入**:
```python
[AI_EXTRACT: 从现有业务代码中提取常用 Thrift 类型的导入方式]
```

### 服务类型常量

> **AI 提取指令**：分析 `Common/constants.py`

**服务类型映射**:
```python
[AI_EXTRACT: 从 Common/constants.py 提取服务类型映射的导入方式]
```

### Thrift 异常处理

> **AI 提取指令**：从现有业务代码中提取 Thrift 异常处理模式

**异常处理示例**:
```python
[AI_EXTRACT: 从现有业务代码中提取 Thrift 异常处理的实际模式]
```

### etcd 服务发现

> **AI 提取指令**：分析 `Common/etcd/` 目录和现有使用方式

**服务发现示例**:
```python
[AI_EXTRACT: 从现有业务代码中提取 etcd 服务发现的实际使用方式]
```

---

## 分页规范

> 所有列表接口必须遵循统一的分页规范。

> **AI 提取指令**：
> 1. 搜索 `grep -r "index.*count\|page.*size" --include="*.py"` 找到分页实现
> 2. 分析分页参数命名和响应格式
> 3. 提取实际的分页实现示例

### 分页参数

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| [AI_EXTRACT] | [AI_EXTRACT] | [AI_EXTRACT] | [AI_EXTRACT] |

### 分页响应格式

```json
[AI_EXTRACT: 从现有代码提取实际响应格式]
```

### 分页实现示例

```python
[AI_EXTRACT: 从现有 Web 层代码提取分页实现示例]
```

---

## HTTP 服务启动规范

> 所有服务必须通过 Django management command 启动。

> **AI 提取指令**：
> 1. 搜索 `find . -name "run_server.py"` 找到服务启动命令
> 2. 分析启动命令的实现模式
> 3. 提取 systemd 服务配置（如有）

### 目录结构

```
[AI_EXTRACT: 从现有服务提取 management/commands 目录结构]
```

### 启动命令实现

```python
[AI_EXTRACT: 从现有 run_server.py 提取启动命令实现模式]
```

### 启动方式

```bash
[AI_EXTRACT: 从现有服务提取启动命令]
```

### systemd 服务配置

```ini
[AI_EXTRACT: 从 src/etc/ 目录提取 systemd 服务配置模板]
```

---

## 接口实现规范

> **openapi.json 是接口实现的唯一权威来源**。如果项目中存在 openapi.json 文档，所有 Web 接口必须严格按照该文档实现。

### 核心原则

1. **openapi.json 优先**：当 openapi.json 与其他文档（如 design.md）存在冲突时，以 openapi.json 为准
2. **完全一致性**：请求参数、响应字段、数据类型必须与 openapi.json 定义完全一致
3. **不得擅自修改**：不得添加、删除或重命名 openapi.json 中未定义的字段

### 请求参数规范

- 参数名称必须与 openapi.json 定义完全一致
- 参数类型必须与 openapi.json 定义一致
- 必填参数必须进行校验
- 参数默认值必须与 openapi.json 定义一致

### 响应结构规范

- 响应字段名称必须与 openapi.json 定义完全一致（注意大小写）
- 响应结构层级必须与 openapi.json 定义一致
- 所有 openapi.json 中定义的字段都必须返回
- 字段类型必须与 openapi.json 定义一致

### 实现检查清单

实现接口前，必须逐项对照 openapi.json 检查：

- [ ] URL 路径与 openapi.json 一致
- [ ] HTTP 方法与 openapi.json 一致
- [ ] 请求参数名称与 openapi.json 一致
- [ ] 请求参数类型与 openapi.json 一致
- [ ] 响应字段名称与 openapi.json 一致
- [ ] 响应字段类型与 openapi.json 一致
- [ ] 响应结构层级与 openapi.json 一致
- [ ] 错误响应格式与 openapi.json 一致

### openapi.json 位置

> **AI 提取指令**：搜索 `find . -name "openapi.json" -o -name "openapi.yaml"` 找到 API 定义文件

**API 定义文件**: [AI_EXTRACT: 从项目中提取 openapi.json 的实际位置]
