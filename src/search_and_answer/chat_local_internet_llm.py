#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
chat_local_internet_llm.py

一个基于 Python 的问答工具：
1. 先用 Bing 搜索获取网页链接
2. 抓取网页内容
3. 用 OpenAI GPT（或本地模型）生成答案

依赖：
  pip install requests beautifulsoup4 openai python-dotenv

使用方法：
  python chat_local_internet_llm.py

"""

import os
import random
import sys
import json
import time
import textwrap
import logging
from dataclasses import dataclass
from typing import List, Optional

import ollama
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# 如果你想改用本地模型，可自行 import 相关库
# from transformers import pipeline

# ---------------------------------------------
# 配置与日志
# ---------------------------------------------
load_dotenv()  # 读取 .env 文件

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BING_API_KEY = os.getenv("BING_API_KEY")
GOOGLE_API_KEY = ""  # os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = ""
# if not OPENAI_API_KEY:
#     print("[ERROR] 没有找到 OPENAI_API_KEY，请在 .env 或环境变量中配置")
#     sys.exit(1)
#
# if not BING_API_KEY:
#     print("[ERROR] 没有找到 BING_API_KEY，请在 .env 或环境变量中配置")
#     sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)


# ---------------------------------------------
# Bing 搜索
# ---------------------------------------------
@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


class BingSearch:
    """
    简单封装 Bing Web Search API
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://api.bing.microsoft.com/v7.0/search"

    """
    <script async src="https://cse.google.com/cse.js?cx=851f57f1a937f44e0">
    </script>
    <div class="gcse-search"></div>
    """

    def search_google(self, query):
        url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CX}&q={query}"
        response = requests.get(url)
        results = response.json().get("items", [])
        return results

    def query(self, q: str, top: int = 5) -> List[SearchResult]:
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {"q": q, "textDecorations": True, "textFormat": "HTML", "count": top}
        try:
            response = requests.get(self.endpoint, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            results = []
            for b in data.get("webPages", {}).get("value", []):
                results.append(
                    SearchResult(
                        title=b.get("name", ""),
                        url=b.get("url", ""),
                        snippet=textwrap.shorten(textwrap.dedent(b.get("snippet", "")), width=200),
                    )
                )
            return results
        except Exception as e:
            log.error(f"搜索失败: {e}")
            return []


# ---------------------------------------------
# 网页抓取与正文提取
# ---------------------------------------------
class WebScraper:
    """
    只抓取正文段落，使用 BeautifulSoup + 简单逻辑
    """

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    @staticmethod
    def _is_valid_tag(tag):
        return tag.name in ["p", "div", "span", "li"]

    def _extract_text(self, soup: BeautifulSoup) -> str:
        """
        简单策略：取页面中 <p>、<div>、<span>、<li> 的文本，按出现顺序拼接
        """
        texts = []
        for tag in soup.find_all(self._is_valid_tag):
            txt = tag.get_text(separator=" ", strip=True)
            if txt:
                texts.append(txt)
        return "\n".join(texts)

    def fetch(self, url: str) -> Optional[str]:
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/121.0.0.0 Safari/537.36"
                )
            }
            resp = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # 去掉脚本、样式等
            for script in soup(["script", "style", "noscript"]):
                script.decompose()

            text = self._extract_text(soup)
            # 简单去除过多空行
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            cleaned = "\n".join(lines)
            with open(f"{url.replace('/', '-')}.md", "w", encoding="utf-8") as f:
                f.write(cleaned)
            return cleaned
        except Exception as e:
            log.warning(f"抓取 {url} 失败: {e}")
            return None


# ---------------------------------------------
# 大模型问答
# ---------------------------------------------
def chat_by_prompt(question, prompt, model):
    length = 0
    answer = ""
    with open(f"{question.replace('/', '-')}.md", "w", encoding="utf-8") as f:
        f.write(f"# 问题：{prompt}\n")
        f.write(f"回答如下：\n")
        for chunk in ollama.generate(model=model, prompt=prompt,
                                     stream=True):
            text = chunk.get("response", "")
            # print(chunk)
            length += len(text)
            if length % 100 == 0:
                print(f"当前长度：{length}")
            f.write(text)
            answer += text
    return answer


class LLM:
    """
    默认使用 OpenAI GPT-4/3.5，若你想使用本地模型，可以在这里自行改写。
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.endpoint = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.model_local = "gpt-oss:20b"

    def ask(self, prompt: str, temperature: float = 0.2) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that uses up-to-date information."},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": 1500,
        }
        try:
            resp = requests.post(self.endpoint, headers=self.headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            answer = data["choices"][0]["message"]["content"].strip()
            return answer
        except Exception as e:
            log.error(f"LLM 请求失败: {e}")
            return "抱歉，我无法回答这个问题。"

    def ask_local(self, question: str, prompt: str, temperature: float = 0.2):
        """
        调用本地模型
        """
        return chat_by_prompt(question, prompt, self.model_local)


# ---------------------------------------------
# 主流程
# ---------------------------------------------
class QATool:
    def __init__(self):
        self.searcher = BingSearch(BING_API_KEY)
        self.scraper = WebScraper()
        self.llm = LLM(OPENAI_API_KEY)

    @staticmethod
    def _chunk_text(text: str, max_words: int = 2000) -> List[str]:
        """
        将大块文本拆分为不超过 max_words 的块
        """
        words = text.split()
        chunks = []
        for i in range(0, len(words), max_words):
            chunk = " ".join(words[i: i + max_words])
            chunks.append(chunk)
        return chunks

    def _prepare_prompt(self, question: str, sources: List[str]) -> str:
        """
        组装最终给模型的 prompt
        """
        # 这里先把来源拼成一段，后面可以自行改成更结构化的格式
        sources_text = "\n\n---\n\n".join(
            [f"来源 {i + 1}:\n{src[:2000]}{'...' if len(src) > 2000 else ''}" for i, src in enumerate(sources)])
        prompt = f"""
                    我在网络上搜索到以下内容（摘自公开可访问的网页）：
                    
                    {sources_text}
                    
                    请根据上述信息回答以下问题，并给出简洁明了的答案，必要时可以引用来源编号。
                    
                    问题: {question}
                    """
        # 对长度进行限制，避免超长导致 API 失败
        return prompt.strip()

    def answer(self, question: str) -> str:
        log.info(f"搜索问题: {question}")
        results = self.searcher.search_google(question)
        if not results:
            return "抱歉，未能在网络上找到相关信息。"

        random_int = random.randint(0, 10000)
        with open(f"search_results_{random_int}.txt", "w", encoding="utf-8") as f:
            f.write(json.dumps(results, ensure_ascii=False, indent=2))
        # random_int = 9617
        # results = json.load(open(f"search_results_{random_int}.json", "r", encoding="utf-8"))
        log.info(f"找到 {len(results)} 条结果，开始抓取内容…")
        sources = []
        for idx, res in enumerate(results):
            log.info(f"抓取 {idx + 1}/{len(results)}: {res['title']} - {res['link']}")
            content = self.scraper.fetch(res['link'])
            if content:
                sources.append(content)
            else:
                sources.append(f"(未能抓取内容) {res['title']}")

        # 若抓取内容过多，先做简短汇总
        log.info("准备 prompt…")
        prompt = self._prepare_prompt(question, sources)

        log.info("调用大模型…")
        answer = self.llm.ask_local(question, prompt)
        return answer


# ---------------------------------------------
# 运行入口
# ---------------------------------------------
def main():
    qa_tool = QATool()
    print("=== 互联网+大模型问答工具 ===")
    print("输入你的问题，按回车即可，输入 '退出' 或 Ctrl+C 结束。")
    while True:
        try:
            q = input("\n你想问：").strip()
            if q.lower() in ("退出", "exit", "quit"):
                print("再见！")
                break
            if not q:
                continue
            ans = qa_tool.answer(q)
            print("\n--- 答案 ---")
            print(ans)
        except KeyboardInterrupt:
            print("\n程序中断，退出。")
            break
        except Exception as e:
            print(f"出现错误: {e}")
            raise e


if __name__ == "__main__":
    main()
