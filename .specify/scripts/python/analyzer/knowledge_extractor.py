# -*- coding: utf-8 -*-
"""
知识提取器 - 主动式规范发现系统

设计理念：
1. 不依赖预定义关键词，自动发现项目特有的概念
2. 分析代码内容和语义，而不仅仅是结构
3. 提供一套通用的知识提取框架
4. 根据项目特点动态生成文档

提取的知识类型：
- 常量定义（不仅仅是 Enum，还包括模块级常量）
- 配置规范（配置文件格式、读取方式）
- 数据模型（字段类型、关系、约束）
- 日志规范（日志格式、级别）
- 依赖关系（模块间调用关系）
- 业务概念（领域术语、业务流程）
"""
import os
import re
import ast
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ConstantDefinition:
    """常量定义"""
    name: str
    value: str
    value_type: str  # string, int, dict, list, etc.
    file_path: str
    line: int
    category: str = ""  # 自动推断的类别
    docstring: str = ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.value,
            "value_type": self.value_type,
            "file_path": self.file_path,
            "line": self.line,
            "category": self.category,
            "docstring": self.docstring,
        }


@dataclass
class ModelField:
    """模型字段"""
    name: str
    field_type: str
    required: bool = True
    default: str = ""
    description: str = ""
    constraints: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "field_type": self.field_type,
            "required": self.required,
            "default": self.default,
            "description": self.description,
            "constraints": self.constraints,
        }


@dataclass
class ModelDefinition:
    """数据模型定义"""
    name: str
    base_class: str
    fields: List[ModelField]
    file_path: str
    line: int
    docstring: str = ""
    table_name: str = ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "base_class": self.base_class,
            "fields": [f.to_dict() for f in self.fields],
            "file_path": self.file_path,
            "line": self.line,
            "docstring": self.docstring,
            "table_name": self.table_name,
        }


@dataclass
class ImportPattern:
    """导入模式"""
    module: str
    names: List[str]
    count: int = 1
    example_files: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "module": self.module,
            "names": self.names,
            "count": self.count,
            "example_files": self.example_files[:3],
        }


@dataclass
class LogPattern:
    """日志模式"""
    logger_name: str
    log_levels: List[str]
    format_pattern: str = ""
    count: int = 1
    example_files: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "logger_name": self.logger_name,
            "log_levels": self.log_levels,
            "format_pattern": self.format_pattern,
            "count": self.count,
            "example_files": self.example_files[:3],
        }


class KnowledgeExtractor:
    """知识提取器 - 主动发现项目规范"""

    def __init__(self):
        self.constants: List[ConstantDefinition] = []
        self.models: List[ModelDefinition] = []
        self.import_patterns: Dict[str, ImportPattern] = {}
        self.log_patterns: Dict[str, LogPattern] = {}
        self.config_patterns: List[Dict] = []
        self.business_terms: Set[str] = set()

    def extract_all(self, source_dir: str) -> Dict:
        """
        提取所有知识

        返回: 包含所有提取知识的字典
        """
        self.constants = []
        self.models = []
        self.import_patterns = {}
        self.log_patterns = {}
        self.config_patterns = []
        self.business_terms = set()

        # 遍历所有 Python 文件
        for root, dirs, files in os.walk(source_dir):
            # 跳过不需要的目录
            dirs[:] = [d for d in dirs if not d.startswith('.')
                       and d not in ('__pycache__', 'Thrift', 'migrations', 'node_modules')]

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self._extract_from_file(file_path)

        return self._build_knowledge_base()

    def _extract_from_file(self, file_path: str):
        """从单个文件提取知识"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
        except Exception:
            return

        # 1. 提取常量定义
        self._extract_constants(tree, file_path, content)

        # 2. 提取模型定义
        self._extract_models(tree, file_path, content)

        # 3. 提取导入模式
        self._extract_imports(tree, file_path)

        # 4. 提取日志模式
        self._extract_log_patterns(content, file_path)

        # 5. 提取配置模式
        self._extract_config_patterns(tree, file_path, content)

        # 6. 提取业务术语
        self._extract_business_terms(tree, content)

    def _extract_constants(self, tree: ast.AST, file_path: str, content: str):
        """提取常量定义"""
        lines = content.split('\n')

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        # 检查是否是常量（全大写或特定模式）
                        if self._is_constant_name(name):
                            value, value_type = self._get_value_info(node.value)
                            if value:
                                # 获取上一行的注释作为文档
                                docstring = ""
                                if node.lineno > 1:
                                    prev_line = lines[node.lineno - 2].strip()
                                    if prev_line.startswith('#'):
                                        docstring = prev_line[1:].strip()

                                category = self._categorize_constant(name, value, file_path)

                                self.constants.append(ConstantDefinition(
                                    name=name,
                                    value=value,
                                    value_type=value_type,
                                    file_path=file_path,
                                    line=node.lineno,
                                    category=category,
                                    docstring=docstring,
                                ))

    def _is_constant_name(self, name: str) -> bool:
        """判断是否是常量名"""
        # 全大写
        if name.isupper() and len(name) > 1:
            return True
        # 以大写开头且包含下划线（如 Upgrade_Job_NotFound）
        if name[0].isupper() and '_' in name:
            return True
        # 特定后缀
        if name.endswith(('_CHOICES', '_STATUS', '_TYPE', '_LEVEL', '_CODE')):
            return True
        return False

    def _get_value_info(self, node) -> Tuple[str, str]:
        """获取值信息"""
        if isinstance(node, ast.Constant):
            value = str(node.value)
            if isinstance(node.value, str):
                return value[:100], 'string'
            elif isinstance(node.value, int):
                return value, 'int'
            elif isinstance(node.value, float):
                return value, 'float'
            elif isinstance(node.value, bool):
                return value, 'bool'
            return value[:100], 'unknown'
        elif isinstance(node, ast.Dict):
            return '{...}', 'dict'
        elif isinstance(node, ast.List):
            return '[...]', 'list'
        elif isinstance(node, ast.Tuple):
            return '(...)', 'tuple'
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return f'{node.func.id}(...)', 'call'
        return None, 'unknown'

    def _categorize_constant(self, name: str, value: str, file_path: str) -> str:
        """自动推断常量类别"""
        name_lower = name.lower()
        path_lower = file_path.lower()

        if 'error' in name_lower or 'error' in path_lower:
            return 'error_code'
        if 'status' in name_lower:
            return 'status'
        if 'type' in name_lower:
            return 'type'
        if 'level' in name_lower:
            return 'level'
        if 'choice' in name_lower:
            return 'choices'
        if 'config' in path_lower or 'setting' in path_lower:
            return 'config'
        if 'constant' in path_lower:
            return 'constant'
        return 'other'

    def _extract_models(self, tree: ast.AST, file_path: str, content: str):
        """提取数据模型定义"""
        # 只在 models.py 或包含 Model 的文件中提取
        if 'models' not in file_path.lower() and 'model' not in file_path.lower():
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查是否是 Django Model
                base_names = [self._get_base_name(b) for b in node.bases]
                model_bases = [b for b in base_names if 'Model' in b or 'Base' in b]

                if model_bases:
                    fields = self._extract_model_fields(node)
                    docstring = ast.get_docstring(node) or ""

                    # 提取 Meta 中的 table_name
                    table_name = ""
                    for item in node.body:
                        if isinstance(item, ast.ClassDef) and item.name == 'Meta':
                            for meta_item in item.body:
                                if isinstance(meta_item, ast.Assign):
                                    for target in meta_item.targets:
                                        if isinstance(target, ast.Name) and target.id == 'db_table':
                                            if isinstance(meta_item.value, ast.Constant):
                                                table_name = str(meta_item.value.value)

                    self.models.append(ModelDefinition(
                        name=node.name,
                        base_class=model_bases[0] if model_bases else 'Model',
                        fields=fields,
                        file_path=file_path,
                        line=node.lineno,
                        docstring=docstring[:200],
                        table_name=table_name,
                    ))

    def _extract_model_fields(self, class_node: ast.ClassDef) -> List[ModelField]:
        """提取模型字段"""
        fields = []

        for node in class_node.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        field_name = target.id
                        if field_name.startswith('_'):
                            continue

                        # 检查是否是 Django 字段
                        if isinstance(node.value, ast.Call):
                            field_type = self._get_field_type(node.value)
                            if field_type:
                                required = self._is_field_required(node.value)
                                default = self._get_field_default(node.value)
                                constraints = self._get_field_constraints(node.value)

                                fields.append(ModelField(
                                    name=field_name,
                                    field_type=field_type,
                                    required=required,
                                    default=default,
                                    constraints=constraints,
                                ))

        return fields

    def _get_field_type(self, call_node: ast.Call) -> Optional[str]:
        """获取字段类型"""
        if isinstance(call_node.func, ast.Attribute):
            # models.CharField
            if call_node.func.attr.endswith('Field'):
                return call_node.func.attr
        elif isinstance(call_node.func, ast.Name):
            # CharField (直接导入)
            if call_node.func.id.endswith('Field'):
                return call_node.func.id
        return None

    def _is_field_required(self, call_node: ast.Call) -> bool:
        """判断字段是否必填"""
        for keyword in call_node.keywords:
            if keyword.arg in ('null', 'blank'):
                if isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                    return False
        return True

    def _get_field_default(self, call_node: ast.Call) -> str:
        """获取字段默认值"""
        for keyword in call_node.keywords:
            if keyword.arg == 'default':
                value, _ = self._get_value_info(keyword.value)
                return value or ""
        return ""

    def _get_field_constraints(self, call_node: ast.Call) -> List[str]:
        """获取字段约束"""
        constraints = []
        for keyword in call_node.keywords:
            if keyword.arg == 'max_length':
                if isinstance(keyword.value, ast.Constant):
                    constraints.append(f"max_length={keyword.value.value}")
            elif keyword.arg == 'unique':
                if isinstance(keyword.value, ast.Constant) and keyword.value.value:
                    constraints.append("unique")
            elif keyword.arg == 'choices':
                constraints.append("has_choices")
        return constraints

    def _get_base_name(self, node) -> str:
        """获取基类名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return ""

    def _extract_imports(self, tree: ast.AST, file_path: str):
        """提取导入模式"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    key = node.module
                    names = [alias.name for alias in node.names]

                    if key in self.import_patterns:
                        self.import_patterns[key].count += 1
                        if file_path not in self.import_patterns[key].example_files:
                            self.import_patterns[key].example_files.append(file_path)
                        # 合并 names
                        for name in names:
                            if name not in self.import_patterns[key].names:
                                self.import_patterns[key].names.append(name)
                    else:
                        self.import_patterns[key] = ImportPattern(
                            module=key,
                            names=names,
                            count=1,
                            example_files=[file_path],
                        )

    def _extract_log_patterns(self, content: str, file_path: str):
        """提取日志模式"""
        # 匹配 logger = logging.getLogger('xxx')
        logger_pattern = r"logger\s*=\s*logging\.getLogger\(['\"]([^'\"]+)['\"]\)"
        for match in re.finditer(logger_pattern, content):
            logger_name = match.group(1)
            key = logger_name

            if key in self.log_patterns:
                self.log_patterns[key].count += 1
                if file_path not in self.log_patterns[key].example_files:
                    self.log_patterns[key].example_files.append(file_path)
            else:
                self.log_patterns[key] = LogPattern(
                    logger_name=logger_name,
                    log_levels=[],
                    count=1,
                    example_files=[file_path],
                )

        # 匹配日志调用 logger.info/error/warning/debug
        log_call_pattern = r"logger\.(info|error|warning|debug|exception)\("
        for match in re.finditer(log_call_pattern, content):
            level = match.group(1)
            # 更新所有 logger 的 levels
            for pattern in self.log_patterns.values():
                if level not in pattern.log_levels:
                    pattern.log_levels.append(level)

    def _extract_config_patterns(self, tree: ast.AST, file_path: str, content: str):
        """提取配置模式"""
        # 检测 settings.py 或 config.py
        if 'settings' in file_path.lower() or 'config' in file_path.lower():
            # 提取配置项
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            value, value_type = self._get_value_info(node.value)
                            if value:
                                self.config_patterns.append({
                                    "name": target.id,
                                    "value_type": value_type,
                                    "file_path": file_path,
                                    "line": node.lineno,
                                })

    def _extract_business_terms(self, tree: ast.AST, content: str):
        """提取业务术语"""
        # 从类名和函数名中提取业务术语
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 分解驼峰命名
                terms = self._split_camel_case(node.name)
                self.business_terms.update(terms)
            elif isinstance(node, ast.FunctionDef):
                # 分解下划线命名
                terms = node.name.split('_')
                self.business_terms.update([t for t in terms if len(t) > 2])

    def _split_camel_case(self, name: str) -> List[str]:
        """分解驼峰命名"""
        terms = re.findall(r'[A-Z][a-z]+|[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)', name)
        return [t.lower() for t in terms if len(t) > 2]

    def _build_knowledge_base(self) -> Dict:
        """构建知识库"""
        # 按类别分组常量
        constants_by_category = defaultdict(list)
        for const in self.constants:
            constants_by_category[const.category].append(const.to_dict())

        # 按模块分组导入
        top_imports = sorted(
            self.import_patterns.values(),
            key=lambda x: x.count,
            reverse=True
        )[:30]

        # 按使用频率排序日志模式
        top_log_patterns = sorted(
            self.log_patterns.values(),
            key=lambda x: x.count,
            reverse=True
        )[:10]

        # 过滤常见词汇，保留业务术语
        common_words = {'get', 'set', 'create', 'delete', 'update', 'list', 'view',
                        'handler', 'service', 'model', 'test', 'init', 'self', 'cls',
                        'args', 'kwargs', 'request', 'response', 'data', 'result'}
        business_terms = [t for t in self.business_terms if t not in common_words]

        return {
            "constants": {
                "total": len(self.constants),
                "by_category": dict(constants_by_category),
            },
            "models": {
                "total": len(self.models),
                "definitions": [m.to_dict() for m in self.models],
            },
            "imports": {
                "total": len(self.import_patterns),
                "top_patterns": [p.to_dict() for p in top_imports],
            },
            "logging": {
                "total": len(self.log_patterns),
                "patterns": [p.to_dict() for p in top_log_patterns],
            },
            "config": {
                "total": len(self.config_patterns),
                "patterns": self.config_patterns[:20],
            },
            "business_terms": sorted(business_terms)[:50],
        }


def extract_knowledge(source_dir: str) -> Dict:
    """提取知识的便捷函数"""
    extractor = KnowledgeExtractor()
    return extractor.extract_all(source_dir)
