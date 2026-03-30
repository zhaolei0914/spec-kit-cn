# -*- coding: utf-8 -*-
"""
知识融合器

将多个提取器的结果整合、去重、排序
"""
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from .base import KnowledgeItem, BaseExtractor, calculate_confidence


class KnowledgeFusion:
    """知识融合器 - 整合多个提取器的结果"""

    def __init__(self):
        self.items: List[KnowledgeItem] = []
        self.by_type: Dict[str, List[KnowledgeItem]] = defaultdict(list)
        self.by_key: Dict[str, KnowledgeItem] = {}

    def add_items(self, items: List[KnowledgeItem]):
        """添加知识项（自动去重）"""
        for item in items:
            self._add_item(item)

    def _add_item(self, item: KnowledgeItem):
        """添加单个知识项"""
        # 检查是否已存在
        if item.key in self.by_key:
            existing = self.by_key[item.key]
            # 合并：提高置信度，保留更详细的信息
            merged = self._merge_items(existing, item)
            self.by_key[item.key] = merged
            # 更新列表中的项
            for i, it in enumerate(self.items):
                if it.key == item.key:
                    self.items[i] = merged
                    break
        else:
            self.items.append(item)
            self.by_type[item.type].append(item)
            self.by_key[item.key] = item

    def _merge_items(self, existing: KnowledgeItem, new: KnowledgeItem) -> KnowledgeItem:
        """合并两个知识项"""
        # 置信度取较高值，并略微提升（因为多次出现）
        merged_confidence = min(max(existing.confidence, new.confidence) * 1.1, 1.0)

        # 优先级取较高值（数字越小优先级越高）
        merged_priority = min(existing.priority, new.priority)

        # 合并元数据
        merged_metadata = {**existing.metadata, **new.metadata}

        # 合并关联项
        merged_related = list(set(existing.related_items + new.related_items))

        # 选择更详细的值
        merged_value = existing.value
        if isinstance(new.value, dict) and isinstance(existing.value, dict):
            merged_value = {**existing.value, **new.value}
        elif isinstance(new.value, str) and isinstance(existing.value, str):
            if len(new.value) > len(existing.value):
                merged_value = new.value

        return KnowledgeItem(
            type=existing.type,
            key=existing.key,
            value=merged_value,
            source_file=existing.source_file or new.source_file,
            source_line=existing.source_line or new.source_line,
            source_type=existing.source_type,
            confidence=round(merged_confidence, 3),
            priority=merged_priority,
            metadata=merged_metadata,
            related_items=merged_related,
        )

    def get_by_type(self, knowledge_type: str) -> List[KnowledgeItem]:
        """按类型获取知识项"""
        return self.by_type.get(knowledge_type, [])

    def get_by_priority(self, max_priority: int) -> List[KnowledgeItem]:
        """按优先级获取知识项"""
        return [item for item in self.items if item.priority <= max_priority]

    def get_high_confidence(self, min_confidence: float = 0.7) -> List[KnowledgeItem]:
        """获取高置信度知识项"""
        return [item for item in self.items if item.confidence >= min_confidence]

    def sort_by_priority(self) -> List[KnowledgeItem]:
        """按优先级排序"""
        return sorted(self.items, key=lambda x: (x.priority, -x.confidence))

    def sort_by_confidence(self) -> List[KnowledgeItem]:
        """按置信度排序"""
        return sorted(self.items, key=lambda x: -x.confidence)

    def get_summary(self) -> Dict:
        """获取融合结果摘要"""
        by_type_count = {k: len(v) for k, v in self.by_type.items()}
        by_priority = defaultdict(int)
        for item in self.items:
            by_priority[item.priority] += 1

        avg_confidence = sum(item.confidence for item in self.items) / len(self.items) if self.items else 0

        return {
            "total": len(self.items),
            "by_type": dict(by_type_count),
            "by_priority": dict(by_priority),
            "avg_confidence": round(avg_confidence, 3),
        }

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "items": [item.to_dict() for item in self.items],
            "summary": self.get_summary(),
        }

    def check_consistency(self) -> List[Dict]:
        """
        检查知识一致性

        返回不一致的项列表
        """
        issues = []

        # 检查同类型项的一致性
        for knowledge_type, items in self.by_type.items():
            if len(items) < 2:
                continue

            # 检查命名一致性
            names = set()
            for item in items:
                if isinstance(item.value, dict) and 'name' in item.value:
                    names.add(item.value['name'])

            # 如果同一类型有太多不同的命名模式，可能存在不一致
            if len(names) > len(items) * 0.8:
                issues.append({
                    "type": "naming_inconsistency",
                    "knowledge_type": knowledge_type,
                    "message": f"类型 {knowledge_type} 中存在大量不同的命名模式",
                    "count": len(names),
                })

        return issues

    def check_coverage(self, expected_types: List[str]) -> Dict:
        """
        检查知识覆盖率

        Args:
            expected_types: 期望的知识类型列表

        Returns:
            覆盖率报告
        """
        covered = set(self.by_type.keys())
        expected = set(expected_types)

        missing = expected - covered
        extra = covered - expected

        coverage_rate = len(covered & expected) / len(expected) if expected else 1.0

        return {
            "coverage_rate": round(coverage_rate, 3),
            "covered_types": list(covered),
            "missing_types": list(missing),
            "extra_types": list(extra),
        }


class ExtractorOrchestrator:
    """提取器编排器 - 协调多个提取器的执行"""

    def __init__(self):
        self.extractors: List[BaseExtractor] = []
        self.fusion = KnowledgeFusion()

    def add_extractor(self, extractor: BaseExtractor):
        """添加提取器"""
        self.extractors.append(extractor)

    def extract_all(self, source_dir: str) -> KnowledgeFusion:
        """
        执行所有提取器并融合结果

        Args:
            source_dir: 源码目录

        Returns:
            融合后的知识库
        """
        self.fusion = KnowledgeFusion()

        for extractor in self.extractors:
            try:
                items = extractor.extract(source_dir)
                self.fusion.add_items(items)
                print(f"  [{extractor.name}] 提取了 {len(items)} 个知识项")
            except Exception as e:
                print(f"  [{extractor.name}] 提取失败: {e}")

        return self.fusion

    def get_summary(self) -> Dict:
        """获取提取结果摘要"""
        extractor_summaries = []
        for extractor in self.extractors:
            extractor_summaries.append({
                "name": extractor.name,
                "description": extractor.description,
                "supported_types": extractor.get_supported_types(),
                "summary": extractor.get_summary(),
            })

        return {
            "extractors": extractor_summaries,
            "fusion": self.fusion.get_summary(),
        }
