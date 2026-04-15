# -*- coding: utf-8 -*-
"""
Shell 模式挖掘器

挖掘 Shell 脚本中的常见模式：
- 日志模式
- 错误处理模式
- 服务管理模式
- 文件操作模式
"""
import re
from typing import List, Dict
from collections import defaultdict
from .base import BaseShellExtractor, ShellPattern


class ShellPatternMiner(BaseShellExtractor):
    """Shell 模式挖掘器"""

    # 日志模式
    LOGGING_PATTERNS = {
        'echo_log': re.compile(r'echo\s+.*>>\s*\$?\w*[Ll][Oo][Gg]'),
        'logger': re.compile(r'logger\s+'),
        'log_function': re.compile(r'(Message_log|Warning_log|Error_log|Debug_log|ShowInfo|ShowError|ShowWarning)\s*'),
        'printf_log': re.compile(r'printf\s+.*\\033'),  # 带颜色的输出
    }

    # 错误处理模式
    ERROR_PATTERNS = {
        'set_e': re.compile(r'^\s*set\s+-e'),
        'set_pipefail': re.compile(r'^\s*set\s+-o\s+pipefail'),
        'trap': re.compile(r'^\s*trap\s+'),
        'exit_check': re.compile(r'if\s+\[\s*\$\?\s*'),
        'or_exit': re.compile(r'\|\|\s*exit'),
        'and_continue': re.compile(r'&&\s*\{'),
    }

    # 服务管理模式
    SERVICE_PATTERNS = {
        'systemctl': re.compile(r'systemctl\s+(start|stop|restart|status|enable|disable)'),
        'service': re.compile(r'service\s+\S+\s+(start|stop|restart|status)'),
        'init_d': re.compile(r'/etc/init\.d/'),
    }

    # 文件操作模式
    FILE_PATTERNS = {
        'backup': re.compile(r'cp\s+-[rfp]*\s+.*backup', re.IGNORECASE),
        'mkdir_p': re.compile(r'mkdir\s+-p'),
        'rm_rf': re.compile(r'rm\s+-rf'),
        'chmod': re.compile(r'chmod\s+[0-7]{3,4}'),
        'chown': re.compile(r'chown\s+'),
        'tar_create': re.compile(r'tar\s+-[czf]+'),
        'tar_extract': re.compile(r'tar\s+-[xzf]+'),
    }

    # 配置读取模式
    CONFIG_PATTERNS = {
        'grep_config': re.compile(r'grep\s+.*\|\s*awk'),
        'source_config': re.compile(r'(?:source|\.)\s+.*config'),
        'read_ini': re.compile(r'awk.*\[.*\]'),
    }

    @property
    def name(self) -> str:
        return "ShellPatternMiner"

    def extract(self, file_path: str, content: str) -> List[ShellPattern]:
        """从单个文件挖掘模式"""
        patterns = []
        lines = content.split('\n')

        # 收集各类模式
        pattern_matches = defaultdict(list)

        for i, line in enumerate(lines):
            # 日志模式
            for name, pattern in self.LOGGING_PATTERNS.items():
                if pattern.search(line):
                    pattern_matches[('logging', name)].append({
                        'file': file_path,
                        'line': i + 1,
                        'code': line.strip(),
                    })

            # 错误处理模式
            for name, pattern in self.ERROR_PATTERNS.items():
                if pattern.search(line):
                    pattern_matches[('error_handling', name)].append({
                        'file': file_path,
                        'line': i + 1,
                        'code': line.strip(),
                    })

            # 服务管理模式
            for name, pattern in self.SERVICE_PATTERNS.items():
                if pattern.search(line):
                    pattern_matches[('service_management', name)].append({
                        'file': file_path,
                        'line': i + 1,
                        'code': line.strip(),
                    })

            # 文件操作模式
            for name, pattern in self.FILE_PATTERNS.items():
                if pattern.search(line):
                    pattern_matches[('file_operation', name)].append({
                        'file': file_path,
                        'line': i + 1,
                        'code': line.strip(),
                    })

            # 配置读取模式
            for name, pattern in self.CONFIG_PATTERNS.items():
                if pattern.search(line):
                    pattern_matches[('config_read', name)].append({
                        'file': file_path,
                        'line': i + 1,
                        'code': line.strip(),
                    })

        # 转换为 ShellPattern 对象
        for (pattern_type, pattern_name), examples in pattern_matches.items():
            patterns.append(ShellPattern(
                pattern_type=pattern_type,
                pattern_name=pattern_name,
                count=len(examples),
                examples=examples[:3],  # 只保留前3个示例
            ))

        return patterns

    def extract_all(self, source_dir: str) -> List[ShellPattern]:
        """从目录挖掘所有模式"""
        all_patterns = defaultdict(lambda: {'count': 0, 'examples': []})

        for file_path in self._find_shell_files(source_dir):
            content = self._read_file(file_path)
            if content:
                patterns = self.extract(file_path, content)
                for p in patterns:
                    key = (p.pattern_type, p.pattern_name)
                    all_patterns[key]['count'] += p.count
                    all_patterns[key]['examples'].extend(p.examples)

        # 转换为列表
        result = []
        for (pattern_type, pattern_name), data in all_patterns.items():
            result.append(ShellPattern(
                pattern_type=pattern_type,
                pattern_name=pattern_name,
                count=data['count'],
                examples=data['examples'][:5],  # 只保留前5个示例
            ))

        # 按数量排序
        result.sort(key=lambda x: x.count, reverse=True)

        return result

    def get_pattern_summary(self, patterns: List[ShellPattern]) -> Dict:
        """获取模式摘要"""
        summary = defaultdict(list)

        for p in patterns:
            summary[p.pattern_type].append({
                'name': p.pattern_name,
                'count': p.count,
            })

        return dict(summary)
