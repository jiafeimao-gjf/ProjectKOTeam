# mcp_server.py
import os
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import inspect

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPTool:
    """MCP工具基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具"""
        raise NotImplementedError("子类必须实现execute方法")

    def get_input_schema(self) -> Dict[str, Any]:
        """获取输入参数的schema"""
        return {}

    def get_output_schema(self) -> Dict[str, Any]:
        """获取输出参数的schema"""
        return {}


class FileListTool(MCPTool):
    """读取文件列表工具"""

    def __init__(self):
        super().__init__("file_list", "读取指定目录下的文件列表")

    def execute(self, path: str = ".", recursive: bool = False) -> Dict[str, Any]:
        try:
            if not os.path.exists(path):
                return {"success": False, "error": f"路径不存在: {path}"}

            files = []
            if recursive:
                for root, dirs, filenames in os.walk(path):
                    for filename in filenames:
                        full_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(full_path, path)
                        files.append({
                            "name": filename,
                            "path": full_path,
                            "relative_path": rel_path,
                            "is_directory": False
                        })
            else:
                for item in os.listdir(path):
                    full_path = os.path.join(path, item)
                    is_dir = os.path.isdir(full_path)
                    files.append({
                        "name": item,
                        "path": full_path,
                        "relative_path": item,
                        "is_directory": is_dir
                    })

            return {
                "success": True,
                "files": files,
                "total": len(files),
                "path": path
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class ReadFileTool(MCPTool):
    """读取文件内容工具"""

    def __init__(self):
        super().__init__("read_file", "读取指定文件的内容")

    def execute(self, file_path: str) -> Dict[str, Any]:
        try:
            if not os.path.exists(file_path):
                return {"success": False, "error": f"文件不存在: {file_path}"}

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "success": True,
                "content": content,
                "file_path": file_path,
                "size": len(content)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class UpdateFileTool(MCPTool):
    """更新文件内容工具"""

    def __init__(self):
        super().__init__("update_file", "根据代码块更新文件内容")

    def execute(self, file_path: str, content: str) -> Dict[str, Any]:
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "file_path": file_path,
                "size": len(content)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class CreateDirectoryTool(MCPTool):
    """创建目录工具"""

    def __init__(self):
        super().__init__("create_directory", "根据目录结构创建目录")

    def execute(self, path: str, recursive: bool = True) -> Dict[str, Any]:
        try:
            os.makedirs(path, exist_ok=True)
            return {
                "success": True,
                "path": path,
                "created": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class CreateFileTool(MCPTool):
    """创建文件并写入内容工具"""

    def __init__(self):
        super().__init__("create_file", "创建文件并写入内容")

    def execute(self, file_path: str, content: str = "") -> Dict[str, Any]:
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "file_path": file_path,
                "size": len(content)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class ToolInfoTool(MCPTool):
    """工具说明接口"""

    def __init__(self, tools: List[MCPTool]):
        super().__init__("tool_info", "提供所有工具的说明")
        self.tools = tools

    def execute(self) -> Dict[str, Any]:
        tool_info = []
        for tool in self.tools:
            tool_info.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.get_input_schema(),
                "output_schema": tool.get_output_schema()
            })

        return {
            "success": True,
            "tools": tool_info
        }


class MCPService:
    """MCP服务主类"""

    def __init__(self):
        self.tools = {}
        self.register_default_tools()

    def register_tool(self, tool: MCPTool):
        """注册工具"""
        self.tools[tool.name] = tool

    def register_default_tools(self):
        """注册默认工具"""
        self.register_tool(FileListTool())
        self.register_tool(ReadFileTool())
        self.register_tool(UpdateFileTool())
        self.register_tool(CreateDirectoryTool())
        self.register_tool(CreateFileTool())
        self.register_tool(ToolInfoTool(list(self.tools.values())))

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """执行指定工具"""
        if tool_name not in self.tools:
            return {"success": False, "error": f"工具不存在: {tool_name}"}

        try:
            result = self.tools[tool_name].execute(**kwargs)
            return result
        except Exception as e:
            logger.error(f"执行工具 {tool_name} 时出错: {e}")
            return {"success": False, "error": str(e)}

    def get_tool_info(self) -> Dict[str, Any]:
        """获取所有工具信息"""
        tool_info = []
        for name, tool in self.tools.items():
            tool_info.append({
                "name": name,
                "description": tool.description
            })
        return {"tools": tool_info}