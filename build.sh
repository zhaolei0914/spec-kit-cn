#!/usr/bin/env bash
set -euo pipefail

# build.sh - 本地构建 Spec Kit 模板包
#
# 用法:
#   ./build.sh                    # 构建所有 agent 和脚本类型
#   ./build.sh windsurf           # 只构建 windsurf agent
#   ./build.sh windsurf sh        # 只构建 windsurf agent 的 sh 版本
#   AGENTS=claude,copilot ./build.sh  # 通过环境变量指定多个 agent
#
# 输出目录: .genreleases/
#
# 构建完成后可以用 specify-cn init --local-package .genreleases/xxx.zip 来使用本地包

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 默认版本号（本地构建用）
VERSION="${VERSION:-v0.0.0-local}"

# 处理命令行参数
if [[ $# -ge 1 ]]; then
    export AGENTS="$1"
fi

if [[ $# -ge 2 ]]; then
    export SCRIPTS="$2"
fi

# 清理旧的构建目录，确保每次构建都是最新的
if [[ -d ".genreleases" ]]; then
    echo "清理旧的构建目录 .genreleases/ ..."
    rm -rf .genreleases
fi

echo "============================================"
echo "  Spec Kit 本地构建"
echo "============================================"
echo ""
echo "版本: $VERSION"
[[ -n "${AGENTS:-}" ]] && echo "Agents: $AGENTS"
[[ -n "${SCRIPTS:-}" ]] && echo "Scripts: $SCRIPTS"
echo ""

# 打包前同步 templates/scripts -> scripts (打包脚本从 scripts/ 读取)
if [[ -d "templates/scripts" ]]; then
    mkdir -p scripts
    cp -a templates/scripts/. scripts/
    echo "已同步 templates/scripts -> scripts/"
fi

# 调用实际的构建脚本
if [[ -f ".github/workflows/scripts/create-release-packages.sh" ]]; then
    bash .github/workflows/scripts/create-release-packages.sh "$VERSION"

    # 把移动到根目录的文件移回 .genreleases/
    for f in spec-kit-template-*.zip; do
        [[ -f "$f" ]] && mv "$f" .genreleases/ 2>/dev/null || true
    done
else
    echo "错误: 找不到构建脚本 .github/workflows/scripts/create-release-packages.sh"
    exit 1
fi

echo ""
echo "============================================"
echo "  构建完成!"
echo "============================================"
echo ""
echo "输出目录: .genreleases/"
echo ""
echo "可用的包:"
ls -1 .genreleases/*.zip 2>/dev/null || ls -1 *.zip 2>/dev/null | head -20
echo ""
echo "使用方法:"
echo "  specify-cn init <项目名> --local-package .genreleases/<包名>.zip"
echo "  specify-cn init --here --local-package .genreleases/<包名>.zip"
