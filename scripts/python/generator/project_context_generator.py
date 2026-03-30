# -*- coding: utf-8 -*-
"""
项目上下文生成器

基于骨架数据自动生成 project-context Skill 的所有文件
确保每次执行结果一致
"""
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

from .cluster_doc_generator import ClusterDocGenerator


class ProjectContextGenerator:
    """项目上下文生成器"""

    # 必须生成的文件列表
    REQUIRED_FILES = [
        'SKILL.md',
        # 聚类规范
        'web.md',
        'models.md',
        'service.md',
        'handler.md',
        'error.md',
        'constants.md',
        'naming.md',
        'test.md',
        # 通用规范
        'common.md',
        'config.md',
        # 开发辅助文件
        'imports.md',
        'urls.md',
        'models_reference.md',
    ]

    def __init__(self):
        self.skeleton: Dict = {}
        self.output_dir: str = ""
        self.source_root: str = ""  # 源码根目录

    def _read_code_snippet(self, file_path: str, start_line: int, max_lines: int = 30) -> Optional[str]:
        """
        从源文件读取代码片段

        参数:
            file_path: 文件路径（相对于项目根目录）
            start_line: 起始行号
            max_lines: 最大读取行数

        返回: 代码片段字符串，如果读取失败返回 None
        """
        # 尝试多个可能的路径
        # source_root 是 cache 目录，需要回到项目根目录
        project_root = os.path.abspath(os.path.join(self.source_root, '..', '..', '..'))
        possible_paths = [
            file_path,
            os.path.join(project_root, file_path),
            os.path.join(self.source_root, '..', '..', '..', file_path),
            os.path.join(self.source_root, '..', file_path),
        ]

        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                try:
                    with open(abs_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    # 找到代码块的结束位置（通过缩进判断）
                    if start_line > len(lines):
                        return None

                    result_lines = []
                    base_indent = None

                    for i in range(start_line - 1, min(start_line - 1 + max_lines, len(lines))):
                        line = lines[i]

                        # 跳过空行开头
                        if not result_lines and not line.strip():
                            continue

                        # 计算缩进
                        stripped = line.lstrip()
                        if stripped:
                            current_indent = len(line) - len(stripped)
                            if base_indent is None:
                                base_indent = current_indent
                            elif current_indent < base_indent and stripped and not stripped.startswith('#'):
                                # 缩进减少，代码块结束
                                break

                        result_lines.append(line.rstrip())

                    # 移除尾部空行
                    while result_lines and not result_lines[-1].strip():
                        result_lines.pop()

                    return '\n'.join(result_lines) if result_lines else None
                except Exception:
                    continue

        return None

    def _extract_class_code(self, example: Dict) -> Optional[str]:
        """
        提取类的完整代码（包括方法）
        """
        if example.get('type') != 'class':
            return None

        file_path = example.get('file', '')
        line = example.get('line', 0)

        return self._read_code_snippet(file_path, line, max_lines=50)

    def _extract_function_code(self, example: Dict) -> Optional[str]:
        """
        提取函数的完整代码
        """
        if example.get('type') != 'function':
            return None

        file_path = example.get('file', '')
        line = example.get('line', 0)

        return self._read_code_snippet(file_path, line, max_lines=30)

    def generate(self, skeleton_path: str, output_dir: str) -> List[str]:
        """
        生成 project-context Skill

        参数:
            skeleton_path: 骨架数据文件路径
            output_dir: 输出目录

        返回: 生成的文件列表
        """
        # 加载骨架数据
        with open(skeleton_path, 'r', encoding='utf-8') as f:
            self.skeleton = json.load(f)

        self.output_dir = output_dir
        self.source_root = os.path.dirname(os.path.abspath(skeleton_path))
        os.makedirs(output_dir, exist_ok=True)

        generated_files = []

        # 生成所有必需文件
        generators = {
            'SKILL.md': self._generate_skill_md,
            'web.md': self._generate_web_md,
            'models.md': self._generate_models_md,
            'service.md': self._generate_service_md,
            'handler.md': self._generate_handler_md,
            'error.md': self._generate_error_md,
            'constants.md': self._generate_constants_md,
            'naming.md': self._generate_naming_md,
            'test.md': self._generate_test_md,
            'common.md': self._generate_common_md,
            'config.md': self._generate_config_md,
            'imports.md': self._generate_imports_md,
            'urls.md': self._generate_urls_md,
            'models_reference.md': self._generate_models_reference_md,
        }

        for filename in self.REQUIRED_FILES:
            if filename in generators:
                filepath = os.path.join(output_dir, filename)
                content = generators[filename]()
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                generated_files.append(filepath)

        return generated_files

    def _get_project_info(self) -> Dict:
        """获取项目信息"""
        project = self.skeleton.get('project', {})

        # 获取项目名称，如果是无效值则从服务列表或目录结构推断
        name = project.get('name', '')
        if not name or name in ['..', '.', '']:
            # 尝试从服务列表获取
            services = project.get('services', [])
            if services:
                name = services[0].get('name', '项目')
            else:
                # 尝试从目录结构获取
                dirs = self.skeleton.get('directory_structure', {}).get('directories', [])
                if dirs:
                    name = dirs[0].get('name', '项目')
                else:
                    name = '项目'

        return {
            'name': name,
            'framework': project.get('framework', {}).get('primary', 'unknown'),
            'language': project.get('language', 'Python'),
            'source_dir': project.get('source_dir', 'src'),
        }

    def _get_cluster_patterns(self, cluster_name: str) -> List[Dict]:
        """获取聚类模式"""
        clusters = self.skeleton.get('clusters', {})
        cluster = clusters.get(cluster_name, {})
        return cluster.get('patterns', [])

    def _get_cluster_examples(self, cluster_name: str) -> List[Dict]:
        """获取聚类示例"""
        clusters = self.skeleton.get('clusters', {})
        cluster = clusters.get(cluster_name, {})
        return cluster.get('examples', [])

    def _get_unit_statistics(self) -> Dict:
        """获取代码单元统计"""
        return self.skeleton.get('unit_statistics', {})

    def _group_examples_by_service(self, examples: List[Dict]) -> Dict[str, List[Dict]]:
        """按服务分组示例"""
        grouped = {}
        for ex in examples:
            file_path = ex.get('file', '')
            # 从文件路径提取服务名
            service = 'other'
            if 'v7tov8Service' in file_path:
                service = 'v7tov8Service'
            elif 'DeploymentService' in file_path:
                service = 'DeploymentService'

            if service not in grouped:
                grouped[service] = []
            grouped[service].append(ex)
        return grouped

    def _extract_examples_from_multiple_services(self, examples: List[Dict],
                                                   filter_func, max_per_service: int = 1) -> List[tuple]:
        """从多个服务中提取示例

        返回: [(service_name, example_dict, code_str), ...]
        """
        grouped = self._group_examples_by_service(examples)
        results = []

        for service, service_examples in grouped.items():
            count = 0
            for ex in service_examples:
                if filter_func(ex):
                    if ex.get('type') == 'class':
                        code = self._extract_class_code(ex)
                    else:
                        code = self._extract_function_code(ex)

                    if code and len(code) > 30:
                        results.append((service, ex, code))
                        count += 1
                        if count >= max_per_service:
                            break

        return results

    def _generate_skill_md(self) -> str:
        """生成 SKILL.md"""
        info = self._get_project_info()
        stats = self._get_unit_statistics()
        dirs = self.skeleton.get('directory_structure', {}).get('directories', [])
        project = self.skeleton.get('project', {})
        services = project.get('services', [])

        # 构建目录结构
        dir_tree = []
        for d in dirs[:10]:  # 只显示前 10 个
            dir_tree.append(f"├── {d['name']}/")

        # 构建服务列表
        service_table = []
        for s in services:
            service_table.append(f"| **{s.get('name', '')}** | `{s.get('path', '')}` |")

        return f'''---
name: project-context
description: 项目上下文。用于了解项目结构、技术栈、开发规范，开发前必读。
---

# 项目上下文

src 目录下全部服务的完整上下文和开发规范。

## 何时使用

- **开发前准备**：了解项目结构和技术栈
- **编写代码**：查阅对应的开发规范
- **代码审查**：验证是否符合项目规范

## 项目概述

本项目使用 **{info['framework'].title()}** 框架开发，包含 **{len(services)} 个服务**。

## 服务列表

| 服务名称 | 路径 |
|----------|------|
{chr(10).join(service_table)}

## 技术栈

| 类别 | 技术 |
|------|------|
| **语言** | {info['language']} |
| **Web 框架** | {info['framework'].title()} |

## 项目结构

```
{info['source_dir']}/
{chr(10).join(dir_tree)}
```

## 开发规范导航

| 规范 | 说明 | 何时查阅 |
|------|------|----------|
| [web.md](./web.md) | Web 接口规范 | 开发 API 接口 |
| [models.md](./models.md) | 数据模型规范 | 定义数据模型 |
| [service.md](./service.md) | 服务层规范 | 编写业务逻辑 |
| [handler.md](./handler.md) | 处理器规范 | 后台任务处理 |
| [error.md](./error.md) | 错误处理规范 | 定义错误码 |
| [constants.md](./constants.md) | 常量定义规范 | 定义常量枚举 |
| [common.md](./common.md) | 公共库规范 | 使用公共库 |
| [config.md](./config.md) | 配置规范 | 配置文件 |
| [naming.md](./naming.md) | 命名规范 | 函数/类命名 |
| [test.md](./test.md) | 测试规范 | 编写测试 |

## 开发辅助文件

| 文件 | 说明 |
|------|------|
| [imports.md](./imports.md) | 各场景 import 模板 |
| [urls.md](./urls.md) | URL 路由规范 |
| [models_reference.md](./models_reference.md) | 模型字段速查 |

## 代码统计

- **总代码单元**: {stats.get('total', 0)}
- **类**: {stats.get('classes', 0)}
- **函数**: {stats.get('functions', 0)}

## 相关 Skill

- [API 接口文档](../api-external/SKILL.md) - 对外 API 接口信息
- [业务规则](../business-rules/SKILL.md) - API 和 Handler 的业务逻辑

**版本**: 1.0.0 | **最后修正**: {datetime.now().strftime('%Y-%m-%d')}
'''

    def _generate_web_md(self) -> str:
        """生成 web.md"""
        patterns = self._get_cluster_patterns('web')
        examples = self._get_cluster_examples('web')

        # 提取装饰器模式
        decorators = [p for p in patterns if p.get('type') == 'decorator']
        combos = [p for p in patterns if p.get('type') == 'structure' and 'combo' in p.get('key', '')]

        decorator_table = []
        for d in decorators[:5]:
            decorator_table.append(f"| `{d['key']}` | {d.get('count', 0)} 次 |")

        combo_table = []
        for c in combos[:3]:
            combo_table.append(f"| `{c['key'].replace('combo:', '')}` | {c.get('count', 0)} 次 |")

        # 从多个服务提取 View 类示例
        view_examples = self._extract_examples_from_multiple_services(
            examples,
            lambda ex: ex.get('type') == 'class' and 'View' in ex.get('bases', []),
            max_per_service=1
        )

        # 构建示例部分
        examples_section = ""
        if view_examples:
            for service, ex, code in view_examples:
                examples_section += f"""
### {service}

```python
{code}
```
"""
        else:
            examples_section = """
```python
class MyView(View):
    @formatting()
    @authenticated()
    def get(self, request):
        return data
```
"""

        return f'''# Web 接口规范

## 概述

本项目使用 Class-Based Views (CBV) 模式开发 Web 接口。

## 装饰器规范

### 常用装饰器

| 装饰器 | 出现次数 |
|--------|----------|
{chr(10).join(decorator_table)}

### 常用装饰器组合

| 组合 | 出现次数 |
|------|----------|
{chr(10).join(combo_table)}

## View 类示例（来自项目代码）
{examples_section}
## 响应格式

所有响应由 `@formatting()` 装饰器自动包装。
'''

    def _generate_models_md(self) -> str:
        """生成 models.md - 使用知识数据"""
        # 从知识数据获取模型信息
        knowledge = self.skeleton.get('knowledge', {})
        models_data = knowledge.get('models', {})
        model_definitions = models_data.get('definitions', [])

        # 从骨架数据中获取模型基类
        clusters = self.skeleton.get('clusters', {})
        model_base = "BaseModel"
        for cluster_name, cluster in clusters.items():
            for pattern in cluster.get('patterns', []):
                if pattern.get('type') == 'inheritance' and 'Model' in pattern.get('key', ''):
                    key = pattern.get('key', '')
                    if 'extends:' in key:
                        model_base = key.replace('extends:', '')
                        break

        # 生成模型列表
        model_table = []
        for m in model_definitions[:15]:
            name = m.get('name', '')
            base = m.get('base_class', '')
            field_count = len(m.get('fields', []))
            file_path = m.get('file_path', '').split('/')[-1]
            model_table.append(f"| `{name}` | `{base}` | {field_count} | `{file_path}` |")

        # 生成字段类型统计
        field_types = {}
        for m in model_definitions:
            for f in m.get('fields', []):
                ft = f.get('field_type', '')
                if ft:
                    field_types[ft] = field_types.get(ft, 0) + 1

        field_type_table = []
        for ft, count in sorted(field_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            field_type_table.append(f"| `{ft}` | {count} |")

        return f'''# 数据模型规范

## 概述

本项目使用 Django ORM 定义数据模型。共发现 **{models_data.get('total', 0)}** 个模型。

## 基类规范

所有模型必须继承 `{model_base}`。

## 模型列表

| 模型名 | 基类 | 字段数 | 文件 |
|--------|------|--------|------|
{chr(10).join(model_table) if model_table else "| - | - | - | - |"}

## 常用字段类型

| 字段类型 | 使用次数 |
|----------|----------|
{chr(10).join(field_type_table) if field_type_table else "| - | - |"}

## 字段规范

### 主键
- 使用 UUID 作为主键（{model_base} 已定义）

### 外键
```python
job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='sub_jobs')
```

### 时间字段
```python
create_time = models.DateTimeField(auto_now_add=True)
update_time = models.DateTimeField(auto_now=True)
```

## 查询规范

```python
# 推荐：使用 ORM 查询
jobs = Job.objects.filter(status=1)

# 禁止：原生 SQL（除非必要）
```

## 事务处理

```python
from django.db import transaction

with transaction.atomic():
    job.status = 2
    job.save()
```
'''

    def _generate_service_md(self) -> str:
        """生成 service.md"""
        patterns = self._get_cluster_patterns('service')
        examples = self._get_cluster_examples('service')

        # 从多个服务提取 Service/Manager 类示例
        service_examples = self._extract_examples_from_multiple_services(
            examples,
            lambda ex: ex.get('type') == 'class' and ('Service' in ex.get('name', '') or 'Manager' in ex.get('name', '')),
            max_per_service=1
        )

        # 构建示例部分
        examples_section = ""
        if service_examples:
            for service, ex, code in service_examples:
                examples_section += f"""
### {service}

```python
{code}
```
"""

        return f'''# 服务层规范

## 概述

服务层负责业务逻辑处理，位于 Web 层和 Model 层之间。

{f"""## 服务类示例（来自项目代码）
{examples_section}""" if examples_section else ""}
## 调用规范

- Web 层调用 Service 层
- Service 层调用 Model 层
- 禁止 Web 层直接操作复杂业务逻辑

## 日志规范

使用 `logger` 记录日志，禁止使用 `print()`。
'''

    def _generate_handler_md(self) -> str:
        """生成 handler.md"""
        patterns = self._get_cluster_patterns('handler')
        examples = self._get_cluster_examples('handler')

        # 提取 Handler 基类名称
        handler_bases = []
        for p in patterns:
            if p.get('type') == 'inheritance' and 'Handler' in p.get('key', ''):
                base_name = p.get('key', '').replace('extends:', '')
                handler_bases.append((base_name, p.get('count', 0)))

        # 生成 Handler 类型表格
        handler_table = []
        for base, count in handler_bases[:5]:
            handler_table.append(f"| `{base}` | {count} 个 |")

        # 从多个服务提取 Handler 示例
        handler_examples = self._extract_examples_from_multiple_services(
            examples,
            lambda ex: ex.get('type') == 'class' and 'Handler' in ex.get('name', ''),
            max_per_service=1
        )

        # 构建示例部分
        examples_section = ""
        if handler_examples:
            for service, ex, code in handler_examples:
                examples_section += f"""
### {service}

```python
{code}
```
"""

        return f'''# 处理器规范

## 概述

Handler 用于处理后台任务、Thrift 请求等非 Web 请求。

## Handler 类型统计

| 基类 | 数量 |
|------|------|
{chr(10).join(handler_table) if handler_table else "| - | - |"}

{f"""## Handler 示例（来自项目代码）
{examples_section}""" if examples_section else ""}
## Django Command

```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = '执行数据迁移'

    def handle(self, *args, **options):
        pass
```
'''

    def _generate_error_md(self) -> str:
        """生成 error.md - 使用错误码数据生成完整文档"""
        # 获取错误码和异常类数据
        error_codes = self.skeleton.get('error_codes', [])
        exception_classes = self.skeleton.get('exception_classes', [])

        # 按模块分组错误码
        by_module = {}
        for ec in error_codes:
            module = ec.get('module', 'other')
            if module not in by_module:
                by_module[module] = []
            by_module[module].append(ec)

        # 按基类分组异常类
        by_base = {}
        for exc in exception_classes:
            base = exc.get('base_class', 'Exception')
            if base not in by_base:
                by_base[base] = []
            by_base[base].append(exc)

        # 生成异常基类表格
        base_table = []
        for base, classes in sorted(by_base.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            base_table.append(f"| `{base}` | {len(classes)} 个 |")

        # 生成错误码文件列表
        errorcode_files = set()
        for ec in error_codes:
            file_path = ec.get('file_path', '')
            if file_path:
                # 简化路径
                parts = file_path.split('/')
                for i, p in enumerate(parts):
                    if p == 'src':
                        errorcode_files.add('/'.join(parts[i+1:]))
                        break
                else:
                    errorcode_files.add(file_path.split('/')[-1])

        file_table = []
        for f in sorted(errorcode_files)[:10]:
            file_table.append(f"| `{f}` |")

        # 生成错误码列表（每个模块取前5个）
        errorcode_table = []
        for module, codes in sorted(by_module.items()):
            for ec in codes[:8]:
                code = ec.get('code', '')
                desc = ec.get('description', '-')
                solution = ec.get('solution', '-')
                if desc or solution != '-':
                    errorcode_table.append(f"| `{code}` | {desc} | {solution} |")

        # 生成异常类示例
        exception_examples = ""
        for exc in exception_classes[:3]:
            name = exc.get('name', '')
            base = exc.get('base_class', '')
            docstring = exc.get('docstring', '')
            if name and base:
                exception_examples += f"- `{name}` (继承 `{base}`)"
                if docstring:
                    exception_examples += f" - {docstring[:50]}"
                exception_examples += "\n"

        # 如果没有提取到错误码数据，回退到聚类数据
        if not error_codes and not exception_classes:
            patterns = self._get_cluster_patterns('error')
            examples = self._get_cluster_examples('error')

            error_patterns_table = []
            for p in patterns[:10]:
                error_patterns_table.append(f"| `{p.get('key', '')}` | {p.get('count', 0)} |")

            return f'''# 错误处理规范

## 概述

本项目使用统一的错误处理机制。

{f"""## 错误模式统计

| 模式 | 出现次数 |
|------|----------|
{chr(10).join(error_patterns_table)}
""" if error_patterns_table else ""}

## 使用规范

- 禁止裸 `except:`，必须指定异常类型
- 使用项目统一的错误码定义
- 错误信息应支持国际化
'''

        return f'''# 错误处理规范

## 概述

本项目使用统一的异常基类和错误码体系处理错误。

## 异常基类体系

| 基类 | 数量 |
|------|------|
{chr(10).join(base_table) if base_table else "| - | - |"}

### 常用异常类

{exception_examples if exception_examples else "- 无"}

## 错误码定义规范

### 错误码格式

```
模块.子模块.错误类型
```

示例：`Upgrade.Job.NotFound`、`Upgrade.UserImport.DbAuthRequired`

### 错误码定义文件

| 文件 |
|------|
{chr(10).join(file_table) if file_table else "| - |"}

### 常用错误码列表

| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
{chr(10).join(errorcode_table[:15]) if errorcode_table else "| - | - | - |"}

## 错误码定义示例

```python
# 位置: exception/upgrade_errorcode.py

\'\'\'
    {{
        "errorcode": "Upgrade.Job.NotFound",
        "description": "作业不存在。",
        "cause": "指定的作业ID不存在或已被删除。",
        "solution": "请检查作业ID是否正确。"
    }}
\'\'\'
Upgrade_Job_NotFound = 'Upgrade.Job.NotFound'
```

## 抛出异常示例

```python
from Common.exception.defines import ABGeneralPurposeException, I18nErrorData
from exception.upgrade_errorcode import Upgrade_Job_NotFound

raise ABGeneralPurposeException(I18nErrorData(
    error_code=Upgrade_Job_NotFound,
    description="作业不存在。",
    cause="指定的作业ID不存在或已被删除。",
    solution="请检查作业ID是否正确。"
))
```

## 开发建议

- **禁止**裸 `except:`，必须指定异常类型
- **必须**使用项目定义的错误码常量，禁止硬编码错误码字符串
- **必须**在错误码定义中包含 description、cause、solution
- 错误信息应支持国际化（使用 `I18nErrorData`）
- 新增错误码需在对应的 `*_errorcode.py` 文件中定义
'''

    def _generate_constants_md(self) -> str:
        """生成 constants.md - 使用知识数据"""
        # 从知识数据获取常量信息
        knowledge = self.skeleton.get('knowledge', {})
        constants_data = knowledge.get('constants', {})
        by_category = constants_data.get('by_category', {})

        # 生成常量类别统计
        category_table = []
        for category, consts in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
            if category and len(consts) > 0:
                category_table.append(f"| `{category}` | {len(consts)} 个 |")

        # 生成各类别的常量示例
        category_examples = ""
        for category in ['status', 'type', 'level', 'choices']:
            if category in by_category and by_category[category]:
                consts = by_category[category][:5]
                category_examples += f"\n### {category.title()} 常量\n\n"
                category_examples += "| 常量名 | 值 | 文件 |\n"
                category_examples += "|--------|-----|------|\n"
                for c in consts:
                    name = c.get('name', '')
                    value = c.get('value', '')[:30]
                    file_path = c.get('file_path', '').split('/')[-1]
                    category_examples += f"| `{name}` | `{value}` | `{file_path}` |\n"

        # 回退到聚类数据
        patterns = self._get_cluster_patterns('constants')
        enum_bases = []
        for p in patterns:
            if p.get('type') == 'inheritance' and 'Enum' in p.get('key', ''):
                base_name = p.get('key', '').replace('extends:', '')
                enum_bases.append((base_name, p.get('count', 0)))

        enum_table = []
        for base, count in enum_bases[:5]:
            enum_table.append(f"| `{base}` | {count} 个 |")

        return f'''# 常量定义规范

## 概述

本项目使用模块级常量和枚举类定义常量值。共发现 **{constants_data.get('total', 0)}** 个常量。

## 常量类别统计

| 类别 | 数量 |
|------|------|
{chr(10).join(category_table) if category_table else "| - | - |"}

{f"""## 枚举基类统计

| 基类 | 数量 |
|------|------|
{chr(10).join(enum_table)}
""" if enum_table else ""}
{category_examples if category_examples else ""}
## 使用规范

- **正确**：使用常量名称（如 `JobStatus.RUNNING`）
- **禁止**：使用魔法数字（如 `status == 1`）
- 新增常量应放在对应的 `constants.py` 文件中
'''

    def _generate_naming_md(self) -> str:
        """生成 naming.md"""
        patterns = self._get_cluster_patterns('naming')

        # 提取命名模式
        prefix_patterns = [p for p in patterns if 'prefix:' in p.get('key', '')]
        suffix_patterns = [p for p in patterns if 'suffix:' in p.get('key', '')]

        prefix_table = []
        for p in prefix_patterns[:10]:
            name = p['key'].replace('prefix:', '')
            prefix_table.append(f"| `{name}` | {p.get('count', 0)} 次 |")

        suffix_table = []
        for p in suffix_patterns[:8]:
            name = p['key'].replace('suffix:', '')
            suffix_table.append(f"| `{name}` | {p.get('count', 0)} 次 |")

        return f'''# 命名规范

## 概述

本项目遵循 Python PEP 8 命名规范。

## 函数命名前缀

| 前缀 | 出现次数 |
|------|----------|
{chr(10).join(prefix_table)}

## 类命名后缀

| 后缀 | 出现次数 |
|------|----------|
{chr(10).join(suffix_table)}

## 示例

```python
# 获取数据
def get_job_list():
    pass

# 布尔判断
def is_job_running(job_id):
    pass

# 类命名
class JobListView(View):
    pass
```
'''

    def _generate_test_md(self) -> str:
        """生成 test.md - 使用通用生成器"""
        cluster_gen = ClusterDocGenerator(self.skeleton, self.source_root)

        # 检查是否有 test 聚类数据
        test_cluster = self.skeleton.get('clusters', {}).get('test', {})
        if test_cluster.get('patterns') or test_cluster.get('examples'):
            return cluster_gen.generate_cluster_doc('test')

        # 如果没有聚类数据，使用基础模板
        patterns = self._get_cluster_patterns('test')
        examples = self._get_cluster_examples('test')

        # 提取 TestCase 数量
        testcase_count = 0
        test_bases = []
        for p in patterns:
            if p.get('type') == 'inheritance':
                base_name = p.get('key', '').replace('extends:', '')
                test_bases.append((base_name, p.get('count', 0)))
                if 'TestCase' in base_name:
                    testcase_count += p.get('count', 0)

        # 提取真实的测试类示例
        test_example = ""
        for ex in examples:
            if ex.get('type') == 'class' and 'Test' in ex.get('name', ''):
                code = self._extract_class_code(ex)
                if code and len(code) > 20:
                    test_example = code
                    break

        # 构建基类表格
        base_table = []
        for base, count in test_bases[:5]:
            base_table.append(f"| `{base}` | {count} |")

        return f'''# 测试规范

## 概述

本项目使用 Django TestCase 和 unittest 进行测试。

## 测试统计

- **TestCase 类**: {testcase_count} 个

{f"""## 测试基类统计

| 基类 | 数量 |
|------|------|
{chr(10).join(base_table)}
""" if base_table else ""}

{f"""## 测试类示例（来自项目代码）

```python
{test_example}
```
""" if test_example else ""}

## 使用规范

- 测试类应继承 TestCase 或项目基类
- 测试方法以 `test_` 开头
- 使用 setUp/tearDown 管理测试状态

## 运行测试

```bash
python manage.py test
```
'''

    def _generate_common_md(self) -> str:
        """生成 common.md - 使用通用生成器"""
        cluster_gen = ClusterDocGenerator(self.skeleton, self.source_root)

        # 检查是否有 common 聚类数据
        common_cluster = self.skeleton.get('clusters', {}).get('common', {})

        # 从骨架数据中获取目录结构
        dirs = self.skeleton.get('directory_structure', {}).get('directories', [])

        # 查找 Common 目录
        common_items = []
        common_path = ""
        for d in dirs:
            if d.get('name') == 'Common':
                common_items = d.get('items', [])
                common_path = d.get('name', '')
                break
            # 检查子目录中是否有 Common
            items = d.get('items', [])
            if 'Common' in items:
                common_items = [item for item in items if not item.endswith('.py')][:10]
                common_path = f"{d.get('name', '')}/Common"
                break

        # 如果还是没找到，使用第一个服务目录的内容
        if not common_items and dirs:
            first_service = dirs[0]
            common_items = first_service.get('items', [])[:10]
            common_path = first_service.get('name', '')

        # 生成目录列表
        dir_list = []
        for item in common_items[:10]:
            dir_list.append(f"- `{item}/`" if not item.endswith('.py') else f"- `{item}`")

        # 如果有聚类数据，使用通用生成器生成模式和示例部分
        patterns_section = ""
        examples_section = ""
        if common_cluster.get('patterns') or common_cluster.get('examples'):
            # 生成模式表格
            patterns = common_cluster.get('patterns', [])
            if patterns:
                patterns_section = "## 代码模式\n\n"
                patterns_section += "| 模式 | 出现次数 | 置信度 |\n"
                patterns_section += "|------|----------|--------|\n"
                for p in patterns[:10]:
                    patterns_section += f"| `{p.get('key', '')}` | {p.get('count', 0)} | {p.get('confidence', 0):.1%} |\n"
                patterns_section += "\n"

            # 生成示例
            examples = common_cluster.get('examples', [])
            if examples:
                examples_section = "## 代码示例（来自项目代码）\n\n"
                for ex in examples[:3]:
                    if ex.get('type') == 'class':
                        code = self._extract_class_code(ex)
                    else:
                        code = self._extract_function_code(ex)
                    if code:
                        examples_section += f"**{ex.get('name', '')}** (`{ex.get('file', '')}:{ex.get('line', 0)}`)\n\n"
                        examples_section += f"```python\n{code}\n```\n\n"

        return f'''# 公共库规范

## 概述

项目共享的公共组件，位于 `{common_path}` 目录。

## 主要目录

{chr(10).join(dir_list) if dir_list else "- 无"}

{patterns_section}
{examples_section}
## 使用说明

查看具体组件时，直接打开对应的文件。
'''

    def _generate_config_md(self) -> str:
        """生成 config.md - 使用通用生成器"""
        cluster_gen = ClusterDocGenerator(self.skeleton, self.source_root)

        # 检查是否有 config 聚类数据
        config_cluster = self.skeleton.get('clusters', {}).get('config', {})
        if config_cluster.get('patterns') or config_cluster.get('examples'):
            return cluster_gen.generate_cluster_doc('config')

        # 如果没有聚类数据，使用基础模板
        patterns = self._get_cluster_patterns('config')
        examples = self._get_cluster_examples('config')

        # 提取配置相关的模式
        config_patterns_table = []
        for p in patterns[:10]:
            config_patterns_table.append(f"| `{p.get('key', '')}` | {p.get('count', 0)} |")

        # 提取真实的配置类示例
        config_example = ""
        for ex in examples:
            if ex.get('type') == 'class' and 'Config' in ex.get('name', ''):
                code = self._extract_class_code(ex)
                if code and len(code) > 20:
                    config_example = code
                    break

        return f'''# 配置规范

## 概述

本项目使用统一的配置管理机制。

{f"""## 配置模式统计

| 模式 | 出现次数 |
|------|----------|
{chr(10).join(config_patterns_table)}
""" if config_patterns_table else ""}

{f"""## 配置类示例（来自项目代码）

```python
{config_example}
```
""" if config_example else ""}

## 使用规范

- 使用项目统一的配置读取方式
- 敏感配置不要硬编码
- 环境变量优先于配置文件
'''

    def _generate_imports_md(self) -> str:
        """生成 imports.md - 包含完整的 import 路径"""
        # 从骨架数据中提取常用装饰器
        web_patterns = self._get_cluster_patterns('web')
        decorators = []
        for p in web_patterns:
            if p.get('type') == 'decorator':
                dec_name = p.get('key', '').replace('@', '')
                if dec_name and dec_name not in decorators:
                    decorators.append(dec_name)

        decorator_list = decorators[:5] if decorators else ['formatting', 'authenticated']

        return f'''# Import 模板

## Web 接口开发（V8 版本）

```python
import json
import logging
from django.views import View

# 装饰器（V8 版本）
from Common.web.auth_v8 import authenticated
from Common.web.http_v8 import formatting

# 异常处理
from Common.exception.defines import I18nErrorData, ABGeneralPurposeException

# 日志
logger = logging.getLogger('v7tov8Service')
```

## Web 接口开发（旧版本）

```python
import json
from django.views import View

# 装饰器（旧版本）
from Common.web.auth import authenticated
from Common.web.http import formatting

# 日志
from Common.log import logger
```

## 数据模型开发

```python
from django.db import models
```

## 服务层开发

```python
import logging
from django.db import transaction

# 日志
logger = logging.getLogger('v7tov8Service')
```

## 错误码定义

```python
# 位置: v7tov8Service/exception/upgrade_errorcode.py
from Common.exception.defines import I18nErrorData, ABGeneralPurposeException
from exception.upgrade_errorcode import (
    Upgrade_ParamsError,
    Upgrade_ObjectNotExists,
    Upgrade_Job_NotFound,
    # ... 其他错误码
)
```

## 测试开发

```python
from django.test import TestCase
import unittest
```

## 常用工具导入

```python
# Thrift 客户端
from Common.thrift.client import ThriftClient
from Common.thrift.thrift_util import webtasklogger

# 常量
from Common.constants import JobTypeEnum
from v7tov8Service.common.constants import JobType, JobStatus
```
'''

    def _generate_urls_md(self) -> str:
        """生成 urls.md"""
        entries = self.skeleton.get('entries', {})
        apis = entries.get('apis', [])

        api_table = []
        for api in apis[:15]:
            api_table.append(f"| {api.get('method', 'GET')} | `{api.get('name', '')}` | `{api.get('file_path', '')}` |")

        return f'''# URL 路由规范

## 路由配置

```python
from django.urls import path
from . import views

urlpatterns = [
    path('jobs/', views.JobListView.as_view()),
    path('job/<str:job_id>/', views.JobDetailView.as_view()),
]
```

## 现有 API 入口

| 方法 | 名称 | 文件 |
|------|------|------|
{chr(10).join(api_table)}
'''

    def _generate_models_reference_md(self) -> str:
        """生成 models_reference.md - 使用动态数据"""
        info = self._get_project_info()

        # 从 models 聚类获取模型信息
        models_examples = self._get_cluster_examples('models')

        # 按服务分组模型
        grouped = self._group_examples_by_service(models_examples)

        # 构建模型列表
        model_sections = []
        for service, examples in grouped.items():
            model_list = []
            for ex in examples:
                if ex.get('type') == 'class':
                    file_path = ex.get('file', '')
                    line = ex.get('line', 0)
                    model_list.append(f"- `{ex.get('name', '')}` - `{file_path}:{line}`")

            if model_list:
                model_sections.append(f"### {service}\n\n" + "\n".join(model_list))

        return f'''# 模型字段速查表

## 概述

本文件提供项目中所有数据模型的快速导航。

{chr(10).join(model_sections) if model_sections else f"""## 模型文件位置

查看模型字段时，直接打开对应的 `models.py` 文件：

- `{info['source_dir']}/models.py`"""}

## 使用说明

在 IDE 中打开对应文件并搜索类名即可查看字段定义。
'''


def generate_project_context(skeleton_path: str, output_dir: str) -> List[str]:
    """生成 project-context 的便捷函数"""
    generator = ProjectContextGenerator()
    return generator.generate(skeleton_path, output_dir)
