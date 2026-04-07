#!/usr/bin/env bash
# GitNexus Docker wrapper — 在容器内运行 GitNexus 分析
# 用法:
#   ./gitnexus.sh analyze [project_path] [options]
#   ./gitnexus.sh query <query> [project_path]
#   ./gitnexus.sh impact <symbol> [project_path]
#   ./gitnexus.sh build          # 首次使用前构建镜像
#
# 环境变量:
#   GITNEXUS_IMAGE   镜像名（默认 gitnexus:latest）
#   GITNEXUS_OUTPUT  Skill 输出子目录（默认 .claude/skills/generated）

set -euo pipefail

IMAGE="${GITNEXUS_IMAGE:-gitnexus:latest}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------- 辅助函数 ----------

ensure_image() {
    if ! docker image inspect "$IMAGE" &>/dev/null; then
        echo "[gitnexus] 镜像 $IMAGE 不存在，开始构建..."
        docker build -t "$IMAGE" "$SCRIPT_DIR"
    fi
}

usage() {
    cat <<EOF
GitNexus Docker Wrapper

用法:
  $(basename "$0") build                         构建/重建 Docker 镜像
  $(basename "$0") analyze [path] [--skills]     分析项目（默认当前目录）
  $(basename "$0") query <query> [path]          在知识图谱中搜索
  $(basename "$0") impact <symbol> [path]        影响分析
  $(basename "$0") <any gitnexus args>           透传任意参数

选项:
  --skills    分析时同时生成 Skill 文件（推荐）

环境变量:
  GITNEXUS_IMAGE    Docker 镜像名 (默认: gitnexus:latest)
EOF
    exit 0
}

# ---------- 子命令 ----------

cmd_build() {
    echo "[gitnexus] 构建镜像 $IMAGE ..."
    docker build -t "$IMAGE" "$SCRIPT_DIR"
    echo "[gitnexus] 构建完成"
}

cmd_run() {
    ensure_image

    # 确定项目路径：从参数中找到一个存在的目录路径，或用当前目录
    local project_path=""
    local args=()

    for arg in "$@"; do
        if [[ -z "$project_path" && -d "$arg" ]]; then
            project_path="$(cd "$arg" && pwd)"
        else
            args+=("$arg")
        fi
    done

    if [[ -z "$project_path" ]]; then
        project_path="$(pwd)"
    fi

    # 运行容器：挂载项目到 /repo
    docker run --rm \
        -v "$project_path":/repo \
        "$IMAGE" \
        "${args[@]}" /repo
}

# ---------- 入口 ----------

if [[ $# -eq 0 ]] || [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    usage
fi

case "${1:-}" in
    build)
        cmd_build
        ;;
    *)
        cmd_run "$@"
        ;;
esac
