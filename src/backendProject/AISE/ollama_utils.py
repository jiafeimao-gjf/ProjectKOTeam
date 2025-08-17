# ollama_utils.py
import random

import ollama
import logging

logger = logging.getLogger(__name__)


def ollama_sync(prompt: str, model: str = "gemma3n:e4b") -> str:
    """
    同步调用本地 Ollama 模型，返回完整响应文本
    适用于 FSM 内部逻辑处理
    """
    logger.info(f"[Ollama] 同步调用模型: {model}")
    logger.info(f"[Ollama] Prompt: {prompt[:100]}...")

    try:
        # 流式实现
        answer = ""
        # 打开一个文件
        random_int = random.randint(0, 10000000)
        with open(f"llm_history/ollama_{random_int}.md", "a+", encoding="utf-8") as f:
            for chunk in ollama.generate(model=model, prompt=prompt, stream=True):
                text = chunk.get("response", "")
                logger.info(text)
                answer += text
                f.write(text)
        # response = ollama.generate(
        #     model=model,
        #     prompt=prompt,
        #     stream=True
        # )
        # answer = response.get("response", "").strip()
        # if not answer:
        #     logger.error("[Ollama] 返回内容为空")
        #     return "错误：模型返回为空。"
        logger.info(f"[Ollama] 成功生成响应，长度: {len(answer)}")
        return answer
    except Exception as e:
        logger.error(f"[Ollama] 调用失败: {e}")
        return f"错误：调用本地模型失败 - {str(e)}"
