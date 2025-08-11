#!/usr/bin/env python
# ai_assistant.py
"""
命令行 AI 助手：支持多轮对话、流式输出、上下文记忆
"""

import os
import sys
import json

import ollama
import typer
import openai
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from dotenv import load_dotenv

app = typer.Typer()
console = Console()

# ---------------------- 初始化 ---------------------- #
# load_dotenv()  # 读取 .env
# openai.api_key = os.getenv("OPENAI_API_KEY")
# if not openai.api_key:
#     console.print("[red]❌  没有找到 OPENAI_API_KEY，请在 .env 中配置！[/red]")
#     raise SystemExit(1)

# 保存对话历史（可持久化）
CHAT_HISTORY_FILE = Path.home() / "PycharmProjects/ProjectKOTeam/src/cliProject/localCliLLM/.ai_cli_chat.json"


def load_history() -> list:
    if CHAT_HISTORY_FILE.exists():
        with CHAT_HISTORY_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history: list):
    console.print("保存对话历史到：" + str(CHAT_HISTORY_FILE))
    with CHAT_HISTORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


history = load_history()


# ---------------------- 工具函数 ---------------------- #
def build_messages(history: list, user_input: str) -> list:
    """
    把历史记录和本次用户输入转换成 OpenAI 的 chat 格式
    """
    messages = history.copy()
    messages.append({"role": "user", "content": user_input})
    return messages


def print_response(role: str, content: str):
    """
    用 Rich 打印角色对话
    """
    panel = Panel(content, title=role.title(), expand=False)
    console.print(panel)


def stream_response_online(messages: list):
    load_dotenv()  # 读取 .env
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        console.print("[red]❌  没有找到 OPENAI_API_KEY，请在 .env 中配置！[/red]")
        raise SystemExit(1)
    """
    使用 OpenAI 的流式接口
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # 或者 gpt-3.5-turbo
            messages=messages,
            temperature=0.7,
            stream=True,
        )
        partial_text = ""
        for chunk in response:
            chunk_text = chunk["choices"][0]["delta"].get("content", "")
            if chunk_text:
                partial_text += chunk_text
                # 实时刷新显示
                console.print(chunk_text, end="", style="cyan")
        console.print()  # 换行
        return partial_text
    except openai.error.OpenAIError as e:
        console.print(f"[red]OpenAI 错误: {e}[/red]")
        return ""


def stream_response(messages: list):
    """
    使用 OpenAI 的流式接口
    """
    try:

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # 或者 gpt-3.5-turbo
            messages=messages,
            temperature=0.7,
            stream=True,
        )
        partial_text = ""
        for chunk in response:
            chunk_text = chunk["choices"][0]["delta"].get("content", "")
            if chunk_text:
                partial_text += chunk_text
                # 实时刷新显示
                console.print(chunk_text, end="", style="cyan")
        console.print()  # 换行
        return partial_text
    except openai.error.OpenAIError as e:
        console.print(f"[red]OpenAI 错误: {e}[/red]")
        return ""


def ollama_stream(prompt, target_model):
    # 调用 ollama 流式生成
    save_data = {"prompt": prompt, "answer": ""}
    for chunk in ollama.generate(model="gemma3n:e4b" if target_model == "gemma3n:e4b" else target_model, prompt=prompt,
                                 stream=True):
        text = chunk.get("response", "")
        if text:
            save_data["answer"] += text
            # 实时刷新显示
            console.print(text, end="", style="cyan")
    console.print()  # 换行

    return save_data["answer"]


# ---------------------- CLI 命令 ---------------------- #
@app.command("chat")
def chat():
    """
    开始与 AI 的对话（支持多轮）
    """
    console.print("[green]💬 开始对话！输入 'exit' 返回主菜单，'quit' 退出程序。[/green]")
    try:
        while True:
            # 用户输入
            user_text = Prompt.ask("[bold cyan]你[/bold cyan]").strip()
            
            # 检查特殊命令
            if user_text.lower() == 'exit':
                console.print("[yellow]🔚 返回主菜单。[/yellow]")
                return
            elif user_text.lower() == 'quit':
                console.print("[green]👋 再见！[/green]")
                sys.exit(0)
            elif not user_text:
                continue

            console.print("输入内容：" + user_text)

            # 生成消息列表
            # msgs = build_messages(history, user_text)

            # 调用模型（流式）
            # assistant_text = stream_response(msgs)

            assistant_text = ollama_stream(user_text, "gemma3n:e4b")

            # 记录到历史
            history.append({"role": "user", "content": user_text})
            history.append({"role": "assistant", "content": assistant_text})
            save_history(history)

    except KeyboardInterrupt:
        console.print("\n[yellow]🔚 返回主菜单。[/yellow]")
        return


@app.command("history")
def history_cmd():
    """查看最近的对话历史"""
    if not history:
        console.print("[yellow]暂无历史记录。[/yellow]")
        return
    for idx, turn in enumerate(history):
        role = turn["role"].title()
        content = turn["content"]
        panel = Panel(content, title=f"{role} #{idx + 1}", expand=False)
        console.print(panel)


@app.command("clear_history")
def clear_history():
    """清空对话历史"""
    if CHAT_HISTORY_FILE.exists():
        CHAT_HISTORY_FILE.unlink()
    global history
    history = []
    console.print("[green]✅ 对话历史已清空。[/green]")


def show_help():
    """显示帮助信息"""
    console.print("[bold green]AI 助手交互终端[/bold green]")
    console.print("可用命令:")
    console.print("  [cyan]chat[/cyan]           - 开始与 AI 对话")
    console.print("  [cyan]history[/cyan]        - 查看对话历史")
    console.print("  [cyan]clear_history[/cyan]  - 清空对话历史")
    console.print("  [cyan]help[/cyan]           - 显示帮助信息")
    console.print("  [cyan]exit[/cyan]           - 退出程序")
    console.print()


def interactive_mode():
    """进入交互终端模式"""
    console.print("[green]🤖 欢迎使用 AI 助手！输入 'help' 查看可用命令。[/green]")
    show_help()
    
    while True:
        try:
            command = Prompt.ask("[bold yellow]>>>[/bold yellow]").strip().lower()
            
            if command == "chat":
                chat()
            elif command == "history":
                history_cmd()
            elif command == "clear_history":
                clear_history()
            elif command == "help":
                show_help()
            elif command in ["exit", "quit"]:
                console.print("[green]👋 再见！[/green]")
                sys.exit(0)
            elif command == "":
                continue
            else:
                console.print(f"[red]未知命令: {command}。输入 'help' 查看可用命令。[/red]")
        except KeyboardInterrupt:
            console.print("\n[green]👋 再见！[/green]")
            sys.exit(0)
        except Exception as e:
            console.print(f"[red]发生错误: {e}[/red]")


# ---------------------- 入口 ---------------------- #
if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 没有参数时进入交互终端模式
        interactive_mode()
    else:
        # 有参数时使用 Typer 命令行模式
        app()
