# -*- coding: utf-8 -*-
"""
函数提取器

提取函数定义、参数、返回类型、装饰器等信息
"""
from typing import Dict, List, Optional, Sequence

try:
    import libcst as cst
except ImportError:
    cst = None

from .base_libcst import LibCSTExtractor, CodeUnit, CodeLocation


class FunctionExtractor(LibCSTExtractor):
    """函数提取器"""

    @property
    def name(self) -> str:
        return "function_extractor"

    @property
    def description(self) -> str:
        return "提取函数定义、参数、返回类型和装饰器"

    def extract_from_tree(
        self,
        tree: 'cst.Module',
        file_path: str,
        source_code: str,
        wrapper: 'cst.MetadataWrapper' = None
    ) -> List[CodeUnit]:
        """从 CST 树中提取函数"""
        visitor = FunctionVisitor(file_path, source_code, self)
        if wrapper:
            wrapper.visit(visitor)
        return visitor.functions


class FunctionVisitor(cst.CSTVisitor):
    """函数访问器"""

    def __init__(self, file_path: str, source_code: str, extractor: FunctionExtractor):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.split('\n')
        self.extractor = extractor
        self.functions: List[CodeUnit] = []
        self._scope_stack: List[str] = []  # 作用域栈
        self._in_class = False

    def visit_ClassDef(self, node: 'cst.ClassDef') -> Optional[bool]:
        """进入类定义"""
        self._scope_stack.append(node.name.value)
        self._in_class = True
        return True

    def leave_ClassDef(self, node: 'cst.ClassDef') -> None:
        """离开类定义"""
        if self._scope_stack:
            self._scope_stack.pop()
        self._in_class = len(self._scope_stack) > 0

    def visit_FunctionDef(self, node: 'cst.FunctionDef') -> Optional[bool]:
        """访问函数定义"""
        func_name = node.name.value

        # 构建完整名称
        if self._scope_stack:
            full_name = ".".join(self._scope_stack + [func_name])
        else:
            full_name = func_name

        # 获取位置信息
        location = self._get_location(node, func_name)

        # 获取装饰器
        decorators = self._get_decorators(node.decorators)

        # 获取参数
        parameters = self._get_parameters(node.params)

        # 获取返回类型
        return_type = ""
        if node.returns:
            return_type = self.extractor._get_annotation_string(node.returns)

        # 获取 docstring
        docstring = self.extractor._get_docstring(node.body)

        # 获取源代码
        try:
            source_code = cst.Module([]).code_for_node(node)
        except Exception:
            source_code = ""

        # 生成签名
        signature = self._generate_signature(func_name, parameters, return_type, decorators)

        # 提取异常信息
        raised_exceptions = self._extract_raised_exceptions(node.body)

        # 确定函数类型
        func_type = self._determine_function_type(decorators, parameters)

        # 创建 CodeUnit
        unit = CodeUnit(
            name=full_name,
            type="function",
            location=location,
            source_code=source_code,
            signature=signature,
            docstring=docstring,
            decorators=decorators,
            parameters=parameters,
            return_type=return_type,
            raised_exceptions=raised_exceptions,
            confidence=1.0,
            confidence_level="fact",
            metadata={
                "is_method": self._in_class,
                "function_type": func_type,
                "param_count": len(parameters),
                "has_docstring": bool(docstring),
                "is_async": isinstance(node, cst.FunctionDef) and node.asynchronous is not None,
            }
        )

        self.functions.append(unit)

        # 不继续访问嵌套函数内部（避免重复）
        self._scope_stack.append(func_name)
        return True

    def leave_FunctionDef(self, node: 'cst.FunctionDef') -> None:
        """离开函数定义"""
        if self._scope_stack and self._scope_stack[-1] == node.name.value:
            self._scope_stack.pop()

    def _get_location(self, node: 'cst.FunctionDef', func_name: str) -> CodeLocation:
        """获取函数的位置信息"""
        try:
            code = cst.Module([]).code_for_node(node)
            # 在源码中查找函数定义
            func_def_pattern = f"def {func_name}"
            start_line = 1
            for i, line in enumerate(self.source_lines, 1):
                if func_def_pattern in line:
                    start_line = i
                    break
            end_line = start_line + code.count('\n')
        except Exception:
            start_line = 1
            end_line = 1

        return CodeLocation(
            file_path=self.file_path,
            start_line=start_line,
            end_line=end_line
        )

    def _get_decorators(self, decorators: Sequence['cst.Decorator']) -> List[str]:
        """获取装饰器列表"""
        result = []
        for dec in decorators:
            try:
                dec_str = cst.Module([]).code_for_node(dec.decorator)
                result.append(f"@{dec_str}")
            except Exception:
                pass
        return result

    def _get_parameters(self, params: 'cst.Parameters') -> List[Dict]:
        """获取参数列表"""
        result = []

        # 普通参数
        for param in params.params:
            param_info = self._extract_param_info(param)
            result.append(param_info)

        # *args
        if params.star_arg and isinstance(params.star_arg, cst.Param):
            param_info = self._extract_param_info(params.star_arg)
            param_info["kind"] = "var_positional"
            result.append(param_info)

        # 仅关键字参数
        for param in params.kwonly_params:
            param_info = self._extract_param_info(param)
            param_info["kind"] = "keyword_only"
            result.append(param_info)

        # **kwargs
        if params.star_kwarg:
            param_info = self._extract_param_info(params.star_kwarg)
            param_info["kind"] = "var_keyword"
            result.append(param_info)

        return result

    def _extract_param_info(self, param: 'cst.Param') -> Dict:
        """提取单个参数信息"""
        info = {
            "name": param.name.value,
            "type": "",
            "default": None,
            "kind": "positional_or_keyword",
        }

        # 类型注解
        if param.annotation:
            info["type"] = self.extractor._get_annotation_string(param.annotation)

        # 默认值
        if param.default:
            try:
                info["default"] = cst.Module([]).code_for_node(param.default)
            except Exception:
                info["default"] = "..."

        return info

    def _generate_signature(
        self,
        name: str,
        parameters: List[Dict],
        return_type: str,
        decorators: List[str]
    ) -> str:
        """生成函数签名"""
        parts = []

        # 装饰器
        for dec in decorators:
            parts.append(dec)

        # 参数字符串
        param_strs = []
        for param in parameters:
            p = param["name"]
            if param.get("type"):
                p += f": {param['type']}"
            if param.get("default"):
                p += f" = {param['default']}"

            kind = param.get("kind", "")
            if kind == "var_positional":
                p = f"*{p}"
            elif kind == "var_keyword":
                p = f"**{p}"

            param_strs.append(p)

        # 函数定义
        func_def = f"def {name}({', '.join(param_strs)})"
        if return_type:
            func_def += f" -> {return_type}"
        func_def += ":"

        parts.append(func_def)

        return "\n".join(parts)

    def _extract_raised_exceptions(self, body: 'cst.BaseSuite') -> List[str]:
        """提取函数中 raise 的异常"""
        exceptions = []

        class RaiseVisitor(cst.CSTVisitor):
            def visit_Raise(self, node: 'cst.Raise') -> None:
                if node.exc:
                    if isinstance(node.exc, cst.Call):
                        exc_name = self._get_exc_name(node.exc.func)
                    else:
                        exc_name = self._get_exc_name(node.exc)
                    if exc_name:
                        exceptions.append(exc_name)

            def _get_exc_name(self, node) -> str:
                if isinstance(node, cst.Name):
                    return node.value
                elif isinstance(node, cst.Attribute):
                    return f"{self._get_exc_name(node.value)}.{node.attr.value}"
                return ""

        def visit_node(node):
            """递归遍历节点"""
            if isinstance(node, cst.Raise) and node.exc:
                if isinstance(node.exc, cst.Call):
                    exc_name = get_exc_name(node.exc.func)
                else:
                    exc_name = get_exc_name(node.exc)
                if exc_name:
                    exceptions.append(exc_name)

            # 递归遍历子节点
            for child in node.children:
                visit_node(child)

        def get_exc_name(node) -> str:
            if isinstance(node, cst.Name):
                return node.value
            elif isinstance(node, cst.Attribute):
                return f"{get_exc_name(node.value)}.{node.attr.value}"
            return ""

        if isinstance(body, cst.IndentedBlock):
            for stmt in body.body:
                visit_node(stmt)

        return list(set(exceptions))

    def _determine_function_type(self, decorators: List[str], parameters: List[Dict]) -> str:
        """确定函数类型"""
        dec_str = " ".join(decorators).lower()

        if "@staticmethod" in dec_str:
            return "staticmethod"
        elif "@classmethod" in dec_str:
            return "classmethod"
        elif "@property" in dec_str:
            return "property"
        elif any("setter" in d for d in decorators):
            return "setter"
        elif parameters and parameters[0]["name"] == "self":
            return "method"
        elif parameters and parameters[0]["name"] == "cls":
            return "classmethod"
        else:
            return "function"
