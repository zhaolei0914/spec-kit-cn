# -*- coding: utf-8 -*-
"""
Shell 注释提取器

提取 Shell 脚本中的注释，包括：
- 文件头注释（描述、作者、日期）
- 函数注释
- 行内注释
- TODO/FIXME
"""
import re
from typing import List, Optional, Tuple
from .base import BaseShellExtractor, ShellComment


class ShellCommentExtractor(BaseShellExtractor):
    """Shell 注释提取器"""

    # 注释模式
    COMMENT_PATTERN = re.compile(r'^\s*#\s*(.*)$')

    # 特殊注释模式
    TODO_PATTERN = re.compile(r'#\s*(TODO|FIXME|XXX|HACK|NOTE)[\s:]+(.*)$', re.IGNORECASE)

    # 文件头关键词
    HEADER_KEYWORDS = {
        'description': re.compile(r'^#?\s*Description:\s*(.+)$', re.IGNORECASE),
        'author': re.compile(r'^#?\s*Author:\s*(.+)$', re.IGNORECASE),
        'date': re.compile(r'^#?\s*Date:\s*(.+)$', re.IGNORECASE),
        'version': re.compile(r'^#?\s*Version:\s*(.+)$', re.IGNORECASE),
    }

    @property
    def name(self) -> str:
        return "ShellCommentExtractor"

    def extract(self, file_path: str, content: str) -> List[ShellComment]:
        """从单个文件提取注释"""
        comments = []
        lines = content.split('\n')

        # 提取文件头注释
        header_comments = self._extract_header_comments(file_path, lines)
        comments.extend(header_comments)

        # 提取 TODO/FIXME 等特殊注释
        todo_comments = self._extract_todo_comments(file_path, lines)
        comments.extend(todo_comments)

        # 提取函数注释（在函数定义前的注释）
        func_comments = self._extract_function_comments(file_path, lines)
        comments.extend(func_comments)

        return comments

    def extract_all(self, source_dir: str) -> List[ShellComment]:
        """从目录提取所有注释"""
        all_comments = []

        for file_path in self._find_shell_files(source_dir):
            content = self._read_file(file_path)
            if content:
                comments = self.extract(file_path, content)
                all_comments.extend(comments)

        return all_comments

    def _extract_header_comments(self, file_path: str, lines: List[str]) -> List[ShellComment]:
        """提取文件头注释"""
        comments = []
        header_lines = []

        # 跳过 shebang
        start = 0
        if lines and lines[0].startswith('#!'):
            start = 1

        # 收集文件头的连续注释
        for i in range(start, min(len(lines), 30)):  # 只看前30行
            line = lines[i].strip()
            if line.startswith('#'):
                header_lines.append((i + 1, line))
            elif line == '':
                continue
            else:
                break

        # 解析文件头信息
        for line_num, line in header_lines:
            for key, pattern in self.HEADER_KEYWORDS.items():
                match = pattern.match(line)
                if match:
                    comments.append(ShellComment(
                        content=match.group(1).strip(),
                        file_path=file_path,
                        line=line_num,
                        comment_type="header",
                        related_to=key,
                    ))
                    break

        # 如果有文件头注释但没有匹配到关键词，也记录
        if header_lines and not comments:
            content = '\n'.join([line for _, line in header_lines])
            comments.append(ShellComment(
                content=content.lstrip('#').strip(),
                file_path=file_path,
                line=header_lines[0][0],
                comment_type="header",
                related_to="general",
            ))

        return comments

    def _extract_todo_comments(self, file_path: str, lines: List[str]) -> List[ShellComment]:
        """提取 TODO/FIXME 等特殊注释"""
        comments = []

        for i, line in enumerate(lines):
            match = self.TODO_PATTERN.search(line)
            if match:
                comments.append(ShellComment(
                    content=f"{match.group(1)}: {match.group(2).strip()}",
                    file_path=file_path,
                    line=i + 1,
                    comment_type="todo",
                    related_to=match.group(1).upper(),
                ))

        return comments

    def _extract_function_comments(self, file_path: str, lines: List[str]) -> List[ShellComment]:
        """提取函数注释"""
        comments = []

        # 函数定义模式
        func_pattern = re.compile(r'^(\w+)\s*\(\s*\)\s*\{?\s*$')
        func_pattern_alt = re.compile(r'^function\s+(\w+)\s*\(?\s*\)?\s*\{?\s*$')

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # 检查是否是函数定义
            func_name = None
            match = func_pattern.match(line_stripped)
            if match:
                func_name = match.group(1)
            else:
                match = func_pattern_alt.match(line_stripped)
                if match:
                    func_name = match.group(1)

            if func_name:
                # 获取函数前的注释
                comment_lines = []
                j = i - 1
                while j >= 0:
                    prev_line = lines[j].strip()
                    if prev_line.startswith('#'):
                        comment_lines.insert(0, prev_line.lstrip('#').strip())
                        j -= 1
                    elif prev_line == '':
                        j -= 1
                    else:
                        break

                if comment_lines:
                    comments.append(ShellComment(
                        content='\n'.join(comment_lines),
                        file_path=file_path,
                        line=j + 2,  # 注释开始行
                        comment_type="function_doc",
                        related_to=func_name,
                    ))

        return comments

    def get_file_description(self, file_path: str, content: str) -> Optional[str]:
        """获取文件描述"""
        lines = content.split('\n')
        header_comments = self._extract_header_comments(file_path, lines)

        for comment in header_comments:
            if comment.related_to == 'description':
                return comment.content

        # 如果没有 description，返回第一个 header 注释
        for comment in header_comments:
            if comment.comment_type == 'header':
                return comment.content

        return None
