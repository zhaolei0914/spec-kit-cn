# -*- coding: utf-8 -*-
"""
Django View 提取器

提取 Django 视图定义、装饰器、HTTP 方法等
"""
from typing import Dict, List, Optional

try:
    import libcst as cst
except ImportError:
    cst = None

from ..base_libcst import LibCSTExtractor, CodeUnit, CodeLocation


class DjangoViewExtractor(LibCSTExtractor):
    """Django View 提取器"""

    # Django 视图基类
    VIEW_BASES = {
        'View', 'TemplateView', 'RedirectView', 'ListView', 'DetailView',
        'CreateView', 'UpdateView', 'DeleteView', 'FormView', 'ArchiveIndexView',
        'APIView', 'GenericAPIView', 'ViewSet', 'ModelViewSet', 'ReadOnlyModelViewSet',
        'GenericViewSet', 'CreateAPIView', 'ListAPIView', 'RetrieveAPIView',
        'DestroyAPIView', 'UpdateAPIView', 'ListCreateAPIView',
        'RetrieveUpdateAPIView', 'RetrieveDestroyAPIView', 'RetrieveUpdateDestroyAPIView',
    }

    # HTTP 方法
    HTTP_METHODS = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'}

    # 视图装饰器
    VIEW_DECORATORS = {
        'api_view', 'login_required', 'permission_required', 'csrf_exempt',
        'require_http_methods', 'require_GET', 'require_POST', 'require_safe',
        'throttle_classes', 'permission_classes', 'authentication_classes',
        'action', 'formatting', 'authenticated',
    }

    @property
    def name(self) -> str:
        return "django_view_extractor"

    @property
    def description(self) -> str:
        return "提取 Django 视图定义、装饰器和 HTTP 方法"

    def extract_from_tree(
        self,
        tree: 'cst.Module',
        file_path: str,
        source_code: str,
        wrapper: 'cst.MetadataWrapper' = None
    ) -> List[CodeUnit]:
        """从 CST 树中提取 Django 视图"""
        visitor = DjangoViewVisitor(file_path, source_code, self)
        if wrapper:
            wrapper.visit(visitor)
        return visitor.views


class DjangoViewVisitor(cst.CSTVisitor):
    """Django View 访问器"""

    def __init__(self, file_path: str, source_code: str, extractor: DjangoViewExtractor):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.split('\n')
        self.extractor = extractor
        self.views: List[CodeUnit] = []
        self._in_class = False
        self._current_class = ""
        self._current_class_bases = []

    def visit_ClassDef(self, node: 'cst.ClassDef') -> Optional[bool]:
        """访问类定义"""
        class_name = node.name.value
        bases = self._get_bases(node.bases)

        # 检查是否是 Django View
        is_view = any(
            base in self.extractor.VIEW_BASES or
            base.endswith('View') or
            base.endswith('ViewSet') or
            base.endswith('APIView')
            for base in bases
        )

        if is_view:
            self._in_class = True
            self._current_class = class_name
            self._current_class_bases = bases

            # 提取类级别的视图信息
            self._extract_class_view(node, class_name, bases)

        return True

    def leave_ClassDef(self, node: 'cst.ClassDef') -> None:
        """离开类定义"""
        self._in_class = False
        self._current_class = ""
        self._current_class_bases = []

    def visit_FunctionDef(self, node: 'cst.FunctionDef') -> Optional[bool]:
        """访问函数定义"""
        func_name = node.name.value
        decorators = self._get_decorators(node.decorators)

        # 检查是否是函数视图（通过装饰器判断）
        is_function_view = any(
            dec_name in self.extractor.VIEW_DECORATORS
            for dec_name, _ in decorators
        )

        if is_function_view and not self._in_class:
            self._extract_function_view(node, func_name, decorators)
        elif self._in_class:
            # 检查是否是 HTTP 方法
            if func_name.lower() in self.extractor.HTTP_METHODS:
                self._extract_http_method(node, func_name, decorators)
            # 检查是否是 action
            elif any(dec_name == 'action' for dec_name, _ in decorators):
                self._extract_action_method(node, func_name, decorators)

        return True

    def _extract_class_view(
        self,
        node: 'cst.ClassDef',
        class_name: str,
        bases: List[str]
    ) -> None:
        """提取类视图"""
        location = self._get_location(class_name)
        docstring = self.extractor._get_docstring(node.body)

        # 获取装饰器
        decorators = []
        for dec in node.decorators:
            try:
                dec_str = cst.Module([]).code_for_node(dec.decorator)
                decorators.append(f"@{dec_str}")
            except Exception:
                pass

        # 提取类属性
        attributes = self._extract_class_attributes(node.body)

        # 提取方法
        methods = self._extract_methods(node.body)

        # 确定视图类型
        view_type = self._determine_view_type(bases)

        try:
            source_code = cst.Module([]).code_for_node(node)
        except Exception:
            source_code = ""

        signature = f"class {class_name}({', '.join(bases)}):"

        unit = CodeUnit(
            name=class_name,
            type="django_view",
            location=location,
            source_code=source_code,
            signature=signature,
            docstring=docstring,
            decorators=decorators,
            bases=bases,
            attributes=attributes,
            methods=methods,
            confidence=1.0,
            confidence_level="fact",
            metadata={
                "view_type": view_type,
                "is_class_view": True,
                "is_api_view": 'APIView' in ' '.join(bases) or 'ViewSet' in ' '.join(bases),
                "http_methods": [m for m in methods if m.lower() in self.extractor.HTTP_METHODS],
                "has_authentication": any('authentication' in str(a).lower() for a in attributes),
                "has_permission": any('permission' in str(a).lower() for a in attributes),
            }
        )

        self.views.append(unit)

    def _extract_function_view(
        self,
        node: 'cst.FunctionDef',
        func_name: str,
        decorators: List[tuple]
    ) -> None:
        """提取函数视图"""
        location = self._get_location(func_name)
        docstring = self.extractor._get_docstring(node.body)

        # 格式化装饰器
        dec_strs = []
        for dec_name, dec_args in decorators:
            if dec_args:
                dec_strs.append(f"@{dec_name}({', '.join(dec_args)})")
            else:
                dec_strs.append(f"@{dec_name}")

        # 获取参数
        parameters = self._get_parameters(node.params)

        # 获取返回类型
        return_type = ""
        if node.returns:
            return_type = self.extractor._get_annotation_string(node.returns)

        try:
            source_code = cst.Module([]).code_for_node(node)
        except Exception:
            source_code = ""

        # 确定允许的 HTTP 方法
        http_methods = self._extract_http_methods_from_decorators(decorators)

        unit = CodeUnit(
            name=func_name,
            type="django_view",
            location=location,
            source_code=source_code,
            docstring=docstring,
            decorators=dec_strs,
            parameters=parameters,
            return_type=return_type,
            confidence=1.0,
            confidence_level="fact",
            metadata={
                "view_type": "function_view",
                "is_class_view": False,
                "is_api_view": any(d[0] == 'api_view' for d in decorators),
                "http_methods": http_methods,
                "has_authentication": any(d[0] in ('authenticated', 'login_required') for d in decorators),
                "has_permission": any(d[0] == 'permission_required' for d in decorators),
                "has_formatting": any(d[0] == 'formatting' for d in decorators),
            }
        )

        self.views.append(unit)

    def _extract_http_method(
        self,
        node: 'cst.FunctionDef',
        method_name: str,
        decorators: List[tuple]
    ) -> None:
        """提取 HTTP 方法"""
        location = self._get_location(method_name)
        docstring = self.extractor._get_docstring(node.body)

        # 格式化装饰器
        dec_strs = [f"@{d[0]}" if not d[1] else f"@{d[0]}({', '.join(d[1])})" for d in decorators]

        # 获取参数
        parameters = self._get_parameters(node.params)

        try:
            source_code = cst.Module([]).code_for_node(node)
        except Exception:
            source_code = ""

        full_name = f"{self._current_class}.{method_name}"

        unit = CodeUnit(
            name=full_name,
            type="http_method",
            location=location,
            source_code=source_code,
            docstring=docstring,
            decorators=dec_strs,
            parameters=parameters,
            confidence=1.0,
            confidence_level="fact",
            metadata={
                "class_name": self._current_class,
                "method_name": method_name,
                "http_method": method_name.upper(),
            }
        )

        self.views.append(unit)

    def _extract_action_method(
        self,
        node: 'cst.FunctionDef',
        method_name: str,
        decorators: List[tuple]
    ) -> None:
        """提取 ViewSet action 方法"""
        location = self._get_location(method_name)
        docstring = self.extractor._get_docstring(node.body)

        # 获取 action 装饰器参数
        action_config = {}
        for dec_name, dec_args in decorators:
            if dec_name == 'action':
                # 解析 action 参数
                for arg in dec_args:
                    if '=' in arg:
                        key, value = arg.split('=', 1)
                        action_config[key.strip()] = value.strip()

        # 格式化装饰器
        dec_strs = [f"@{d[0]}" if not d[1] else f"@{d[0]}({', '.join(d[1])})" for d in decorators]

        try:
            source_code = cst.Module([]).code_for_node(node)
        except Exception:
            source_code = ""

        full_name = f"{self._current_class}.{method_name}"

        unit = CodeUnit(
            name=full_name,
            type="viewset_action",
            location=location,
            source_code=source_code,
            docstring=docstring,
            decorators=dec_strs,
            confidence=1.0,
            confidence_level="fact",
            metadata={
                "class_name": self._current_class,
                "action_name": method_name,
                "detail": action_config.get('detail', 'False'),
                "methods": action_config.get('methods', "['get']"),
                "url_path": action_config.get('url_path', method_name),
            }
        )

        self.views.append(unit)

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

    def _get_decorators(self, decorators) -> List[tuple]:
        """获取装饰器列表"""
        result = []
        for dec in decorators:
            dec_name, dec_args = self._parse_decorator(dec.decorator)
            if dec_name:
                result.append((dec_name, dec_args))
        return result

    def _parse_decorator(self, node) -> tuple:
        """解析装饰器"""
        if isinstance(node, cst.Name):
            return node.value, []
        elif isinstance(node, cst.Attribute):
            return self._get_name(node), []
        elif isinstance(node, cst.Call):
            if isinstance(node.func, cst.Name):
                name = node.func.value
            elif isinstance(node.func, cst.Attribute):
                name = self._get_name(node.func)
            else:
                return "", []

            args = []
            for arg in node.args:
                try:
                    arg_str = cst.Module([]).code_for_node(arg)
                    args.append(arg_str)
                except Exception:
                    pass

            return name, args

        return "", []

    def _get_location(self, name: str) -> CodeLocation:
        """获取位置"""
        start_line = 1
        for i, line in enumerate(self.source_lines, 1):
            if f"class {name}" in line or f"def {name}" in line:
                start_line = i
                break

        return CodeLocation(
            file_path=self.file_path,
            start_line=start_line,
            end_line=start_line
        )

    def _get_parameters(self, params: 'cst.Parameters') -> List[Dict]:
        """获取参数列表"""
        result = []
        for param in params.params:
            info = {
                "name": param.name.value,
                "type": self.extractor._get_annotation_string(param.annotation) if param.annotation else "",
            }
            result.append(info)
        return result

    def _extract_class_attributes(self, body: 'cst.BaseSuite') -> List[Dict]:
        """提取类属性"""
        attributes = []

        if not isinstance(body, cst.IndentedBlock):
            return attributes

        for stmt in body.body:
            if isinstance(stmt, cst.SimpleStatementLine):
                for item in stmt.body:
                    if isinstance(item, cst.Assign):
                        for target in item.targets:
                            if isinstance(target.target, cst.Name):
                                name = target.target.value
                                try:
                                    value = cst.Module([]).code_for_node(item.value)
                                    attributes.append({"name": name, "value": value})
                                except Exception:
                                    attributes.append({"name": name, "value": ""})

        return attributes

    def _extract_methods(self, body: 'cst.BaseSuite') -> List[str]:
        """提取方法列表"""
        methods = []

        if not isinstance(body, cst.IndentedBlock):
            return methods

        for stmt in body.body:
            if isinstance(stmt, cst.FunctionDef):
                methods.append(stmt.name.value)

        return methods

    def _determine_view_type(self, bases: List[str]) -> str:
        """确定视图类型"""
        bases_str = ' '.join(bases).lower()

        if 'viewset' in bases_str:
            return 'viewset'
        elif 'apiview' in bases_str:
            return 'api_view'
        elif 'genericapiview' in bases_str:
            return 'generic_api_view'
        elif 'templateview' in bases_str:
            return 'template_view'
        elif 'listview' in bases_str or 'detailview' in bases_str:
            return 'generic_view'
        elif 'formview' in bases_str or 'createview' in bases_str:
            return 'form_view'
        else:
            return 'class_view'

    def _extract_http_methods_from_decorators(self, decorators: List[tuple]) -> List[str]:
        """从装饰器中提取 HTTP 方法"""
        methods = []

        for dec_name, dec_args in decorators:
            if dec_name == 'api_view':
                # @api_view(['GET', 'POST'])
                for arg in dec_args:
                    if '[' in arg:
                        # 解析列表
                        import re
                        found = re.findall(r"'(\w+)'", arg)
                        methods.extend([m.upper() for m in found])
            elif dec_name == 'require_http_methods':
                for arg in dec_args:
                    if '[' in arg:
                        import re
                        found = re.findall(r"'(\w+)'", arg)
                        methods.extend([m.upper() for m in found])
            elif dec_name == 'require_GET':
                methods.append('GET')
            elif dec_name == 'require_POST':
                methods.append('POST')
            elif dec_name == 'require_safe':
                methods.extend(['GET', 'HEAD'])

        return list(set(methods)) if methods else ['GET']
