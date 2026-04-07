FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# 安装基础工具
RUN apt-get update && \
    apt-get install -y ca-certificates curl git xz-utils python3 make g++ && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 安装 Node.js 20 LTS
RUN curl -fsSL https://npmmirror.com/mirrors/node/v20.20.1/node-v20.20.1-linux-x64.tar.xz | \
    tar -xJ -C /usr/local --strip-components=1 && \
    npm config set registry https://registry.npmmirror.com

# 从 GitHub 源码构建 GitNexus（TypeScript monorepo）
RUN git clone --depth 1 https://github.com/abhigyanpatwari/GitNexus.git /opt/gitnexus && \
    cd /opt/gitnexus && \
    # 1. 根目录安装（跳过 postinstall 避免 onnxruntime 下载失败）
    npm install --ignore-scripts && \
    # 2. rebuild 必要的原生模块
    npm rebuild @ladybugdb/core 2>/dev/null || true && \
    # 3. 编译 gitnexus-shared
    cd /opt/gitnexus/gitnexus-shared && npm install --ignore-scripts 2>/dev/null && npx tsc 2>/dev/null || true && \
    # 4. 编译 gitnexus CLI（安装子目录依赖以获取 @types/node）
    cd /opt/gitnexus/gitnexus && npm install --ignore-scripts 2>/dev/null && \
    npm rebuild @ladybugdb/core 2>/dev/null || true && \
    npx tsc && \
    # 5. 创建全局入口
    chmod +x dist/cli/index.js && \
    ln -sf /opt/gitnexus/gitnexus/dist/cli/index.js /usr/local/bin/gitnexus && \
    # 6. 清理
    rm -rf /opt/gitnexus/.git

WORKDIR /repo

ENTRYPOINT ["gitnexus"]
CMD ["--help"]
