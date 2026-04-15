#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Skill 提取工具

简化的命令行工具，用于从 Python/Django 项目中提取 AI Skill 文档。

用法:
    # 1. 分析项目，生成骨架数据
    python main.py analyze --source /path/to/src --output ./cache/project_skeleton.json

    # 2. 生成各类 Skill 文档
    python main.py project-context --skeleton ./cache/project_skeleton.json --output ./skills/project-context/
    python main.py api-skill --skeleton ./cache/project_skeleton.json --output ./skills/api-external/
    python main.py business-rules --skeleton ./cache/project_skeleton.json --output ./skills/business-rules/

核心命令:
    analyze          分析项目，生成骨架数据（必须首先执行）
    project-context  生成项目上下文 Skill
    api-skill        生成 API Skill
    business-rules   生成业务规则 Skill
"""
import argparse
import json
import os
import sys

# 添加脚本目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from parser.base import CodeUnit, CodePattern, save_units, load_units, save_patterns, load_patterns
from parser.python_parser import PythonParser
from miner.pattern_miner import PatternMiner


def cmd_analyze(args):
    """
    分析项目，生成骨架数据

    这是所有 Skill 生成的基础，必须首先执行。
    骨架数据包含：项目信息、目录结构、代码模式、API 入口、业务规则等。
    """
    print(f"分析项目: {args.source}")

    from analyzer.skeleton_generator import SkeletonGenerator
    from analyzer.entry_analyzer import analyze_entries
    from analyzer.api_extractor import ApiExtractor

    # 1. 解析代码
    print("解析代码...")
    parser = PythonParser()
    exclude = ['*/__pycache__/*', '*/node_modules/*', '*/.git/*',
               '*/migrations/*', '*/Thrift/*']
    units = parser.parse_directory(args.source, exclude_patterns=exclude)
    print(f"  发现 {len(units)} 个代码单元")

    # 2. 挖掘模式
    print("挖掘模式...")
    miner = PatternMiner(min_occurrences=args.min_occurrences)
    patterns = miner.mine_patterns(units)
    print(f"  发现 {len(patterns)} 个模式")

    # 3. 分析入口（API + Handler）
    print("分析入口...")
    flows, entries_summary = analyze_entries(args.source)
    print(f"  发现 {entries_summary['total']} 个入口")

    # 4. 提取 API 详细信息
    print("提取 API 信息...")
    api_extractor = ApiExtractor()
    endpoints, framework = api_extractor.extract(args.source)
    print(f"  发现 {len(endpoints)} 个 API 端点")

    # 5. 检测反模式（可选）
    violations = []
    try:
        from analyzer.antipattern_detector import detect_antipatterns
        violations = detect_antipatterns(args.source)
        print(f"  发现 {len(violations)} 个违规")
    except Exception:
        pass

    # 6. 提取错误码定义
    error_codes = []
    exception_classes = []
    try:
        from analyzer.errorcode_extractor import ErrorCodeExtractor
        print("提取错误码...")
        ec_extractor = ErrorCodeExtractor()
        error_codes, exception_classes = ec_extractor.extract(args.source)
        print(f"  发现 {len(error_codes)} 个错误码, {len(exception_classes)} 个异常类")
    except Exception as e:
        print(f"  错误码提取失败: {e}")

    # 7. 提取项目知识（常量、模型、导入、日志等）
    knowledge = {}
    try:
        from analyzer.knowledge_extractor import KnowledgeExtractor
        print("提取项目知识...")
        knowledge_extractor = KnowledgeExtractor()
        knowledge = knowledge_extractor.extract_all(args.source)
        print(f"  发现 {knowledge.get('constants', {}).get('total', 0)} 个常量")
        print(f"  发现 {knowledge.get('models', {}).get('total', 0)} 个数据模型")
        print(f"  发现 {knowledge.get('imports', {}).get('total', 0)} 个导入模式")
        print(f"  发现 {len(knowledge.get('business_terms', []))} 个业务术语")
    except Exception as e:
        print(f"  知识提取失败: {e}")

    # 8. 生成骨架数据
    print("生成骨架数据...")
    generator = SkeletonGenerator()
    skeleton = generator.generate(units, patterns, args.source, entries_summary, violations)

    # 9. 添加 API 端点详细信息到骨架数据
    skeleton['api_endpoints'] = [ep.to_dict() for ep in endpoints]
    skeleton['api_framework'] = framework

    # 10. 添加业务流程信息到骨架数据
    skeleton['business_flows'] = [flow.to_dict() for flow in flows]

    # 11. 添加错误码信息到骨架数据
    skeleton['error_codes'] = [ec.to_dict() for ec in error_codes]
    skeleton['exception_classes'] = [exc.to_dict() for exc in exception_classes]

    # 12. 添加项目知识到骨架数据
    skeleton['knowledge'] = knowledge

    # 13. 保存骨架数据
    generator.save(skeleton, args.output)

    print(f"\n骨架数据已保存到: {args.output}")
    print(f"  - 项目: {skeleton['project']['name']}")
    print(f"  - 框架: {skeleton['project']['framework']['primary']}")
    print(f"  - 服务: {len(skeleton['project']['services'])} 个")
    print(f"  - 聚类: {len(skeleton['clusters'])} 个")
    print(f"  - API 端点: {len(endpoints)} 个")
    print(f"  - 业务流程: {len(flows)} 个")

    return skeleton


def cmd_project_context(args):
    """
    生成项目上下文 Skill 文档

    从骨架数据生成项目开发规范文档，包括：
    - 代码模式规范（web、models、service、handler 等）
    - 命名规范
    - 配置规范
    - 测试规范
    """
    print(f"生成项目上下文: {args.skeleton}")

    from generator.project_context_generator import ProjectContextGenerator

    generator = ProjectContextGenerator()
    files = generator.generate(args.skeleton, args.output)

    print(f"\n生成 {len(files)} 个文件:")
    for f in files:
        print(f"  - {os.path.basename(f)}")

    # 验证必需文件
    missing = []
    for required in generator.REQUIRED_FILES:
        filepath = os.path.join(args.output, required)
        if not os.path.exists(filepath):
            missing.append(required)

    if missing:
        print(f"\n⚠️ 缺失文件: {', '.join(missing)}")
    else:
        print(f"\n✅ 所有 {len(generator.REQUIRED_FILES)} 个必需文件已生成")

    print(f"\n输出目录: {args.output}")

    return files


def cmd_api_skill(args):
    """
    生成 API Skill 文档

    从骨架数据生成供外部服务对接的 API 文档，包括：
    - API 概述和导航
    - 每个端点的详细说明
    - 请求参数和响应结构
    """
    print(f"生成 API Skill: {args.skeleton}")

    from generator.api_skill_generator import ApiSkillGenerator

    # 加载骨架数据
    with open(args.skeleton, 'r', encoding='utf-8') as f:
        skeleton = json.load(f)

    # 获取 API 端点
    endpoints_data = skeleton.get('api_endpoints', [])
    framework = skeleton.get('api_framework', 'unknown')

    if not endpoints_data:
        print("⚠️ 骨架数据中没有 API 端点信息")
        print("请重新运行 analyze 命令以提取 API 信息")
        return []

    # 转换为 ApiEndpoint 对象
    from analyzer.api_extractor import ApiEndpoint, ApiParameter
    endpoints = []
    for ep_data in endpoints_data:
        params = [ApiParameter(**p) for p in ep_data.get('parameters', [])]
        ep = ApiEndpoint(
            path=ep_data.get('path', ''),
            method=ep_data.get('method', 'GET'),
            handler=ep_data.get('handler', ''),
            summary=ep_data.get('summary', ''),
            description=ep_data.get('description', ''),
            tags=ep_data.get('tags', []),
            parameters=params,
            request_body=ep_data.get('request_body', {}),
            response=ep_data.get('response', {}),
            decorators=ep_data.get('decorators', []),
            source_file=ep_data.get('source_file', ''),
            source_line=ep_data.get('source_line', 0),
        )
        endpoints.append(ep)

    print(f"  框架: {framework}")
    print(f"  API 端点: {len(endpoints)} 个")

    # 生成 Skill 文档
    generator = ApiSkillGenerator()
    files = generator.generate(
        endpoints=endpoints,
        framework=framework,
        output_dir=args.output,
        service_name=getattr(args, 'service_name', None) or "",
        base_url=getattr(args, 'base_url', None) or "",
    )

    print(f"\n生成 {len(files)} 个文件:")
    for f in files:
        print(f"  - {os.path.basename(f)}")

    print(f"\n输出目录: {args.output}")

    return files


def cmd_business_rules(args):
    """
    生成业务规则 Skill 文档

    从骨架数据生成业务规则文档，包括：
    - 业务流程概述
    - API 相关的业务规则
    - Handler 相关的业务规则
    """
    print(f"生成业务规则 Skill: {args.skeleton}")

    from analyzer.business_rule_generator import BusinessRuleGenerator
    from analyzer.entry_analyzer import BusinessFlow, EntryPoint, FunctionCall, BusinessCondition, StateChange

    # 加载骨架数据
    with open(args.skeleton, 'r', encoding='utf-8') as f:
        skeleton = json.load(f)

    # 获取业务流程
    flows_data = skeleton.get('business_flows', [])

    if not flows_data:
        print("⚠️ 骨架数据中没有业务流程信息")
        print("请重新运行 analyze 命令以提取业务流程信息")
        return []

    # 转换为 BusinessFlow 对象
    flows = []
    for flow_data in flows_data:
        entry_data = flow_data.get('entry', {})
        entry = EntryPoint(
            type=entry_data.get('type', ''),
            name=entry_data.get('name', ''),
            file_path=entry_data.get('file_path', ''),
            line=entry_data.get('line', 0),
            method=entry_data.get('method', ''),
            path=entry_data.get('path', ''),
            description=entry_data.get('description', ''),
            decorators=entry_data.get('decorators', []),
        )

        call_chain = [FunctionCall(**c) for c in flow_data.get('call_chain', [])]
        conditions = [BusinessCondition(**c) for c in flow_data.get('conditions', [])]
        state_changes = [StateChange(**s) for s in flow_data.get('state_changes', [])]

        flow = BusinessFlow(
            entry=entry,
            call_chain=call_chain,
            conditions=conditions,
            state_changes=state_changes,
            parameters=flow_data.get('parameters', []),
        )
        flows.append(flow)

    print(f"  业务流程: {len(flows)} 个")

    # 生成业务规则文档
    generator = BusinessRuleGenerator()
    files = generator.generate(flows, args.output)

    print(f"\n生成 {len(files)} 个文件:")
    for f in files:
        print(f"  - {os.path.basename(f)}")

    print(f"\n输出目录: {args.output}")

    return files


def main():
    parser = argparse.ArgumentParser(
        description='AI Skill 提取工具 - 从 Python/Django 项目中提取 AI Skill 文档',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # analyze 命令 - 生成骨架数据
    analyze_parser = subparsers.add_parser('analyze', help='分析项目，生成骨架数据')
    analyze_parser.add_argument('--source', '-s', required=True, help='源代码目录')
    analyze_parser.add_argument('--output', '-o', required=True, help='输出 JSON 文件')
    analyze_parser.add_argument('--min-occurrences', '-m', type=int, default=2, help='最小出现次数')

    # project-context 命令 - 生成项目上下文 Skill
    pc_parser = subparsers.add_parser('project-context', help='生成项目上下文 Skill')
    pc_parser.add_argument('--skeleton', '-s', required=True, help='骨架数据文件路径')
    pc_parser.add_argument('--output', '-o', default='.specify/skills/project-context/', help='输出目录')

    # api-skill 命令 - 生成 API Skill
    api_parser = subparsers.add_parser('api-skill', help='生成 API Skill')
    api_parser.add_argument('--skeleton', '-s', required=True, help='骨架数据文件路径')
    api_parser.add_argument('--output', '-o', default='.specify/skills/api-external/', help='输出目录')
    api_parser.add_argument('--service-name', help='服务名称（可选，自动检测）')
    api_parser.add_argument('--base-url', help='API 基础路径（可选，自动检测）')

    # business-rules 命令 - 生成业务规则 Skill
    biz_parser = subparsers.add_parser('business-rules', help='生成业务规则 Skill')
    biz_parser.add_argument('--skeleton', '-s', required=True, help='骨架数据文件路径')
    biz_parser.add_argument('--output', '-o', default='.specify/skills/business-rules/', help='输出目录')

    args = parser.parse_args()

    if args.command == 'analyze':
        cmd_analyze(args)
    elif args.command == 'project-context':
        cmd_project_context(args)
    elif args.command == 'api-skill':
        cmd_api_skill(args)
    elif args.command == 'business-rules':
        cmd_business_rules(args)
    else:
        parser.print_help()
        print("\n推荐使用流程:")
        print("  1. python main.py analyze --source /path/to/src --output ./cache/project_skeleton.json")
        print("  2. python main.py project-context --skeleton ./cache/project_skeleton.json")
        print("  3. python main.py api-skill --skeleton ./cache/project_skeleton.json")
        print("  4. python main.py business-rules --skeleton ./cache/project_skeleton.json")


if __name__ == '__main__':
    main()
