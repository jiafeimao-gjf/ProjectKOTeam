# ollama_integration.py - 大模型集成模块
import requests
import json
from typing import Generator, Dict, Any


def ollama_stream(prompt: str, target_model: str = "llama3", subfix: str = "mcp") -> Generator[str, None, None]:
    """
    流式调用Ollama模型

    :param prompt: 输入的描述
    :param target_model: 输入模型
    :param subfix: 保存的后缀
    :return: 流式输出生成器
    """
    try:
        # Ollama API端点
        url = "http://localhost:11434/api/generate"

        payload = {
            "model": target_model,
            "prompt": prompt,
            "stream": True
        }

        response = requests.post(
            url,
            json=payload,
            stream=True,
            timeout=30
        )

        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if 'response' in data:
                            yield data['response']
                    except json.JSONDecodeError:
                        continue
        else:
            yield f"错误: HTTP {response.status_code}"

    except requests.exceptions.RequestException as e:
        yield f"请求错误: {str(e)}"
    except Exception as e:
        yield f"未知错误: {str(e)}"


def ollama_generate(prompt: str, target_model: str = "llama3") -> str:
    """
    非流式调用Ollama模型

    :param prompt: 输入的描述
    :param target_model: 输入模型
    :return: 生成结果
    """
    try:
        url = "http://localhost:11434/api/generate"

        payload = {
            "model": target_model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            return data.get('response', '')
        else:
            return f"错误: HTTP {response.status_code}"

    except Exception as e:
        return f"错误: {str(e)}"


# 使用示例
def demo_ollama_integration():
    """Ollama集成使用示例"""

    # 流式调用示例
    print("=== 流式调用示例 ===")
    prompt = "请写一个Python函数来读取文件并返回内容"
    for chunk in ollama_stream(prompt, target_model="llama3"):
        print(chunk, end='', flush=True)

    print("\n\n=== 非流式调用示例 ===")
    result = ollama_generate(prompt, target_model="llama3")
    print(result)


if __name__ == "__main__":
    demo_ollama_integration()