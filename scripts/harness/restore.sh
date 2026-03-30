#!/bin/bash
# ============================================================
# M6: 从检查点恢复 (restore.sh)
# 参考: FSPEC Checkpoint restore
#
# 用法: ./restore.sh <REQ-ID> <tag-name>
#        ./restore.sh <REQ-ID> --latest
# ============================================================

set -euo pipefail

REQ_ID="${1:?用法: $0 <REQ-ID> <tag-name|--latest>}"
TAG_ARG="${2:?请指定 tag 名称或 --latest}"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# 解析 tag
if [ "$TAG_ARG" = "--latest" ]; then
    TAG=$(git tag -l "harness/ckpt/${REQ_ID}/*" --sort=-creatordate | head -1)
    if [ -z "$TAG" ]; then
        echo -e "${RED}❌ 未找到 ${REQ_ID} 的检查点${NC}"
        exit 1
    fi
else
    TAG="$TAG_ARG"
    if ! git rev-parse "$TAG" >/dev/null 2>&1; then
        echo -e "${RED}❌ 检查点不存在: ${TAG}${NC}"
        exit 1
    fi
fi

# 安全: 先 stash 当前修改
STASH_MSG="pre-restore-$(date +%s)"
git stash push -m "$STASH_MSG" 2>/dev/null || true

# 从检查点恢复 specs 目录
git checkout "$TAG" -- "specs/${REQ_ID}/" 2>/dev/null || {
    echo -e "${RED}❌ 恢复失败: 检查点中不包含 specs/${REQ_ID}/${NC}"
    git stash pop 2>/dev/null || true
    exit 1
}

echo -e "${GREEN}✅ Restored: ${TAG}${NC}"
echo "ℹ️  原始修改已 stash: ${STASH_MSG}"
