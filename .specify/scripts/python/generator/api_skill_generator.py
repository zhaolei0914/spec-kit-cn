# -*- coding: utf-8 -*-
"""
API Skill 文档生成器

生成供其他服务对接使用的 API Skill 文档
- SKILL.md: API 概述和导航
- api-spec.json: 结构化 API 规范
- endpoints/*.md: 按模块分组的 API 详情
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict


class ApiSkillGenerator:
    """API Skill 文档生成器"""

    def __init__(self):
        self.service_name = ""
        self.base_url = ""
        self.framework = ""
        self.version = "1.0.0"

    def generate(self, endpoints: List, framework: str, output_dir: str,
                 service_name: str = "", base_url: str = "") -> List[str]:
        """
        生成 API Skill 文档

        参数:
            endpoints: API 端点列表
            framework: Web 框架
            output_dir: 输出目录
            service_name: 服务名称（可选，自动检测）
            base_url: 基础 URL（可选，自动检测）

        返回: 生成的文件列表
        """
        self.framework = framework
        self.service_name = service_name or self._detect_service_name(endpoints)
        self.base_url = base_url or self._detect_base_url(endpoints)

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'endpoints'), exist_ok=True)

        generated_files = []

        # 1. 按模块分组
        modules = self._group_by_module(endpoints)

        # 2. 生成 api-spec.json（保留用于机器读取）
        spec_file = os.path.join(output_dir, 'api-spec.json')
        self._generate_api_spec(endpoints, modules, spec_file)
        generated_files.append(spec_file)

        # 3. 为每个接口生成单独的 md 文件
        for ep in endpoints:
            endpoint_id = self._generate_endpoint_id(ep)
            filename = endpoint_id + '.md'
            filepath = os.path.join(output_dir, 'endpoints', filename)
            self._generate_single_endpoint_doc(ep, filepath)
            generated_files.append(filepath)

        # 4. 生成 SKILL.md
        skill_file = os.path.join(output_dir, 'SKILL.md')
        self._generate_skill_md(endpoints, modules, skill_file)
        generated_files.append(skill_file)

        return generated_files

    def _detect_service_name(self, endpoints: List) -> str:
        """检测服务名称"""
        if not endpoints:
            return "API Service"

        # 从路径中提取
        paths = [ep.path for ep in endpoints if hasattr(ep, 'path')]
        if paths:
            # 取第一个路径段
            for path in paths:
                parts = path.strip('/').split('/')
                if parts and parts[0] not in ('api', 'v1', 'v2'):
                    return parts[0].replace('_', ' ').title() + " Service"

        # 从源文件路径提取
        for ep in endpoints:
            if hasattr(ep, 'source_file') and ep.source_file:
                parts = ep.source_file.split(os.sep)
                for part in parts:
                    if 'service' in part.lower():
                        return part.replace('_', ' ').title()

        return "API Service"

    def _detect_base_url(self, endpoints: List) -> str:
        """检测基础 URL"""
        if not endpoints:
            return ""

        paths = [ep.path for ep in endpoints if hasattr(ep, 'path')]
        if not paths:
            return ""

        # 找到公共前缀
        if len(paths) == 1:
            parts = paths[0].strip('/').split('/')
            if len(parts) >= 2:
                return '/' + '/'.join(parts[:2])
            return paths[0]

        # 多个路径，找公共前缀
        common = paths[0].strip('/').split('/')
        for path in paths[1:]:
            parts = path.strip('/').split('/')
            new_common = []
            for i, (a, b) in enumerate(zip(common, parts)):
                if a == b:
                    new_common.append(a)
                else:
                    break
            common = new_common
            if not common:
                break

        if common:
            return '/' + '/'.join(common)
        return ""

    def _group_by_module(self, endpoints: List) -> Dict[str, List]:
        """按模块分组"""
        modules = defaultdict(list)

        for ep in endpoints:
            # 尝试从路径推断模块
            path = ep.path if hasattr(ep, 'path') else ""
            parts = path.strip('/').split('/')

            module_name = "其他"
            if len(parts) >= 3:
                # /upgrade/v1/jobs -> jobs
                module_name = parts[2].replace('_', ' ').title()
            elif len(parts) >= 2:
                module_name = parts[1].replace('_', ' ').title()

            # 合并相似模块
            module_name = self._normalize_module_name(module_name)
            modules[module_name].append(ep)

        return dict(modules)

    def _normalize_module_name(self, name: str) -> str:
        """规范化模块名称"""
        # 合并相似名称
        name_lower = name.lower()
        if 'job' in name_lower:
            return "作业管理"
        elif 'sub_job' in name_lower or 'subjob' in name_lower:
            return "子作业管理"
        elif 'log' in name_lower:
            return "日志管理"
        elif 'user' in name_lower:
            return "用户管理"
        elif 'host' in name_lower:
            return "主机管理"
        elif 'client' in name_lower:
            return "客户端管理"
        elif 'config' in name_lower:
            return "配置管理"
        return name

    def _sanitize_filename(self, name: str) -> str:
        """转换为安全的文件名"""
        # 中文转拼音或保留
        import re
        # 移除特殊字符
        name = re.sub(r'[^\w\u4e00-\u9fa5]', '_', name)
        return name.lower()

    def _generate_api_spec(self, endpoints: List, modules: Dict, filepath: str):
        """生成 api-spec.json"""
        spec = {
            "service": {
                "name": self.service_name,
                "version": self.version,
                "base_url": self.base_url,
                "framework": self.framework,
                "generated_at": datetime.now().isoformat(),
            },
            "endpoints": [],
            "schemas": {},
        }

        for ep in endpoints:
            endpoint_data = {
                "id": self._generate_endpoint_id(ep),
                "path": ep.path if hasattr(ep, 'path') else "",
                "method": ep.method if hasattr(ep, 'method') else "GET",
                "summary": ep.summary if hasattr(ep, 'summary') else "",
                "description": ep.description if hasattr(ep, 'description') else "",
                "parameters": [],
                "request_body": ep.request_body if hasattr(ep, 'request_body') else {},
                "response": ep.response if hasattr(ep, 'response') else {},
                "errors": self._get_common_errors(),
            }

            # 添加参数
            if hasattr(ep, 'parameters'):
                for param in ep.parameters:
                    if hasattr(param, 'to_dict'):
                        endpoint_data["parameters"].append(param.to_dict())
                    elif isinstance(param, dict):
                        endpoint_data["parameters"].append(param)

            spec["endpoints"].append(endpoint_data)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(spec, f, ensure_ascii=False, indent=2)

    def _generate_endpoint_id(self, ep) -> str:
        """生成端点 ID"""
        method = (ep.method if hasattr(ep, 'method') else "get").lower()
        path = ep.path if hasattr(ep, 'path') else ""
        # /upgrade/v1/jobs -> upgrade_v1_jobs
        path_id = path.strip('/').replace('/', '_').replace('{', '').replace('}', '')
        return f"{method}_{path_id}"

    def _generate_single_endpoint_doc(self, ep, filepath: str):
        """为单个接口生成完整的文档"""
        method = ep.method if hasattr(ep, 'method') else "GET"
        path = ep.path if hasattr(ep, 'path') else ""
        summary = ep.summary if hasattr(ep, 'summary') else ""
        description = ep.description if hasattr(ep, 'description') else ""

        # 简化 summary
        if summary and ' - ' in summary:
            summary = summary.split(' - ', 1)[1]

        lines = [
            f"# {method} {path}",
            "",
            f"**{summary}**" if summary else "",
            "",
        ]

        if description:
            lines.extend([description, ""])

        # 设计追溯
        if hasattr(ep, 'design_ref') and ep.design_ref:
            lines.extend([f"*{ep.design_ref}*", ""])

        # 调用信息
        lines.extend([
            "## 调用信息",
            "",
            f"- **URL**: `{{BASE_URL}}{path}`",
            f"- **方法**: `{method}`",
            "- **认证**: 请求头携带 `Authorization: Bearer {token}`",
            "",
        ])

        # 请求参数
        params = ep.parameters if hasattr(ep, 'parameters') else []
        if params:
            lines.extend([
                "## 请求参数",
                "",
                "| 参数名 | 位置 | 类型 | 必填 | 默认值 | 描述 |",
                "|--------|------|------|------|--------|------|",
            ])
            for param in params:
                if hasattr(param, 'name'):
                    name = param.name
                    location = param.location if hasattr(param, 'location') else "query"
                    param_type = param.param_type if hasattr(param, 'param_type') else "string"
                    required = "是" if (param.required if hasattr(param, 'required') else False) else "否"
                    default = param.default if hasattr(param, 'default') else "-"
                    desc = param.description if hasattr(param, 'description') else ""
                    lines.append(f"| {name} | {location} | {param_type} | {required} | {default or '-'} | {desc} |")
                elif isinstance(param, dict):
                    name = param.get('name', '')
                    location = param.get('location', 'query')
                    param_type = param.get('param_type', 'string')
                    required = "是" if param.get('required', False) else "否"
                    default = param.get('default', '-')
                    desc = param.get('description', '')
                    lines.append(f"| {name} | {location} | {param_type} | {required} | {default or '-'} | {desc} |")
            lines.append("")
        else:
            lines.extend([
                "## 请求参数",
                "",
                "无",
                "",
            ])

        # 响应结构
        response = ep.response if hasattr(ep, 'response') else {}
        lines.extend([
            "## 响应结构",
            "",
            "```json",
            "{",
            '  "code": 0,',
            '  "message": "success",',
            f'  "data": {json.dumps(response, ensure_ascii=False) if response else "{}"}',
            "}",
            "```",
            "",
        ])

        # 响应字段说明
        if response:
            lines.extend([
                "### 响应字段",
                "",
                "| 字段 | 类型 | 描述 |",
                "|------|------|------|",
            ])
            for field, field_type in response.items():
                lines.append(f"| {field} | {field_type} | - |")
            lines.append("")

        # 示例请求
        lines.extend([
            "## 示例",
            "",
            "### 请求",
            "",
        ])

        if method == "GET":
            # 构造示例 URL
            example_params = []
            for param in params:
                if hasattr(param, 'name'):
                    name = param.name
                    default = param.default if hasattr(param, 'default') and param.default else self._get_example_value(name)
                else:
                    name = param.get('name', '')
                    default = param.get('default', '') or self._get_example_value(name)
                if default:
                    example_params.append(f"{name}={default}")

            example_url = path
            if example_params:
                example_url += "?" + "&".join(example_params[:3])  # 最多显示 3 个参数

            lines.extend([
                "```",
                f"GET {example_url}",
                "Authorization: Bearer {{token}}",
                "```",
                "",
            ])
        else:
            # POST 请求
            body_example = {}
            for param in params:
                if hasattr(param, 'name'):
                    name = param.name
                    location = param.location if hasattr(param, 'location') else 'body'
                else:
                    name = param.get('name', '')
                    location = param.get('location', 'body')
                if location == 'body':
                    body_example[name] = self._get_example_value(name)

            lines.extend([
                "```",
                f"POST {path}",
                "Authorization: Bearer {{token}}",
                "Content-Type: application/json",
                "",
                json.dumps(body_example, ensure_ascii=False, indent=2) if body_example else "{}",
                "```",
                "",
            ])

        # 示例响应
        lines.extend([
            "### 响应",
            "",
            "```json",
            "{",
            '  "code": 0,',
            '  "message": "success",',
        ])

        if response:
            response_example = self._generate_response_example(response)
            lines.append(f'  "data": {json.dumps(response_example, ensure_ascii=False, indent=4).replace(chr(10), chr(10) + "  ")}')
        else:
            lines.append('  "data": {}')

        lines.extend([
            "}",
            "```",
            "",
        ])

        # 错误处理
        lines.extend([
            "## 错误处理",
            "",
            "| 错误码 | 含义 | 处理建议 |",
            "|--------|------|----------|",
            "| 0 | 成功 | - |",
            "| 400 | 参数错误 | 检查请求参数 |",
            "| 401 | 未认证 | 检查 Token |",
            "| 403 | 无权限 | 检查权限 |",
            "| 404 | 资源不存在 | 检查 ID |",
            "| 500 | 服务器错误 | 重试或报告 |",
            "",
        ])

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def _get_example_value(self, name: str) -> str:
        """根据参数名生成示例值"""
        examples = {
            'index': '0',
            'offset': '0',
            'page': '1',
            'count': '15',
            'limit': '20',
            'size': '10',
            'type': '1',
            'status': '1',
            'filter': '',
            'keyword': '',
            'search': '',
            'name': 'example',
            'id': '123',
            'job_id': 'job_123',
            'jobId': 'job_123',
            'sub_job_id': 'sub_job_456',
            'subJobId': 'sub_job_456',
        }
        return examples.get(name, 'example')

    def _generate_response_example(self, response: Dict) -> Dict:
        """生成响应示例"""
        example = {}
        for field, field_type in response.items():
            if field_type == 'array':
                example[field] = [{"id": "1", "name": "示例"}]
            elif field_type == 'object':
                example[field] = {"key": "value"}
            elif field_type == 'integer':
                example[field] = 10
            elif field_type == 'number':
                example[field] = 10.5
            elif field_type == 'boolean':
                example[field] = True
            elif field_type == 'string':
                example[field] = "示例值"
            else:
                example[field] = "..."
        return example

    def _generate_endpoint_doc(self, module_name: str, endpoints: List, filepath: str):
        """生成单个模块的端点文档"""
        lines = [
            f"# {module_name} API",
            "",
        ]

        for ep in endpoints:
            method = ep.method if hasattr(ep, 'method') else "GET"
            path = ep.path if hasattr(ep, 'path') else ""
            summary = ep.summary if hasattr(ep, 'summary') else ep.handler if hasattr(ep, 'handler') else ""
            description = ep.description if hasattr(ep, 'description') else ""

            lines.append(f"## {method} {path}")
            lines.append("")
            if summary:
                lines.append(f"**{summary}**")
                lines.append("")
            if description:
                lines.append(description)
                lines.append("")

            # 设计追溯
            if hasattr(ep, 'design_ref') and ep.design_ref:
                lines.append(f"*{ep.design_ref}*")
                lines.append("")

            # 请求参数
            params = ep.parameters if hasattr(ep, 'parameters') else []
            if params:
                lines.append("### 请求参数")
                lines.append("")
                lines.append("| 参数名 | 位置 | 类型 | 必填 | 默认值 | 描述 |")
                lines.append("|--------|------|------|------|--------|------|")
                for param in params:
                    if hasattr(param, 'name'):
                        name = param.name
                        location = param.location if hasattr(param, 'location') else "query"
                        param_type = param.param_type if hasattr(param, 'param_type') else "string"
                        required = "是" if (param.required if hasattr(param, 'required') else False) else "否"
                        default = param.default if hasattr(param, 'default') else "-"
                        desc = param.description if hasattr(param, 'description') else ""
                        lines.append(f"| {name} | {location} | {param_type} | {required} | {default or '-'} | {desc} |")
                    elif isinstance(param, dict):
                        name = param.get('name', '')
                        location = param.get('location', 'query')
                        param_type = param.get('param_type', 'string')
                        required = "是" if param.get('required', False) else "否"
                        default = param.get('default', '-')
                        desc = param.get('description', '')
                        lines.append(f"| {name} | {location} | {param_type} | {required} | {default or '-'} | {desc} |")
                lines.append("")

            # 响应结构
            response = ep.response if hasattr(ep, 'response') else {}
            if response:
                lines.append("### 响应结构")
                lines.append("")
                lines.append("```json")
                lines.append(json.dumps(response, ensure_ascii=False, indent=2))
                lines.append("```")
                lines.append("")

            # 错误处理
            lines.append("### 错误处理")
            lines.append("")
            lines.append("| 错误码 | 含义 | 处理建议 |")
            lines.append("|--------|------|----------|")
            lines.append("| 0 | 成功 | - |")
            lines.append("| 400 | 参数错误 | 检查请求参数 |")
            lines.append("| 401 | 未认证 | 检查 Token |")
            lines.append("| 403 | 无权限 | 检查权限 |")
            lines.append("| 404 | 资源不存在 | 检查 ID |")
            lines.append("| 500 | 服务器错误 | 重试或联系管理员 |")
            lines.append("")

            lines.append("---")
            lines.append("")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def _generate_skill_md(self, endpoints: List, modules: Dict, filepath: str):
        """生成 SKILL.md - 遵循 Anthropic Agent Skills 最佳实践"""
        # 统计信息
        total = len(endpoints)

        # 检测认证方式
        auth_type = self._detect_auth_type(endpoints)

        # 生成 description（200字符内，说明何时使用）
        short_desc = f"调用 {self.service_name} API 接口。用于外部服务对接、前端开发、API 测试时查询接口参数和响应格式。"
        if len(short_desc) > 200:
            short_desc = short_desc[:197] + "..."

        # 按照 Anthropic Skills 最佳实践生成
        lines = [
            "---",
            f"name: {self.service_name.lower().replace(' ', '-')}",
            f"description: {short_desc}",
            "---",
            "",
            f"# {self.service_name} API",
            "",
            f"调用 **{self.service_name}** 的 API 接口，包含 {total} 个端点。",
            "",
            "## 何时使用",
            "",
            "- **外部服务对接**：了解接口参数和响应格式",
            "- **前端开发**：查询 API 端点和数据结构",
            "- **API 测试**：获取请求示例和错误码",
            "- **接口文档查阅**：快速定位接口详情",
            "",
            "## 概述",
            "",
            f"- **基础路径**: `{self.base_url}`",
            f"- **接口总数**: {total}",
            f"- **认证方式**: {auth_type}",
            "",
            "## 调用规范",
            "",
            "### 请求",
            "",
            "- **URL**: `{BASE_URL}" + self.base_url + "/{endpoint}`",
            "- **认证**: 请求头携带 `Authorization: Bearer {token}`",
            "- **GET 请求**: 参数通过 Query String 传递",
            "- **POST 请求**: 参数通过 JSON Body 传递，`Content-Type: application/json`",
            "",
            "### 响应",
            "",
            "```json",
            "{",
            '  "code": 0,',
            '  "message": "success",',
            '  "data": { ... }',
            "}",
            "```",
            "",
            "### 错误码",
            "",
            "| code | 含义 | 处理方式 |",
            "|------|------|----------|",
            "| 0 | 成功 | 正常处理 data |",
            "| 400 | 参数错误 | 检查请求参数 |",
            "| 401 | 未认证 | 检查 Token |",
            "| 403 | 无权限 | 检查权限 |",
            "| 404 | 资源不存在 | 检查资源 ID |",
            "| 500 | 服务器错误 | 重试或报告 |",
            "",
            "## 接口索引",
            "",
        ]

        # 按模块列出接口，每个接口链接到单独的文件
        for module_name, module_endpoints in modules.items():
            lines.append(f"### {module_name}")
            lines.append("")
            lines.append("| 方法 | 路径 | 描述 | 文档 |")
            lines.append("|------|------|------|------|")
            for ep in module_endpoints:
                method = ep.method if hasattr(ep, 'method') else "GET"
                path = ep.path if hasattr(ep, 'path') else ""
                summary = ep.summary if hasattr(ep, 'summary') else ""
                # 简化 summary
                if summary and ' - ' in summary:
                    summary = summary.split(' - ', 1)[1]
                # 生成文件名
                endpoint_id = self._generate_endpoint_id(ep)
                lines.append(f"| {method} | `{path}` | {summary} | [详情](./endpoints/{endpoint_id}.md) |")
            lines.append("")

        lines.extend([
            "## 使用说明",
            "",
            "1. 在上方索引中找到需要的接口",
            "2. 点击「详情」链接查看完整的参数和响应结构",
            "3. 按照文档中的调用信息发起请求",
            "",
            "## 示例",
            "",
            "**场景**：查询列表接口",
            "",
            "```",
            "1. 在索引中找到 GET 请求 → 点击 [详情]",
            "2. 查看请求参数：page, page_size, filter 等",
            "3. 查看响应结构：data.list, data.total",
            "4. 发起请求：",
            f"   GET {{BASE_URL}}{self.base_url}/xxx?page=1&page_size=10",
            "   Authorization: Bearer {token}",
            "```",
            "",
            "**场景**：创建资源接口",
            "",
            "```",
            "1. 在索引中找到 POST 请求 → 点击 [详情]",
            "2. 查看请求参数和必填字段",
            "3. 查看响应结构和错误码",
            "4. 发起请求：",
            f"   POST {{BASE_URL}}{self.base_url}/xxx",
            "   Content-Type: application/json",
            "   Authorization: Bearer {token}",
            '   {"name": "示例", ...}',
            "```",
            "",
        ])

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def _detect_auth_type(self, endpoints: List) -> str:
        """检测认证方式"""
        for ep in endpoints:
            decorators = ep.decorators if hasattr(ep, 'decorators') else []
            for dec in decorators:
                if 'authenticated' in dec.lower():
                    return "Bearer Token 认证。请求头需携带 `Authorization: Bearer {token}`"
                if 'login_required' in dec.lower():
                    return "Session 认证。需要先登录获取 Session"
                if 'api_key' in dec.lower():
                    return "API Key 认证。请求头需携带 `X-API-Key: {api_key}`"
        return "请参考具体接口文档"

    def _get_common_errors(self) -> List[Dict]:
        """获取通用错误码"""
        return [
            {"code": 0, "message": "成功", "action": "-"},
            {"code": 400, "message": "参数错误", "action": "检查请求参数"},
            {"code": 401, "message": "未认证", "action": "检查 Token"},
            {"code": 403, "message": "无权限", "action": "检查权限"},
            {"code": 404, "message": "资源不存在", "action": "检查 ID"},
            {"code": 500, "message": "服务器错误", "action": "重试或联系管理员"},
        ]


def generate_api_skill(endpoints: List, framework: str, output_dir: str,
                       service_name: str = "", base_url: str = "") -> List[str]:
    """生成 API Skill 的便捷函数"""
    generator = ApiSkillGenerator()
    return generator.generate(endpoints, framework, output_dir, service_name, base_url)
