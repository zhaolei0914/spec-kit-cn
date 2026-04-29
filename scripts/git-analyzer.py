#!/usr/bin/env python3
"""
Git 历史分析工具（统一版本）

功能：
1. 基础分析：检测 Git 仓库、获取提交历史、生成热点文件
2. 深度分析：智能分类提交、深度分析、生成 Memory 文件

使用方法：
    python3 git-analyzer.py              # 仅基础分析
    python3 git-analyzer.py --deep       # 基础 + 深度分析

输出：
    - .specify/memory/git-extraction-report.md
    - .specify/memory/hotspot-files.md
    - .specify/memory/git-commits-for-analysis.txt
    - （深度分析）coding-standards.md, design-decisions.md, known-pitfalls.md
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from collections import Counter

# 配置
CONFIG = {
    "output_dir": ".specify/memory",
    "max_commits": 20,  # 分析的最大提交数（降低到 20）
    "max_diff_lines": 200,  # 每个提交的最大 diff 行数
}

class GitAnalyzer:
    """Git 历史分析器"""

    def __init__(self, config: Dict, deep_analysis: bool = False):
        self.config = config
        self.deep_analysis = deep_analysis
        self.commits = []
        self.stats = {
            "total_commits": 0,
            "hotspot_files": 0,
            "start_time": None,
            "end_time": None,
        }

        # 确保输出目录存在
        Path(config["output_dir"]).mkdir(parents=True, exist_ok=True)

        self.report_file = Path(config["output_dir"]) / "git-extraction-report.md"
        self.commits_file = Path(config["output_dir"]) / "git-commits-for-analysis.txt"

    def log(self, message: str, to_report: bool = True):
        """输出日志（同时写入报告文件）"""
        print(message)
        if to_report and hasattr(self, '_report_handle'):
            self._report_handle.write(message + '\n')

    def check_git_repo(self) -> bool:
        """检测 Git 仓库"""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_commits_from_git(self) -> List[Dict]:
        """从 Git 获取提交历史"""
        try:
            result = subprocess.run(
                ["git", "log", f"-n{self.config['max_commits']}",
                 "--pretty=format:%H|%an|%ad|%s", "--date=short"],
                capture_output=True,
                text=True,
                check=True
            )

            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line or '|' not in line:
                    continue

                parts = line.split('|', 3)
                if len(parts) >= 4:
                    commits.append({
                        "hash": parts[0].strip(),
                        "author": parts[1].strip(),
                        "date": parts[2].strip(),
                        "message": parts[3].strip(),
                    })

            return commits
        except subprocess.CalledProcessError as e:
            self.log(f"❌ 获取提交历史失败: {e}")
            return []

    def save_commits_data(self):
        """保存提交数据到文件"""
        with open(self.commits_file, 'w', encoding='utf-8') as f:
            for commit in self.commits:
                f.write(f"{commit['hash']}|{commit['author']}|{commit['date']}|{commit['message']}\n")

    def get_commit_stats(self, commit_hash: str) -> Dict:
        """获取提交的统计信息"""
        try:
            # 获取文件修改统计
            result = subprocess.run(
                ["git", "show", "--stat", "--pretty=format:", commit_hash],
                capture_output=True,
                text=True,
                check=True
            )

            lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
            if not lines:
                return {"files": 0, "insertions": 0, "deletions": 0}

            # 解析最后一行的统计信息
            last_line = lines[-1]
            files = insertions = deletions = 0

            if "file" in last_line:
                parts = last_line.split(',')
                for part in parts:
                    if "file" in part:
                        files = int(''.join(filter(str.isdigit, part)) or 0)
                    elif "insertion" in part:
                        insertions = int(''.join(filter(str.isdigit, part)) or 0)
                    elif "deletion" in part:
                        deletions = int(''.join(filter(str.isdigit, part)) or 0)

            return {"files": files, "insertions": insertions, "deletions": deletions}
        except:
            return {"files": 0, "insertions": 0, "deletions": 0}

    def calculate_priority(self, commit: Dict, stats: Dict) -> tuple:
        """计算提交的优先级"""
        score = 0

        # 基于文件数量
        if stats["files"] >= 5:
            score += 3
        elif stats["files"] >= 3:
            score += 2
        elif stats["files"] >= 1:
            score += 1

        # 基于代码行数
        total_lines = stats["insertions"] + stats["deletions"]
        if total_lines >= 100:
            score += 3
        elif total_lines >= 50:
            score += 2
        elif total_lines >= 20:
            score += 1

        # 基于 commit message 关键词
        message = commit["message"].lower()
        high_keywords = ["refactor", "重构", "架构", "architecture", "breaking"]
        medium_keywords = ["fix", "修复", "bug", "feature", "功能"]

        if any(kw in message for kw in high_keywords):
            score += 3
        elif any(kw in message for kw in medium_keywords):
            score += 2

        # 确定优先级
        if score >= 6:
            return ("🔴 高", score)
        elif score >= 3:
            return ("🟡 中", score)
        else:
            return ("⚪ 低", score)

    def generate_commit_details(self):
        """生成提交详情文件"""
        commits_dir = Path(self.config["output_dir"]) / "git-commits"
        commits_dir.mkdir(parents=True, exist_ok=True)

        self.log("▶ 步骤 5：生成提交详情文件")

        # 收集所有提交的统计信息和优先级
        commit_data = []
        for i, commit in enumerate(self.commits, 1):
            stats = self.get_commit_stats(commit["hash"])
            priority, score = self.calculate_priority(commit, stats)

            commit_data.append({
                "index": i,
                "commit": commit,
                "stats": stats,
                "priority": priority,
                "score": score
            })

        # 生成摘要文件
        summary_file = commits_dir / "summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Git 提交摘要（最近 {len(self.commits)} 个）\n\n")
            f.write("| # | Hash | Date | Author | Message | 文件 | 行数 | 优先级 |\n")
            f.write("|---|------|------|--------|---------|------|------|--------|\n")

            for data in commit_data:
                commit = data["commit"]
                stats = data["stats"]
                total_lines = stats["insertions"] + stats["deletions"]

                f.write(f"| {data['index']} | "
                       f"`{commit['hash'][:7]}` | "
                       f"{commit['date']} | "
                       f"{commit['author']} | "
                       f"{commit['message'][:40]}{'...' if len(commit['message']) > 40 else ''} | "
                       f"{stats['files']} | "
                       f"+{stats['insertions']}/-{stats['deletions']} | "
                       f"{data['priority']} |\n")

            # 统计优先级分布
            high_count = sum(1 for d in commit_data if d['priority'] == '🔴 高')
            medium_count = sum(1 for d in commit_data if d['priority'] == '🟡 中')
            low_count = sum(1 for d in commit_data if d['priority'] == '⚪ 低')

            f.write(f"\n## 优先级分布\n\n")
            f.write(f"- 🔴 高优先级: {high_count} 个（建议优先分析）\n")
            f.write(f"- 🟡 中优先级: {medium_count} 个（可选分析）\n")
            f.write(f"- ⚪ 低优先级: {low_count} 个（可跳过）\n\n")

            f.write(f"## 分析建议\n\n")
            f.write(f"1. **优先分析** 🔴 高优先级提交（{high_count} 个）\n")
            f.write(f"2. **可选分析** 🟡 中优先级提交（{medium_count} 个）\n")
            f.write(f"3. **可跳过** ⚪ 低优先级提交（{low_count} 个）\n\n")
            f.write(f"详细信息请查看 `details/commit-<hash>.md` 文件。\n")

        # 生成详细文件（只为高和中优先级生成）
        details_dir = commits_dir / "details"
        details_dir.mkdir(parents=True, exist_ok=True)

        generated_count = 0
        for data in commit_data:
            if data['priority'] in ['🔴 高', '🟡 中']:
                self.generate_single_commit_file(data, details_dir)
                generated_count += 1

        self.log(f"✅ 已生成摘要文件和 {generated_count} 个详情文件")
        self.log("")

        return len(commit_data)

    def generate_single_commit_file(self, data: Dict, output_dir: Path):
        """生成单个提交的详细文件"""
        commit = data["commit"]
        stats = data["stats"]
        commit_hash = commit["hash"]
        short_hash = commit_hash[:7]

        # 获取修改的文件列表
        try:
            result = subprocess.run(
                ["git", "show", "--name-status", "--pretty=format:", commit_hash],
                capture_output=True,
                text=True,
                check=True
            )
            changed_files = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
        except:
            changed_files = []

        # 获取 diff（限制行数）
        try:
            result = subprocess.run(
                ["git", "show", commit_hash],
                capture_output=True,
                text=True,
                check=True
            )
            diff_lines = result.stdout.split('\n')
            max_lines = self.config.get("max_diff_lines", 200)
            if len(diff_lines) > max_lines:
                diff_content = '\n'.join(diff_lines[:max_lines])
                diff_content += f"\n\n... (省略 {len(diff_lines) - max_lines} 行)"
            else:
                diff_content = result.stdout
        except:
            diff_content = "（无法获取 diff）"

        # 写入文件
        detail_file = output_dir / f"commit-{short_hash}.md"
        with open(detail_file, 'w', encoding='utf-8') as f:
            f.write(f"# Commit {short_hash}\n\n")
            f.write(f"## 基本信息\n\n")
            f.write(f"- **Hash**: `{commit_hash}`\n")
            f.write(f"- **Author**: {commit['author']}\n")
            f.write(f"- **Date**: {commit['date']}\n")
            f.write(f"- **Message**: {commit['message']}\n")
            f.write(f"- **优先级**: {data['priority']}\n\n")

            f.write(f"## 统计信息\n\n")
            f.write(f"- 修改文件数: {stats['files']}\n")
            f.write(f"- 新增行数: {stats['insertions']}\n")
            f.write(f"- 删除行数: {stats['deletions']}\n")
            f.write(f"- 净变化: {stats['insertions'] - stats['deletions']:+d}\n\n")

            if changed_files:
                f.write(f"## 修改的文件\n\n")
                for file_line in changed_files[:20]:  # 最多显示 20 个文件
                    f.write(f"- `{file_line}`\n")
                if len(changed_files) > 20:
                    f.write(f"\n... 还有 {len(changed_files) - 20} 个文件\n")
                f.write(f"\n")

            f.write(f"## Diff\n\n")
            f.write(f"```diff\n{diff_content}\n```\n\n")

            f.write(f"---\n\n")
            f.write(f"## 分析建议\n\n")
            f.write(f"**分类**：\n")
            f.write(f"- [ ] coding_standard（编码规范）\n")
            f.write(f"- [ ] design_decision（设计决策）\n")
            f.write(f"- [ ] bug_fix（Bug 修复）\n")
            f.write(f"- [ ] other（其他）\n\n")
            f.write(f"**值得提取**：\n")
            f.write(f"- [ ] 是\n")
            f.write(f"- [ ] 否\n\n")
            f.write(f"**原因**：\n")
            f.write(f"_（AI 填写）_\n")

    def generate_hotspot_files(self) -> int:
        """生成热点文件分析"""
        try:
            # 获取文件修改统计
            result = subprocess.run(
                ["git", "log", f"-n{self.config['max_commits']}",
                 "--name-only", "--pretty=format:"],
                capture_output=True,
                text=True,
                check=True
            )

            # 统计文件修改次数
            files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            file_counts = Counter(files)
            top_files = file_counts.most_common(20)

            # 生成热点文件报告
            hotspot_file = Path(self.config["output_dir"]) / "hotspot-files.md"
            with open(hotspot_file, 'w', encoding='utf-8') as f:
                f.write("# 热点文件分析\n\n")
                f.write(f"> 基于最近 {self.config['max_commits']} 个提交的统计分析\n\n")
                f.write("## 频繁修改的文件\n\n")
                f.write("以下文件在最近提交中被频繁修改，可能需要：\n")
                f.write("- 增加测试覆盖\n")
                f.write("- 考虑重构或模块拆分\n")
                f.write("- 关注代码质量\n\n")
                f.write("| 修改次数 | 文件路径 |\n")
                f.write("|---------|----------|\n")

                for file_path, count in top_files:
                    f.write(f"| {count} | `{file_path}` |\n")

                f.write(f"\n---\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**分析范围**: 最近 {self.config['max_commits']} 个提交\n")

            return len(top_files)
        except subprocess.CalledProcessError as e:
            self.log(f"⚠️  生成热点文件失败: {e}")
            return 0

    def write_report_header(self):
        """写入报告头部"""
        self._report_handle.write("=== 阶段 4：Git 历史记忆提取 ===\n\n")

    def write_report_footer(self):
        """写入报告尾部"""
        self._report_handle.write("\n## 执行结果\n\n")
        self._report_handle.write(f"- **状态**: ✅ 成功\n")
        self._report_handle.write(f"- **分析范围**: 最近 {self.stats['total_commits']} 个提交\n")
        self._report_handle.write(f"- **热点文件**: {self.stats['hotspot_files']} 个\n\n")

        self._report_handle.write("## 已生成文件\n\n")
        self._report_handle.write(f"1. **热点文件分析**: `{self.config['output_dir']}/hotspot-files.md`\n")
        self._report_handle.write(f"   - 统计最近 {self.config['max_commits']} 个提交中修改最频繁的文件\n")
        self._report_handle.write(f"   - 可用于识别需要重构或增加测试的模块\n\n")

        self._report_handle.write(f"2. **提交数据**: `{self.config['output_dir']}/git-commits-for-analysis.txt`\n")
        self._report_handle.write(f"   - 包含最近 {self.stats['total_commits']} 个提交的元数据\n")
        self._report_handle.write(f"   - 格式: commit_hash|author|date|message\n\n")

        self._report_handle.write(f"3. **提交摘要**: `{self.config['output_dir']}/git-commits/summary.md`\n")
        self._report_handle.write(f"   - 所有提交的优先级排序和统计信息\n")
        self._report_handle.write(f"   - 包含高/中/低优先级分类\n\n")

        self._report_handle.write(f"4. **提交详情**: `{self.config['output_dir']}/git-commits/details/`\n")
        self._report_handle.write(f"   - 高和中优先级提交的详细分析文件\n")
        self._report_handle.write(f"   - 包含 diff、统计信息和分析建议\n\n")

        self._report_handle.write("## 下一步操作\n\n")
        self._report_handle.write("**执行深度分析**（强制，除非非 Git 仓库）：\n\n")
        self._report_handle.write("```bash\n")
        self._report_handle.write("/git-mine\n")
        self._report_handle.write("```\n\n")
        self._report_handle.write("查看 `git-commits/summary.md` 了解提交优先级，然后分析高优先级提交。\n\n")

        self._report_handle.write("---\n\n")
        self._report_handle.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    def run_basic_analysis(self) -> bool:
        """执行基础分析"""
        self.log("▶ 步骤 1：检测 Git 仓库")

        if not self.check_git_repo():
            self.log("⚠️  非 Git 仓库，跳过历史记忆提取")
            self._report_handle.write("\n## 执行结果\n\n")
            self._report_handle.write("- **状态**: 已跳过\n")
            self._report_handle.write("- **原因**: 当前项目不是 Git 仓库\n")
            self._report_handle.write("- **建议**: 如需提取 Git 历史记忆，请先初始化 Git 仓库\n\n")
            self.log("✅ 阶段 4 完成（已跳过）")
            return False

        self.log("✅ 检测到 Git 仓库")
        self.log("")

        # 获取提交历史
        self.log("▶ 步骤 2：获取提交历史")
        self.commits = self.get_commits_from_git()

        if not self.commits:
            self.log("⚠️  未找到提交历史，跳过记忆提取")
            self._report_handle.write("\n## 执行结果\n\n")
            self._report_handle.write("- **状态**: 已跳过\n")
            self._report_handle.write("- **原因**: 仓库无提交历史\n\n")
            self.log("✅ 阶段 4 完成（已跳过）")
            return False

        self.stats["total_commits"] = len(self.commits)
        self.log(f"📊 分析范围: 最近 {self.stats['total_commits']} 个提交")
        self.log("")

        # 生成热点文件分析
        self.log("▶ 步骤 3：生成热点文件分析")
        self.stats["hotspot_files"] = self.generate_hotspot_files()
        self.log(f"✅ 已生成热点文件分析（{self.stats['hotspot_files']} 个文件）")
        self.log("")

        # 保存提交数据
        self.log("▶ 步骤 4：准备提交数据")
        self.save_commits_data()
        self.log(f"✅ 已保存提交数据到 {self.commits_file}")
        self.log("")

        # 生成提交详情文件
        self.generate_commit_details()

        return True

    def run_deep_analysis(self):
        """执行深度分析"""
        self.log("\n=== 深度分析 ===\n")
        self.log("⚠️  深度分析功能待实现")
        self.log("   需要集成 LLM API（OpenAI/Anthropic/本地模型）")
        self.log("   包括：智能分类、深度分析、Memory 文件生成")
        self.log("")

    def run(self) -> bool:
        """执行完整分析流程"""
        self.stats["start_time"] = datetime.now()

        # 打开报告文件
        with open(self.report_file, 'w', encoding='utf-8') as f:
            self._report_handle = f

            # 写入报告头部
            self.write_report_header()

            # 执行基础分析
            if not self.run_basic_analysis():
                return False

            # 执行深度分析（如果启用）
            if self.deep_analysis:
                self.run_deep_analysis()

            # 写入报告尾部
            self.write_report_footer()

        self.stats["end_time"] = datetime.now()

        # 输出完成信息
        self.log("✅ 阶段 4 完成", to_report=False)
        self.log("", to_report=False)
        self.log(f"📄 详细报告: {self.report_file}", to_report=False)

        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Git 历史分析工具")
    parser.add_argument(
        "--deep",
        action="store_true",
        help="启用深度分析（智能分类、深度分析、生成 Memory 文件）"
    )

    args = parser.parse_args()

    analyzer = GitAnalyzer(CONFIG, deep_analysis=args.deep)

    try:
        success = analyzer.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
