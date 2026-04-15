# -*- coding: utf-8 -*-
"""
Django Model 提取器

提取 Django 模型定义、字段、关系、Meta 配置等
"""
from typing import Dict, List, Optional

try:
    import libcst as cst
except ImportError:
    cst = None

from ..base_libcst import LibCSTExtractor, CodeUnit, CodeLocation


class DjangoModelExtractor(LibCSTExtractor):
    """Django Model 提取器"""

    # Django 模型基类
    MODEL_BASES = {'Model', 'models.Model', 'BaseModel', 'AbstractBaseModel'}

    # Django 字段类型
    FIELD_TYPES = {
        'CharField', 'TextField', 'IntegerField', 'FloatField', 'DecimalField',
        'BooleanField', 'NullBooleanField', 'DateField', 'DateTimeField',
        'TimeField', 'DurationField', 'AutoField', 'BigAutoField',
        'SmallAutoField', 'BigIntegerField', 'SmallIntegerField',
        'PositiveIntegerField', 'PositiveSmallIntegerField', 'PositiveBigIntegerField',
        'BinaryField', 'FileField', 'ImageField', 'FilePathField',
        'EmailField', 'URLField', 'UUIDField', 'GenericIPAddressField',
        'SlugField', 'JSONField', 'ArrayField', 'HStoreField',
        # 关系字段
        'ForeignKey', 'OneToOneField', 'ManyToManyField',
        'GenericForeignKey', 'GenericRelation',
    }

    @property
    def name(self) -> str:
        return "django_model_extractor"

    @property
    def description(self) -> str:
        return "提取 Django 模型定义、字段、关系和 Meta 配置"

    def extract_from_tree(
        self,
        tree: 'cst.Module',
        file_path: str,
        source_code: str,
        wrapper: 'cst.MetadataWrapper' = None
    ) -> List[CodeUnit]:
        """从 CST 树中提取 Django 模型"""
        visitor = DjangoModelVisitor(file_path, source_code, self)
        if wrapper:
            wrapper.visit(visitor)
        return visitor.models


class DjangoModelVisitor(cst.CSTVisitor):
    """Django Model 访问器"""

    def __init__(self, file_path: str, source_code: str, extractor: DjangoModelExtractor):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.split('\n')
        self.extractor = extractor
        self.models: List[CodeUnit] = []

    def visit_ClassDef(self, node: 'cst.ClassDef') -> Optional[bool]:
        """访问类定义"""
        class_name = node.name.value

        # 检查是否是 Django Model
        bases = self._get_bases(node.bases)
        is_model = any(
            base in self.extractor.MODEL_BASES or
            base.endswith('Model') or
            'models.Model' in base
            for base in bases
        )

        if not is_model:
            return True

        # 获取位置
        location = self._get_location(class_name)

        # 获取 docstring
        docstring = self.extractor._get_docstring(node.body)

        # 提取字段
        fields = self._extract_fields(node.body)

        # 提取 Meta 配置
        meta_config = self._extract_meta(node.body)

        # 提取方法
        methods = self._extract_methods(node.body)

        # 提取关系
        relations = self._extract_relations(fields)

        try:
            source_code = cst.Module([]).code_for_node(node)
        except Exception:
            source_code = ""

        # 生成签名
        signature = f"class {class_name}({', '.join(bases)}):"

        unit = CodeUnit(
            name=class_name,
            type="django_model",
            location=location,
            source_code=source_code,
            signature=signature,
            docstring=docstring,
            bases=bases,
            attributes=fields,
            methods=methods,
            confidence=1.0,
            confidence_level="fact",
            metadata={
                "is_abstract": meta_config.get('abstract', False),
                "db_table": meta_config.get('db_table', ''),
                "ordering": meta_config.get('ordering', []),
                "verbose_name": meta_config.get('verbose_name', ''),
                "verbose_name_plural": meta_config.get('verbose_name_plural', ''),
                "unique_together": meta_config.get('unique_together', []),
                "indexes": meta_config.get('indexes', []),
                "constraints": meta_config.get('constraints', []),
                "meta_config": meta_config,
                "field_count": len(fields),
                "relation_count": len(relations),
                "relations": relations,
            }
        )

        self.models.append(unit)

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
        """获取类位置"""
        start_line = 1
        end_line = 1
        for i, line in enumerate(self.source_lines, 1):
            if f"class {class_name}" in line:
                start_line = i
                # 估算结束行
                end_line = start_line
                indent_level = len(line) - len(line.lstrip())
                for j in range(i, len(self.source_lines)):
                    next_line = self.source_lines[j]
                    if next_line.strip() and not next_line.startswith(' ' * (indent_level + 1)):
                        if j > i:
                            end_line = j
                            break
                    end_line = j + 1
                break

        return CodeLocation(
            file_path=self.file_path,
            start_line=start_line,
            end_line=end_line
        )

    def _extract_fields(self, body: 'cst.BaseSuite') -> List[Dict]:
        """提取模型字段"""
        fields = []

        if not isinstance(body, cst.IndentedBlock):
            return fields

        for stmt in body.body:
            if isinstance(stmt, cst.SimpleStatementLine):
                for item in stmt.body:
                    if isinstance(item, cst.Assign):
                        field_info = self._parse_field_assign(item)
                        if field_info:
                            fields.append(field_info)

        return fields

    def _parse_field_assign(self, node: 'cst.Assign') -> Optional[Dict]:
        """解析字段赋值"""
        if not node.targets:
            return None

        target = node.targets[0].target
        if not isinstance(target, cst.Name):
            return None

        field_name = target.value

        # 检查是否是字段定义
        if not isinstance(node.value, cst.Call):
            return None

        call = node.value
        field_type = self._get_name(call.func)

        # 检查是否是 Django 字段
        type_name = field_type.split('.')[-1]
        if type_name not in self.extractor.FIELD_TYPES:
            return None

        # 提取字段参数
        field_args = self._extract_field_args(call)

        return {
            "name": field_name,
            "type": type_name,
            "full_type": field_type,
            "args": field_args,
            "is_relation": type_name in ('ForeignKey', 'OneToOneField', 'ManyToManyField'),
            "is_required": not field_args.get('null', False) and not field_args.get('blank', False),
            "has_default": 'default' in field_args,
        }

    def _extract_field_args(self, call: 'cst.Call') -> Dict:
        """提取字段参数"""
        args = {}

        # 位置参数
        positional_args = []
        for i, arg in enumerate(call.args):
            try:
                arg_value = cst.Module([]).code_for_node(arg.value)
                if arg.keyword:
                    args[arg.keyword.value] = arg_value
                else:
                    positional_args.append(arg_value)
            except Exception:
                pass

        if positional_args:
            args['_positional'] = positional_args

        return args

    def _extract_meta(self, body: 'cst.BaseSuite') -> Dict:
        """提取 Meta 配置"""
        meta_config = {}

        if not isinstance(body, cst.IndentedBlock):
            return meta_config

        for stmt in body.body:
            if isinstance(stmt, cst.ClassDef) and stmt.name.value == 'Meta':
                meta_config = self._parse_meta_class(stmt.body)
                break

        return meta_config

    def _parse_meta_class(self, body: 'cst.BaseSuite') -> Dict:
        """解析 Meta 类"""
        config = {}

        if not isinstance(body, cst.IndentedBlock):
            return config

        for stmt in body.body:
            if isinstance(stmt, cst.SimpleStatementLine):
                for item in stmt.body:
                    if isinstance(item, cst.Assign):
                        for target in item.targets:
                            if isinstance(target.target, cst.Name):
                                key = target.target.value
                                try:
                                    value = cst.Module([]).code_for_node(item.value)
                                    # 尝试解析简单值
                                    if value in ('True', 'False'):
                                        config[key] = value == 'True'
                                    else:
                                        config[key] = value
                                except Exception:
                                    pass

        return config

    def _extract_methods(self, body: 'cst.BaseSuite') -> List[str]:
        """提取模型方法"""
        methods = []

        if not isinstance(body, cst.IndentedBlock):
            return methods

        for stmt in body.body:
            if isinstance(stmt, cst.FunctionDef):
                method_name = stmt.name.value
                # 获取装饰器
                decorators = []
                for dec in stmt.decorators:
                    try:
                        dec_str = cst.Module([]).code_for_node(dec.decorator)
                        decorators.append(f"@{dec_str}")
                    except Exception:
                        pass

                # 格式化方法签名
                if decorators:
                    methods.append(f"{' '.join(decorators)} {method_name}()")
                else:
                    methods.append(f"{method_name}()")

        return methods

    def _extract_relations(self, fields: List[Dict]) -> List[Dict]:
        """提取关系字段"""
        relations = []

        for field in fields:
            if field.get('is_relation'):
                relation = {
                    "field_name": field['name'],
                    "relation_type": field['type'],
                    "related_model": field['args'].get('_positional', [''])[0] if field['args'].get('_positional') else '',
                    "on_delete": field['args'].get('on_delete', ''),
                    "related_name": field['args'].get('related_name', ''),
                }
                relations.append(relation)

        return relations
