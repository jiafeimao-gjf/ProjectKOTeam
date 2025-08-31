# run_server.py - 启动服务器脚本
from src.archProject.mcp.server.server_api import app

if __name__ == '__main__':
    print("启动MCP服务器...")
    print("访问 http://localhost:8000/tools 查看工具列表")
    print("访问 http://localhost:8000/execute 调用工具")
    app.run(host='0.0.0.0', port=8000, debug=True)