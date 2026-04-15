# -*- coding: utf-8 -*-
"""
业务规则生成器

基于入口分析结果生成业务规则 Markdown 文档
"""
import os
import sys
from typing import List, Dict
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .entry_analyzer import BusinessFlow, EntryPoint, FunctionCall, BusinessCondition, StateChange


class BusinessRuleGenerator:
    """业务规则生成器"""

    def __init__(self):
        pass

    def generate(self, flows: List[BusinessFlow], output_dir: str) -> List[str]:
        """生成业务规则文档"""
        os.makedirs(output_dir, exist_ok=True)
        generated_files = []

        # 按类型分组
        api_flows = [f for f in flows if f.entry.type == 'api']
        handler_flows = [f for f in flows if f.entry.type == 'handler']

        # 为每个 API 生成单独的文件
        if api_flows:
            api_dir = os.path.join(output_dir, 'api')
            os.makedirs(api_dir, exist_ok=True)
            for flow in api_flows:
                filename = self._generate_entry_filename(flow.entry)
                filepath = os.path.join(api_dir, filename)
                content = self._generate_single_entry_doc(flow)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                generated_files.append(filepath)

        # 为每个 Handler 生成单独的文件
        if handler_flows:
            handler_dir = os.path.join(output_dir, 'handler')
            os.makedirs(handler_dir, exist_ok=True)
            for flow in handler_flows:
                filename = self._generate_entry_filename(flow.entry)
                filepath = os.path.join(handler_dir, filename)
                content = self._generate_single_entry_doc(flow)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                generated_files.append(filepath)

        # 生成汇总文档
        summary_file = os.path.join(output_dir, 'BUSINESS_RULES.md')
        content = self._generate_summary(flows, api_flows, handler_flows)
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(content)
        generated_files.append(summary_file)

        # 生成 SKILL.md（符合 Anthropic Agent Skills 最佳实践）
        skill_file = os.path.join(output_dir, 'SKILL.md')
        content = self._generate_skill_md(len(api_flows), len(handler_flows))
        with open(skill_file, 'w', encoding='utf-8') as f:
            f.write(content)
        generated_files.append(skill_file)

        return generated_files

    def _generate_entry_filename(self, entry) -> str:
        """生成入口文件名"""
        # 使用入口名称生成文件名
        name = entry.name
        # 转换为小写下划线格式
        import re
        # 处理 PascalCase -> snake_case
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
        # 移除特殊字符
        name = re.sub(r'[^a-z0-9_]', '_', name)
        # 移除连续下划线
        name = re.sub(r'_+', '_', name).strip('_')
        return f"{name}.md"

    def _generate_single_entry_doc(self, flow: BusinessFlow) -> str:
        """生成单个入口的完整文档"""
        entry = flow.entry
        lines = []

        # 标题
        if entry.type == 'api':
            title = f"# {entry.method} {entry.path or entry.name}"
        else:
            title = f"# {entry.name}"
        lines.append(title)
        lines.append("")

        # 描述
        if entry.description:
            lines.append(f"**{entry.description}**")
            lines.append("")

        # 入口信息
        lines.append("## 入口信息")
        lines.append("")
        lines.append(f"- **类型**: `{entry.type}`")
        lines.append(f"- **处理器**: `{entry.name}`")
        lines.append(f"- **文件**: `{entry.file_path}:{entry.line}`")
        if entry.decorators:
            lines.append(f"- **装饰器**: {', '.join(f'`@{d}`' for d in entry.decorators)}")
        lines.append("")

        # 调用链
        if flow.call_chain:
            lines.append("## 调用链")
            lines.append("")
            seen = set()
            unique_calls = []
            for call in flow.call_chain:
                key = f"{call.caller}->{call.callee}"
                if key not in seen:
                    seen.add(key)
                    unique_calls.append(call)

            for i, call in enumerate(unique_calls, 1):
                args = ', '.join(call.arguments) if call.arguments else ''
                lines.append(f"{i}. `{call.caller}` → `{call.callee}({args})`")
            lines.append("")

        # 业务条件
        if flow.conditions:
            lines.append("## 业务条件")
            lines.append("")
            lines.append("| 条件 | 上下文 | 位置 |")
            lines.append("|------|--------|------|")

            seen = set()
            for cond in flow.conditions:
                if cond.expression in seen:
                    continue
                seen.add(cond.expression)
                expr = cond.expression[:80] + '...' if len(cond.expression) > 80 else cond.expression
                lines.append(f"| `{expr}` | {cond.context} | L{cond.line} |")
            lines.append("")

        # 状态变更
        if flow.state_changes:
            lines.append("## 状态变更")
            lines.append("")
            lines.append("| 对象 | 字段 | 新值 | 上下文 |")
            lines.append("|------|------|------|--------|")

            for change in flow.state_changes:
                lines.append(f"| `{change.target}` | `{change.field}` | `{change.value}` | {change.context} |")
            lines.append("")

        return '\n'.join(lines)

    def _generate_flow_section(self, flow: BusinessFlow) -> List[str]:
        """生成单个业务流程的文档"""
        entry = flow.entry
        lines = []

        # 标题
        if entry.type == 'api':
            title = f"### {entry.method} {entry.path or entry.name}"
        else:
            title = f"### {entry.name}"
        lines.append(title)
        lines.append("")

        # 描述
        if entry.description:
            lines.append(f"**描述**: {entry.description}")
            lines.append("")

        # 入口信息
        lines.append("**入口信息**")
        lines.append("")
        lines.append(f"- 类型: `{entry.type}`")
        lines.append(f"- 处理器: `{entry.name}`")
        lines.append(f"- 文件: `{os.path.basename(entry.file_path)}:{entry.line}`")
        if entry.decorators:
            lines.append(f"- 装饰器: {', '.join(f'`@{d}`' for d in entry.decorators)}")
        lines.append("")

        # 调用链
        if flow.call_chain:
            lines.append("**调用链**")
            lines.append("")
            # 去重并保持顺序
            seen = set()
            unique_calls = []
            for call in flow.call_chain:
                key = f"{call.caller}->{call.callee}"
                if key not in seen:
                    seen.add(key)
                    unique_calls.append(call)

            for i, call in enumerate(unique_calls[:10], 1):
                args = ', '.join(call.arguments) if call.arguments else ''
                lines.append(f"{i}. `{call.caller}` → `{call.callee}({args})`")

            if len(unique_calls) > 10:
                lines.append(f"   *... 还有 {len(unique_calls) - 10} 个调用*")
            lines.append("")

        # 业务条件
        if flow.conditions:
            lines.append("**业务条件**")
            lines.append("")
            lines.append("| 条件 | 上下文 | 位置 |")
            lines.append("|------|--------|------|")

            seen = set()
            for cond in flow.conditions[:10]:
                if cond.expression in seen:
                    continue
                seen.add(cond.expression)

                expr = cond.expression[:60] + '...' if len(cond.expression) > 60 else cond.expression
                lines.append(f"| `{expr}` | {cond.context} | L{cond.line} |")

            if len(flow.conditions) > 10:
                lines.append(f"| *... 还有 {len(flow.conditions) - 10} 个条件* | | |")
            lines.append("")

        # 状态变更
        if flow.state_changes:
            lines.append("**状态变更**")
            lines.append("")
            lines.append("| 对象 | 字段 | 新值 | 上下文 |")
            lines.append("|------|------|------|--------|")

            for change in flow.state_changes[:10]:
                lines.append(f"| `{change.target}` | `{change.field}` | `{change.value}` | {change.context} |")
            lines.append("")

        return lines

    def _generate_summary(self, all_flows: List[BusinessFlow],
                          api_flows: List[BusinessFlow],
                          handler_flows: List[BusinessFlow]) -> str:
        """生成汇总文档"""
        lines = [
            "# 业务规则汇总",
            "",
            f"*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            "",
            "## 概览",
            "",
            f"- **总入口数**: {len(all_flows)}",
            f"- **API 接口**: {len(api_flows)}",
            f"- **定时任务/Handler**: {len(handler_flows)}",
            "",
            "## 详细规则",
            "",
        ]

        if api_flows:
            lines.append(f"- API 业务规则: `api/` 目录下 {len(api_flows)} 个文件")
        if handler_flows:
            lines.append(f"- Handler 业务规则: `handler/` 目录下 {len(handler_flows)} 个文件")

        lines.append("")
        lines.append("## API 入口索引")
        lines.append("")
        lines.append("| 方法 | 路径/名称 | 描述 | 详情 |")
        lines.append("|------|-----------|------|------|")

        for flow in api_flows:
            entry = flow.entry
            path = entry.path or entry.name
            desc = entry.description[:30] + '...' if len(entry.description) > 30 else entry.description
            filename = self._generate_entry_filename(entry)
            lines.append(f"| {entry.method} | `{path}` | {desc} | [查看](./api/{filename}) |")

        lines.append("")

        if handler_flows:
            lines.append("## Handler 入口索引")
            lines.append("")
            lines.append("| 名称 | 描述 | 详情 |")
            lines.append("|------|------|------|")

            for flow in handler_flows:
                entry = flow.entry
                desc = entry.description[:40] + '...' if len(entry.description) > 40 else entry.description
                filename = self._generate_entry_filename(entry)
                lines.append(f"| `{entry.name}` | {desc} | [查看](./handler/{filename}) |")

            lines.append("")

        # 统计业务条件
        all_conditions = []
        for flow in all_flows:
            all_conditions.extend(flow.conditions)

        if all_conditions:
            lines.append("## 常见业务条件")
            lines.append("")

            # 统计条件出现频率
            condition_count = {}
            for cond in all_conditions:
                # 简化条件表达式
                expr = cond.expression
                if expr in condition_count:
                    condition_count[expr] += 1
                else:
                    condition_count[expr] = 1

            # 按频率排序
            sorted_conditions = sorted(condition_count.items(), key=lambda x: x[1], reverse=True)

            lines.append("| 条件 | 出现次数 |")
            lines.append("|------|----------|")

            for expr, count in sorted_conditions[:15]:
                if count > 1:
                    expr_display = expr[:50] + '...' if len(expr) > 50 else expr
                    lines.append(f"| `{expr_display}` | {count} |")

            lines.append("")

        # 统计状态变更
        all_changes = []
        for flow in all_flows:
            all_changes.extend(flow.state_changes)

        if all_changes:
            lines.append("## 状态变更汇总")
            lines.append("")

            # 按字段分组
            by_field = {}
            for change in all_changes:
                if change.field not in by_field:
                    by_field[change.field] = set()
                by_field[change.field].add(change.value)

            lines.append("| 字段 | 可能的值 |")
            lines.append("|------|----------|")

            for field, values in sorted(by_field.items()):
                values_str = ', '.join(f'`{v}`' for v in list(values)[:5])
                if len(values) > 5:
                    values_str += f' *... 还有 {len(values) - 5} 个*'
                lines.append(f"| `{field}` | {values_str} |")

            lines.append("")

        return '\n'.join(lines)

    def _generate_skill_md(self, api_count: int, handler_count: int) -> str:
        """生成符合 Anthropic Agent Skills 最佳实践的 SKILL.md"""
        return f'''---
name: business-rules
description: 查询项目业务规则，了解 API 和 Handler 的调用链、业务条件、状态变更。用于修改现有功能或添加相似功能时参考。
---

# 业务规则 Skill

理解项目中 API 和 Handler 的业务逻辑，包括调用链、业务条件判断、状态变更。

## 何时使用

- **修改现有 API**：了解当前的业务条件和调用链
- **添加相似功能**：参考现有入口的实现模式
- **排查业务问题**：追踪状态变更和条件判断
- **代码审查**：验证业务逻辑是否正确

## 如何使用

1. 打开 `BUSINESS_RULES.md` 查看所有入口索引
2. 找到目标入口，点击「查看」链接
3. 阅读单个入口的详细规则

## 示例

**场景**：修改某个 API 的过滤逻辑

```
1. 打开 BUSINESS_RULES.md
2. 找到目标 API → 点击 [查看] 链接
3. 查看业务条件表格，了解现有过滤条件
4. 根据条件添加新的过滤逻辑
```

**场景**：添加新的列表 API

```
1. 找到类似功能的现有 API
2. 复制其调用链和业务条件模式
3. 根据新业务需求调整
```

## 文件结构

```
business-rules/
├── SKILL.md              ← 你在这里
├── BUSINESS_RULES.md     (入口索引)
├── api/                  ({api_count} 个 API 规则文件)
└── handler/              ({handler_count} 个 Handler 规则文件)
```

## 每个规则文件包含

- **入口信息**：类型、处理器、文件位置、装饰器
- **调用链**：函数调用顺序
- **业务条件**：if 判断条件及上下文
- **状态变更**：数据库字段修改
'''


def generate_business_rules(flows: List[BusinessFlow], output_dir: str) -> List[str]:
    """生成业务规则的便捷函数"""
    generator = BusinessRuleGenerator()
    return generator.generate(flows, output_dir)
