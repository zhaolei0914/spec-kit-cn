# -*- coding: utf-8 -*-
"""
Shell 提取器模块

提供 Shell 脚本的各类提取器：
- ShellFunctionExtractor: 函数提取
- ShellVariableExtractor: 变量提取
- ShellCommentExtractor: 注释提取
- ShellSourceExtractor: source/. 引用提取
- ShellPatternMiner: 模式挖掘
"""

from .function_extractor import ShellFunctionExtractor
from .variable_extractor import ShellVariableExtractor
from .comment_extractor import ShellCommentExtractor
from .source_extractor import ShellSourceExtractor
from .pattern_miner import ShellPatternMiner
from .fusion import ShellKnowledgeBase, ShellKnowledgeBaseFusion

__all__ = [
    'ShellFunctionExtractor',
    'ShellVariableExtractor',
    'ShellCommentExtractor',
    'ShellSourceExtractor',
    'ShellPatternMiner',
    'ShellKnowledgeBase',
    'ShellKnowledgeBaseFusion',
]
