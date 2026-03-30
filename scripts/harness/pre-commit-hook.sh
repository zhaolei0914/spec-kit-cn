#!/bin/bash
# ============================================================
# M3+M4: Git Pre-commit Hook (pre-commit-hook.sh)
# 参考: HumanLayer + ECC CI 集成
#
# 安装: cp scripts/harness/pre-commit-hook.sh .git/hooks/pre-commit
# 或者: ln -sf ../../scripts/harness/pre-commit-hook.sh .git/hooks/pre-commit
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_DIR=".specify/harness"
CONFIG_FILE="${HARNESS_DIR}/config.yml"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查 Harness 是否启用
if [ ! -f "$CONFIG_FILE" ]; then
    exit 0
fi

ERRORS=0

# --- 1. 安全扫描 (仅暂存文件) ---

echo -e "${NC}🔍 Harness Pre-commit: 安全扫描...${NC}"

# 获取暂存的文件列表
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -n "$STAGED_FILES" ]; then
    # 检查敏感信息
    SENSITIVE_PATTERNS=(
        '(password|secret|api_key|token)\s*[:=]\s*["\x27][^"\x27]{8,}'
        'BEGIN.*PRIVATE KEY'
        'AKIA[0-9A-Z]{16}'
        'sk-[a-zA-Z0-9]{20,}'
    )
    
    for pattern in "${SENSITIVE_PATTERNS[@]}"; do
        MATCHES=$(echo "$STAGED_FILES" | xargs grep -lE "$pattern" 2>/dev/null | grep -v "\.sh$" | grep -v "config\.yml$" || true)
        if [ -n "$MATCHES" ]; then
            echo -e "${RED}❌ 敏感信息检测: 以下文件可能包含密钥/密码:${NC}"
            echo "$MATCHES" | while read -r f; do
                echo -e "  ${RED}✖ ${f}${NC}"
            done
            ERRORS=$((ERRORS + 1))
        fi
    done
    
    # 检查 .env 文件
    ENV_FILES=$(echo "$STAGED_FILES" | grep -E "^\.env" || true)
    if [ -n "$ENV_FILES" ]; then
        echo -e "${RED}❌ 环境文件不应被提交: ${ENV_FILES}${NC}"
        ERRORS=$((ERRORS + 1))
    fi
    
    # 检查私钥文件
    KEY_FILES=$(echo "$STAGED_FILES" | grep -E "\.(pem|key|p12|pfx)$" || true)
    if [ -n "$KEY_FILES" ]; then
        echo -e "${RED}❌ 私钥文件不应被提交: ${KEY_FILES}${NC}"
        ERRORS=$((ERRORS + 1))
    fi
fi

# --- 2. 制品 Lint (如果 specs 被修改) ---

SPECS_CHANGED=$(echo "$STAGED_FILES" | grep "^specs/" | head -1 || true)
if [ -n "$SPECS_CHANGED" ]; then
    # 提取被修改的需求 ID
    REQ_IDS=$(echo "$STAGED_FILES" | grep "^specs/" | sed 's|specs/\([^/]*\)/.*|\1|' | sort -u)
    
    for req_id in $REQ_IDS; do
        if [ -d "specs/${req_id}" ]; then
            echo -e "${NC}🔍 Harness Pre-commit: Lint ${req_id}...${NC}"
            if ! bash "${SCRIPT_DIR}/lint-specs.sh" "$req_id" 2>/dev/null; then
                ERRORS=$((ERRORS + 1))
            fi
        fi
    done
fi

# --- 结果 ---

if [ $ERRORS -gt 0 ]; then
    echo ""
    echo -e "${RED}❌ Pre-commit 检查失败 (${ERRORS} 个问题)${NC}"
    echo -e "${YELLOW}提示: 使用 git commit --no-verify 跳过检查 (不推荐)${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Pre-commit PASS${NC}"
    exit 0
fi
