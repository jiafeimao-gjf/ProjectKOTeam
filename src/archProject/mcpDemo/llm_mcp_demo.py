import requests
import json
import time
import threading
from typing import Dict, Any, Optional

class MCPConnector:
    """MCP连接器，负责与模型控制平台通信"""
    
    def __init__(self, mcp_url: str, model_id: str, model_version: str):
        self.mcp_url = mcp_url
        self.model_id = model_id
        self.model_version = model_version
        self.session_id = None
        self.heartbeat_thread = None
        self.running = False
        
    def register(self) -> bool:
        """向MCP注册模型"""
        try:
            response = requests.post(
                f"{self.mcp_url}/api/v1/models/register",
                json={
                    "model_id": self.model_id,
                    "version": self.model_version,
                    "capabilities": ["text_generation", "embedding"],
                    "status": "ready",
                    "metadata": {
                        "framework": "transformers",
                        "max_tokens": 4096,
                        "supported_languages": ["zh", "en"]
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                print(f"模型注册成功，会话ID: {self.session_id}")
                return True
            else:
                print(f"模型注册失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"注册过程出错: {str(e)}")
            return False
    
    def start_heartbeat(self, interval: int = 10):
        """启动心跳机制，向MCP报告模型状态"""
        self.running = True
        
        def heartbeat():
            while self.running:
                try:
                    requests.post(
                        f"{self.mcp_url}/api/v1/models/heartbeat",
                        json={
                            "session_id": self.session_id,
                            "status": "active",
                            "metrics": {
                                "cpu_usage": 35.2,
                                "memory_usage": 62.5,
                                "queue_length": 0
                            }
                        }
                    )
                except Exception as e:
                    print(f"心跳发送失败: {str(e)}")
                
                time.sleep(interval)
        
        self.heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
        self.heartbeat_thread.start()
        print("心跳机制已启动")
    
    def get_task(self) -> Optional[Dict[str, Any]]:
        """从MCP获取任务"""
        try:
            response = requests.get(
                f"{self.mcp_url}/api/v1/models/task",
                params={"session_id": self.session_id}
            )
            
            if response.status_code == 200:
                task = response.json()
                return task if task.get("task_id") else None
            return None
            
        except Exception as e:
            print(f"获取任务失败: {str(e)}")
            return None
    
    def submit_result(self, task_id: str, result: Dict[str, Any]) -> bool:
        """向MCP提交任务结果"""
        try:
            response = requests.post(
                f"{self.mcp_url}/api/v1/models/result",
                json={
                    "session_id": self.session_id,
                    "task_id": task_id,
                    "result": result,
                    "status": "completed"
                }
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"提交结果失败: {str(e)}")
            return False
    
    def unregister(self) -> bool:
        """从MCP注销模型"""
        self.running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join()
            
        try:
            response = requests.post(
                f"{self.mcp_url}/api/v1/models/unregister",
                json={"session_id": self.session_id}
            )
            
            if response.status_code == 200:
                print("模型已成功注销")
                return True
            return False
            
        except Exception as e:
            print(f"注销过程出错: {str(e)}")
            return False


class LargeLanguageModel:
    """大模型核心类，处理实际的推理任务"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        # 实际应用中这里会加载真实的模型
        print(f"初始化大模型: {model_name}")
    
    def generate_text(self, prompt: str, params: Dict[str, Any]) -> str:
        """生成文本响应"""
        # 模拟模型推理过程
        time.sleep(1)  # 模拟推理耗时
        return f"[{self.model_name}] 针对提示 '{prompt}' 的响应（参数: {params}）"
    
    def generate_embedding(self, text: str) -> list[float]:
        """生成文本嵌入"""
        # 模拟生成嵌入向量
        time.sleep(0.5)
        return [0.1 * i for i in range(10)]


def main():
    # 配置信息
    MCP_URL = "http://localhost:8080/mcp"  # MCP平台地址
    MODEL_ID = "llama3-7b-chat"
    MODEL_VERSION = "1.0.0"
    
    # 初始化组件
    mcp_connector = MCPConnector(MCP_URL, MODEL_ID, MODEL_VERSION)
    llm = LargeLanguageModel(MODEL_ID)
    
    try:
        # 1. 注册到MCP
        if not mcp_connector.register():
            return
        
        # 2. 启动心跳
        mcp_connector.start_heartbeat()
        
        # 3. 循环获取并处理任务
        print("开始处理任务... (按Ctrl+C停止)")
        while True:
            task = mcp_connector.get_task()
            
            if task:
                print(f"收到新任务: {task['task_id']}, 类型: {task['task_type']}")
                
                # 根据任务类型处理
                result = None
                if task["task_type"] == "text_generation":
                    result = {
                        "text": llm.generate_text(
                            task["prompt"], 
                            task.get("parameters", {})
                        )
                    }
                elif task["task_type"] == "embedding":
                    result = {
                        "embedding": llm.generate_embedding(task["text"])
                    }
                
                # 提交结果
                if result and mcp_connector.submit_result(task["task_id"], result):
                    print(f"任务 {task['task_id']} 处理完成")
                else:
                    print(f"任务 {task['task_id']} 处理失败")
            
            # 短暂休眠，避免过度轮询
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n用户中断程序")
    finally:
        # 4. 注销
        mcp_connector.unregister()


if __name__ == "__main__":
    main()
