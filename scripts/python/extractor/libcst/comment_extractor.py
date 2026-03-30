# -*- coding: utf-8 -*-
"""
注释提取器

提取代码注释、TODO、FIXME 等标记
"""
import re
from typing import Dict, List, Optional

try:
    import libcst as cst
except ImportError:
    cst = None

from .base_libcst import LibCSTExtractor, CodeUnit, CodeLocation


class CommentExtractor(LibCSTExtractor):
    """注释提取器"""

    # 特殊注释标记
    TODO_PATTERN = re.compile(r'#\s*(TODO|FIXME|XXX|HACK|NOTE|WARNING|BUG)[\s:]+(.+)', re.IGNORECASE)

    @property
    def name(self) -> str:
        return "comment_extractor"

    @property
    def description(self) -> str:
        return "提取代码注释、TODO、FIXME 等标记"

    def extract_from_tree(
        self,
        tree: 'cst.Module',
        file_path: str,
        source_code: str,
        wrapper: 'cst.MetadataWrapper' = None
    ) -> List[CodeUnit]:
        """从源代码中提取注释"""
        comments = []
        lines = source_code.split('\n')

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # 跳过空行
            if not stripped:
                continue

            # 单行注释
            if stripped.startswith('#'):
                comment_text = stripped[1:].strip()

                # 跳过 shebang 和编码声明
                if i <= 2 and (comment_text.startswith('!') or 'coding' in comment_text):
                    continue

                # 检查是否是特殊标记
                match = self.TODO_PATTERN.match(stripped)
                if match:
                    tag = match.group(1).upper()
                    content = match.group(2).strip()

                    unit = CodeUnit(
                        name=f"{tag}_{i}",
                        type="comment_tag",
                        location=CodeLocation(
                            file_path=file_path,
                            start_line=i,
                            end_line=i
                        ),
                        source_code=stripped,
                        comments=[content],
                        confidence=1.0,
                        confidence_level="fact",
                        metadata={
                            "tag": tag,
                            "content": content,
                        }
                    )
                    comments.append(unit)
                else:
                    # 普通注释
                    unit = CodeUnit(
                        name=f"comment_{i}",
                        type="comment",
                        location=CodeLocation(
                            file_path=file_path,
                            start_line=i,
                            end_line=i
                        ),
                        source_code=stripped,
                        comments=[comment_text],
                        confidence=1.0,
                        confidence_level="fact",
                        metadata={
                            "is_block_comment": self._is_block_comment(lines, i-1),
                        }
                    )
                    comments.append(unit)

            # 行内注释
            elif '#' in stripped and not stripped.startswith(('#', '"', "'")):
                # 简单检测行内注释（不在字符串内）
                comment_pos = self._find_comment_position(stripped)
                if comment_pos > 0:
                    comment_text = stripped[comment_pos+1:].strip()

                    unit = CodeUnit(
                        name=f"inline_comment_{i}",
                        type="inline_comment",
                        location=CodeLocation(
                            file_path=file_path,
                            start_line=i,
                            end_line=i
                        ),
                        source_code=stripped,
                        comments=[comment_text],
                        confidence=1.0,
                        confidence_level="fact",
                        metadata={
                            "code_before": stripped[:comment_pos].strip(),
                        }
                    )
                    comments.append(unit)

        return comments

    def _is_block_comment(self, lines: List[str], current_idx: int) -> bool:
        """检查是否是块注释的一部分"""
        if current_idx > 0:
            prev_line = lines[current_idx - 1].strip()
            if prev_line.startswith('#'):
                return True
        if current_idx < len(lines) - 1:
            next_line = lines[current_idx + 1].strip()
            if next_line.startswith('#'):
                return True
        return False

    def _find_comment_position(self, line: str) -> int:
        """找到注释的位置（排除字符串内的 #）"""
        in_string = False
        string_char = None
        escape = False

        for i, char in enumerate(line):
            if escape:
                escape = False
                continue

            if char == '\\':
                escape = True
                continue

            if char in ('"', "'"):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None

            if char == '#' and not in_string:
                return i

        return -1
