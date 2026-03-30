# -*- coding: utf-8 -*-
"""
Shell Source 提取器

提取 Shell 脚本中的 source/. 引用，分析脚本依赖关系
"""
import re
import os
from typing import List, Optional
from .base import BaseShellExtractor, ShellSource


class ShellSourceExtractor(BaseShellExtractor):
    """Shell Source 提取器"""

    # source 语句模式
    # 匹配: source file 或 . file 或 source ./file 或 . ./file
    SOURCE_PATTERN = re.compile(r'^\s*(?:source|\.)\s+(.+)$')

    @property
    def name(self) -> str:
        return "ShellSourceExtractor"

    def extract(self, file_path: str, content: str) -> List[ShellSource]:
        """从单个文件提取 source 引用"""
        sources = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            # 跳过注释
            if line.strip().startswith('#'):
                continue

            match = self.SOURCE_PATTERN.match(line)
            if match:
                target = match.group(1).strip()

                # 去掉可能的注释
                if '#' in target:
                    target = target.split('#')[0].strip()

                # 去掉引号
                target = target.strip('"\'')

                # 尝试解析绝对路径
                resolved_path = self._resolve_path(file_path, target)

                sources.append(ShellSource(
                    source_file=file_path,
                    target_file=target,
                    line=i + 1,
                    resolved_path=resolved_path,
                ))

        return sources

    def extract_all(self, source_dir: str) -> List[ShellSource]:
        """从目录提取所有 source 引用"""
        all_sources = []

        for file_path in self._find_shell_files(source_dir):
            content = self._read_file(file_path)
            if content:
                sources = self.extract(file_path, content)
                all_sources.extend(sources)

        return all_sources

    def _resolve_path(self, source_file: str, target: str) -> str:
        """尝试解析目标文件的绝对路径"""
        # 如果目标包含变量，无法解析
        if '$' in target:
            return ""

        # 如果是绝对路径
        if target.startswith('/'):
            if os.path.exists(target):
                return target
            return ""

        # 相对路径，基于源文件目录
        source_dir = os.path.dirname(source_file)
        resolved = os.path.normpath(os.path.join(source_dir, target))

        if os.path.exists(resolved):
            return resolved

        return ""

    def build_dependency_graph(self, sources: List[ShellSource]) -> dict:
        """构建依赖关系图"""
        graph = {}

        for source in sources:
            if source.source_file not in graph:
                graph[source.source_file] = []
            graph[source.source_file].append({
                'target': source.target_file,
                'resolved': source.resolved_path,
                'line': source.line,
            })

        return graph
