#!/bin/bash
# ============================================================
# M4: 安全扫描 (security-scan.sh)
# 参考: ECC AgentShield (红蓝对抗 + A-F 评级) + GSD deny list
#
# 用法: ./security-scan.sh [scan-dir] [--config config.yml]
# 输出: Back-Pressure 协议 (成功1行，失败详情)
# ============================================================

set -euo pipefail

SCAN_DIR="${1:-.}"
CONFIG_FILE=".specify/harness/config.yml"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

CRITICAL=()
HIGH=()
MEDIUM=()
LOW=()
SCORE=100

# --- 敏感模式 (从设计方案中提取) ---

SENSITIVE_PATTERNS=(
    '(password|secret|api_key|token)\s*[:=]\s*["\x27][^"\x27]{8,}'
    'BEGIN.*PRIVATE KEY'
    'AKIA[0-9A-Z]{16}'
    'sk-[a-zA-Z0-9]{20,}'
    'ghp_[a-zA-Z0-9]{36}'
    'xoxb-[0-9]+'
)

DANGEROUS_COMMANDS=(
    'rm -rf /'
    'DROP TABLE'
    'DROP DATABASE'
    'TRUNCATE TABLE'
    'DELETE FROM.*WHERE 1'
    ':(){:|:&};:'
)

# --- 扫描排除目录 ---

EXCLUDE_DIRS=(
    ".git"
    "node_modules"
    "__pycache__"
    ".venv"
    "venv"
    ".specify/harness"
)

build_exclude_args() {
    local args=""
    for dir in "${EXCLUDE_DIRS[@]}"; do
        args="${args} --exclude-dir=${dir}"
    done
    echo "$args"
}

GREP_EXCLUDE=$(build_exclude_args)

# --- 扫描函数 ---

scan_sensitive_patterns() {
    for pattern in "${SENSITIVE_PATTERNS[@]}"; do
        local matches
        matches=$(grep -rnE ${GREP_EXCLUDE} "$pattern" "$SCAN_DIR" 2>/dev/null | grep -v "\.sh:" | grep -v "config\.yml:" | head -20 || true)
        if [ -n "$matches" ]; then
            while IFS= read -r match; do
                CRITICAL+=("敏感信息泄露: ${match}")
                SCORE=$((SCORE - 20))
            done <<< "$matches"
        fi
    done
}

scan_dangerous_commands() {
    for cmd in "${DANGEROUS_COMMANDS[@]}"; do
        local matches
        matches=$(grep -rnF ${GREP_EXCLUDE} "$cmd" "$SCAN_DIR" 2>/dev/null | head -10 || true)
        if [ -n "$matches" ]; then
            while IFS= read -r match; do
                HIGH+=("危险命令: ${match}")
                SCORE=$((SCORE - 15))
            done <<< "$matches"
        fi
    done
}

scan_env_files() {
    # 检查 .env 文件是否被 gitignore
    local env_files
    env_files=$(find "$SCAN_DIR" -name ".env" -o -name ".env.*" 2>/dev/null | head -10)
    if [ -n "$env_files" ]; then
        while IFS= read -r ef; do
            if git ls-files --error-unmatch "$ef" >/dev/null 2>&1; then
                CRITICAL+=("环境文件已被 Git 追踪: ${ef}")
                SCORE=$((SCORE - 20))
            else
                LOW+=("环境文件存在 (已被 gitignore): ${ef}")
            fi
        done <<< "$env_files"
    fi
}

scan_private_keys() {
    local key_files
    key_files=$(find "$SCAN_DIR" \( -name "*.pem" -o -name "*.key" -o -name "*.p12" -o -name "*.pfx" \) 2>/dev/null | head -10)
    if [ -n "$key_files" ]; then
        while IFS= read -r kf; do
            if git ls-files --error-unmatch "$kf" >/dev/null 2>&1; then
                CRITICAL+=("私钥文件已被 Git 追踪: ${kf}")
                SCORE=$((SCORE - 20))
            else
                MEDIUM+=("私钥文件存在 (已被 gitignore): ${kf}")
                SCORE=$((SCORE - 3))
            fi
        done <<< "$key_files"
    fi
}

scan_hardcoded_urls() {
    local matches
    matches=$(grep -rnE ${GREP_EXCLUDE} 'https?://[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' "$SCAN_DIR" 2>/dev/null | grep -v "127\.0\.0\.1" | grep -v "0\.0\.0\.0" | head -10 || true)
    if [ -n "$matches" ]; then
        while IFS= read -r match; do
            MEDIUM+=("硬编码 IP 地址: ${match}")
            SCORE=$((SCORE - 5))
        done <<< "$matches"
    fi
}

# --- 执行扫描 ---

scan_sensitive_patterns
scan_dangerous_commands
scan_env_files
scan_private_keys
scan_hardcoded_urls

# --- 评级 ---

if [ $SCORE -lt 0 ]; then SCORE=0; fi

if [ $SCORE -ge 90 ]; then GRADE="A"
elif [ $SCORE -ge 80 ]; then GRADE="B"
elif [ $SCORE -ge 70 ]; then GRADE="C"
elif [ $SCORE -ge 60 ]; then GRADE="D"
else GRADE="F"
fi

TOTAL_ISSUES=$(( ${#CRITICAL[@]} + ${#HIGH[@]} + ${#MEDIUM[@]} + ${#LOW[@]} ))

# --- 输出 (Back-Pressure 协议) ---

if [ $TOTAL_ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ Security PASS (${GRADE}, ${SCORE}分)${NC}"
    exit 0
elif [ ${#CRITICAL[@]} -eq 0 ] && [ ${#HIGH[@]} -eq 0 ]; then
    echo -e "${YELLOW}✅ Security PASS (${GRADE}, ${SCORE}分) — ${TOTAL_ISSUES} 低风险问题${NC}"
    for m in "${MEDIUM[@]}"; do
        echo -e "  ${YELLOW}⚠️  ${m}${NC}"
    done
    for l in "${LOW[@]}"; do
        echo -e "  ${NC}ℹ️  ${l}${NC}"
    done
    exit 0
else
    echo -e "${RED}❌ Security FAIL (${GRADE}, ${SCORE}分) — ${#CRITICAL[@]} 严重 / ${#HIGH[@]} 高危${NC}"
    echo ""
    if [ ${#CRITICAL[@]} -gt 0 ]; then
        echo "🔴 严重 (${#CRITICAL[@]}):"
        for c in "${CRITICAL[@]}"; do
            echo -e "  ${RED}✖ ${c}${NC}"
        done
    fi
    if [ ${#HIGH[@]} -gt 0 ]; then
        echo ""
        echo "🟠 高危 (${#HIGH[@]}):"
        for h in "${HIGH[@]}"; do
            echo -e "  ${RED}✖ ${h}${NC}"
        done
    fi
    if [ ${#MEDIUM[@]} -gt 0 ]; then
        echo ""
        echo "🟡 中危 (${#MEDIUM[@]}):"
        for m in "${MEDIUM[@]}"; do
            echo -e "  ${YELLOW}⚠️  ${m}${NC}"
        done
    fi
    exit 1
fi
