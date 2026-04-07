---
name: scripts
description: "Skill for the Scripts area of repo. 111 symbols across 11 files."
---

# Scripts

111 symbols | 11 files | Cohesion: 67%

## When to Use

- Working with code in `ecc-components/`
- Understanding how test_load_from_empty_dir, test_load_from_nonexistent_dir, test_load_annotates_metadata work
- Modifying scripts-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | test_load_from_empty_dir, test_load_from_nonexistent_dir, test_load_annotates_metadata, test_load_defaults_scope_from_label, test_load_preserves_explicit_scope (+53) |
| `ecc-components/skills/continuous-learning-v2/scripts/instinct-cli.py` | _load_instincts_from_dir, parse_instinct_file, _validate_file_path, detect_project, _update_registry (+20) |
| `ecc-components/skills/videodb/scripts/ws_listener.py` | log, append_event, write_pid, cleanup_pid, is_fatal_error (+7) |
| `ecc-components/skills/skill-comply/scripts/runner.py` | ScenarioRun, run_scenario, _safe_sandbox_dir, _setup_sandbox, _parse_stream_json |
| `ecc-components/skills/skill-comply/scripts/report.py` | generate_report, _overall_compliance, _step_compliance_rate, _steps_to_promote |
| `ecc-components/skills/skill-comply/scripts/scenario_generator.py` | Scenario, generate_scenarios |
| `ecc-components/skills/skill-comply/scripts/parser.py` | ObservationEvent |
| `scripts/docker/gitnexus/gitnexus_to_skill.py` | main |
| `scripts/docker/gitnexus/context_drift_detector.py` | main |
| `ecc-components/skills/skill-comply/scripts/utils.py` | extract_yaml |

## Entry Points

Start here when exploring this area:

- **`test_load_from_empty_dir`** (Function) — `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py:406`
- **`test_load_from_nonexistent_dir`** (Function) — `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py:411`
- **`test_load_annotates_metadata`** (Function) — `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py:416`
- **`test_load_defaults_scope_from_label`** (Function) — `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py:428`
- **`test_load_preserves_explicit_scope`** (Function) — `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py:445`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `ScenarioRun` | Class | `ecc-components/skills/skill-comply/scripts/runner.py` | 20 |
| `ObservationEvent` | Class | `ecc-components/skills/skill-comply/scripts/parser.py` | 12 |
| `Scenario` | Class | `ecc-components/skills/skill-comply/scripts/scenario_generator.py` | 16 |
| `test_load_from_empty_dir` | Function | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 406 |
| `test_load_from_nonexistent_dir` | Function | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 411 |
| `test_load_annotates_metadata` | Function | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 416 |
| `test_load_defaults_scope_from_label` | Function | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 428 |
| `test_load_preserves_explicit_scope` | Function | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 445 |
| `test_load_handles_corrupt_file` | Function | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 456 |
| `test_load_supports_yml_extension` | Function | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 468 |
| `test_load_supports_md_extension` | Function | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 477 |
| `test_load_instincts_from_dir_uses_utf8_encoding` | Function | `ecc-components/skills/continuous-learning-v2/scripts/test_parse_instinct.py` | 486 |
| `log` | Function | `ecc-components/skills/videodb/scripts/ws_listener.py` | 107 |
| `append_event` | Function | `ecc-components/skills/videodb/scripts/ws_listener.py` | 112 |
| `write_pid` | Function | `ecc-components/skills/videodb/scripts/ws_listener.py` | 121 |
| `cleanup_pid` | Function | `ecc-components/skills/videodb/scripts/ws_listener.py` | 127 |
| `is_fatal_error` | Function | `ecc-components/skills/videodb/scripts/ws_listener.py` | 135 |
| `listen_with_retry` | Function | `ecc-components/skills/videodb/scripts/ws_listener.py` | 146 |
| `main_async` | Function | `ecc-components/skills/videodb/scripts/ws_listener.py` | 231 |
| `handle_signal` | Function | `ecc-components/skills/videodb/scripts/ws_listener.py` | 236 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Cmd_promote → Parse_instinct_file` | cross_community | 6 |
| `Main → Parse_instinct_file` | cross_community | 5 |
| `Cmd_export → Parse_instinct_file` | cross_community | 5 |
| `Cmd_evolve → Parse_instinct_file` | cross_community | 5 |
| `Main → Get` | cross_community | 5 |
| `Main → _add_unique` | cross_community | 5 |
| `Main → _classify_naming` | cross_community | 5 |
| `Main → _update_registry` | cross_community | 4 |
| `Main → Get` | cross_community | 4 |
| `Main → _collect_pending_dirs` | cross_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Generator | 13 calls |
| Gitnexus | 2 calls |
| Tests | 1 calls |

## How to Explore

1. `gitnexus_context({name: "test_load_from_empty_dir"})` — see callers and callees
2. `gitnexus_query({query: "scripts"})` — find related execution flows
3. Read key files listed above for implementation details
