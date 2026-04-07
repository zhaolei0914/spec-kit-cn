---
name: validator
description: "Skill for the Validator area of repo. 28 symbols across 3 files."
---

# Validator

28 symbols | 3 files | Cohesion: 86%

## When to Use

- Working with code in `scripts/`
- Understanding how add_error, add_warning, add_info work
- Modifying validator-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `scripts/python/validator/skill_validator.py` | ValidationIssue, ValidationResult, add_error, add_warning, add_info (+12) |
| `scripts/python/validator/conflict_detector.py` | ConflictItem, ConflictReport, detect_conflicts, _load_skills, _parse_skill (+5) |
| `scripts/python/skill_main.py` | validate_skills |

## Entry Points

Start here when exploring this area:

- **`add_error`** (Function) — `scripts/python/validator/skill_validator.py:40`
- **`add_warning`** (Function) — `scripts/python/validator/skill_validator.py:50`
- **`add_info`** (Function) — `scripts/python/validator/skill_validator.py:59`
- **`merge`** (Function) — `scripts/python/validator/skill_validator.py:75`
- **`validate_skill_file`** (Function) — `scripts/python/validator/skill_validator.py:134`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `ValidationIssue` | Class | `scripts/python/validator/skill_validator.py` | 23 |
| `ValidationResult` | Class | `scripts/python/validator/skill_validator.py` | 33 |
| `ConflictItem` | Class | `scripts/python/validator/conflict_detector.py` | 15 |
| `ConflictReport` | Class | `scripts/python/validator/conflict_detector.py` | 27 |
| `SkillValidator` | Class | `scripts/python/validator/skill_validator.py` | 84 |
| `ConflictDetector` | Class | `scripts/python/validator/conflict_detector.py` | 45 |
| `add_error` | Function | `scripts/python/validator/skill_validator.py` | 40 |
| `add_warning` | Function | `scripts/python/validator/skill_validator.py` | 50 |
| `add_info` | Function | `scripts/python/validator/skill_validator.py` | 59 |
| `merge` | Function | `scripts/python/validator/skill_validator.py` | 75 |
| `validate_skill_file` | Function | `scripts/python/validator/skill_validator.py` | 134 |
| `validate_skill_directory` | Function | `scripts/python/validator/skill_validator.py` | 162 |
| `detect_conflicts` | Function | `scripts/python/validator/conflict_detector.py` | 51 |
| `validate_skills` | Function | `scripts/python/skill_main.py` | 189 |
| `load_knowledge_base` | Function | `scripts/python/validator/skill_validator.py` | 97 |
| `generate_report` | Function | `scripts/python/validator/skill_validator.py` | 408 |
| `_validate_yaml_header` | Function | `scripts/python/validator/skill_validator.py` | 195 |
| `_validate_code_references` | Function | `scripts/python/validator/skill_validator.py` | 264 |
| `_validate_file_references` | Function | `scripts/python/validator/skill_validator.py` | 295 |
| `_validate_confidence_markers` | Function | `scripts/python/validator/skill_validator.py` | 327 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Validate_skills → ValidationIssue` | cross_community | 5 |
| `Detect_conflicts → Get` | cross_community | 4 |
| `Validate_skills → ValidationResult` | cross_community | 4 |
| `Validate_skill_file → ValidationIssue` | intra_community | 4 |
| `Detect_conflicts → ConflictItem` | intra_community | 3 |
| `Detect_conflicts → _find_contradicting_rules` | intra_community | 3 |
| `Validate_skills → Get` | cross_community | 3 |
| `Validate_skills → Merge` | cross_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Generator | 5 calls |

## How to Explore

1. `gitnexus_context({name: "add_error"})` — see callers and callees
2. `gitnexus_query({query: "validator"})` — find related execution flows
3. Read key files listed above for implementation details
