#!/bin/bash
# ============================================================
# M3: 制品结构 Linter (lint-specs.sh)
# 参考: ECC Harness Audit + OpenAI CI 不变量 + HumanLayer Back-Pressure
#
# 用法: ./lint-specs.sh <REQ-ID> [specs-dir]
# 输出: Back-Pressure 协议 (成功1行，失败详情)
# ============================================================

set -euo pipefail

REQ_ID="${1:?用法: $0 <REQ-ID> [specs-dir]}"
SPECS_DIR="${2:-specs/${REQ_ID}}"
HARNESS_DIR=".specify/harness"
CONFIG_FILE="${HARNESS_DIR}/config.yml"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=()
WARNINGS=()
SCORE=100

# --- 辅助函数 ---

add_error() {
    ERRORS+=("$1")
    SCORE=$((SCORE - ${2:-10}))
}

add_warning() {
    WARNINGS+=("$1")
    SCORE=$((SCORE - ${2:-3}))
}

check_file_exists() {
    local file="$1"
    local name="$2"
    local penalty="${3:-10}"
    if [ ! -f "${SPECS_DIR}/${file}" ]; then
        add_error "缺少必需文件: ${name} (${file})" "$penalty"
        return 1
    fi
    return 0
}

check_section_exists() {
    local file="$1"
    local section_pattern="$2"
    local section_name="$3"
    local penalty="${4:-5}"
    if ! grep -qiE "$section_pattern" "${SPECS_DIR}/${file}" 2>/dev/null; then
        add_error "文件 ${file} 缺少必需章节: ${section_name}" "$penalty"
        return 1
    fi
    return 0
}

# --- 检查项 ---

# 1. 需求目录存在性
if [ ! -d "$SPECS_DIR" ]; then
    echo -e "${RED}❌ Lint FAIL (F) — 需求目录不存在: ${SPECS_DIR}${NC}"
    exit 1
fi

# 2. 必需文件检查 (根据当前阶段动态判断)
check_file_exists "requirement.md" "需求分析文档"

# 可选文件 (存在时检查结构)
HAS_SPEC=false
HAS_DESIGN=false
HAS_TASKS=false
HAS_CASE=false

[ -f "${SPECS_DIR}/spec.md" ] && HAS_SPEC=true
[ -f "${SPECS_DIR}/design.md" ] && HAS_DESIGN=true
[ -f "${SPECS_DIR}/tasks.md" ] && HAS_TASKS=true
[ -f "${SPECS_DIR}/case.md" ] && HAS_CASE=true

# 3. requirement.md 结构检查
if [ -f "${SPECS_DIR}/requirement.md" ]; then
    check_section_exists "requirement.md" "^#+.*需求|^#+.*背景|^#+.*目标" "需求/背景/目标章节"
fi

# 4. spec.md 结构检查
if $HAS_SPEC; then
    check_section_exists "spec.md" "^#+.*功能|^#+.*FR|^#+.*用户故事" "功能需求/用户故事章节"
    check_section_exists "spec.md" "^#+.*非功能|^#+.*NFR|^#+.*约束" "非功能需求/约束章节"
    check_section_exists "spec.md" "^#+.*边界|^#+.*异常|^#+.*错误" "边界条件/异常处理章节" 3
fi

# 5. design.md 结构检查
if $HAS_DESIGN; then
    check_section_exists "design.md" "^#+.*架构|^#+.*模块|^#+.*组件" "架构/模块设计章节"
    check_section_exists "design.md" "^#+.*接口|^#+.*API|^#+.*数据" "接口/数据设计章节"
fi

# 6. tasks.md 结构检查
if $HAS_TASKS; then
    # 检查任务编号格式
    if ! grep -qE "T[0-9]{3}" "${SPECS_DIR}/tasks.md" 2>/dev/null; then
        add_warning "tasks.md 中未发现标准任务编号格式 (TXXX)"
    fi
fi

# 7. FR 追溯检查 (spec → design → tasks)
if $HAS_SPEC && $HAS_DESIGN; then
    # 提取 spec.md 中的 FR 编号
    FR_LIST=$(grep -oE "FR-[0-9]+" "${SPECS_DIR}/spec.md" 2>/dev/null | sort -u)
    if [ -n "$FR_LIST" ]; then
        for fr in $FR_LIST; do
            if ! grep -q "$fr" "${SPECS_DIR}/design.md" 2>/dev/null; then
                add_warning "FR 追溯断裂: ${fr} 在 spec.md 中定义但未在 design.md 中引用" 2
            fi
        done
    fi
fi

# 8. 空文件检查
for f in requirement.md spec.md design.md tasks.md case.md; do
    if [ -f "${SPECS_DIR}/${f}" ] && [ ! -s "${SPECS_DIR}/${f}" ]; then
        add_error "文件为空: ${f}" 15
    fi
done

# --- 评级 ---

if [ $SCORE -lt 0 ]; then SCORE=0; fi

if [ $SCORE -ge 90 ]; then GRADE="A"
elif [ $SCORE -ge 80 ]; then GRADE="B"
elif [ $SCORE -ge 70 ]; then GRADE="C"
elif [ $SCORE -ge 60 ]; then GRADE="D"
else GRADE="F"
fi

# --- 输出 (Back-Pressure 协议) ---

if [ ${#ERRORS[@]} -eq 0 ] && [ ${#WARNINGS[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ Lint PASS (${GRADE}, ${SCORE}分) — ${REQ_ID}${NC}"
    exit 0
elif [ ${#ERRORS[@]} -eq 0 ]; then
    echo -e "${YELLOW}✅ Lint PASS (${GRADE}, ${SCORE}分) — ${REQ_ID} (${#WARNINGS[@]} 警告)${NC}"
    for w in "${WARNINGS[@]}"; do
        echo -e "  ${YELLOW}⚠️  ${w}${NC}"
    done
    exit 0
else
    echo -e "${RED}❌ Lint FAIL (${GRADE}, ${SCORE}分) — ${REQ_ID}${NC}"
    echo ""
    echo "错误 (${#ERRORS[@]}):"
    for e in "${ERRORS[@]}"; do
        echo -e "  ${RED}✖ ${e}${NC}"
    done
    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo ""
        echo "警告 (${#WARNINGS[@]}):"
        for w in "${WARNINGS[@]}"; do
            echo -e "  ${YELLOW}⚠️  ${w}${NC}"
        done
    fi
    exit 1
fi
