# -*- coding: utf-8 -*-
"""
智能化项目上下文提取系统 - 主入口

用法:
    python skill_main.py analyze <project_path> [--output <output_dir>]
    python skill_main.py generate <knowledge_file> [--output <output_dir>]
    python skill_main.py all <project_path> [--output <output_dir>] [--windsurf]
"""
import os
import sys
import argparse
import json
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extractor.libcst import KnowledgeBase, KnowledgeBaseFusion
from generator.skill_generator import SkillGenerator
from generator.windsurf_generator import WindsurfGenerator
from validator import SkillValidator, ConflictDetector


def analyze_project(args):
    """分析项目，生成知识库"""
    print(f"[INFO] 开始分析项目: {args.project_path}")

    # 创建融合器
    config = {
        'exclude_patterns': args.exclude.split(',') if args.exclude else None,
    }
    fusion = KnowledgeBaseFusion(config)

    # 分析项目
    kb = fusion.analyze_project(args.project_path)

    # 保存知识库
    output_dir = args.output or os.path.join(args.project_path, '.specify', 'cache')
    os.makedirs(output_dir, exist_ok=True)

    kb_path = os.path.join(output_dir, 'knowledge.json')
    kb.save(kb_path)

    print(f"[INFO] 知识库已保存到: {kb_path}")
    print(f"[INFO] 统计信息:")
    print(f"  - 文件数: {kb.statistics.get('file_count', 0)}")
    print(f"  - 类数: {kb.statistics.get('class_count', 0)}")
    print(f"  - 函数数: {kb.statistics.get('function_count', 0)}")
    print(f"  - Django 模型数: {kb.statistics.get('django', {}).get('model_count', 0)}")
    print(f"  - Django 视图数: {kb.statistics.get('django', {}).get('view_count', 0)}")

    if kb.errors:
        print(f"[WARN] 错误数: {len(kb.errors)}")

    return kb_path


def generate_skills(args):
    """根据知识库生成 Skill 文档"""
    print(f"[INFO] 加载知识库: {args.knowledge}")

    # 加载知识库
    kb = KnowledgeBase.load(args.knowledge)

    # 创建生成器
    config = {
        'max_examples': args.max_examples,
        'max_example_lines': args.max_lines,
    }
    generator = SkillGenerator(config)

    # 生成 Skill
    output_dir = args.output or os.path.join(
        os.path.dirname(args.knowledge), '..', 'skills', 'project-context'
    )
    output_dir = os.path.abspath(output_dir)

    generated_files = generator.generate_all(kb, output_dir)

    print(f"[INFO] Skill 文档已生成到: {output_dir}")
    print(f"[INFO] 生成的文件:")
    for filename, filepath in generated_files.items():
        print(f"  - {filename}")

    return output_dir


def generate_windsurf(args, kb: KnowledgeBase, skills_dir: str):
    """生成 Windsurf 集成文件"""
    print(f"[INFO] 生成 Windsurf 集成文件...")

    generator = WindsurfGenerator({'project_root': args.project_path})

    # 计算相对路径
    rel_skills_dir = os.path.relpath(skills_dir, args.project_path)

    generated_files = generator.generate_all(kb, rel_skills_dir, args.project_path)

    print(f"[INFO] Windsurf 文件已生成:")
    for filename, filepath in generated_files.items():
        print(f"  - {filename}")


def run_all(args):
    """执行完整流程：分析 + 生成 Skill + Windsurf 集成"""
    print(f"[INFO] 开始完整流程: {args.project_path}")
    print(f"[INFO] 时间: {datetime.now().isoformat()}")
    print("")

    # 1. 分析项目
    print("=" * 50)
    print("步骤 1: 分析项目")
    print("=" * 50)

    config = {
        'exclude_patterns': args.exclude.split(',') if args.exclude else None,
    }
    fusion = KnowledgeBaseFusion(config)
    kb = fusion.analyze_project(args.project_path)

    # 保存知识库
    cache_dir = os.path.join(args.project_path, '.specify', 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    kb_path = os.path.join(cache_dir, 'knowledge.json')
    kb.save(kb_path)

    print(f"[INFO] 知识库已保存: {kb_path}")
    print(f"[INFO] 分析完成，发现:")
    print(f"  - {kb.statistics.get('file_count', 0)} 个 Python 文件")
    print(f"  - {kb.statistics.get('class_count', 0)} 个类")
    print(f"  - {kb.statistics.get('function_count', 0)} 个函数")
    print(f"  - {kb.statistics.get('django', {}).get('model_count', 0)} 个 Django 模型")
    print(f"  - {kb.statistics.get('django', {}).get('view_count', 0)} 个 Django 视图")
    print("")

    # 2. 生成 Skill
    print("=" * 50)
    print("步骤 2: 生成 Skill 文档")
    print("=" * 50)

    skill_config = {
        'max_examples': args.max_examples,
        'max_example_lines': args.max_lines,
    }
    skill_generator = SkillGenerator(skill_config)

    output_dir = args.output or os.path.join(
        args.project_path, '.specify', 'skills', 'project-context'
    )
    output_dir = os.path.abspath(output_dir)

    generated_files = skill_generator.generate_all(kb, output_dir)

    print(f"[INFO] Skill 文档已生成: {output_dir}")
    for filename in generated_files.keys():
        print(f"  - {filename}")
    print("")

    # 3. 生成 Windsurf 集成（可选）
    if args.windsurf:
        print("=" * 50)
        print("步骤 3: 生成 Windsurf 集成")
        print("=" * 50)

        windsurf_generator = WindsurfGenerator({'project_root': args.project_path})
        rel_skills_dir = os.path.relpath(output_dir, args.project_path)

        windsurf_files = windsurf_generator.generate_all(kb, rel_skills_dir, args.project_path)

        print(f"[INFO] Windsurf 文件已生成:")
        for filename in windsurf_files.keys():
            print(f"  - {filename}")
        print("")

    # 完成
    print("=" * 50)
    print("完成!")
    print("=" * 50)
    print(f"[INFO] 知识库: {kb_path}")
    print(f"[INFO] Skill 目录: {output_dir}")
    if args.windsurf:
        print(f"[INFO] Windsurf 规则: {os.path.join(args.project_path, '.windsurfrules')}")

    if kb.errors:
        print(f"\n[WARN] 分析过程中有 {len(kb.errors)} 个错误，请检查知识库文件")


def validate_skills(args):
    """验证 Skill 文档"""
    print(f"[INFO] 开始验证 Skill: {args.skill_dir}")

    # 创建验证器
    validator = SkillValidator({})

    # 加载知识库（如果提供）
    if args.knowledge:
        print(f"[INFO] 加载知识库: {args.knowledge}")
        validator.load_knowledge_base(args.knowledge)

    # 验证 Skill 目录
    result = validator.validate_skill_directory(args.skill_dir)

    print(f"\n[INFO] 验证完成:")
    print(f"  - 检查项目: {result.checked_items}")
    print(f"  - 通过项目: {result.passed_items}")
    print(f"  - 错误数: {result.error_count}")
    print(f"  - 警告数: {result.warning_count}")

    if result.is_valid:
        print("\n✅ 验证通过")
    else:
        print("\n❌ 验证失败")
        for issue in result.issues:
            if issue.level.value == 'error':
                print(f"  [ERROR] {issue.message}")

    # 冲突检测
    if args.check_conflicts:
        print(f"\n[INFO] 检测冲突...")
        detector = ConflictDetector({})
        conflict_report = detector.detect_conflicts(args.skill_dir)

        if conflict_report.has_conflicts:
            print(f"  - 发现 {len(conflict_report.conflicts)} 个冲突")
            for c in conflict_report.conflicts:
                print(f"  [{c.severity.upper()}] {c.description}")
        else:
            print("  - 未发现冲突")

    # 生成报告
    if args.report:
        report_content = validator.generate_report(result)
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"\n[INFO] 报告已保存: {args.report}")

    return result.is_valid


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='智能化项目上下文提取系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析项目并生成知识库
  python skill_main.py analyze /path/to/project

  # 根据知识库生成 Skill 文档
  python skill_main.py generate /path/to/knowledge.json

  # 完整流程（分析 + 生成 + Windsurf 集成）
  python skill_main.py all /path/to/project --windsurf

  # 验证 Skill 文档
  python skill_main.py validate /path/to/skills --check-conflicts
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析项目生成知识库')
    analyze_parser.add_argument('project_path', help='项目路径')
    analyze_parser.add_argument('--output', '-o', help='输出目录')
    analyze_parser.add_argument('--exclude', help='排除的目录模式，逗号分隔')

    # generate 命令
    generate_parser = subparsers.add_parser('generate', help='根据知识库生成 Skill')
    generate_parser.add_argument('knowledge', help='知识库文件路径')
    generate_parser.add_argument('--output', '-o', help='输出目录')
    generate_parser.add_argument('--max-examples', type=int, default=3, help='每个 Skill 的最大示例数')
    generate_parser.add_argument('--max-lines', type=int, default=30, help='示例代码最大行数')

    # all 命令
    all_parser = subparsers.add_parser('all', help='完整流程')
    all_parser.add_argument('project_path', help='项目路径')
    all_parser.add_argument('--output', '-o', help='Skill 输出目录')
    all_parser.add_argument('--exclude', help='排除的目录模式，逗号分隔')
    all_parser.add_argument('--windsurf', action='store_true', help='生成 Windsurf 集成文件')
    all_parser.add_argument('--max-examples', type=int, default=3, help='每个 Skill 的最大示例数')
    all_parser.add_argument('--max-lines', type=int, default=30, help='示例代码最大行数')

    # validate 命令
    validate_parser = subparsers.add_parser('validate', help='验证 Skill 文档')
    validate_parser.add_argument('skill_dir', help='Skill 目录路径')
    validate_parser.add_argument('--knowledge', '-k', help='知识库文件路径（用于验证引用）')
    validate_parser.add_argument('--check-conflicts', action='store_true', help='检测 Skill 之间的冲突')
    validate_parser.add_argument('--report', '-r', help='输出验证报告文件')

    args = parser.parse_args()

    if args.command == 'analyze':
        analyze_project(args)
    elif args.command == 'generate':
        generate_skills(args)
    elif args.command == 'all':
        run_all(args)
    elif args.command == 'validate':
        validate_skills(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
