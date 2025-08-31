# mcp_client.py - 增强版客户端
import requests
import json
from typing import Dict, Any, List, Optional
import re


class MCPClient:
    """MCP客户端"""

    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
        # 添加请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _make_request(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送请求到MCP服务器"""
        try:
            response = self.session.post(
                f"{self.server_url}/execute",
                json={
                    "tool": tool_name,
                    "params": params
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"请求失败: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"JSON解析失败: {str(e)}"}

    def list_files(self, path: str = ".", recursive: bool = False) -> Dict[str, Any]:
        """读取文件列表"""
        return self._make_request("file_list", {
            "path": path,
            "recursive": recursive
        })

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """读取文件内容"""
        return self._make_request("read_file", {
            "file_path": file_path
        })

    def update_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """更新文件内容"""
        return self._make_request("update_file", {
            "file_path": file_path,
            "content": content
        })

    def create_directory(self, path: str, recursive: bool = True) -> Dict[str, Any]:
        """创建目录"""
        return self._make_request("create_directory", {
            "path": path,
            "recursive": recursive
        })

    def create_file(self, file_path: str, content: str = "") -> Dict[str, Any]:
        """创建文件并写入内容"""
        return self._make_request("create_file", {
            "file_path": file_path,
            "content": content
        })

    def get_tool_info(self) -> Dict[str, Any]:
        """获取工具说明"""
        return self._make_request("tools", {})

    def process_code_block_update(self, file_path: str, code_blocks: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        处理代码块更新
        code_blocks: [{'language': 'python', 'code': 'print("hello")'}]
        """
        try:
            # 读取当前文件内容
            read_result = self.read_file(file_path)
            if not read_result.get('success'):
                return read_result

            current_content = read_result['content']

            # 简单的代码块替换逻辑（实际应用中可能需要更复杂的处理）
            new_content = current_content
            for block in code_blocks:
                language = block.get('language', '')
                code = block.get('code', '')
                if language and code:
                    # 这里可以根据具体需求实现代码块替换逻辑
                    new_content += f"\n# {language} code block:\n{code}\n"

            return self.update_file(file_path, new_content)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def process_directory_structure(self, structure: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        处理目录结构创建
        structure: [{'path': 'src', 'type': 'directory'}, {'path': 'src/main.py', 'type': 'file'}]
        """
        results = []
        for item in structure:
            try:
                if item.get('type') == 'directory':
                    result = self.create_directory(item['path'])
                elif item.get('type') == 'file':
                    # 创建文件
                    content = item.get('content', '')
                    result = self.create_file(item['path'], content)
                else:
                    result = {"success": False, "error": f"未知类型: {item.get('type')}"}

                results.append({
                    "path": item['path'],
                    "result": result
                })
            except Exception as e:
                results.append({
                    "path": item['path'],
                    "result": {"success": False, "error": str(e)}
                })

        return {"success": True, "results": results}

    def format_prompt_for_mcp(self, prompt: str) -> str:
        """
        格式化提示词，使其符合MCP服务器接口要求
        """
        return f"""
请根据以下要求执行操作：

{prompt}

输出格式要求：
- 使用JSON格式
- 包含tool字段（工具名称）
- 包含params字段（参数）
- 确保参数符合对应工具的输入格式

示例格式：
{{"tool": "read_file", "params": {{"file_path": "/path/to/file"}}}}
        """

    def execute_with_mcp_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        执行带有MCP提示词的请求
        """
        # 格式化提示词
        formatted_prompt = self.format_prompt_for_mcp(prompt)

        # 这里应该调用您的ollama_stream函数
        # result = ollama_stream(formatted_prompt, target_model="llama3", subfix="mcp")

        # 模拟返回结果
        return {
            "success": True,
            "prompt": formatted_prompt,
            "description": "已格式化为MCP兼容的提示词"
        }


# 使用示例
def demo_usage():
    """使用示例"""
    client = MCPClient("http://localhost:8000")

    # 获取工具信息
    print("=== 工具信息 ===")
    tool_info = client.get_tool_info()
    print(json.dumps(tool_info, indent=2, ensure_ascii=False))

    # 列出文件
    print("\n=== 文件列表 ===")
    files = client.list_files(".")
    print(json.dumps(files, indent=2, ensure_ascii=False))

    # 创建目录
    print("\n=== 创建目录 ===")
    mkdir_result = client.create_directory("./test_dir")
    print(json.dumps(mkdir_result, indent=2, ensure_ascii=False))

    # 创建文件
    print("\n=== 创建文件 ===")
    create_result = client.create_file("./test_dir/test.txt", "Hello MCP!")
    print(json.dumps(create_result, indent=2, ensure_ascii=False))




if __name__ == "__main__":
    demo_usage()