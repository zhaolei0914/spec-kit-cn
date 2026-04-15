#!/bin/bash
# ============================================================
# M6: 创建检查点 (snapshot.sh)
# 参考: FSPEC Checkpoint + GSD Worktree
#
# 用法: ./snapshot.sh <REQ-ID> [description]
# ============================================================

set -euo pipefail

REQ_ID="${1:?用法: $0 <REQ-ID> [description]}"
DESC="${2:-checkpoint}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
TAG="harness/ckpt/${REQ_ID}/${TIMESTAMP}_${DESC}"
SNAPSHOT_INDEX=".specify/harness/snapshots/snapshot-index.md"

# 创建 git tag
git tag "$TAG" -m "Harness checkpoint: ${REQ_ID} - ${DESC}"

# 更新快照索引
if [ -f "$SNAPSHOT_INDEX" ]; then
    echo "| ${TIMESTAMP} | ${REQ_ID} | ${DESC} | \`${TAG}\` |" >> "$SNAPSHOT_INDEX"
fi

echo "✅ Checkpoint: ${TAG}"
