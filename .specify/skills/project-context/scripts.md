---
skill_id: project-context/scripts
title: "Scripts 模块详情"
description: "scripts 模块的文件、符号、入口点和执行流详情"
triggers:
  - scripts
  - Scripts
generated_at: "2026-04-02T13:24:32.632608"
generator: "gitnexus"
---

# Scripts

114 个符号 | 11 个文件 | 内聚度: 69%

## 使用场景

- 处理 `ecc-components/`
- 理解 test_load_from_empty_dir, test_load_from_nonexistent_dir, test_load_annotates_metadata 的工作原理
- 修改 scripts 相关功能

## 关键文件

| 文件 | 符号 |
|------|---------|
| `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | test_load_from_empty_dir, test_load_from_nonexistent_dir, test_load_annotates_metadata, test_load_defaults_scope_from_label, test_load_preserves_explicit_scope (+53) |
| `ecc-components/skills/continuous-learning-v2/scripts/instinct-cli.py` | _load_instincts_from_dir, parse_instinct_file, _validate_file_path, detect_project, _update_registry (+23) |
| `ecc-components/skills/videodb/scripts/ws_listener.py` | log, append_event, write_pid, cleanup_pid, is_fatal_error (+7) |
| `ecc-components/skills/skill-comply/scripts/runner.py` | ScenarioRun, run_scenario, _safe_sandbox_dir, _setup_sandbox, _parse_stream_json |
| `ecc-components/skills/skill-comply/scripts/report.py` | generate_report, _overall_compliance, _step_compliance_rate, _steps_to_promote |
| `ecc-components/skills/skill-comply/scripts/scenario_generator.py` | Scenario, generate_scenarios |
| `ecc-components/skills/skill-comply/scripts/parser.py` | ObservationEvent |
| `ecc-components/skills/skill-comply/scripts/utils.py` | extract_yaml |
| `ecc-components/skills/skill-comply/scripts/spec_generator.py` | generate_spec |
| `ecc-components/skills/skill-comply/scripts/run.py` | main |

## 入口点

探索该模块的起点：

- **`test_load_from_empty_dir`** (函数) — `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py:406`
- **`test_load_from_nonexistent_dir`** (函数) — `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py:411`
- **`test_load_annotates_metadata`** (函数) — `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py:416`
- **`test_load_defaults_scope_from_label`** (函数) — `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py:428`
- **`test_load_preserves_explicit_scope`** (函数) — `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py:445`

## 关键符号

| 符号 | 类型 | 文件 | 行号 |
|--------|------|------|------|
| `ScenarioRun` | 类 | `ecc-components/skills/skill-comply/scripts/runner.py` | 20 |
| `ObservationEvent` | 类 | `ecc-components/skills/skill-comply/scripts/parser.py` | 12 |
| `Scenario` | 类 | `ecc-components/skills/skill-comply/scripts/scenario_generator.py` | 16 |
| `test_load_from_empty_dir` | 函数 | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 406 |
| `test_load_from_nonexistent_dir` | 函数 | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 411 |
| `test_load_annotates_metadata` | 函数 | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 416 |
| `test_load_defaults_scope_from_label` | 函数 | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 428 |
| `test_load_preserves_explicit_scope` | 函数 | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 445 |
| `test_load_handles_corrupt_file` | 函数 | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 456 |
| `test_load_supports_yml_extension` | 函数 | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 468 |
| `test_load_supports_md_extension` | 函数 | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 477 |
| `test_load_instincts_from_dir_uses_utf8_encoding` | 函数 | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 486 |
| `log` | 函数 | `ecc-components/skills/videodb/scripts/ws_listener.py` | 107 |
| `append_event` | 函数 | `ecc-components/skills/videodb/scripts/ws_listener.py` | 112 |
| `write_pid` | 函数 | `ecc-components/skills/videodb/scripts/ws_listener.py` | 121 |
| `cleanup_pid` | 函数 | `ecc-components/skills/videodb/scripts/ws_listener.py` | 127 |
| `is_fatal_error` | 函数 | `ecc-components/skills/videodb/scripts/ws_listener.py` | 135 |
| `listen_with_retry` | 函数 | `ecc-components/skills/videodb/scripts/ws_listener.py` | 146 |
| `main_async` | 函数 | `ecc-components/skills/videodb/scripts/ws_listener.py` | 231 |
| `handle_signal` | 函数 | `ecc-components/skills/videodb/scripts/ws_listener.py` | 236 |

## 执行流

| 执行流 | 类型 | 步骤数 |
|------|------|-------|
| `Cmd_promote → Parse_instinct_file` | 跨模块 | 6 |
| `Main → Parse_instinct_file` | 跨模块 | 5 |
| `Cmd_export → Parse_instinct_file` | 跨模块 | 5 |
| `Cmd_evolve → Parse_instinct_file` | 跨模块 | 5 |
| `Main → _update_registry` | 跨模块 | 4 |
| `Main → _collect_pending_dirs` | 跨模块 | 4 |
| `Main → _parse_created_date` | 跨模块 | 4 |
| `Main → _maybe_refresh` | 跨模块 | 4 |
| `Main → Step` | 跨模块 | 4 |
| `Main → Detector` | 跨模块 | 4 |

## 关联模块

| 模块 | 连接数 |
|------|-------------|
| Analyzer | 3 次调用 |
| Tests | 2 次调用 |
| Python | 1 次调用 |
| Specify_cli | 1 次调用 |
