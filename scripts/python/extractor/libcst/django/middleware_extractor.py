# -*- coding: utf-8 -*-
"""
Django Middleware 提取器

提取 Django 中间件定义和配置
"""
from typing import Dict, List, Optional

try:
    import libcst as cst
except ImportError:
    cst = None

from ..base_libcst import LibCSTExtractor, CodeUnit, CodeLocation


class DjangoMiddlewareExtractor(LibCSTExtractor):
    """Django Middleware 提取器"""

    # 中间件方法
    MIDDLEWARE_METHODS = {
        '__init__', '__call__', 'process_request', 'process_view',
        'process_exception', 'process_template_response', 'process_response',
    }

    # 中间件基类
    MIDDLEWARE_BASES = {'MiddlewareMixin', 'BaseMiddleware'}

    @property
    def name(self) -> str:
        return "django_middleware_extractor"

    @property
    def description(self) -> str:
        return "提取 Django 中间件定义和配置"

    def extract_from_tree(
        self,
        tree: 'cst.Module',
        file_path: str,
        source_code: str,
        wrapper: 'cst.MetadataWrapper' = None
    ) -> List[CodeUnit]:
        """从 CST 树中提取中间件"""
        visitor = DjangoMiddlewareVisitor(file_path, source_code, self)
        if wrapper:
            wrapper.visit(visitor)
        return visitor.middlewares


class DjangoMiddlewareVisitor(cst.CSTVisitor):
    """Django Middleware 访问器"""

    def __init__(self, file_path: str, source_code: str, extractor: DjangoMiddlewareExtractor):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.split('\n')
        self.extractor = extractor
        self.middlewares: List[CodeUnit] = []

    def visit_ClassDef(self, node: 'cst.ClassDef') -> Optional[bool]:
        """访问类定义"""
        class_name = node.name.value
        bases = self._get_bases(node.bases)

        # 检查是否是中间件
        is_middleware = (
            any(base in self.extractor.MIDDLEWARE_BASES for base in bases) or
            class_name.endswith('Middleware') or
            self._has_middleware_methods(node.body)
        )

        if not is_middleware:
            return True

        location = self._get_location(class_name)
        docstring = self.extractor._get_docstring(node.body)

        # 提取方法
        methods = self._extract_methods(node.body)

        # 确定中间件类型
        middleware_type = self._determine_middleware_type(methods)

        try:
            source_code = cst.Module([]).code_for_node(node)
        except Exception:
            source_code = ""

        signature = f"class {class_name}({', '.join(bases)}):" if bases else f"class {class_name}:"

        unit = CodeUnit(
            name=class_name,
            type="django_middleware",
            location=location,
            source_code=source_code,
            signature=signature,
            docstring=docstring,
            bases=bases,
            methods=[m['name'] for m in methods],
            confidence=1.0,
            confidence_level="fact",
            metadata={
                "middleware_type": middleware_type,
                "has_process_request": any(m['name'] == 'process_request' for m in methods),
                "has_process_response": any(m['name'] == 'process_response' for m in methods),
                "has_process_view": any(m['name'] == 'process_view' for m in methods),
                "has_process_exception": any(m['name'] == 'process_exception' for m in methods),
                "is_new_style": any(m['name'] == '__call__' for m in methods),
                "method_details": methods,
            }
        )

        self.middlewares.append(unit)

        return True

    def _get_bases(self, bases) -> List[str]:
        """获取基类列表"""
        result = []
        for base in bases:
            name = self._get_name(base.value)
            if name:
                result.append(name)
        return result

    def _get_name(self, node) -> str:
        """获取名称"""
        if isinstance(node, cst.Name):
            return node.value
        elif isinstance(node, cst.Attribute):
            return f"{self._get_name(node.value)}.{node.attr.value}"
        return ""

    def _get_location(self, class_name: str) -> CodeLocation:
        """获取位置"""
        start_line = 1
        for i, line in enumerate(self.source_lines, 1):
            if f"class {class_name}" in line:
                start_line = i
                break

        return CodeLocation(
            file_path=self.file_path,
            start_line=start_line,
            end_line=start_line
        )

    def _has_middleware_methods(self, body: 'cst.BaseSuite') -> bool:
        """检查是否有中间件方法"""
        if not isinstance(body, cst.IndentedBlock):
            return False

        for stmt in body.body:
            if isinstance(stmt, cst.FunctionDef):
                if stmt.name.value in self.extractor.MIDDLEWARE_METHODS:
                    return True

        return False

    def _extract_methods(self, body: 'cst.BaseSuite') -> List[Dict]:
        """提取方法"""
        methods = []

        if not isinstance(body, cst.IndentedBlock):
            return methods

        for stmt in body.body:
            if isinstance(stmt, cst.FunctionDef):
                method_name = stmt.name.value
                docstring = self.extractor._get_docstring(stmt.body)

                # 获取参数
                params = []
                for param in stmt.params.params:
                    params.append(param.name.value)

                methods.append({
                    "name": method_name,
                    "params": params,
                    "docstring": docstring,
                    "is_middleware_method": method_name in self.extractor.MIDDLEWARE_METHODS,
                })

        return methods

    def _determine_middleware_type(self, methods: List[Dict]) -> str:
        """确定中间件类型"""
        method_names = {m['name'] for m in methods}

        if '__call__' in method_names:
            return "new_style"  # Django 1.10+ 新式中间件
        elif 'process_request' in method_names or 'process_response' in method_names:
            return "old_style"  # 旧式中间件
        else:
            return "unknown"
