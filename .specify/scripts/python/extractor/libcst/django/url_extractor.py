# -*- coding: utf-8 -*-
"""
Django URL 提取器

提取 URL 路由配置、路径模式、视图映射等
"""
from typing import Dict, List, Optional

try:
    import libcst as cst
except ImportError:
    cst = None

from ..base_libcst import LibCSTExtractor, CodeUnit, CodeLocation


class DjangoURLExtractor(LibCSTExtractor):
    """Django URL 提取器"""

    # URL 配置函数
    URL_FUNCTIONS = {'path', 'url', 're_path', 'include'}

    @property
    def name(self) -> str:
        return "django_url_extractor"

    @property
    def description(self) -> str:
        return "提取 Django URL 路由配置和视图映射"

    def extract_from_tree(
        self,
        tree: 'cst.Module',
        file_path: str,
        source_code: str,
        wrapper: 'cst.MetadataWrapper' = None
    ) -> List[CodeUnit]:
        """从 CST 树中提取 URL 配置"""
        visitor = DjangoURLVisitor(file_path, source_code, self)
        if wrapper:
            wrapper.visit(visitor)
        return visitor.urls


class DjangoURLVisitor(cst.CSTVisitor):
    """Django URL 访问器"""

    def __init__(self, file_path: str, source_code: str, extractor: DjangoURLExtractor):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.split('\n')
        self.extractor = extractor
        self.urls: List[CodeUnit] = []
        self._in_urlpatterns = False
        self._current_prefix = ""

    def visit_Assign(self, node: 'cst.Assign') -> Optional[bool]:
        """访问赋值语句"""
        for target in node.targets:
            if isinstance(target.target, cst.Name):
                if target.target.value == 'urlpatterns':
                    self._in_urlpatterns = True
                    self._extract_urlpatterns(node.value)
                    self._in_urlpatterns = False
        return True

    def visit_AugAssign(self, node: 'cst.AugAssign') -> Optional[bool]:
        """访问增量赋值（urlpatterns += [...]）"""
        if isinstance(node.target, cst.Name):
            if node.target.value == 'urlpatterns':
                self._in_urlpatterns = True
                self._extract_urlpatterns(node.value)
                self._in_urlpatterns = False
        return True

    def _extract_urlpatterns(self, node) -> None:
        """提取 urlpatterns 列表"""
        if isinstance(node, cst.List):
            for elem in node.elements:
                if isinstance(elem, cst.Element):
                    self._extract_url_pattern(elem.value)
        elif isinstance(node, cst.Call):
            # 可能是 [*other_patterns, path(...)]
            pass

    def _extract_url_pattern(self, node) -> None:
        """提取单个 URL 模式"""
        if not isinstance(node, cst.Call):
            return

        func_name = self._get_name(node.func)

        if func_name not in self.extractor.URL_FUNCTIONS:
            return

        # 解析参数
        args = self._parse_url_args(node, func_name)

        if not args:
            return

        location = self._get_location(args.get('pattern', ''))

        try:
            source_code = cst.Module([]).code_for_node(node)
        except Exception:
            source_code = ""

        # 确定 URL 类型
        url_type = "url_pattern"
        if func_name == 'include':
            url_type = "url_include"
        elif args.get('is_router'):
            url_type = "router_urls"

        unit = CodeUnit(
            name=args.get('name', '') or args.get('pattern', 'unnamed'),
            type=url_type,
            location=location,
            source_code=source_code,
            confidence=1.0,
            confidence_level="fact",
            metadata={
                "function": func_name,
                "pattern": args.get('pattern', ''),
                "view": args.get('view', ''),
                "name": args.get('name', ''),
                "kwargs": args.get('kwargs', {}),
                "include_module": args.get('include_module', ''),
                "is_regex": func_name in ('url', 're_path'),
                "http_methods": args.get('http_methods', []),
            }
        )

        self.urls.append(unit)

    def _parse_url_args(self, node: 'cst.Call', func_name: str) -> Dict:
        """解析 URL 函数参数"""
        args = {
            'pattern': '',
            'view': '',
            'name': '',
            'kwargs': {},
            'include_module': '',
            'is_router': False,
            'http_methods': [],
        }

        positional_args = []

        for arg in node.args:
            try:
                if arg.keyword:
                    key = arg.keyword.value
                    value = cst.Module([]).code_for_node(arg.value)

                    if key == 'name':
                        args['name'] = value.strip("'\"")
                    elif key == 'kwargs':
                        args['kwargs'] = value
                else:
                    value = cst.Module([]).code_for_node(arg.value)
                    positional_args.append(value)
            except Exception:
                pass

        # 根据函数类型解析位置参数
        if func_name in ('path', 'url', 're_path'):
            if len(positional_args) >= 1:
                args['pattern'] = positional_args[0].strip("'\"")
            if len(positional_args) >= 2:
                args['view'] = positional_args[1]
        elif func_name == 'include':
            if len(positional_args) >= 1:
                args['include_module'] = positional_args[0].strip("'\"")
                args['pattern'] = self._current_prefix

        # 检查是否是 Router URLs
        if 'router' in args.get('view', '').lower():
            args['is_router'] = True

        return args

    def _get_name(self, node) -> str:
        """获取名称"""
        if isinstance(node, cst.Name):
            return node.value
        elif isinstance(node, cst.Attribute):
            return node.attr.value
        return ""

    def _get_location(self, pattern: str) -> CodeLocation:
        """获取位置"""
        start_line = 1
        search_term = pattern[:20] if len(pattern) > 20 else pattern

        for i, line in enumerate(self.source_lines, 1):
            if search_term and search_term in line:
                start_line = i
                break
            elif 'urlpatterns' in line:
                start_line = i

        return CodeLocation(
            file_path=self.file_path,
            start_line=start_line,
            end_line=start_line
        )
