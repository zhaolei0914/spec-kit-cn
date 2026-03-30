# -*- coding: utf-8 -*-
"""
增量缓存

支持增量更新，只处理变更的文件
"""
import os
import json
import hashlib
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class FileState:
    """文件状态"""
    path: str
    hash: str
    mtime: float
    size: int


@dataclass
class CacheState:
    """缓存状态"""
    version: str = "1.0"
    project_path: str = ""
    last_update: str = ""
    files: Dict[str, FileState] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "version": self.version,
            "project_path": self.project_path,
            "last_update": self.last_update,
            "files": {
                path: {
                    "path": state.path,
                    "hash": state.hash,
                    "mtime": state.mtime,
                    "size": state.size,
                }
                for path, state in self.files.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'CacheState':
        state = cls(
            version=data.get("version", "1.0"),
            project_path=data.get("project_path", ""),
            last_update=data.get("last_update", ""),
        )
        for path, file_data in data.get("files", {}).items():
            state.files[path] = FileState(
                path=file_data.get("path", path),
                hash=file_data.get("hash", ""),
                mtime=file_data.get("mtime", 0),
                size=file_data.get("size", 0),
            )
        return state


class FileChangeDetector:
    """文件变更检测器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

    def get_file_hash(self, file_path: str) -> str:
        """获取文件哈希"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def get_file_state(self, file_path: str) -> Optional[FileState]:
        """获取文件状态"""
        try:
            stat = os.stat(file_path)
            return FileState(
                path=file_path,
                hash=self.get_file_hash(file_path),
                mtime=stat.st_mtime,
                size=stat.st_size,
            )
        except Exception:
            return None

    def detect_changes(
        self,
        current_files: List[str],
        cached_state: CacheState
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        检测文件变更

        Returns:
            (added, modified, deleted) 文件列表
        """
        current_set = set(current_files)
        cached_set = set(cached_state.files.keys())

        # 新增的文件
        added = list(current_set - cached_set)

        # 删除的文件
        deleted = list(cached_set - current_set)

        # 修改的文件
        modified = []
        for file_path in current_set & cached_set:
            cached_file = cached_state.files.get(file_path)
            if cached_file:
                current_state = self.get_file_state(file_path)
                if current_state:
                    # 先检查 mtime 和 size（快速检查）
                    if (current_state.mtime != cached_file.mtime or
                        current_state.size != cached_file.size):
                        # 再检查 hash（精确检查）
                        if current_state.hash != cached_file.hash:
                            modified.append(file_path)

        return added, modified, deleted


class IncrementalCache:
    """增量缓存管理器"""

    def __init__(self, cache_dir: str, config: Optional[Dict] = None):
        self.cache_dir = cache_dir
        self.config = config or {}
        self.detector = FileChangeDetector(config)

        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)

        # 缓存文件路径
        self.state_file = os.path.join(cache_dir, 'cache_state.json')
        self.kb_cache_file = os.path.join(cache_dir, 'knowledge_cache.json')

    def load_state(self) -> CacheState:
        """加载缓存状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return CacheState.from_dict(data)
            except Exception:
                pass
        return CacheState()

    def save_state(self, state: CacheState) -> None:
        """保存缓存状态"""
        state.last_update = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)

    def get_changed_files(
        self,
        project_path: str,
        current_files: List[str]
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        获取变更的文件

        Returns:
            (added, modified, deleted) 文件列表
        """
        state = self.load_state()

        # 如果项目路径变了，全部重新处理
        if state.project_path != project_path:
            return current_files, [], []

        return self.detector.detect_changes(current_files, state)

    def update_file_state(self, file_path: str, state: CacheState) -> None:
        """更新单个文件的状态"""
        file_state = self.detector.get_file_state(file_path)
        if file_state:
            state.files[file_path] = file_state

    def remove_file_state(self, file_path: str, state: CacheState) -> None:
        """移除文件状态"""
        if file_path in state.files:
            del state.files[file_path]

    def load_cached_units(self, file_path: str) -> Optional[List[Dict]]:
        """加载缓存的代码单元"""
        if not os.path.exists(self.kb_cache_file):
            return None

        try:
            with open(self.kb_cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            return cache.get('units_by_file', {}).get(file_path)
        except Exception:
            return None

    def save_cached_units(self, units_by_file: Dict[str, List[Dict]]) -> None:
        """保存缓存的代码单元"""
        cache = {'units_by_file': units_by_file}
        with open(self.kb_cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)

    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        state = self.load_state()

        stats = {
            "cached_files": len(state.files),
            "last_update": state.last_update,
            "project_path": state.project_path,
        }

        if os.path.exists(self.kb_cache_file):
            stats["kb_cache_size"] = os.path.getsize(self.kb_cache_file)

        return stats

    def clear_cache(self) -> None:
        """清除缓存"""
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
        if os.path.exists(self.kb_cache_file):
            os.remove(self.kb_cache_file)
