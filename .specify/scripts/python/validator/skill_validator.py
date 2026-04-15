# -*- coding: utf-8 -*-
"""
Skill 验证器

验证生成的 Skill 文档，防止幻觉
"""
import os
import re
import yaml
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ValidationLevel(Enum):
    """验证级别"""
    ERROR = "error"      # 必须修复
    WARNING = "warning"  # 建议修复
    INFO = "info"        # 信息提示


@dataclass
class ValidationIssue:
    """验证问题"""
    level: ValidationLevel
    code: str           # 问题代码，如 "MISSING_SOURCE"
    message: str        # 问题描述
    location: str = ""  # 问题位置
    suggestion: str = ""  # 修复建议


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)
    checked_items: int = 0
    passed_items: int = 0

    def add_error(self, code: str, message: str, location: str = "", suggestion: str = ""):
        self.issues.append(ValidationIssue(
            level=ValidationLevel.ERROR,
            code=code,
            message=message,
            location=location,
            suggestion=suggestion
        ))
        self.is_valid = False

    def add_warning(self, code: str, message: str, location: str = "", suggestion: str = ""):
        self.issues.append(ValidationIssue(
            level=ValidationLevel.WARNING,
            code=code,
            message=message,
            location=location,
            suggestion=suggestion
        ))

    def add_info(self, code: str, message: str, location: str = ""):
        self.issues.append(ValidationIssue(
            level=ValidationLevel.INFO,
            code=code,
            message=message,
            location=location
        ))

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.level == ValidationLevel.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.level == ValidationLevel.WARNING)

    def merge(self, other: 'ValidationResult'):
        """合并另一个验证结果"""
        self.issues.extend(other.issues)
        self.checked_items += other.checked_items
        self.passed_items += other.passed_items
        if not other.is_valid:
            self.is_valid = False


class SkillValidator:
    """Skill 验证器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.project_path = self.config.get('project_path', '')

        # 已知的代码元素（从知识库加载）
        self.known_classes: Set[str] = set()
        self.known_functions: Set[str] = set()
        self.known_constants: Set[str] = set()
        self.known_files: Set[str] = set()

    def load_knowledge_base(self, kb_path: str) -> None:
        """从知识库加载已知元素"""
        import json

        with open(kb_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 加载类名
        for cls in data.get('classes', []):
            if isinstance(cls, dict):
                self.known_classes.add(cls.get('name', ''))
            elif isinstance(cls, str):
                self.known_classes.add(cls)

        # 加载函数名
        for func in data.get('functions', []):
            if isinstance(func, dict):
                self.known_functions.add(func.get('name', ''))
            elif isinstance(func, str):
                self.known_functions.add(func)

        # 加载常量名
        for const in data.get('constants', []):
            if isinstance(const, dict):
                self.known_constants.add(const.get('name', ''))
            elif isinstance(const, str):
                self.known_constants.add(const)

        # 加载文件路径
        for file_info in data.get('files', []):
            if isinstance(file_info, dict):
                self.known_files.add(file_info.get('relative_path', ''))
            elif isinstance(file_info, str):
                self.known_files.add(file_info)

        self.project_path = data.get('project_path', self.project_path)

    def validate_skill_file(self, skill_path: str) -> ValidationResult:
        """验证单个 Skill 文件"""
        result = ValidationResult()

        if not os.path.exists(skill_path):
            result.add_error(
                "FILE_NOT_FOUND",
                f"Skill 文件不存在: {skill_path}"
            )
            return result

        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证 YAML 头部
        self._validate_yaml_header(content, skill_path, result)

        # 验证代码引用
        self._validate_code_references(content, skill_path, result)

        # 验证文件路径引用
        self._validate_file_references(content, skill_path, result)

        # 验证置信度标记
        self._validate_confidence_markers(content, skill_path, result)

        return result

    def validate_skill_directory(self, skill_dir: str) -> ValidationResult:
        """验证整个 Skill 目录"""
        result = ValidationResult()

        if not os.path.isdir(skill_dir):
            result.add_error(
                "DIR_NOT_FOUND",
                f"Skill 目录不存在: {skill_dir}"
            )
            return result

        # 验证 index.yaml
        index_path = os.path.join(skill_dir, 'index.yaml')
        if os.path.exists(index_path):
            index_result = self._validate_index(index_path)
            result.merge(index_result)
        else:
            result.add_warning(
                "MISSING_INDEX",
                "缺少 index.yaml 文件",
                location=skill_dir,
                suggestion="运行生成器创建索引文件"
            )

        # 验证所有 .md 文件
        for filename in os.listdir(skill_dir):
            if filename.endswith('.md'):
                skill_path = os.path.join(skill_dir, filename)
                skill_result = self.validate_skill_file(skill_path)
                result.merge(skill_result)

        return result

    def _validate_yaml_header(
        self,
        content: str,
        file_path: str,
        result: ValidationResult
    ) -> None:
        """验证 YAML 头部"""
        result.checked_items += 1

        # 检查是否有 YAML 头部
        if not content.startswith('---'):
            result.add_error(
                "MISSING_YAML_HEADER",
                "缺少 YAML 头部",
                location=file_path,
                suggestion="添加 YAML 头部，包含 skill_id, title, triggers 等字段"
            )
            return

        # 提取 YAML 头部
        parts = content.split('---', 2)
        if len(parts) < 3:
            result.add_error(
                "INVALID_YAML_HEADER",
                "YAML 头部格式不正确",
                location=file_path
            )
            return

        try:
            header = yaml.safe_load(parts[1])
        except yaml.YAMLError as e:
            result.add_error(
                "YAML_PARSE_ERROR",
                f"YAML 解析错误: {str(e)}",
                location=file_path
            )
            return

        if not header:
            result.add_error(
                "EMPTY_YAML_HEADER",
                "YAML 头部为空",
                location=file_path
            )
            return

        # 检查必需字段
        required_fields = ['skill_id', 'title']
        for field in required_fields:
            if field not in header:
                result.add_error(
                    "MISSING_REQUIRED_FIELD",
                    f"缺少必需字段: {field}",
                    location=file_path
                )

        # 检查推荐字段
        recommended_fields = ['description', 'triggers', 'confidence']
        for field in recommended_fields:
            if field not in header:
                result.add_warning(
                    "MISSING_RECOMMENDED_FIELD",
                    f"缺少推荐字段: {field}",
                    location=file_path
                )

        result.passed_items += 1

    def _validate_code_references(
        self,
        content: str,
        file_path: str,
        result: ValidationResult
    ) -> None:
        """验证代码引用"""
        # 提取代码块中的类名和函数名引用
        code_block_pattern = r'```[\w]*\n(.*?)```'
        inline_code_pattern = r'`([A-Z][a-zA-Z0-9_]*)`'

        # 检查内联代码引用
        for match in re.finditer(inline_code_pattern, content):
            name = match.group(1)
            result.checked_items += 1

            # 检查是否是已知的类、函数或常量
            if (name in self.known_classes or
                name in self.known_functions or
                name in self.known_constants):
                result.passed_items += 1
            else:
                # 可能是标准库或第三方库的类
                if not self._is_standard_name(name):
                    result.add_warning(
                        "UNKNOWN_REFERENCE",
                        f"未知的代码引用: {name}",
                        location=file_path,
                        suggestion="确认该名称在项目中存在"
                    )

    def _validate_file_references(
        self,
        content: str,
        file_path: str,
        result: ValidationResult
    ) -> None:
        """验证文件路径引用"""
        # 匹配文件路径模式
        file_patterns = [
            r'`([a-zA-Z_][a-zA-Z0-9_/]*\.py)`',  # Python 文件
            r'`([a-zA-Z_][a-zA-Z0-9_/]*\.md)`',  # Markdown 文件
        ]

        for pattern in file_patterns:
            for match in re.finditer(pattern, content):
                file_ref = match.group(1)
                result.checked_items += 1

                # 检查文件是否存在
                if file_ref in self.known_files:
                    result.passed_items += 1
                elif self.project_path:
                    full_path = os.path.join(self.project_path, file_ref)
                    if os.path.exists(full_path):
                        result.passed_items += 1
                    else:
                        result.add_warning(
                            "FILE_NOT_FOUND",
                            f"引用的文件不存在: {file_ref}",
                            location=file_path
                        )

    def _validate_confidence_markers(
        self,
        content: str,
        file_path: str,
        result: ValidationResult
    ) -> None:
        """验证置信度标记"""
        # 检查是否有置信度标记
        confidence_patterns = [
            r'\[事实层[^\]]*\]',
            r'\[统计层[^\]]*\]',
            r'\[推断层[^\]]*\]',
            r'\[建议层[^\]]*\]',
        ]

        has_confidence_marker = False
        for pattern in confidence_patterns:
            if re.search(pattern, content):
                has_confidence_marker = True
                break

        if not has_confidence_marker:
            result.add_info(
                "NO_CONFIDENCE_MARKERS",
                "文档中没有置信度标记",
                location=file_path
            )

    def _validate_index(self, index_path: str) -> ValidationResult:
        """验证 index.yaml"""
        result = ValidationResult()
        result.checked_items += 1

        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            result.add_error(
                "INDEX_PARSE_ERROR",
                f"index.yaml 解析错误: {str(e)}",
                location=index_path
            )
            return result

        if not index_data:
            result.add_error(
                "EMPTY_INDEX",
                "index.yaml 为空",
                location=index_path
            )
            return result

        # 检查必需字段
        if 'skills' not in index_data:
            result.add_error(
                "MISSING_SKILLS_FIELD",
                "index.yaml 缺少 skills 字段",
                location=index_path
            )

        result.passed_items += 1
        return result

    def _is_standard_name(self, name: str) -> bool:
        """检查是否是标准库或常见名称"""
        standard_names = {
            # Python 内置
            'Exception', 'ValueError', 'TypeError', 'KeyError',
            'RuntimeError', 'AttributeError', 'IndexError',
            'True', 'False', 'None', 'List', 'Dict', 'Set', 'Tuple',
            'Optional', 'Any', 'Union', 'Callable',
            # Django
            'Model', 'View', 'Form', 'QuerySet', 'Manager',
            'CharField', 'IntegerField', 'TextField', 'DateTimeField',
            'ForeignKey', 'ManyToManyField', 'OneToOneField',
            'HttpRequest', 'HttpResponse', 'JsonResponse',
            # 常见
            'Enum', 'ABC', 'abstractmethod', 'dataclass',
        }
        return name in standard_names

    def generate_report(self, result: ValidationResult) -> str:
        """生成验证报告"""
        lines = [
            "# Skill 验证报告",
            "",
            f"**检查项目**: {result.checked_items}",
            f"**通过项目**: {result.passed_items}",
            f"**错误数**: {result.error_count}",
            f"**警告数**: {result.warning_count}",
            "",
        ]

        if result.is_valid:
            lines.append("✅ **验证通过**")
        else:
            lines.append("❌ **验证失败**")

        lines.append("")

        # 按级别分组
        errors = [i for i in result.issues if i.level == ValidationLevel.ERROR]
        warnings = [i for i in result.issues if i.level == ValidationLevel.WARNING]
        infos = [i for i in result.issues if i.level == ValidationLevel.INFO]

        if errors:
            lines.append("## 错误")
            lines.append("")
            for issue in errors:
                lines.append(f"- **[{issue.code}]** {issue.message}")
                if issue.location:
                    lines.append(f"  - 位置: `{issue.location}`")
                if issue.suggestion:
                    lines.append(f"  - 建议: {issue.suggestion}")
            lines.append("")

        if warnings:
            lines.append("## 警告")
            lines.append("")
            for issue in warnings:
                lines.append(f"- **[{issue.code}]** {issue.message}")
                if issue.location:
                    lines.append(f"  - 位置: `{issue.location}`")
                if issue.suggestion:
                    lines.append(f"  - 建议: {issue.suggestion}")
            lines.append("")

        if infos:
            lines.append("## 信息")
            lines.append("")
            for issue in infos:
                lines.append(f"- **[{issue.code}]** {issue.message}")
            lines.append("")

        return "\n".join(lines)
