# app.py
import base64
import os
import time
import urllib
import uuid

from flask import Flask, Response, request
import ollama

from log.log_utils import logger
from src.llm_caller import ollama_stream, ollama_stream_inner

app = Flask(__name__)

# CORS(app)


# 获取格式化时间 2025-08-09 23:59:59
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
postfix = time.strftime("%Y%m%d%H%M%S", time.localtime())

# POST 请求
body_dict = {}


@app.route("/chat_start", methods=["POST"])
def chat_start():
    # 获取body里面的prompt
    prompt = request.json.get("prompt")
    if not prompt:
        return "prompt is empty"
    model = request.json.get("model")
    if not model:
        return "model is empty"
    global body_dict

    uuid_key = str(uuid.uuid4())
    body_dict[uuid_key] = {"prompt": prompt, "model": model}
    return f"/api/chat?uuid={uuid_key}"


@app.get("/chat")
def chat():
    global body_dict
    body = body_dict.get(request.args.get("uuid"))
    if not body:
        return "body is empty"
    # 获取body里面的prompt
    prompt = body.get("prompt")
    if not prompt:
        return "prompt is empty"
    model = body.get("model")
    if not model:
        return "model is empty"
    # 解码%XX
    prompt = urllib.parse.unquote(prompt)
    model = urllib.parse.unquote(model)
    logger.info(f"prompt: {prompt}, model: {model}")

    global current_time
    global postfix
    # current_time 时间距离当前时间超过5分钟，更新 current_time
    if time.time() - time.mktime(time.strptime(current_time, "%Y-%m-%d %H:%M:%S")) > 300:
        logger.info(f"时间距离当前时间超过5分钟，更新 postfix from {postfix}")
        postfix = time.strftime("%Y%m%d%H%M%S", time.localtime())
        logger.info(f"时间距离当前时间超过5分钟，更新 postfix to {postfix}")
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    return Response(
        ollama_stream(prompt, model, postfix),
        mimetype="text/event-stream",  # SSE 必须用这个 MIME
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 关闭 Nginx 等的缓冲
        }
    )


@app.get("/models")
def models():
    models = ollama.list()
    response = {"models": []}
    for model in models.models:
        # logger.info(model.model)
        response["models"].append(model.model)
    return response


@app.get("/prompt_config")
def prompt_config():
    # results = chat_collection.find({"key": "prompt_config"})
    # for result in results:
    #     logger.info(result["prompts"])
    #     # 解码\u4f60\u662f
    #     # 解码Unicode转义字符
    #     return {"prompts": result["prompts"]}
    return {"prompts": [
        "你是一个具备十年项目管理经验的项目经理，可以针对项目需求，进行规划项目迭代交付计划，你可以将项目下发到产品经理、架构师，开发测试人员，保障项目正常迭代。",
        "你是一个具备十年产品经验的产品经理，可以针对项目需求，进行产品功能设计，你可以将产品功能设计下发到开发人员，保障产品功能正常实现。",
        "你是一个具备十年开发经验和架构经验的架构师，可以针对项目需求，设计详尽的技术方案，输出技术方案文档。",
        "你是一个具备十年开发经验的全栈开发者，可以针对项目需求和技术方案，进行项目开发，输出实现代码，保证完成需求里面的每一个功能。",
        "你是一个具备十年测试经验的测试工程师，可以针对项目需求，进行项目测试，你可以将项目测试下发到测试人员，保障项目测试正常进行。"]}


@app.post("/prompt_config")
def post_prompt_config():
    # prompts = request.json.get("prompts")
    # if not prompts:
    #     return "prompts is empty"
    # # 插入或者更新
    # update_result = chat_collection.update_one({"key": "prompt_config"}, {"$set": {"prompts": prompts}}, upsert=True)
    # if update_result.modified_count == 0:
    #     logger.error("update failed")
    #
    # results = chat_collection.find({"key": "prompt_config"})
    # # logger.info(results)
    # for result in results:
    #     logger.info(result["prompts"])

    return {"msg": "success", "code": 0}


@app.post("/browser_chat")
def browser_chat():
    # 获取body里面的question
    question = request.json.get("question")
    if not question:
        return {"error": "question is required"}, 400

    logger.info(f"Received question: {question}")

    # 使用默认模型进行流式响应
    # 这里可以根据需要指定特定的模型
    def generate():
        for chunk in ollama_stream_inner(question, "gpt-oss:20b", postfix, need_save=True):
            yield chunk

    return Response(
        generate(),
        mimetype="text/event-stream",  # SSE 必须用这个 MIME
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 关闭 Nginx 等的缓冲
        }
    )


@app.route('/image_chat', methods=["POST"])
def image_chat():
    image_file = request.files.get("image")
    model = request.form.get("model", "qwen3-vl:4b")
    prompt = request.form.get("prompt", "请分析图片, 最后一行用10个字以内的总结这个图片")

    logger.info(f"Received model: {model}, prompt: {prompt}")
    if image_file is None:
        return {"error": "No image uploaded"}, 400

    # 读取文件并转base64
    image_bytes = image_file.read()
    image_b64 = base64.b64encode(image_bytes).decode()

    logger.info(f"Received image_b64: {image_b64[:10]}...")

    # 生成器：逐块返回模型输出
    def generate():
        try:
            stream = ollama.chat(
                model=model,
                stream=True,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [image_b64]
                    }
                ]
            )
            answer = ""
            for part in stream:
                if "thinking" in part["message"] and part["message"]["thinking"]:
                    thinking = part["message"]["thinking"]
                    token = thinking
                else:
                    token = part["message"]["content"]
                logger.info(token)
                answer += token
                yield token  # 每次一个 token
                # 以\n为分割，获取最后一个文字
            file_name = answer.split("\n")[-1]
            if not file_name:
                file_name = answer.split("\n")[-2]

            with open(f"{model}_{file_name}_{time.time()}.md", "w", encoding="utf-8") as f:
                f.write(answer)
        except Exception as e:
            yield f"[ERROR] {str(e)}"

    return Response(
        generate(),
        mimetype="text/event-stream",  # SSE 必须用这个 MIME
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 关闭 Nginx 等的缓冲
        }
    )


@app.route('/get_his_list', methods=["GET"])
def get_his_list():
    """
    获取历史记录文件列表
    
    该函数遍历history目录下的所有子目录，收集每个子目录中的文件列表
    
    Returns:
        dict: 以子目录名为键，文件列表为值的字典
    """
    his_list = {}
    # 遍历history目录及其所有子目录，收集非空目录中的文件
    for root, dirs, files in os.walk("./history"):
        if len(files) > 0:
            his_list[root.split("/")[-1]] = files

    return his_list


# 获取某一个日志文件的内容
@app.route('/get_his_content', methods=["GET"])  # 定义API路由，仅接受GET请求
def get_his_content():
    """
    获取指定历史日志文件的内容
    
    通过文件名参数读取history目录下对应文件的内容
    
    Args:
        file_name (str): Query参数，必需。指定要读取的历史日志文件名，位于history目录下
    
    Returns:
        dict: 包含操作结果、状态码和文件内容的字典
        int: HTTP状态码(成功时200，参数缺失时400)
    """
    # 从请求参数中获取文件名
    file_name = request.args.get("file_name")

    # 检查必需的文件名参数是否存在
    if not file_name:
        # 如果文件名参数缺失，返回错误信息和400状态码
        return {"error": "file_name is required"}, 400

    file_name = "history_" + file_name
    # 使用with语句安全地打开和关闭文件，确保异常处理
    # 读取history目录下指定文件的全部内容，使用UTF-8编码
    if not os.path.exists(f"history/{file_name}"):
        return {"content": "file not found"}
    with open(f"history/{file_name}", "r", encoding="utf-8") as f:
        content = f.read()

    # 返回成功响应，包含操作状态、状态码和文件内容
    return {"msg": "success", "code": 0, "content": content}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5888, debug=True, threaded=True)