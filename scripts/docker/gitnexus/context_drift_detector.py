#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目上下文漂移检测器

对比 .context-facts.json 中的快照与当前项目状态，检测上下文是否过期。
支持两种检测模式：
  1. git diff 模式：分析 git 变更，识别受影响的模块
  2. 全量对比模式：重新扫描项目，与快照对比

用法:
    python context_drift_detector.py <project_path> [--facts <facts_path>] [--threshold <0-100>]

示例:
    # 快速检测（git diff 模式）
    python context_drift_detector.py /path/to/project

    # 指定事实文件路径
    python context_drift_detector.py /path/to/project --facts .specify/skills/project-context/.context-facts.json

    # 设置漂移阈值（默认 30，越低越敏感）
    python context_drift_detector.py /path/to/project --threshold 20
"""
import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime


def load_facts(facts_path: str) -> dict:
    """加载 .context-facts.json"""
    if not os.path.exists(facts_path):
        return {}
    with open(facts_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_git_changes(project_path: str, since_date: str = None) -> dict:
    """获取 git 变更信息"""
    result = {
        'has_git': False,
        'changed_files': [],
        'added_files': [],
        'deleted_files': [],
        'commit_count': 0,
        'authors': [],
        'affected_dirs': set(),
    }

    git_dir = os.path.join(project_path, '.git')
    if not os.path.isdir(git_dir):
        return result

    result['has_git'] = True

    try:
        # 获取变更文件（相对于上次生成时间）
        diff_cmd = ['git', 'diff', '--name-status', 'HEAD']
        if since_date:
            # 使用 git log 获取自某日期以来的变更
            diff_cmd = ['git', 'log', '--name-status', '--pretty=format:', f'--since={since_date}']

        proc = subprocess.run(
            diff_cmd, capture_output=True, text=True,
            cwd=project_path, timeout=30
        )
        if proc.returncode == 0:
            for line in proc.stdout.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue
                parts = line.split('\t', 1)
                if len(parts) < 2:
                    continue
                status, filepath = parts[0], parts[1]
                if status.startswith('A'):
                    result['added_files'].append(filepath)
                elif status.startswith('D'):
                    result['deleted_files'].append(filepath)
                elif status.startswith('M') or status.startswith('R'):
                    result['changed_files'].append(filepath)
                # 记录受影响的顶层目录
                top_dir = filepath.split('/')[0] if '/' in filepath else '.'
                result['affected_dirs'].add(top_dir)

        # 获取 commit 数量
        if since_date:
            count_cmd = ['git', 'rev-list', '--count', f'--since={since_date}', 'HEAD']
            proc = subprocess.run(
                count_cmd, capture_output=True, text=True,
                cwd=project_path, timeout=10
            )
            if proc.returncode == 0:
                result['commit_count'] = int(proc.stdout.strip() or '0')

        # 获取 staged + unstaged 变更
        status_cmd = ['git', 'status', '--porcelain']
        proc = subprocess.run(
            status_cmd, capture_output=True, text=True,
            cwd=project_path, timeout=10
        )
        if proc.returncode == 0:
            for line in proc.stdout.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue
                status = line[:2].strip()
                filepath = line[3:].strip()
                if filepath.startswith('"'):
                    filepath = filepath.strip('"')
                if status == '??' or 'A' in status:
                    if filepath not in result['added_files']:
                        result['added_files'].append(filepath)
                elif 'D' in status:
                    if filepath not in result['deleted_files']:
                        result['deleted_files'].append(filepath)
                elif 'M' in status:
                    if filepath not in result['changed_files']:
                        result['changed_files'].append(filepath)
                top_dir = filepath.split('/')[0] if '/' in filepath else '.'
                result['affected_dirs'].add(top_dir)

    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    result['affected_dirs'] = sorted(result['affected_dirs'])
    return result


def detect_language_drift(facts: dict, project_path: str) -> list:
    """检测语言分布变化"""
    drifts = []
    old_langs = facts.get('project_facts', {}).get('languages', {})
    if not old_langs:
        return drifts

    # 快速重新统计语言（简化版，只统计扩展名）
    from gitnexus_to_skill import EXT_LANG_MAP
    new_langs = Counter()
    skip_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv',
                 'dist', 'build', '.next', 'target', 'vendor',
                 '.gitnexus', '.claude', '.specify'}
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in EXT_LANG_MAP:
                new_langs[EXT_LANG_MAP[ext]] += 1

    # 比较
    all_langs = set(list(old_langs.keys()) + list(new_langs.keys()))
    for lang in all_langs:
        old_count = old_langs.get(lang, 0)
        new_count = new_langs.get(lang, 0)
        if old_count == 0 and new_count > 0:
            drifts.append({
                'type': 'language_added',
                'severity': 'high',
                'detail': f'新增语言: {lang} ({new_count} 文件)',
            })
        elif old_count > 0 and new_count == 0:
            drifts.append({
                'type': 'language_removed',
                'severity': 'high',
                'detail': f'移除语言: {lang} (原 {old_count} 文件)',
            })
        elif old_count > 0:
            change_pct = abs(new_count - old_count) / old_count * 100
            if change_pct > 30:
                direction = '增加' if new_count > old_count else '减少'
                drifts.append({
                    'type': 'language_shift',
                    'severity': 'medium',
                    'detail': f'{lang} 文件{direction}: {old_count} → {new_count} ({change_pct:.0f}% 变化)',
                })
    return drifts


def detect_dependency_drift(facts: dict, project_path: str) -> list:
    """检测依赖变化（检查包管理文件是否被修改）"""
    drifts = []
    dep_files = ['package.json', 'pyproject.toml', 'requirements.txt', 'go.mod',
                 'Cargo.toml', 'pom.xml', 'Gemfile', 'composer.json', 'pubspec.yaml']

    old_frameworks = set(facts.get('project_facts', {}).get('frameworks', []))
    old_middleware = set(facts.get('project_facts', {}).get('middleware', []))

    for dep_file in dep_files:
        dep_path = os.path.join(project_path, dep_file)
        if os.path.exists(dep_path):
            # 检查文件修改时间 vs facts 生成时间
            facts_time = facts.get('generated_at', '')
            if facts_time:
                try:
                    facts_dt = datetime.fromisoformat(facts_time)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(dep_path))
                    if file_mtime > facts_dt:
                        drifts.append({
                            'type': 'dependency_file_changed',
                            'severity': 'high',
                            'detail': f'依赖文件已更新: {dep_file} (修改于 {file_mtime.isoformat()[:19]})',
                        })
                except (ValueError, OSError):
                    pass
    return drifts


def detect_structure_drift(facts: dict, project_path: str) -> list:
    """检测目录结构变化"""
    drifts = []
    old_dirs = set(facts.get('structure_facts', {}).get('dir_structure', {}).keys())
    if not old_dirs:
        return drifts

    skip = {'.git', 'node_modules', '__pycache__', '.venv', 'venv',
            'dist', 'build', '.gitnexus', '.claude', '.specify'}

    new_dirs = set()
    for entry in os.listdir(project_path):
        if entry.startswith('.') or entry in skip:
            continue
        full = os.path.join(project_path, entry)
        if os.path.isdir(full) or os.path.isfile(full):
            new_dirs.add(entry)

    added = new_dirs - old_dirs
    removed = old_dirs - new_dirs

    for d in added:
        if os.path.isdir(os.path.join(project_path, d)):
            drifts.append({
                'type': 'dir_added',
                'severity': 'medium',
                'detail': f'新增目录: {d}/',
            })
    for d in removed:
        drifts.append({
            'type': 'dir_removed',
            'severity': 'medium',
            'detail': f'移除目录/文件: {d}',
        })
    return drifts


def detect_config_drift(facts: dict, project_path: str) -> list:
    """检测配置文件变化"""
    drifts = []
    old_configs = set(facts.get('structure_facts', {}).get('config_files', []))

    new_configs = set()
    for f in os.listdir(project_path):
        if f.endswith(('.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf', '.json')):
            if os.path.isfile(os.path.join(project_path, f)):
                new_configs.add(f)

    added = new_configs - old_configs
    removed = old_configs - new_configs

    for c in added:
        drifts.append({
            'type': 'config_added',
            'severity': 'low',
            'detail': f'新增配置文件: {c}',
        })
    for c in removed:
        drifts.append({
            'type': 'config_removed',
            'severity': 'low',
            'detail': f'移除配置文件: {c}',
        })
    return drifts


def compute_drift_score(drifts: list, git_changes: dict) -> int:
    """计算漂移分数（0-100），越高越需要更新"""
    score = 0

    # git 变更贡献
    total_changes = len(git_changes.get('changed_files', [])) + \
                    len(git_changes.get('added_files', [])) + \
                    len(git_changes.get('deleted_files', []))
    if total_changes > 50:
        score += 30
    elif total_changes > 20:
        score += 20
    elif total_changes > 5:
        score += 10

    # 漂移项贡献
    severity_weights = {'high': 15, 'medium': 8, 'low': 3}
    for drift in drifts:
        score += severity_weights.get(drift.get('severity', 'low'), 3)

    # 受影响目录数贡献
    affected = len(git_changes.get('affected_dirs', []))
    if affected > 5:
        score += 15
    elif affected > 2:
        score += 8

    return min(score, 100)


def detect_drift(project_path: str, facts_path: str = None, threshold: int = 30) -> dict:
    """执行完整漂移检测"""
    # 定位 facts 文件
    if not facts_path:
        facts_path = os.path.join(project_path, '.specify', 'skills', 'project-context', '.context-facts.json')

    facts = load_facts(facts_path)
    if not facts:
        return {
            'status': 'no_facts',
            'message': '未找到 .context-facts.json，需要首次生成项目上下文',
            'recommendation': 'full_rebuild',
            'score': 100,
            'drifts': [],
            'git_changes': {},
        }

    facts_time = facts.get('generated_at', '')

    # 1. Git 变更检测
    git_changes = get_git_changes(project_path, since_date=facts_time)

    # 2. 各维度漂移检测
    drifts = []
    drifts.extend(detect_language_drift(facts, project_path))
    drifts.extend(detect_dependency_drift(facts, project_path))
    drifts.extend(detect_structure_drift(facts, project_path))
    drifts.extend(detect_config_drift(facts, project_path))

    # 3. 计算总分
    score = compute_drift_score(drifts, git_changes)

    # 4. 生成建议
    if score >= 60:
        recommendation = 'full_rebuild'
        status = 'stale'
        message = f'项目上下文已严重过期（漂移分数: {score}/100），建议全量重建'
    elif score >= threshold:
        recommendation = 'incremental_update'
        status = 'drifted'
        message = f'项目上下文有漂移（漂移分数: {score}/100），建议增量更新'
    else:
        recommendation = 'none'
        status = 'fresh'
        message = f'项目上下文仍然有效（漂移分数: {score}/100）'

    return {
        'status': status,
        'message': message,
        'recommendation': recommendation,
        'score': score,
        'threshold': threshold,
        'facts_generated_at': facts_time,
        'checked_at': datetime.now().isoformat(),
        'drifts': drifts,
        'git_changes': {
            'has_git': git_changes['has_git'],
            'changed_files_count': len(git_changes.get('changed_files', [])),
            'added_files_count': len(git_changes.get('added_files', [])),
            'deleted_files_count': len(git_changes.get('deleted_files', [])),
            'commit_count': git_changes.get('commit_count', 0),
            'affected_dirs': git_changes.get('affected_dirs', []),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description='项目上下文漂移检测器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('project_path', help='项目路径')
    parser.add_argument('--facts', '-f', help='.context-facts.json 文件路径')
    parser.add_argument('--threshold', '-t', type=int, default=30,
                        help='漂移阈值（0-100，默认 30）')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出')

    args = parser.parse_args()
    project_path = os.path.abspath(args.project_path)

    report = detect_drift(project_path, facts_path=args.facts, threshold=args.threshold)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    # 人类可读输出
    status_emoji = {'fresh': '✅', 'drifted': '⚠️', 'stale': '❌', 'no_facts': '❓'}
    print(f"\n{status_emoji.get(report['status'], '?')} {report['message']}")

    if report.get('facts_generated_at'):
        print(f"   上次生成: {report['facts_generated_at'][:19]}")

    git = report.get('git_changes', {})
    if git.get('has_git'):
        total = git.get('changed_files_count', 0) + git.get('added_files_count', 0) + git.get('deleted_files_count', 0)
        if total > 0:
            print(f"   Git 变更: {total} 文件 (修改 {git['changed_files_count']}, "
                  f"新增 {git['added_files_count']}, 删除 {git['deleted_files_count']})")
        if git.get('affected_dirs'):
            print(f"   受影响目录: {', '.join(git['affected_dirs'][:8])}")

    if report.get('drifts'):
        print(f"\n漂移详情 ({len(report['drifts'])} 项):")
        for d in report['drifts']:
            sev = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(d.get('severity'), '⚪')
            print(f"   {sev} {d['detail']}")

    rec = report.get('recommendation', 'none')
    if rec == 'full_rebuild':
        print(f"\n💡 建议: 运行 `python gitnexus_to_skill.py {project_path}` 全量重建项目上下文")
    elif rec == 'incremental_update':
        print(f"\n💡 建议: 运行 `python gitnexus_to_skill.py {project_path}` 更新项目上下文")
    print()


if __name__ == '__main__':
    main()
