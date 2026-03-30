#!/bin/bash
# ============================================================
# M3: 跨制品一致性检查 (consistency-check.sh)
# 参考: OpenAI CI 不变量 + ECC 验证循环
#
# 用法: ./consistency-check.sh <REQ-ID> [specs-dir]
# 输出: Back-Pressure 协议 (成功1行，失败详情)
# ============================================================

set -euo pipefail

REQ_ID="${1:?用法: $0 <REQ-ID> [specs-dir]}"
SPECS_DIR="${2:-specs/${REQ_ID}}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=()
WARNINGS=()
SCORE=100

add_error() {
    ERRORS+=("$1")
    SCORE=$((SCORE - ${2:-10}))
}

add_warning() {
    WARNINGS+=("$1")
    SCORE=$((SCORE - ${2:-3}))
}

# --- 前置检查 ---

if [ ! -d "$SPECS_DIR" ]; then
    echo -e "${RED}❌ Consistency FAIL — 需求目录不存在: ${SPECS_DIR}${NC}"
    exit 1
fi

# 确定可用制品
HAS_REQ=false; HAS_SPEC=false; HAS_DESIGN=false; HAS_TASKS=false; HAS_CASE=false
[ -f "${SPECS_DIR}/requirement.md" ] && HAS_REQ=true
[ -f "${SPECS_DIR}/spec.md" ] && HAS_SPEC=true
[ -f "${SPECS_DIR}/design.md" ] && HAS_DESIGN=true
[ -f "${SPECS_DIR}/tasks.md" ] && HAS_TASKS=true
[ -f "${SPECS_DIR}/case.md" ] && HAS_CASE=true

# --- 一致性检查项 ---

# 1. requirement.md → spec.md: 需求 ID 引用一致性
if $HAS_REQ && $HAS_SPEC; then
    REQ_IDS=$(grep -oE "REQ-[0-9]+" "${SPECS_DIR}/requirement.md" 2>/dev/null | sort -u)
    if [ -n "$REQ_IDS" ]; then
        for rid in $REQ_IDS; do
            if ! grep -q "$rid" "${SPECS_DIR}/spec.md" 2>/dev/null; then
                add_warning "需求 ${rid} 在 requirement.md 中定义但未在 spec.md 中引用"
            fi
        done
    fi
fi

# 2. spec.md → design.md: FR 覆盖检查
if $HAS_SPEC && $HAS_DESIGN; then
    FR_IN_SPEC=$(grep -oE "FR-[0-9]+" "${SPECS_DIR}/spec.md" 2>/dev/null | sort -u)
    FR_IN_DESIGN=$(grep -oE "FR-[0-9]+" "${SPECS_DIR}/design.md" 2>/dev/null | sort -u)
    
    if [ -n "$FR_IN_SPEC" ]; then
        MISSING_IN_DESIGN=$(comm -23 <(echo "$FR_IN_SPEC") <(echo "$FR_IN_DESIGN") 2>/dev/null)
        if [ -n "$MISSING_IN_DESIGN" ]; then
            for fr in $MISSING_IN_DESIGN; do
                add_error "FR 断裂: ${fr} 在 spec.md 中定义但在 design.md 中缺失" 5
            done
        fi
    fi
fi

# 3. design.md → tasks.md: 设计要素覆盖
if $HAS_DESIGN && $HAS_TASKS; then
    # 检查 design.md 中的接口/模块是否在 tasks.md 中有对应任务
    DESIGN_MODULES=$(grep -oE "模块[：:]\s*\S+" "${SPECS_DIR}/design.md" 2>/dev/null | sort -u)
    DESIGN_APIS=$(grep -oE "(GET|POST|PUT|DELETE|PATCH)\s+/\S+" "${SPECS_DIR}/design.md" 2>/dev/null | sort -u)
    
    if [ -n "$DESIGN_APIS" ]; then
        API_COUNT=$(echo "$DESIGN_APIS" | wc -l)
        TASKS_API_REF=$(grep -cE "(GET|POST|PUT|DELETE|PATCH)\s+/" "${SPECS_DIR}/tasks.md" 2>/dev/null || true)
        if [ "$TASKS_API_REF" -eq 0 ] && [ "$API_COUNT" -gt 0 ]; then
            add_warning "design.md 定义了 ${API_COUNT} 个 API 但 tasks.md 中未引用"
        fi
    fi
fi

# 4. spec.md → case.md: 用户故事覆盖
if $HAS_SPEC && $HAS_CASE; then
    US_IN_SPEC=$(grep -oE "US-[0-9]+" "${SPECS_DIR}/spec.md" 2>/dev/null | sort -u)
    US_IN_CASE=$(grep -oE "US-[0-9]+" "${SPECS_DIR}/case.md" 2>/dev/null | sort -u)
    
    if [ -n "$US_IN_SPEC" ]; then
        MISSING_IN_CASE=$(comm -23 <(echo "$US_IN_SPEC") <(echo "$US_IN_CASE") 2>/dev/null)
        if [ -n "$MISSING_IN_CASE" ]; then
            for us in $MISSING_IN_CASE; do
                add_warning "用户故事 ${us} 在 spec.md 中定义但 case.md 中无对应测试用例" 2
            done
        fi
    fi
fi

# 5. tasks.md 内部: 任务依赖关系检查
if $HAS_TASKS; then
    # 检查是否有引用了不存在的任务ID的依赖
    TASK_IDS=$(grep -oE "T[0-9]{3}" "${SPECS_DIR}/tasks.md" 2>/dev/null | sort -u)
    DEPS=$(grep -oE "依赖[：:]\s*T[0-9]{3}" "${SPECS_DIR}/tasks.md" 2>/dev/null | grep -oE "T[0-9]{3}" | sort -u)
    
    if [ -n "$DEPS" ] && [ -n "$TASK_IDS" ]; then
        for dep in $DEPS; do
            if ! echo "$TASK_IDS" | grep -q "^${dep}$"; then
                add_error "任务依赖断裂: 引用了不存在的任务 ${dep}" 5
            fi
        done
    fi
fi

# 6. 术语一致性: 检查关键术语在各制品中是否一致使用
if $HAS_SPEC && $HAS_DESIGN; then
    # 简单检查: 同一概念是否用了不同名称（基于引号中的术语）
    SPEC_TERMS=$(grep -oE "「[^」]+」|"[^"]*"" "${SPECS_DIR}/spec.md" 2>/dev/null | sort -u | head -20)
    if [ -n "$SPEC_TERMS" ]; then
        TERM_COUNT=$(echo "$SPEC_TERMS" | wc -l)
        if [ "$TERM_COUNT" -gt 0 ]; then
            # 仅作为信息提示，不扣分
            :
        fi
    fi
fi

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
    echo -e "${GREEN}✅ Consistency PASS (${GRADE}, ${SCORE}分) — ${REQ_ID}${NC}"
    exit 0
elif [ ${#ERRORS[@]} -eq 0 ]; then
    echo -e "${YELLOW}✅ Consistency PASS (${GRADE}, ${SCORE}分) — ${REQ_ID} (${#WARNINGS[@]} 警告)${NC}"
    for w in "${WARNINGS[@]}"; do
        echo -e "  ${YELLOW}⚠️  ${w}${NC}"
    done
    exit 0
else
    echo -e "${RED}❌ Consistency FAIL (${GRADE}, ${SCORE}分) — ${REQ_ID}${NC}"
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
