# -*- coding: utf-8 -*-
"""
Shell 知识融合器

将各个提取器的结果融合成统一的知识库
"""
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

from .function_extractor import ShellFunctionExtractor
from .variable_extractor import ShellVariableExtractor
from .comment_extractor import ShellCommentExtractor
from .source_extractor import ShellSourceExtractor
from .pattern_miner import ShellPatternMiner
from .base import ShellFunction, ShellVariable, ShellComment, ShellSource, ShellPattern


@dataclass
class ShellKnowledgeBase:
    """Shell 知识库"""

    # 项目信息
    project_name: str = ""
    project_path: str = ""

    # 提取的知识
    functions: List[ShellFunction] = field(default_factory=list)
    variables: List[ShellVariable] = field(default_factory=list)
    comments: List[ShellComment] = field(default_factory=list)
    sources: List[ShellSource] = field(default_factory=list)
    patterns: List[ShellPattern] = field(default_factory=list)

    # 统计信息
    statistics: Dict = field(default_factory=dict)

    # 错误信息
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "version": "1.0",
            "language": "shell",
            "project": {
                "name": self.project_name,
                "path": self.project_path,
            },
            "shell_specific": {
                "functions": [f.to_dict() for f in self.functions],
                "variables": [v.to_dict() for v in self.variables],
                "comments": [c.to_dict() for c in self.comments],
                "sources": [s.to_dict() for s in self.sources],
                "patterns": [p.to_dict() for p in self.patterns],
            },
            "statistics": self.statistics,
            "errors": self.errors,
            "generated_at": datetime.now().isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ShellKnowledgeBase':
        """从字典创建"""
        kb = cls()

        project = data.get("project", {})
        kb.project_name = project.get("name", "")
        kb.project_path = project.get("path", "")

        shell_specific = data.get("shell_specific", {})
        kb.functions = [ShellFunction.from_dict(f) for f in shell_specific.get("functions", [])]
        kb.variables = [ShellVariable.from_dict(v) for v in shell_specific.get("variables", [])]
        kb.comments = [ShellComment.from_dict(c) for c in shell_specific.get("comments", [])]
        kb.sources = [ShellSource.from_dict(s) for s in shell_specific.get("sources", [])]
        kb.patterns = [ShellPattern.from_dict(p) for p in shell_specific.get("patterns", [])]

        kb.statistics = data.get("statistics", {})
        kb.errors = data.get("errors", [])

        return kb

    def save(self, file_path: str):
        """保存到文件"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, file_path: str) -> 'ShellKnowledgeBase':
        """从文件加载"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def get_functions_by_file(self) -> Dict[str, List[ShellFunction]]:
        """按文件分组函数"""
        result = {}
        for func in self.functions:
            if func.file_path not in result:
                result[func.file_path] = []
            result[func.file_path].append(func)
        return result

    def get_variables_by_category(self) -> Dict[str, List[ShellVariable]]:
        """按分类分组变量"""
        result = {}
        for var in self.variables:
            if var.category not in result:
                result[var.category] = []
            result[var.category].append(var)
        return result

    def get_patterns_by_type(self) -> Dict[str, List[ShellPattern]]:
        """按类型分组模式"""
        result = {}
        for pattern in self.patterns:
            if pattern.pattern_type not in result:
                result[pattern.pattern_type] = []
            result[pattern.pattern_type].append(pattern)
        return result


class ShellKnowledgeBaseFusion:
    """Shell 知识库融合器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.errors: List[str] = []

    def analyze_project(self, project_path: str) -> ShellKnowledgeBase:
        """分析项目，生成知识库"""
        kb = ShellKnowledgeBase()
        kb.project_path = os.path.abspath(project_path)
        kb.project_name = os.path.basename(kb.project_path)

        print(f"[INFO] 开始分析 Shell 项目: {kb.project_path}")

        # 创建提取器
        func_extractor = ShellFunctionExtractor(self.config)
        var_extractor = ShellVariableExtractor(self.config)
        comment_extractor = ShellCommentExtractor(self.config)
        source_extractor = ShellSourceExtractor(self.config)
        pattern_miner = ShellPatternMiner(self.config)

        # 提取函数
        print("[INFO] 提取函数...")
        kb.functions = func_extractor.extract_all(project_path)
        self.errors.extend(func_extractor.errors)

        # 提取变量
        print("[INFO] 提取变量...")
        kb.variables = var_extractor.extract_all(project_path)
        self.errors.extend(var_extractor.errors)

        # 提取注释
        print("[INFO] 提取注释...")
        kb.comments = comment_extractor.extract_all(project_path)
        self.errors.extend(comment_extractor.errors)

        # 提取 source 引用
        print("[INFO] 提取 source 引用...")
        kb.sources = source_extractor.extract_all(project_path)
        self.errors.extend(source_extractor.errors)

        # 挖掘模式
        print("[INFO] 挖掘代码模式...")
        kb.patterns = pattern_miner.extract_all(project_path)
        self.errors.extend(pattern_miner.errors)

        # 统计信息
        kb.statistics = self._compute_statistics(kb, func_extractor)
        kb.errors = self.errors

        print(f"[INFO] 分析完成")

        return kb

    def _compute_statistics(self, kb: ShellKnowledgeBase, func_extractor: ShellFunctionExtractor) -> Dict:
        """计算统计信息"""
        # 获取文件列表
        shell_files = func_extractor._find_shell_files(kb.project_path)

        # 按分类统计变量
        var_by_category = {}
        for var in kb.variables:
            if var.category not in var_by_category:
                var_by_category[var.category] = 0
            var_by_category[var.category] += 1

        # 按类型统计模式
        pattern_by_type = {}
        for pattern in kb.patterns:
            if pattern.pattern_type not in pattern_by_type:
                pattern_by_type[pattern.pattern_type] = 0
            pattern_by_type[pattern.pattern_type] += pattern.count

        return {
            "file_count": len(shell_files),
            "function_count": len(kb.functions),
            "variable_count": len(kb.variables),
            "comment_count": len(kb.comments),
            "source_count": len(kb.sources),
            "pattern_count": len(kb.patterns),
            "variables_by_category": var_by_category,
            "patterns_by_type": pattern_by_type,
            "analysis_time": datetime.now().isoformat(),
        }
