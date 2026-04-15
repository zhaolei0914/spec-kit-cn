# -*- coding: utf-8 -*-
"""
导入提取器

提取 import 语句、模块依赖关系
"""
from typing import Dict, List, Optional

try:
    import libcst as cst
except ImportError:
    cst = None

from .base_libcst import LibCSTExtractor, CodeUnit, CodeLocation


class ImportExtractor(LibCSTExtractor):
    """导入提取器"""

    @property
    def name(self) -> str:
        return "import_extractor"

    @property
    def description(self) -> str:
        return "提取 import 语句和模块依赖关系"

    def extract_from_tree(
        self,
        tree: 'cst.Module',
        file_path: str,
        source_code: str,
        wrapper: 'cst.MetadataWrapper' = None
    ) -> List[CodeUnit]:
        """从 CST 树中提取导入"""
        visitor = ImportVisitor(file_path, source_code, self)
        if wrapper:
            wrapper.visit(visitor)
        return visitor.imports


class ImportVisitor(cst.CSTVisitor):
    """导入访问器"""

    def __init__(self, file_path: str, source_code: str, extractor: ImportExtractor):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.split('\n')
        self.extractor = extractor
        self.imports: List[CodeUnit] = []
        self._current_line = 0

    def visit_Import(self, node: 'cst.Import') -> None:
        """访问 import 语句"""
        for name in node.names if isinstance(node.names, tuple) else [node.names]:
            if isinstance(name, cst.ImportAlias):
                module_name = self._get_module_name(name.name)
                alias = name.asname.name.value if name.asname else None

                location = self._get_location(module_name)

                try:
                    source_code = cst.Module([]).code_for_node(node)
                except Exception:
                    source_code = f"import {module_name}"

                unit = CodeUnit(
                    name=module_name,
                    type="import",
                    location=location,
                    source_code=source_code,
                    module=module_name,
                    is_from_import=False,
                    confidence=1.0,
                    confidence_level="fact",
                    metadata={
                        "alias": alias,
                        "is_standard_lib": self._is_standard_lib(module_name),
                        "is_third_party": self._is_third_party(module_name),
                        "is_local": self._is_local_import(module_name),
                    }
                )

                self.imports.append(unit)

    def visit_ImportFrom(self, node: 'cst.ImportFrom') -> None:
        """访问 from ... import 语句"""
        # 获取模块名
        if node.module:
            module_name = self._get_module_name(node.module)
        else:
            module_name = ""

        # 处理相对导入
        relative_prefix = ""
        if node.relative:
            relative_prefix = "." * len(node.relative)

        full_module = relative_prefix + module_name

        # 获取导入的名称
        imported_names = []
        if isinstance(node.names, cst.ImportStar):
            imported_names = ["*"]
        elif isinstance(node.names, tuple):
            for name in node.names:
                if isinstance(name, cst.ImportAlias):
                    import_name = self._get_module_name(name.name)
                    alias = name.asname.name.value if name.asname else None
                    imported_names.append({
                        "name": import_name,
                        "alias": alias
                    })

        location = self._get_location(full_module or "from")

        try:
            source_code = cst.Module([]).code_for_node(node)
        except Exception:
            source_code = f"from {full_module} import ..."

        unit = CodeUnit(
            name=full_module,
            type="import",
            location=location,
            source_code=source_code,
            module=full_module,
            imported_names=[n["name"] if isinstance(n, dict) else n for n in imported_names],
            is_from_import=True,
            confidence=1.0,
            confidence_level="fact",
            metadata={
                "is_relative": bool(relative_prefix),
                "relative_level": len(relative_prefix),
                "import_details": imported_names,
                "is_star_import": imported_names == ["*"],
                "is_standard_lib": self._is_standard_lib(module_name),
                "is_third_party": self._is_third_party(module_name),
                "is_local": self._is_local_import(module_name) or bool(relative_prefix),
            }
        )

        self.imports.append(unit)

    def _get_module_name(self, node) -> str:
        """获取模块名称"""
        if isinstance(node, cst.Name):
            return node.value
        elif isinstance(node, cst.Attribute):
            return f"{self._get_module_name(node.value)}.{node.attr.value}"
        return ""

    def _get_location(self, search_term: str) -> CodeLocation:
        """获取导入位置"""
        start_line = 1
        for i, line in enumerate(self.source_lines, 1):
            if search_term in line and ('import' in line or 'from' in line):
                start_line = i
                break

        return CodeLocation(
            file_path=self.file_path,
            start_line=start_line,
            end_line=start_line
        )

    def _is_standard_lib(self, module_name: str) -> bool:
        """检查是否是标准库"""
        standard_libs = {
            'os', 'sys', 'io', 're', 'json', 'typing', 'collections',
            'itertools', 'functools', 'operator', 'pathlib', 'datetime',
            'time', 'logging', 'unittest', 'abc', 'copy', 'pickle',
            'hashlib', 'base64', 'urllib', 'http', 'email', 'html',
            'xml', 'csv', 'sqlite3', 'threading', 'multiprocessing',
            'subprocess', 'socket', 'ssl', 'asyncio', 'concurrent',
            'contextlib', 'dataclasses', 'enum', 'warnings', 'traceback',
            'inspect', 'importlib', 'pkgutil', 'tempfile', 'shutil',
            'glob', 'fnmatch', 'stat', 'fileinput', 'struct', 'codecs',
            'unicodedata', 'string', 'textwrap', 'difflib', 'math',
            'decimal', 'fractions', 'random', 'statistics', 'secrets',
        }
        root_module = module_name.split('.')[0] if module_name else ""
        return root_module in standard_libs

    def _is_third_party(self, module_name: str) -> bool:
        """检查是否是第三方库"""
        third_party_libs = {
            'django', 'flask', 'fastapi', 'requests', 'numpy', 'pandas',
            'sqlalchemy', 'celery', 'redis', 'pymongo', 'boto3', 'pytest',
            'libcst', 'jinja2', 'pydantic', 'httpx', 'aiohttp', 'uvicorn',
            'gunicorn', 'pillow', 'matplotlib', 'scipy', 'sklearn',
            'tensorflow', 'torch', 'transformers', 'openai', 'anthropic',
        }
        root_module = module_name.split('.')[0] if module_name else ""
        return root_module in third_party_libs

    def _is_local_import(self, module_name: str) -> bool:
        """检查是否是本地导入"""
        if not module_name:
            return False
        # 如果不是标准库也不是已知第三方库，可能是本地模块
        return not self._is_standard_lib(module_name) and not self._is_third_party(module_name)
