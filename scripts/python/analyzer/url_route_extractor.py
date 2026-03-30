# -*- coding: utf-8 -*-
"""
URL 路由抽取器

支持框架：Django、Flask、FastAPI
从源码中提取 URL 路由映射
"""
import ast
import os
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict


@dataclass
class UrlRoute:
    """URL 路由"""
    path: str                       # URL 路径
    method: str = "GET"             # HTTP 方法
    handler: str = ""               # Handler 类/函数名
    handler_module: str = ""        # Handler 所在模块
    source_file: str = ""           # 路由定义文件
    source_line: int = 0            # 行号
    path_params: List[str] = field(default_factory=list)  # 路径参数
    name: str = ""                  # 路由名称

    def to_dict(self) -> dict:
        return asdict(self)


class UrlRouteExtractor:
    """URL 路由抽取器"""

    # Django 路由模式 - 支持多种 handler 格式
    # 1. Class-based views: path('jobs/', JobListView.as_view())
    DJANGO_URL_CBV_PATTERN = re.compile(
        r"""url\s*\(\s*r?['"]([^'"]+)['"]\s*,\s*([\w.]+)\.as_view\(\)""",
        re.VERBOSE
    )
    DJANGO_PATH_CBV_PATTERN = re.compile(
        r"""path\s*\(\s*['"]([^'"]+)['"]\s*,\s*([\w.]+)\.as_view\(\)""",
        re.VERBOSE
    )
    # 2. Function-based views: path('jobs/', views.job_list)
    DJANGO_PATH_FBV_PATTERN = re.compile(
        r"""path\s*\(\s*['"]([^'"]+)['"]\s*,\s*([\w.]+)\s*[,)]""",
        re.VERBOSE
    )
    # 3. DRF ViewSet: router.register('jobs', JobViewSet)
    DRF_ROUTER_PATTERN = re.compile(
        r"""register\s*\(\s*r?['"]([^'"]+)['"]\s*,\s*([\w.]+)""",
        re.VERBOSE
    )
    # 4. Django path with <type:name> params: path('job/<int:pk>/', ...)
    DJANGO_PATH_PARAM_PATTERN = re.compile(r'<(\w+:)?(\w+)>')

    # Flask 路由模式
    FLASK_ROUTE_PATTERN = re.compile(
        r"""@(\w+)\.route\s*\(\s*['"]([^'"]+)['"](?:\s*,\s*methods\s*=\s*\[([^\]]+)\])?""",
        re.VERBOSE
    )

    # FastAPI 路由模式
    FASTAPI_ROUTE_PATTERN = re.compile(
        r"""@(\w+)\.(get|post|put|delete|patch)\s*\(\s*['"]([^'"]+)['"]""",
        re.VERBOSE | re.IGNORECASE
    )

    def __init__(self):
        self.routes: List[UrlRoute] = []
        self.framework: str = ""

    def extract_routes(self, source_dir: str) -> Tuple[List[UrlRoute], str]:
        """
        从源码目录提取所有 URL 路由

        返回: (路由列表, 检测到的框架)
        """
        self.routes = []
        self.framework = self._detect_framework(source_dir)

        # 查找路由文件
        route_files = self._find_route_files(source_dir)

        # 解析每个文件
        for filepath in route_files:
            self._parse_route_file(filepath)

        return self.routes, self.framework

    def _detect_framework(self, source_dir: str) -> str:
        """检测 Web 框架"""
        # 检查 Django 特征
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'migrations')]
            for filename in files:
                if filename == 'urls.py':
                    return 'Django'
                if filename.endswith('.py'):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read(5000)  # 只读前 5000 字符
                            if '@app.route' in content or 'Blueprint' in content:
                                return 'Flask'
                            if '@app.get' in content or '@app.post' in content or 'FastAPI' in content:
                                return 'FastAPI'
                    except Exception:
                        continue
        return 'Unknown'

    def _find_route_files(self, source_dir: str) -> List[str]:
        """查找路由文件"""
        route_files = []

        for root, dirs, files in os.walk(source_dir):
            # 排除目录
            dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'migrations', 'Thrift')]

            for filename in files:
                if not filename.endswith('.py'):
                    continue

                filepath = os.path.join(root, filename)

                # Django: urls.py 文件
                if 'urls' in filename.lower():
                    route_files.append(filepath)
                    continue

                # Flask/FastAPI: 检查文件内容
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read(3000)
                        if self.FLASK_ROUTE_PATTERN.search(content) or \
                           self.FASTAPI_ROUTE_PATTERN.search(content):
                            route_files.append(filepath)
                except Exception:
                    continue

        return route_files

    def _parse_route_file(self, filepath: str):
        """解析路由文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception:
            return

        # 根据框架选择解析方法
        if self.framework == 'Django':
            self._parse_django_routes(filepath, content, lines)
        elif self.framework == 'Flask':
            self._parse_flask_routes(filepath, content, lines)
        elif self.framework == 'FastAPI':
            self._parse_fastapi_routes(filepath, content, lines)
        else:
            # 尝试所有模式
            self._parse_django_routes(filepath, content, lines)
            self._parse_flask_routes(filepath, content, lines)
            self._parse_fastapi_routes(filepath, content, lines)

    def _parse_django_routes(self, filepath: str, content: str, lines: List[str]):
        """解析 Django 路由"""
        # 1. 解析 url() CBV 模式
        for match in self.DJANGO_URL_CBV_PATTERN.finditer(content):
            path_pattern = match.group(1)
            handler_str = match.group(2).strip()
            line_num = content[:match.start()].count('\n') + 1
            handler, handler_module = self._parse_django_handler(handler_str)
            path = self._convert_django_path(path_pattern)
            path_params = self._extract_path_params(path_pattern)

            route = UrlRoute(
                path=path,
                method="*",  # Django View 类支持多方法，后续从 Handler 分析
                handler=handler,
                handler_module=handler_module,
                source_file=filepath,
                source_line=line_num,
                path_params=path_params,
            )
            self.routes.append(route)

        # 2. 解析 path() CBV 模式
        for match in self.DJANGO_PATH_CBV_PATTERN.finditer(content):
            path_pattern = match.group(1)
            handler_str = match.group(2).strip()
            line_num = content[:match.start()].count('\n') + 1
            handler, handler_module = self._parse_django_handler(handler_str)
            path = '/' + path_pattern.lstrip('/')
            path_params = self._extract_path_params(path_pattern)

            route = UrlRoute(
                path=path,
                method="*",
                handler=handler,
                handler_module=handler_module,
                source_file=filepath,
                source_line=line_num,
                path_params=path_params,
            )
            self.routes.append(route)

        # 3. 解析 path() FBV 模式（函数视图）
        for match in self.DJANGO_PATH_FBV_PATTERN.finditer(content):
            path_pattern = match.group(1)
            handler_str = match.group(2).strip()
            # 跳过已经被 CBV 模式匹配的（包含 .as_view）
            if '.as_view' in handler_str:
                continue
            line_num = content[:match.start()].count('\n') + 1
            handler, handler_module = self._parse_django_handler(handler_str)
            path = '/' + path_pattern.lstrip('/')
            path_params = self._extract_path_params(path_pattern)

            route = UrlRoute(
                path=path,
                method="*",
                handler=handler,
                handler_module=handler_module,
                source_file=filepath,
                source_line=line_num,
                path_params=path_params,
            )
            self.routes.append(route)

        # 4. 解析 DRF router.register() 模式
        for match in self.DRF_ROUTER_PATTERN.finditer(content):
            path_pattern = match.group(1)
            handler_str = match.group(2).strip()
            line_num = content[:match.start()].count('\n') + 1
            handler, handler_module = self._parse_django_handler(handler_str)
            path = '/' + path_pattern.lstrip('/')

            # ViewSet 生成多个路由
            for method, suffix in [('GET', ''), ('POST', ''), ('GET', '/{id}'), ('PUT', '/{id}'), ('DELETE', '/{id}')]:
                route = UrlRoute(
                    path=path + suffix,
                    method=method,
                    handler=handler,
                    handler_module=handler_module,
                    source_file=filepath,
                    source_line=line_num,
                    path_params=['id'] if '{id}' in suffix else [],
                )
                self.routes.append(route)

    def _parse_django_handler(self, handler_str: str) -> Tuple[str, str]:
        """解析 Django handler 字符串"""
        # 示例: job_view.JobListView
        # 示例: JobListView
        handler_str = handler_str.strip()

        # 移除可能残留的 .as_view()
        handler_str = handler_str.replace('.as_view()', '').replace('.as_view', '')

        if '.' in handler_str:
            parts = handler_str.rsplit('.', 1)
            return parts[1], parts[0]  # (类名, 模块名)
        return handler_str, ""

    def _convert_django_path(self, pattern: str) -> str:
        """转换 Django URL 正则为标准路径"""
        # 去除 ^ 和 $
        path = pattern.strip('^$')

        # 转换命名组 (?P<name>...) 为 {name}
        path = re.sub(r'\(\?P<(\w+)>[^)]+\)', r'{\1}', path)

        # 转换普通组 (...) 为 {param}
        path = re.sub(r'\([^)]+\)', '{param}', path)

        # 确保以 / 开头
        if not path.startswith('/'):
            path = '/' + path

        return path

    def _extract_path_params(self, pattern: str) -> List[str]:
        """提取路径参数"""
        params = []
        # Django 命名组 (?P<name>...)
        for match in re.finditer(r'\(\?P<(\w+)>', pattern):
            params.append(match.group(1))
        # Django path 参数 <type:name> 或 <name>
        for match in self.DJANGO_PATH_PARAM_PATTERN.finditer(pattern):
            params.append(match.group(2))
        # 标准 {param} 格式
        for match in re.finditer(r'\{(\w+)\}', pattern):
            if match.group(1) not in params:
                params.append(match.group(1))
        return params

    def _parse_flask_routes(self, filepath: str, content: str, lines: List[str]):
        """解析 Flask 路由"""
        for match in self.FLASK_ROUTE_PATTERN.finditer(content):
            app_name = match.group(1)
            path = match.group(2)
            methods_str = match.group(3)

            line_num = content[:match.start()].count('\n') + 1

            # 解析方法
            methods = ['GET']
            if methods_str:
                methods = [m.strip().strip("'\"") for m in methods_str.split(',')]

            # 查找下一行的函数名
            handler = self._find_next_function(lines, line_num - 1)

            # 提取路径参数
            path_params = self._extract_path_params(path)

            for method in methods:
                route = UrlRoute(
                    path=path,
                    method=method.upper(),
                    handler=handler,
                    handler_module="",
                    source_file=filepath,
                    source_line=line_num,
                    path_params=path_params,
                )
                self.routes.append(route)

    def _parse_fastapi_routes(self, filepath: str, content: str, lines: List[str]):
        """解析 FastAPI 路由"""
        for match in self.FASTAPI_ROUTE_PATTERN.finditer(content):
            app_name = match.group(1)
            method = match.group(2).upper()
            path = match.group(3)

            line_num = content[:match.start()].count('\n') + 1

            # 查找下一行的函数名
            handler = self._find_next_function(lines, line_num - 1)

            # 提取路径参数
            path_params = self._extract_path_params(path)

            route = UrlRoute(
                path=path,
                method=method,
                handler=handler,
                handler_module="",
                source_file=filepath,
                source_line=line_num,
                path_params=path_params,
            )
            self.routes.append(route)

    def _find_next_function(self, lines: List[str], start_line: int) -> str:
        """查找装饰器后的函数名"""
        for i in range(start_line + 1, min(start_line + 10, len(lines))):
            line = lines[i].strip()
            if line.startswith('def ') or line.startswith('async def '):
                match = re.match(r'(?:async\s+)?def\s+(\w+)', line)
                if match:
                    return match.group(1)
        return ""

    def get_routes_summary(self) -> Dict:
        """获取路由摘要"""
        methods = {}
        for route in self.routes:
            method = route.method
            methods[method] = methods.get(method, 0) + 1

        return {
            'total': len(self.routes),
            'framework': self.framework,
            'by_method': methods,
            'routes': [r.to_dict() for r in self.routes[:50]],  # 最多返回 50 个
        }


def extract_routes(source_dir: str) -> Tuple[List[UrlRoute], str]:
    """提取路由的便捷函数"""
    extractor = UrlRouteExtractor()
    return extractor.extract_routes(source_dir)
