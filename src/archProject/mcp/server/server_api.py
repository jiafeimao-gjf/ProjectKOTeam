# server_api.py - Flask API 服务器实现
from flask import Flask, request, jsonify
from src.archProject.mcp.server.mcp_server import MCPService

app = Flask(__name__)
mcp_service = MCPService()


@app.route('/execute', methods=['POST'])
def execute_tool():
    """执行工具接口"""
    try:
        data = request.get_json()
        tool_name = data.get('tool')
        params = data.get('params', {})

        if not tool_name:
            return jsonify({"success": False, "error": "缺少工具名称"}), 400

        result = mcp_service.execute_tool(tool_name, **params)
        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/tools', methods=['GET'])
def get_tools():
    """获取工具列表"""
    try:
        result = mcp_service.get_tool_info()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)