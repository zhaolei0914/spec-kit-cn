#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitNexus Context Fetcher - 客户端脚本

从 GitNexus MCP 服务获取项目上下文文档，自动保存到 .specify/ 目录

用法:
    python fetch_context.py <repo_name> [--server <url>]

示例:
    python fetch_context.py spec-kit-cn
    python fetch_context.py markitdown --server http://remote:8001

LLM 使用:
    只需调用此脚本并传递仓库名称，所有文档会自动下载到 .specify/ 目录
"""

import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def get_context_files(server_url: str, repo_name: str) -> dict:
    """获取项目上下文文件（使用简单的 HTTP GET）"""
    # 使用简单 API 端点
    url = f"{server_url}/api/context?repo={repo_name}"
    
    try:
        req = Request(url, method='GET')
        with urlopen(req, timeout=120) as response:
            files_data = json.loads(response.read().decode('utf-8'))
            return files_data
    
    except HTTPError as e:
        raise Exception(f"HTTP Error {e.code}: {e.reason}")
    except URLError as e:
        raise Exception(f"Connection Error: {e.reason}")
    except Exception as e:
        raise Exception(f"Request failed: {str(e)}")


def fetch_and_save_context(repo_name: str, server_url: str, target_dir: str = ".specify"):
    """获取并保存项目上下文"""
    
    print(f"📦 Fetching context for: {repo_name}")
    print(f"🌐 Server: {server_url}")
    print(f"📁 Target: {target_dir}/\n")
    
    # 1. 调用 get_context_files API
    print("⏳ Fetching files from server...")
    try:
        files_data = get_context_files(
            server_url=server_url,
            repo_name=repo_name
        )
    except Exception as e:
        print(f"❌ Failed to fetch files: {e}")
        return False
    
    # 2. 验证返回的数据格式
    if not isinstance(files_data, dict):
        print(f"❌ Unexpected response format: {type(files_data)}")
        return False
    
    if not files_data:
        print(f"⚠️  No files found for repository: {repo_name}")
        return False
    
    # 3. 写入文件
    print(f"💾 Writing {len(files_data)} files...\n")
    
    success = 0
    failed = 0
    
    for rel_path, content in files_data.items():
        full_path = os.path.join(target_dir, rel_path)
        
        try:
            # 创建目录
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # 写入文件
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ {full_path}")
            success += 1
            
        except Exception as e:
            print(f"❌ {full_path}: {e}")
            failed += 1
    
    print(f"\n📊 Complete! Success: {success}, Failed: {failed}")
    print(f"✅ Context saved to {target_dir}/")
    
    return failed == 0


def main():
    parser = argparse.ArgumentParser(
        description="GitNexus Context Fetcher - 获取项目上下文文档",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python fetch_context.py spec-kit-cn
  python fetch_context.py markitdown --server http://192.168.1.100:8001

LLM 使用:
  只需调用此脚本并传递仓库名称，所有文档会自动下载到 .specify/ 目录
        """
    )
    
    parser.add_argument(
        "repo_name",
        help="仓库名称（如 spec-kit-cn, markitdown）"
    )
    
    parser.add_argument(
        "--server",
        default="http://localhost:8001",
        help="GitNexus API 服务器地址（默认: http://localhost:8001）"
    )
    
    parser.add_argument(
        "--target",
        default=".specify",
        help="目标目录（默认: .specify）"
    )
    
    args = parser.parse_args()
    
    # 执行获取
    success = fetch_and_save_context(
        repo_name=args.repo_name,
        server_url=args.server,
        target_dir=args.target
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
