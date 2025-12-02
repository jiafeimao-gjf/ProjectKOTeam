#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
toolset.py
~~~~~~~~~~

一个极简的脚本工具集框架，内置文件读取/写入功能，后续可按需扩展新工具。

使用方式：
    python toolset.py read <文件路径>
    python toolset.py write <文件路径> <内容>
"""

from __future__ import annotations

import argparse
import logging
import json
import os.path
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Dict, List, Type

import pandas


def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    return logger


logger = setup_logger("tools")


# --------------------------------------------------------------------------- #
# 1. 工具基类与工具注册机制
# --------------------------------------------------------------------------- #

class BaseTool(ABC):
    """
    所有工具必须继承此基类。

    每个工具都应该实现 `run(args: argparse.Namespace) -> int` 方法，
    其中 `args` 是通过 argparse 解析后的参数对象。
    返回值为程序退出码（0 表示成功）。
    """

    @abstractmethod
    def run(self, args: argparse.Namespace) -> int:
        """执行工具主逻辑。"""


class ToolRegistry:
    """
    用于注册与查找工具。内部维护一个名称 -> 工具类 的字典。
    """

    _registry: Dict[str, Type[BaseTool]] = {}

    @classmethod
    def register(cls, name: str, tool_cls: Type[BaseTool]) -> None:
        if name in cls._registry:
            raise ValueError(f"Tool '{name}' 已经被注册")
        cls._registry[name] = tool_cls

    @classmethod
    def get(cls, name: str) -> Type[BaseTool]:
        return cls._registry[name]

    @classmethod
    def list_tools(cls) -> List[str]:
        return list(cls._registry.keys())


# --------------------------------------------------------------------------- #
# 2. 具体工具实现
# --------------------------------------------------------------------------- #

class ReadTool(BaseTool):
    """
    读取文件内容并打印到标准输出。
    用法：`read <文件路径>`
    """

    def run(self, args: argparse.Namespace) -> int:
        file_path = Path(args.file).expanduser().resolve()
        if not file_path.is_file():
            print(f"[错误] 文件不存在：{file_path}", file=sys.stderr)
            return 1
        try:
            content = file_path.read_text(encoding=args.encoding)
        except Exception as e:
            print(f"[错误] 读取文件失败：{e}", file=sys.stderr)
            return 1
        print(content)
        return 0


class WriteTool(BaseTool):
    """
    写入文本到文件。若文件不存在会自动创建。
    用法：`write <文件路径> <内容>`
    """

    def run(self, args: argparse.Namespace) -> int:
        if not os.path.exists(os.path.dirname(args.file)):
            print(f"[错误] 目录不存在：{os.path.dirname(args.file)} 新创建！", file=sys.stderr)
            os.mkdir(os.path.dirname(args.file))
        file_path = Path(args.file).expanduser().resolve()
        try:
            file_path.write_text(args.content, encoding=args.encoding)
        except Exception as e:
            print(f"[错误] 写入文件失败：{e}", file=sys.stderr)
            return 1
        print(f"[成功] 已写入 {file_path}")
        return 0


# json转换成excel
class Json2Excel(BaseTool):

    def run(self, args: argparse.Namespace) -> int:
        logger.info(f"正在转换 {args.file}")
        data = pandas.read_json(args.file)
        data.to_excel(f"{args.file.replace('.json', '')}.xlsx")

        return 0


# 注册工具
ToolRegistry.register("read", ReadTool)
ToolRegistry.register("write", WriteTool)
ToolRegistry.register("json2excel", Json2Excel)


# --------------------------------------------------------------------------- #
# 3. 命令行解析与入口
# --------------------------------------------------------------------------- #

def build_main_parser() -> argparse.ArgumentParser:
    """构造主解析器（含子命令）。"""
    parser = argparse.ArgumentParser(
        description="Python 脚本工具集框架（文件读取/写入）",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- read ----
    read_parser = subparsers.add_parser(
        "read",
        help="读取文件内容并打印",
    )
    read_parser.add_argument(
        "file",
        help="待读取的文件路径",
    )
    read_parser.add_argument(
        "--encoding",
        default="utf-8",
        help="文件编码",
    )
    read_parser.set_defaults(func=ReadTool().run)

    # ---- write ----
    write_parser = subparsers.add_parser(
        "write",
        help="写入文本到文件",
    )
    write_parser.add_argument(
        "file",
        help="目标文件路径",
    )
    write_parser.add_argument(
        "content",
        help="要写入的文本内容",
    )
    write_parser.add_argument(
        "--encoding",
        default="utf-8",
        help="写入时使用的编码",
    )
    write_parser.set_defaults(func=WriteTool().run)

    json2excel_parser = subparsers.add_parser(
        "json2excel",
        help=""
    )

    json2excel_parser.add_argument(
        "file",
        help=""
    )

    json2excel_parser.set_defaults(func=Json2Excel().run)

    # ---- 可扩展性示例（自定义工具） ----
    # 下面代码演示如何在同一文件中定义一个新工具并注册
    # class EchoTool(BaseTool):
    #     def run(self, args):
    #         print(args.message)
    #         return 0
    # ToolRegistry.register("echo", EchoTool)
    # echo_parser = subparsers.add_parser("echo", help="简单回显")
    # echo_parser.add_argument("message", help="要回显的消息")
    # echo_parser.set_defaults(func=EchoTool().run)

    return parser


def main() -> None:
    """脚本入口。"""
    parser = build_main_parser()
    args = parser.parse_args()
    # `args.func` 是每个子命令注册的 `run` 方法
    exit_code = args.func(args)
    sys.exit(exit_code)


# --------------------------------------------------------------------------- #
# 4. 直接运行时调用 main()
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    main()
