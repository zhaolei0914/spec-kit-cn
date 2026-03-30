# -*- coding: utf-8 -*-
"""
API 信息抽取器

从业务代码中提取完整的 API 接口信息
- 关联 URL 路由和 Handler
- 提取请求参数
- 提取响应结构
"""
import ast
import os
import re
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict

from .url_route_extractor import UrlRoute, UrlRouteExtractor


@dataclass
class ApiParameter:
    """API 参数"""
    name: str                       # 参数名
    location: str = "query"         # 位置: query, path, body, header
    param_type: str = "string"      # 类型
    required: bool = False          # 是否必填
    default: str = ""               # 默认值
    description: str = ""           # 描述

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ApiEndpoint:
    """API 端点"""
    path: str                       # URL 路径
    method: str                     # HTTP 方法
    handler: str                    # Handler 类/函数名
    summary: str = ""               # 摘要
    description: str = ""           # 描述
    tags: List[str] = field(default_factory=list)  # 标签
    parameters: List[ApiParameter] = field(default_factory=list)  # 参数
    request_body: Dict = field(default_factory=dict)  # 请求体
    response: Dict = field(default_factory=dict)  # 响应结构
    decorators: List[str] = field(default_factory=list)  # 装饰器
    source_file: str = ""           # 源文件
    source_line: int = 0            # 行号
    design_ref: str = ""            # 设计追溯

    def to_dict(self) -> dict:
        result = asdict(self)
        result['parameters'] = [p.to_dict() if hasattr(p, 'to_dict') else p for p in self.parameters]
        return result


class ApiExtractor:
    """API 信息抽取器"""

    def __init__(self):
        self.endpoints: List[ApiEndpoint] = []
        self.framework: str = ""
        self.file_asts: Dict[str, ast.AST] = {}
        self.file_contents: Dict[str, List[str]] = {}
        self.classes: Dict[str, Tuple[ast.ClassDef, str]] = {}  # 类名 -> (AST, 文件路径)

    def extract(self, source_dir: str) -> Tuple[List[ApiEndpoint], str]:
        """
        从源码目录提取所有 API 信息

        返回: (API 端点列表, 框架)
        """
        # 1. 提取 URL 路由
        route_extractor = UrlRouteExtractor()
        routes, self.framework = route_extractor.extract_routes(source_dir)

        # 2. 解析所有 Python 文件
        self._parse_directory(source_dir)

        # 3. 关联路由和 Handler
        self.endpoints = []
        for route in routes:
            endpoint = self._analyze_route(route, source_dir)
            if endpoint:
                self.endpoints.append(endpoint)

        return self.endpoints, self.framework

    def _parse_directory(self, source_dir: str):
        """解析目录下所有 Python 文件"""
        exclude_dirs = {'__pycache__', '.git', 'migrations', 'Thrift', 'node_modules'}

        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for filename in files:
                if not filename.endswith('.py'):
                    continue

                filepath = os.path.join(root, filename)
                self._parse_file(filepath)

    def _parse_file(self, filepath: str):
        """解析单个文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                self.file_contents[filepath] = content.split('\n')
        except Exception:
            return

        try:
            tree = ast.parse(content)
            self.file_asts[filepath] = tree
        except SyntaxError:
            return

        # 收集类定义
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self.classes[node.name] = (node, filepath)

    def _analyze_route(self, route: UrlRoute, source_dir: str) -> Optional[ApiEndpoint]:
        """分析单个路由"""
        handler_name = route.handler
        if not handler_name:
            return None

        # 查找 Handler 类/函数
        handler_node, handler_file = self._find_handler(handler_name, route, source_dir)
        if not handler_node:
            # 即使找不到 Handler，也返回基本信息
            return ApiEndpoint(
                path=route.path,
                method=route.method,
                handler=handler_name,
                source_file=route.source_file,
                source_line=route.source_line,
            )

        # 分析 Handler
        if isinstance(handler_node, ast.ClassDef):
            return self._analyze_class_handler(route, handler_node, handler_file)
        elif isinstance(handler_node, ast.FunctionDef) or isinstance(handler_node, ast.AsyncFunctionDef):
            return self._analyze_function_handler(route, handler_node, handler_file)

        return None

    def _find_handler(self, handler_name: str, route: UrlRoute, source_dir: str) -> Tuple[Optional[ast.AST], str]:
        """查找 Handler"""
        # 1. 直接从类缓存查找
        if handler_name in self.classes:
            return self.classes[handler_name]

        # 2. 根据模块名查找
        if route.handler_module:
            module_path = route.handler_module.replace('.', '/')
            possible_files = [
                os.path.join(source_dir, f"{module_path}.py"),
                os.path.join(os.path.dirname(route.source_file), f"{route.handler_module}.py"),
            ]
            for filepath in possible_files:
                if filepath in self.file_asts:
                    tree = self.file_asts[filepath]
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and node.name == handler_name:
                            return node, filepath
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == handler_name:
                            return node, filepath

        # 3. 在同目录下查找
        route_dir = os.path.dirname(route.source_file)
        for filepath, tree in self.file_asts.items():
            if not filepath.startswith(route_dir):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == handler_name:
                    return node, filepath

        return None, ""

    def _analyze_class_handler(self, route: UrlRoute, node: ast.ClassDef, filepath: str) -> ApiEndpoint:
        """分析类 Handler（Django View）"""
        # 提取类 docstring
        class_docstring = ast.get_docstring(node) or ""
        summary, description, design_ref = self._parse_docstring(class_docstring)

        # 查找 HTTP 方法
        methods = []
        parameters = []
        response = {}
        decorators = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_name = item.name.lower()
                if method_name in ('get', 'post', 'put', 'delete', 'patch'):
                    methods.append(method_name.upper())

                    # 提取方法 docstring
                    method_docstring = ast.get_docstring(item) or ""
                    if method_docstring and not summary:
                        summary, description, design_ref = self._parse_docstring(method_docstring)

                    # 提取装饰器
                    for dec in item.decorator_list:
                        dec_name = self._get_decorator_name(dec)
                        if dec_name:
                            decorators.append(dec_name)

                    # 提取参数
                    params = self._extract_parameters(item, method_name, filepath)
                    parameters.extend(params)

                    # 提取响应结构
                    resp = self._extract_response(item)
                    if resp:
                        response = resp

        # 确定 HTTP 方法
        method = route.method
        if method == "*" and methods:
            method = methods[0]  # 取第一个方法

        # 添加路径参数
        for param_name in route.path_params:
            if not any(p.name == param_name for p in parameters):
                parameters.insert(0, ApiParameter(
                    name=param_name,
                    location="path",
                    param_type="string",
                    required=True,
                ))

        return ApiEndpoint(
            path=route.path,
            method=method,
            handler=node.name,
            summary=summary or node.name,
            description=description,
            parameters=parameters,
            response=response,
            decorators=decorators,
            source_file=filepath,
            source_line=node.lineno,
            design_ref=design_ref,
        )

    def _analyze_function_handler(self, route: UrlRoute, node, filepath: str) -> ApiEndpoint:
        """分析函数 Handler（Flask/FastAPI）"""
        # 提取 docstring
        docstring = ast.get_docstring(node) or ""
        summary, description, design_ref = self._parse_docstring(docstring)

        # 提取装饰器
        decorators = []
        for dec in node.decorator_list:
            dec_name = self._get_decorator_name(dec)
            if dec_name:
                decorators.append(dec_name)

        # 提取参数
        parameters = self._extract_function_parameters(node, route.method, filepath)

        # 添加路径参数
        for param_name in route.path_params:
            if not any(p.name == param_name for p in parameters):
                parameters.insert(0, ApiParameter(
                    name=param_name,
                    location="path",
                    param_type="string",
                    required=True,
                ))

        # 提取响应结构
        response = self._extract_response(node)

        return ApiEndpoint(
            path=route.path,
            method=route.method,
            handler=node.name,
            summary=summary or node.name,
            description=description,
            parameters=parameters,
            response=response,
            decorators=decorators,
            source_file=filepath,
            source_line=node.lineno,
            design_ref=design_ref,
        )

    def _parse_docstring(self, docstring: str) -> Tuple[str, str, str]:
        """解析 docstring"""
        if not docstring:
            return "", "", ""

        lines = docstring.strip().split('\n')
        summary = lines[0].strip() if lines else ""
        description = ""
        design_ref = ""

        # 提取设计追溯
        for line in lines:
            if '设计追溯' in line or 'design' in line.lower():
                design_ref = line.strip()
                break

        # 提取描述
        if len(lines) > 1:
            desc_lines = [l.strip() for l in lines[1:] if l.strip() and '设计追溯' not in l]
            description = ' '.join(desc_lines)

        return summary, description, design_ref

    def _get_decorator_name(self, decorator) -> str:
        """获取装饰器名称"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        return ""

    def _extract_parameters(self, node: ast.FunctionDef, method: str, filepath: str) -> List[ApiParameter]:
        """从 Django View 方法提取参数"""
        parameters = []
        lines = self.file_contents.get(filepath, [])

        for child in ast.walk(node):
            # 检测类型转换: int(request.GET.get('xxx'))
            if isinstance(child, ast.Call):
                param = self._parse_typed_get_call(child)
                if param:
                    parameters.append(param)
                    continue

            # request.GET.get('xxx')
            if isinstance(child, ast.Call):
                call_str = self._get_call_string(child)
                if '.GET.get' in call_str or '.args.get' in call_str:
                    param = self._parse_get_call(child, "query")
                    if param:
                        parameters.append(param)
                elif '.POST.get' in call_str or '.form.get' in call_str:
                    param = self._parse_get_call(child, "body")
                    if param:
                        parameters.append(param)

            # json.loads(request.body) 后的 body.get('xxx')
            if isinstance(child, ast.Call):
                call_str = self._get_call_string(child)
                if '.get(' in call_str and 'body' in call_str.lower():
                    param = self._parse_body_get_call(child)
                    if param:
                        parameters.append(param)

        # 去重
        seen = set()
        unique_params = []
        for p in parameters:
            if p.name not in seen:
                seen.add(p.name)
                unique_params.append(p)

        return unique_params

    def _extract_function_parameters(self, node, method: str, filepath: str) -> List[ApiParameter]:
        """从函数签名提取参数（FastAPI 风格）"""
        parameters = []

        # 从函数参数提取（FastAPI 风格）
        for arg in node.args.args:
            if arg.arg in ('self', 'request', 'cls'):
                continue

            param_type = "string"
            if arg.annotation:
                param_type = self._get_type_annotation(arg.annotation)

            # 检查是否有默认值
            required = True
            default = ""
            # 这里简化处理，实际需要匹配 defaults

            parameters.append(ApiParameter(
                name=arg.arg,
                location="query" if method == "GET" else "body",
                param_type=param_type,
                required=required,
                default=default,
            ))

        # 也检查函数体内的参数获取
        body_params = self._extract_parameters(node, method, filepath)
        for p in body_params:
            if not any(ep.name == p.name for ep in parameters):
                parameters.append(p)

        return parameters

    def _get_type_annotation(self, annotation) -> str:
        """获取类型注解"""
        if isinstance(annotation, ast.Name):
            type_map = {
                'int': 'integer',
                'str': 'string',
                'bool': 'boolean',
                'float': 'number',
                'list': 'array',
                'dict': 'object',
            }
            return type_map.get(annotation.id.lower(), annotation.id)
        elif isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                if annotation.value.id in ('List', 'list'):
                    return 'array'
                elif annotation.value.id in ('Dict', 'dict'):
                    return 'object'
        return "string"

    def _get_call_string(self, node: ast.Call) -> str:
        """获取调用字符串"""
        if isinstance(node.func, ast.Attribute):
            value = self._expr_to_string(node.func.value)
            return f"{value}.{node.func.attr}"
        elif isinstance(node.func, ast.Name):
            return node.func.id
        return ""

    def _expr_to_string(self, node) -> str:
        """表达式转字符串"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value = self._expr_to_string(node.value)
            return f"{value}.{node.attr}"
        return ""

    def _parse_get_call(self, node: ast.Call, location: str) -> Optional[ApiParameter]:
        """解析 .get() 调用"""
        if not node.args:
            return None

        # 第一个参数是参数名
        if isinstance(node.args[0], ast.Constant):
            name = str(node.args[0].value)
        elif isinstance(node.args[0], ast.Str):  # Python 3.7
            name = node.args[0].s
        else:
            return None

        # 第二个参数是默认值
        default = ""
        required = True
        if len(node.args) > 1:
            required = False
            if isinstance(node.args[1], ast.Constant):
                default = str(node.args[1].value)

        # 推断参数类型和描述
        param_type, description = self._infer_param_info(name)

        return ApiParameter(
            name=name,
            location=location,
            param_type=param_type,
            required=required,
            default=default,
            description=description,
        )

    def _infer_param_info(self, name: str) -> Tuple[str, str]:
        """根据参数名推断类型和描述"""
        # 常见参数名映射
        param_info = {
            # 分页参数
            'index': ('integer', '分页起始位置'),
            'offset': ('integer', '分页偏移量'),
            'page': ('integer', '页码'),
            'count': ('integer', '每页数量'),
            'limit': ('integer', '返回数量限制'),
            'size': ('integer', '每页大小'),
            # ID 参数
            'id': ('string', '资源 ID'),
            'job_id': ('string', '作业 ID'),
            'jobId': ('string', '作业 ID'),
            'sub_job_id': ('string', '子作业 ID'),
            'subJobId': ('string', '子作业 ID'),
            # 筛选参数
            'type': ('integer', '类型筛选'),
            'status': ('integer', '状态筛选'),
            'filter': ('string', '关键词筛选'),
            'keyword': ('string', '搜索关键词'),
            'search': ('string', '搜索关键词'),
            'name': ('string', '名称'),
            # 时间参数
            'start_time': ('integer', '开始时间戳'),
            'end_time': ('integer', '结束时间戳'),
            'startTime': ('integer', '开始时间戳'),
            'endTime': ('integer', '结束时间戳'),
            # 排序参数
            'sort': ('string', '排序字段'),
            'order': ('string', '排序方向 (asc/desc)'),
        }

        if name in param_info:
            return param_info[name]

        # 根据命名规则推断
        name_lower = name.lower()
        if name_lower.endswith('id') or name_lower.endswith('_id'):
            return ('string', f'{name} 标识符')
        if name_lower.endswith('time') or name_lower.endswith('_time'):
            return ('integer', '时间戳 (毫秒)')
        if name_lower.endswith('count') or name_lower.endswith('num'):
            return ('integer', '数量')
        if name_lower.startswith('is_') or name_lower.startswith('has_'):
            return ('boolean', '布尔标志')

        return ('string', '')

    def _parse_body_get_call(self, node: ast.Call) -> Optional[ApiParameter]:
        """解析 body.get() 调用"""
        return self._parse_get_call(node, "body")

    def _parse_typed_get_call(self, node: ast.Call) -> Optional[ApiParameter]:
        """解析带类型转换的参数获取: int(request.GET.get('xxx'))"""
        # 检查是否是类型转换函数
        if not isinstance(node.func, ast.Name):
            return None

        type_func = node.func.id
        type_map = {
            'int': 'integer',
            'float': 'number',
            'bool': 'boolean',
            'str': 'string',
        }

        if type_func not in type_map:
            return None

        # 检查参数是否是 request.GET.get() 调用
        if not node.args:
            return None

        inner_call = node.args[0]
        if not isinstance(inner_call, ast.Call):
            return None

        call_str = self._get_call_string(inner_call)
        if '.GET.get' not in call_str and '.args.get' not in call_str:
            return None

        # 解析内部的 get 调用
        if not inner_call.args:
            return None

        # 获取参数名
        if isinstance(inner_call.args[0], ast.Constant):
            name = str(inner_call.args[0].value)
        elif isinstance(inner_call.args[0], ast.Str):
            name = inner_call.args[0].s
        else:
            return None

        # 获取默认值
        default = ""
        required = True
        if len(inner_call.args) > 1:
            required = False
            if isinstance(inner_call.args[1], ast.Constant):
                default = str(inner_call.args[1].value)

        # 获取描述
        _, description = self._infer_param_info(name)

        return ApiParameter(
            name=name,
            location="query",
            param_type=type_map[type_func],
            required=required,
            default=default,
            description=description,
        )

    def _extract_response(self, node) -> Dict:
        """提取响应结构"""
        response = {}

        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value:
                if isinstance(child.value, ast.Dict):
                    response = self._parse_dict_structure(child.value)
                    break

        return response

    def _parse_dict_structure(self, node: ast.Dict) -> Dict:
        """解析字典结构"""
        result = {}
        for key, value in zip(node.keys, node.values):
            if isinstance(key, ast.Constant):
                key_name = str(key.value)
            elif isinstance(key, ast.Str):
                key_name = key.s
            else:
                continue

            # 推断值类型
            if isinstance(value, ast.List):
                result[key_name] = "array"
            elif isinstance(value, ast.Dict):
                result[key_name] = "object"
            elif isinstance(value, ast.Constant):
                if isinstance(value.value, int):
                    result[key_name] = "integer"
                elif isinstance(value.value, float):
                    result[key_name] = "number"
                elif isinstance(value.value, bool):
                    result[key_name] = "boolean"
                else:
                    result[key_name] = "string"
            elif isinstance(value, ast.Name):
                # 变量引用，尝试推断
                name = value.id.lower()
                if 'list' in name or 'data' in name:
                    result[key_name] = "array"
                elif 'count' in name or 'num' in name or 'total' in name:
                    result[key_name] = "integer"
                else:
                    result[key_name] = "any"
            else:
                result[key_name] = "any"

        return result

    def get_endpoints_summary(self) -> Dict:
        """获取端点摘要"""
        methods = {}
        for ep in self.endpoints:
            method = ep.method
            methods[method] = methods.get(method, 0) + 1

        return {
            'total': len(self.endpoints),
            'framework': self.framework,
            'by_method': methods,
            'endpoints': [ep.to_dict() for ep in self.endpoints[:50]],
        }


def extract_api(source_dir: str) -> Tuple[List[ApiEndpoint], str]:
    """提取 API 的便捷函数"""
    extractor = ApiExtractor()
    return extractor.extract(source_dir)
