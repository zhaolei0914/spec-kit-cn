import os
import sys
import json
import re
import urllib.request
import urllib.parse
from pathlib import Path

# 配置默认 Ollama API
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

def call_ollama(prompt: str) -> str:
    """调用本地 Ollama API 进行推理"""
    data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('response', '').strip()
    except Exception as e:
        print(f"调用 Ollama 失败: {e}")
        return ""

def process_skill_file(skill_file_path: str, facts_file_path: str):
    """读取 SKILL.md，用本地大模型替换占位符，生成最终 Wiki"""
    if not os.path.exists(skill_file_path):
        print(f"找不到 Skill 文件: {skill_file_path}")
        return
        
    facts_content = ""
    if os.path.exists(facts_file_path):
        with open(facts_file_path, 'r', encoding='utf-8') as f:
            facts_content = f.read()
    
    with open(skill_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配模式：{{LLM_XXX}}\n<!-- 填充指导: ... -->
    pattern = r'\{\{LLM_[A-Z_]+\}\}\n<!-- 填充指导: (.*?) -->'
    
    def replacer(match):
        placeholder = match.group(0)
        instruction = match.group(1)
        placeholder_name = re.search(r'\{\{(LLM_[A-Z_]+)\}\}', placeholder).group(1)
        
        print(f"正在生成 {placeholder_name}...")
        
        # 构造给大模型的 Prompt
        prompt = f"""你是一个高级程序员和架构师，正在为一个项目编写 Wiki / 项目上下文文档。
请根据下面提供的项目代码提取的事实数据，完成特定章节的编写。

【任务】
{instruction}

【项目事实数据】
{facts_content}

【要求】
直接输出生成的 Markdown 文本，不要包含任何前缀、解释性的话语或代码块标记，直接给出最终的段落内容。"""

        generated_text = call_ollama(prompt)
        
        if generated_text:
            print(f"✓ {placeholder_name} 生成完成\n")
            return generated_text
        else:
            print(f"✗ {placeholder_name} 生成失败，保留原样\n")
            return placeholder

    new_content = re.sub(pattern, replacer, content)
    
    # 覆盖保存
    with open(skill_file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Wiki 生成完成！已保存到 {skill_file_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="使用本地 Ollama 模型生成项目 Wiki (填充 SKILL.md)")
    parser.add_argument("--skill", default=".specify/skills/project-context/SKILL.md", help="SKILL.md 路径")
    parser.add_argument("--facts", default=".specify/skills/project-context/.context-facts.json", help="facts.json 路径")
    parser.add_argument("--model", default="qwen2.5:3b", help="Ollama 模型名称")
    
    args = parser.parse_args()
    
    OLLAMA_MODEL = args.model
    print(f"🚀 开始使用本地模型 ({OLLAMA_MODEL}) 生成 Wiki 项目上下文...")
    process_skill_file(args.skill, args.facts)
