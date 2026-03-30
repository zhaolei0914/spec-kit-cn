# -*- coding: utf-8 -*-
"""
智能规范提取系统 - 模式挖掘器

从代码单元中挖掘重复出现的模式
"""
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Set
import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parser.base import CodeUnit, CodePattern


class PatternMiner:
    """模式挖掘器"""

    def __init__(self, min_occurrences: int = 2, min_confidence: float = 0.05):
        """
        初始化挖掘器

        Args:
            min_occurrences: 最小出现次数
            min_confidence: 最小置信度
        """
        self.min_occurrences = min_occurrences
        self.min_confidence = min_confidence

    def mine_patterns(self, units: List[CodeUnit]) -> List[CodePattern]:
        """
        挖掘所有模式

        Args:
            units: 代码单元列表

        Returns:
            代码模式列表
        """
        patterns = []

        # 1. 继承模式
        patterns.extend(self._mine_inheritance_patterns(units))

        # 2. 装饰器模式
        patterns.extend(self._mine_decorator_patterns(units))

        # 3. 命名模式
        patterns.extend(self._mine_naming_patterns(units))

        # 4. 结构模式（装饰器组合）
        patterns.extend(self._mine_structure_patterns(units))

        # 5. 参数模式
        patterns.extend(self._mine_param_patterns(units))

        # 6. 文件组织模式
        patterns.extend(self._mine_file_patterns(units))

        # 7. 文档字符串模式
        patterns.extend(self._mine_docstring_patterns(units))

        # 8. 返回类型模式
        patterns.extend(self._mine_return_type_patterns(units))

        # 过滤不显著的模式
        significant_patterns = [
            p for p in patterns
            if p.occurrences >= self.min_occurrences
        ]

        # 按出现次数排序
        significant_patterns.sort(key=lambda p: p.occurrences, reverse=True)

        return significant_patterns

    def _mine_inheritance_patterns(self, units: List[CodeUnit]) -> List[CodePattern]:
        """挖掘继承模式"""
        classes = [u for u in units if u.type == 'class']
        if not classes:
            return []

        base_counter = Counter()
        base_examples = defaultdict(list)

        for cls in classes:
            for base in cls.bases:
                if base and base != 'object':
                    base_counter[base] += 1
                    if len(base_examples[base]) < 5:
                        base_examples[base].append(cls)

        total_classes = len(classes)
        patterns = []

        for base, count in base_counter.items():
            patterns.append(CodePattern(
                pattern_type='inheritance',
                pattern_key=f'extends:{base}',
                occurrences=count,
                examples=base_examples[base],
                confidence=count / total_classes,
                description=f'继承自 {base} 的类',
            ))

        return patterns

    def _mine_decorator_patterns(self, units: List[CodeUnit]) -> List[CodePattern]:
        """挖掘装饰器模式"""
        functions = [u for u in units if u.type == 'function']
        classes = [u for u in units if u.type == 'class']

        decorator_counter = Counter()
        decorator_examples = defaultdict(list)

        # 函数装饰器
        for func in functions:
            for dec in func.decorators:
                if dec:
                    decorator_counter[dec] += 1
                    if len(decorator_examples[dec]) < 5:
                        decorator_examples[dec].append(func)

        # 类装饰器
        for cls in classes:
            for dec in cls.decorators:
                if dec:
                    key = f'class:{dec}'
                    decorator_counter[key] += 1
                    if len(decorator_examples[key]) < 5:
                        decorator_examples[key].append(cls)

        total = len(functions) + len(classes)
        if total == 0:
            return []

        patterns = []
        for dec, count in decorator_counter.items():
            patterns.append(CodePattern(
                pattern_type='decorator',
                pattern_key=f'@{dec}',
                occurrences=count,
                examples=decorator_examples[dec],
                confidence=count / total,
                description=f'使用 @{dec} 装饰器',
            ))

        return patterns

    def _mine_naming_patterns(self, units: List[CodeUnit]) -> List[CodePattern]:
        """挖掘命名模式"""
        patterns = []

        # 函数命名前缀
        functions = [u for u in units if u.type == 'function']
        prefix_counter = Counter()
        prefix_examples = defaultdict(list)

        common_prefixes = [
            'get_', 'set_', 'create_', 'delete_', 'update_',
            'is_', 'has_', 'can_', 'should_',
            'find_', 'fetch_', 'load_', 'save_',
            'validate_', 'check_', 'verify_',
            'handle_', 'process_', 'parse_',
            '_',  # 私有方法
        ]

        for func in functions:
            for prefix in common_prefixes:
                if func.name.startswith(prefix) and func.name != prefix.rstrip('_'):
                    prefix_counter[prefix] += 1
                    if len(prefix_examples[prefix]) < 5:
                        prefix_examples[prefix].append(func)
                    break

        for prefix, count in prefix_counter.items():
            if count >= self.min_occurrences:
                patterns.append(CodePattern(
                    pattern_type='naming',
                    pattern_key=f'prefix:{prefix}',
                    occurrences=count,
                    examples=prefix_examples[prefix],
                    confidence=count / len(functions) if functions else 0,
                    description=f'以 {prefix} 开头的函数',
                ))

        # 类命名后缀
        classes = [u for u in units if u.type == 'class']
        suffix_counter = Counter()
        suffix_examples = defaultdict(list)

        common_suffixes = [
            'View', 'Service', 'Model', 'Handler', 'Manager',
            'Factory', 'Exception', 'Error', 'Controller',
            'Repository', 'Validator', 'Serializer', 'Form',
            'Mixin', 'Base', 'Abstract', 'Interface',
            'Client', 'Server', 'Worker', 'Task',
        ]

        for cls in classes:
            for suffix in common_suffixes:
                if cls.name.endswith(suffix) and cls.name != suffix:
                    suffix_counter[suffix] += 1
                    if len(suffix_examples[suffix]) < 5:
                        suffix_examples[suffix].append(cls)
                    break

        for suffix, count in suffix_counter.items():
            if count >= self.min_occurrences:
                patterns.append(CodePattern(
                    pattern_type='naming',
                    pattern_key=f'suffix:{suffix}',
                    occurrences=count,
                    examples=suffix_examples[suffix],
                    confidence=count / len(classes) if classes else 0,
                    description=f'以 {suffix} 结尾的类',
                ))

        return patterns

    def _mine_structure_patterns(self, units: List[CodeUnit]) -> List[CodePattern]:
        """挖掘结构模式（装饰器组合）"""
        functions = [u for u in units if u.type == 'function' and len(u.decorators) > 1]
        if not functions:
            return []

        combo_counter = Counter()
        combo_examples = defaultdict(list)

        for func in functions:
            # 排序装饰器以确保相同组合被识别
            combo = tuple(sorted(func.decorators))
            combo_counter[combo] += 1
            if len(combo_examples[combo]) < 5:
                combo_examples[combo].append(func)

        patterns = []
        for combo, count in combo_counter.items():
            if count >= self.min_occurrences:
                combo_str = ' + '.join(combo)
                patterns.append(CodePattern(
                    pattern_type='structure',
                    pattern_key=f'combo:@{combo_str}',
                    occurrences=count,
                    examples=combo_examples[combo],
                    confidence=count / len(functions),
                    description=f'装饰器组合: @{combo_str}',
                ))

        return patterns

    def _mine_param_patterns(self, units: List[CodeUnit]) -> List[CodePattern]:
        """挖掘参数模式"""
        functions = [u for u in units if u.type == 'function' and u.params]
        if not functions:
            return []

        # 常见参数名
        param_counter = Counter()
        param_examples = defaultdict(list)

        for func in functions:
            for param in func.params:
                if param not in ('self', 'cls', 'args', 'kwargs'):
                    param_counter[param] += 1
                    if len(param_examples[param]) < 5:
                        param_examples[param].append(func)

        patterns = []
        for param, count in param_counter.items():
            if count >= self.min_occurrences * 2:  # 参数需要更高频率
                patterns.append(CodePattern(
                    pattern_type='param',
                    pattern_key=f'param:{param}',
                    occurrences=count,
                    examples=param_examples[param],
                    confidence=count / len(functions),
                    description=f'常用参数名: {param}',
                ))

        return patterns

    def _mine_file_patterns(self, units: List[CodeUnit]) -> List[CodePattern]:
        """挖掘文件组织模式"""
        import os

        # 按文件分组
        file_units = defaultdict(list)
        for unit in units:
            file_units[unit.file_path].append(unit)

        # 分析文件名与内容的关系
        file_type_counter = Counter()
        file_type_examples = defaultdict(list)

        for file_path, file_unit_list in file_units.items():
            filename = os.path.basename(file_path)
            name_without_ext = os.path.splitext(filename)[0]

            # 检测文件类型
            classes = [u for u in file_unit_list if u.type == 'class']
            if classes:
                # 检查类名是否与文件名相关
                for cls in classes:
                    if name_without_ext.lower() in cls.name.lower():
                        file_type_counter['class_per_file'] += 1
                        if len(file_type_examples['class_per_file']) < 5:
                            file_type_examples['class_per_file'].append(cls)

            # 检测特定文件名模式
            if name_without_ext.endswith('_view') or name_without_ext.endswith('_views'):
                file_type_counter['view_file'] += 1
            elif name_without_ext.endswith('_service') or name_without_ext.endswith('_services'):
                file_type_counter['service_file'] += 1
            elif name_without_ext == 'models':
                file_type_counter['models_file'] += 1
            elif name_without_ext == 'urls':
                file_type_counter['urls_file'] += 1
            elif name_without_ext.startswith('test_') or name_without_ext.endswith('_test'):
                file_type_counter['test_file'] += 1

        patterns = []
        for file_type, count in file_type_counter.items():
            if count >= self.min_occurrences:
                patterns.append(CodePattern(
                    pattern_type='file',
                    pattern_key=f'file:{file_type}',
                    occurrences=count,
                    examples=file_type_examples.get(file_type, []),
                    confidence=count / len(file_units) if file_units else 0,
                    description=f'文件组织模式: {file_type}',
                ))

        return patterns

    def _mine_docstring_patterns(self, units: List[CodeUnit]) -> List[CodePattern]:
        """挖掘文档字符串模式"""
        patterns = []

        # 统计有文档字符串的单元
        with_docstring = [u for u in units if u.docstring]
        without_docstring = [u for u in units if not u.docstring]

        total = len(units)
        if total == 0:
            return patterns

        # 有文档字符串的比例
        if len(with_docstring) >= self.min_occurrences:
            patterns.append(CodePattern(
                pattern_type='docstring',
                pattern_key='has_docstring',
                occurrences=len(with_docstring),
                examples=with_docstring[:5],
                confidence=len(with_docstring) / total,
                description='有文档字符串的代码单元',
            ))

        # 按类型统计文档字符串
        classes_with_doc = [u for u in units if u.type == 'class' and u.docstring]
        functions_with_doc = [u for u in units if u.type == 'function' and u.docstring]

        classes_total = len([u for u in units if u.type == 'class'])
        functions_total = len([u for u in units if u.type == 'function'])

        if len(classes_with_doc) >= self.min_occurrences and classes_total > 0:
            patterns.append(CodePattern(
                pattern_type='docstring',
                pattern_key='class_docstring',
                occurrences=len(classes_with_doc),
                examples=classes_with_doc[:5],
                confidence=len(classes_with_doc) / classes_total,
                description='有文档字符串的类',
            ))

        if len(functions_with_doc) >= self.min_occurrences and functions_total > 0:
            patterns.append(CodePattern(
                pattern_type='docstring',
                pattern_key='function_docstring',
                occurrences=len(functions_with_doc),
                examples=functions_with_doc[:5],
                confidence=len(functions_with_doc) / functions_total,
                description='有文档字符串的函数',
            ))

        return patterns

    def _mine_return_type_patterns(self, units: List[CodeUnit]) -> List[CodePattern]:
        """挖掘返回类型模式"""
        patterns = []

        functions = [u for u in units if u.type == 'function']
        if not functions:
            return patterns

        # 统计有返回类型注解的函数
        return_type_counter = Counter()
        return_type_examples = defaultdict(list)

        for func in functions:
            return_type = func.metadata.get('return_annotation')
            if return_type:
                return_type_counter[return_type] += 1
                if len(return_type_examples[return_type]) < 5:
                    return_type_examples[return_type].append(func)

        for return_type, count in return_type_counter.items():
            if count >= self.min_occurrences:
                patterns.append(CodePattern(
                    pattern_type='return_type',
                    pattern_key=f'returns:{return_type}',
                    occurrences=count,
                    examples=return_type_examples[return_type],
                    confidence=count / len(functions),
                    description=f'返回类型为 {return_type} 的函数',
                ))

        return patterns

    def get_pattern_summary(self, patterns: List[CodePattern]) -> Dict:
        """
        获取模式摘要

        Args:
            patterns: 代码模式列表

        Returns:
            摘要字典
        """
        summary = {
            'total_patterns': len(patterns),
            'by_type': defaultdict(int),
            'top_patterns': [],
            'high_confidence': [],
        }

        for pattern in patterns:
            summary['by_type'][pattern.pattern_type] += 1

        # 按出现次数排序的前 10 个模式
        sorted_by_occurrences = sorted(patterns, key=lambda p: p.occurrences, reverse=True)
        summary['top_patterns'] = [
            {'key': p.pattern_key, 'occurrences': p.occurrences, 'confidence': p.confidence}
            for p in sorted_by_occurrences[:10]
        ]

        # 高置信度模式（>20%）
        high_conf = [p for p in patterns if p.confidence > 0.2]
        summary['high_confidence'] = [
            {'key': p.pattern_key, 'occurrences': p.occurrences, 'confidence': p.confidence}
            for p in sorted(high_conf, key=lambda p: p.confidence, reverse=True)[:10]
        ]

        return dict(summary)
