# -*- coding: utf-8 -*-
"""
Shell 项目上下文提取系统 - 主入口

用法:
    python skill_main.py analyze <project_path> [--output <output_dir>]
    python skill_main.py generate <knowledge_file> [--output <output_dir>]
    python skill_main.py all <project_path> [--output <output_dir>]
"""
import os
import sys
import argparse
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extractor.fusion import ShellKnowledgeBase, ShellKnowledgeBaseFusion
from generator.skill_generator import ShellSkillGenerator


def analyze_project(args):
    """分析项目，生成知识库"""
    print(f"[INFO] 开始分析 Shell 项目: {args.project_path}")

    # 创建融合器
    config = {
        'exclude_patterns': args.exclude.split(',') if args.exclude else None,
    }
    fusion = ShellKnowledgeBaseFusion(config)

    # 分析项目
    kb = fusion.analyze_project(args.project_path)

    # 保存知识库
    output_dir = args.output or os.path.join(args.project_path, '.specify', 'cache')
    os.makedirs(output_dir, exist_ok=True)

    kb_path = os.path.join(output_dir, 'shell_knowledge.json')
    kb.save(kb_path)

    print(f"[INFO] 知识库已保存到: {kb_path}")
    print(f"[INFO] 统计信息:")
    print(f"  - Shell 文件数: {kb.statistics.get('file_count', 0)}")
    print(f"  - 函数数: {kb.statistics.get('function_count', 0)}")
    print(f"  - 变量数: {kb.statistics.get('variable_count', 0)}")
    print(f"  - 注释数: {kb.statistics.get('comment_count', 0)}")
    print(f"  - Source 引用数: {kb.statistics.get('source_count', 0)}")
    print(f"  - 模式数: {kb.statistics.get('pattern_count', 0)}")

    if kb.errors:
        print(f"[WARN] 错误数: {len(kb.errors)}")

    return kb_path


def generate_skills(args):
    """根据知识库生成 Skill 文档"""
    print(f"[INFO] 加载知识库: {args.knowledge}")

    # 加载知识库
    kb = ShellKnowledgeBase.load(args.knowledge)

    # 创建生成器
    config = {
        'max_examples': args.max_examples,
        'max_example_lines': args.max_lines,
    }
    generator = ShellSkillGenerator(config)

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


def run_all(args):
    """执行完整流程：分析 + 生成 Skill"""
    print(f"[INFO] 开始完整流程: {args.project_path}")
    print(f"[INFO] 时间: {datetime.now().isoformat()}")
    print("")

    # 1. 分析项目
    print("=" * 50)
    print("步骤 1: 分析 Shell 项目")
    print("=" * 50)

    config = {
        'exclude_patterns': args.exclude.split(',') if args.exclude else None,
    }
    fusion = ShellKnowledgeBaseFusion(config)
    kb = fusion.analyze_project(args.project_path)

    # 保存知识库
    cache_dir = os.path.join(args.project_path, '.specify', 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    kb_path = os.path.join(cache_dir, 'shell_knowledge.json')
    kb.save(kb_path)

    print(f"[INFO] 知识库已保存: {kb_path}")
    print(f"[INFO] 分析完成，发现:")
    print(f"  - {kb.statistics.get('file_count', 0)} 个 Shell 文件")
    print(f"  - {kb.statistics.get('function_count', 0)} 个函数")
    print(f"  - {kb.statistics.get('variable_count', 0)} 个变量")
    print(f"  - {kb.statistics.get('comment_count', 0)} 个注释")
    print(f"  - {kb.statistics.get('source_count', 0)} 个 source 引用")
    print(f"  - {kb.statistics.get('pattern_count', 0)} 个代码模式")
    print("")

    # 2. 生成 Skill
    print("=" * 50)
    print("步骤 2: 生成 Skill 文档")
    print("=" * 50)

    skill_config = {
        'max_examples': args.max_examples,
        'max_example_lines': args.max_lines,
    }
    skill_generator = ShellSkillGenerator(skill_config)

    output_dir = args.output or os.path.join(
        args.project_path, '.specify', 'skills', 'project-context'
    )
    output_dir = os.path.abspath(output_dir)

    generated_files = skill_generator.generate_all(kb, output_dir)

    print(f"[INFO] Skill 文档已生成: {output_dir}")
    for filename in generated_files.keys():
        print(f"  - {filename}")
    print("")

    # 完成
    print("=" * 50)
    print("完成!")
    print("=" * 50)
    print(f"[INFO] 知识库: {kb_path}")
    print(f"[INFO] Skill 目录: {output_dir}")

    if kb.errors:
        print(f"\n[WARN] 分析过程中有 {len(kb.errors)} 个错误，请检查知识库文件")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Shell 项目上下文提取系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析项目并生成知识库
  python skill_main.py analyze /path/to/project

  # 根据知识库生成 Skill 文档
  python skill_main.py generate /path/to/shell_knowledge.json

  # 完整流程（分析 + 生成）
  python skill_main.py all /path/to/project
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
    all_parser.add_argument('--max-examples', type=int, default=3, help='每个 Skill 的最大示例数')
    all_parser.add_argument('--max-lines', type=int, default=30, help='示例代码最大行数')

    args = parser.parse_args()

    if args.command == 'analyze':
        analyze_project(args)
    elif args.command == 'generate':
        generate_skills(args)
    elif args.command == 'all':
        run_all(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
