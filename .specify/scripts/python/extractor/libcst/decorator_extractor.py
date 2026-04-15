# -*- coding: utf-8 -*-
"""
装饰器提取器

提取装饰器定义和使用模式
"""
from typing import Dict, List, Optional
from collections import defaultdict

try:
    import libcst as cst
except ImportError:
    cst = None

from .base_libcst import LibCSTExtractor, CodeUnit, CodeLocation


class DecoratorExtractor(LibCSTExtractor):
    """装饰器提取器"""

    @property
    def name(self) -> str:
        return "decorator_extractor"

    @property
    def description(self) -> str:
        return "提取装饰器定义和使用模式"

    def extract_from_tree(
        self,
        tree: 'cst.Module',
        file_path: str,
        source_code: str,
        wrapper: 'cst.MetadataWrapper' = None
    ) -> List[CodeUnit]:
        """从 CST 树中提取装饰器"""
        visitor = DecoratorVisitor(file_path, source_code, self)
        if wrapper:
            wrapper.visit(visitor)
        return visitor.decorators


class DecoratorVisitor(cst.CSTVisitor):
    """装饰器访问器"""

    def __init__(self, file_path: str, source_code: str, extractor: DecoratorExtractor):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.split('\n')
        self.extractor = extractor
        self.decorators: List[CodeUnit] = []
        self._decorator_usage: Dict[str, List[Dict]] = defaultdict(list)
        self._current_class = ""

    def visit_ClassDef(self, node: 'cst.ClassDef') -> Optional[bool]:
        """访问类定义"""
        self._current_class = node.name.value

        # 提取类装饰器
        for dec in node.decorators:
            self._extract_decorator_usage(dec, "class", node.name.value)

        return True

    def leave_ClassDef(self, node: 'cst.ClassDef') -> None:
        """离开类定义"""
        self._current_class = ""

    def visit_FunctionDef(self, node: 'cst.FunctionDef') -> Optional[bool]:
        """访问函数定义"""
        func_name = node.name.value
        if self._current_class:
            full_name = f"{self._current_class}.{func_name}"
        else:
            full_name = func_name

        # 提取函数装饰器
        for dec in node.decorators:
            self._extract_decorator_usage(dec, "function", full_name)

        return True

    def _extract_decorator_usage(
        self,
        dec: 'cst.Decorator',
        target_type: str,
        target_name: str
    ) -> None:
        """提取装饰器使用"""
        dec_name, dec_args, dec_kwargs = self._parse_decorator(dec.decorator)

        if not dec_name:
            return

        # 记录使用
        self._decorator_usage[dec_name].append({
            "target_type": target_type,
            "target_name": target_name,
            "args": dec_args,
            "kwargs": dec_kwargs,
        })

        # 获取位置
        location = self._get_location(dec_name)

        try:
            source_code = cst.Module([]).code_for_node(dec)
        except Exception:
            source_code = f"@{dec_name}"

        unit = CodeUnit(
            name=f"{dec_name}_on_{target_name}",
            type="decorator_usage",
            location=location,
            source_code=source_code,
            confidence=1.0,
            confidence_level="fact",
            metadata={
                "decorator_name": dec_name,
                "target_type": target_type,
                "target_name": target_name,
                "has_args": bool(dec_args),
                "has_kwargs": bool(dec_kwargs),
                "args": dec_args,
                "kwargs": dec_kwargs,
                "is_builtin": self._is_builtin_decorator(dec_name),
                "is_django": self._is_django_decorator(dec_name),
            }
        )

        self.decorators.append(unit)

    def _parse_decorator(self, node) -> tuple:
        """解析装饰器"""
        if isinstance(node, cst.Name):
            return node.value, [], {}
        elif isinstance(node, cst.Attribute):
            return self._get_attr_name(node), [], {}
        elif isinstance(node, cst.Call):
            # 带参数的装饰器
            if isinstance(node.func, cst.Name):
                name = node.func.value
            elif isinstance(node.func, cst.Attribute):
                name = self._get_attr_name(node.func)
            else:
                return "", [], {}

            args = []
            kwargs = {}

            for arg in node.args:
                try:
                    arg_str = cst.Module([]).code_for_node(arg.value)
                    if arg.keyword:
                        kwargs[arg.keyword.value] = arg_str
                    else:
                        args.append(arg_str)
                except Exception:
                    pass

            return name, args, kwargs

        return "", [], {}

    def _get_attr_name(self, node: 'cst.Attribute') -> str:
        """获取属性名称"""
        parts = []
        current = node
        while isinstance(current, cst.Attribute):
            parts.append(current.attr.value)
            current = current.value
        if isinstance(current, cst.Name):
            parts.append(current.value)
        return ".".join(reversed(parts))

    def _get_location(self, dec_name: str) -> CodeLocation:
        """获取装饰器位置"""
        start_line = 1
        for i, line in enumerate(self.source_lines, 1):
            if f"@{dec_name}" in line or f"@{dec_name.split('.')[-1]}" in line:
                start_line = i
                break

        return CodeLocation(
            file_path=self.file_path,
            start_line=start_line,
            end_line=start_line
        )

    def _is_builtin_decorator(self, name: str) -> bool:
        """检查是否是内置装饰器"""
        builtins = {
            'property', 'staticmethod', 'classmethod', 'abstractmethod',
            'dataclass', 'cached_property', 'contextmanager', 'wraps',
            'lru_cache', 'singledispatch', 'total_ordering',
        }
        return name in builtins or name.split('.')[-1] in builtins

    def _is_django_decorator(self, name: str) -> bool:
        """检查是否是 Django 装饰器"""
        django_decorators = {
            'login_required', 'permission_required', 'user_passes_test',
            'csrf_exempt', 'csrf_protect', 'require_http_methods',
            'require_GET', 'require_POST', 'require_safe',
            'transaction.atomic', 'receiver', 'admin.register',
            'api_view', 'action', 'throttle_classes', 'permission_classes',
            'authentication_classes', 'renderer_classes', 'parser_classes',
        }
        return name in django_decorators or name.split('.')[-1] in django_decorators
