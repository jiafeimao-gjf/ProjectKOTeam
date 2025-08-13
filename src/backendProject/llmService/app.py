# app.py
import logging
import os
import time
import urllib
import uuid

import ollama

from flask import Flask, Response, request
import ollama
import json
# from pymongo import MongoClient


# from .log.log_utils import logger
def get_logger(name):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return logging.getLogger(name)


logger = get_logger(__name__)

app = Flask(__name__)

# 添加MongoDB连接
# client = MongoClient('mongodb://localhost:27017/')  # 假设MongoDB本地运行
# db = client['llm_chat_history']  # 数据库名称
# chat_collection = db['chat_records']  # 集合名称

# 获取格式化时间 2025-08-09 23:59:59
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
postfix = time.strftime("%Y%m%d%H%M%S", time.localtime())


def ollama_stream(prompt, target_model, subfix):
    logger.info(f"ollama_stream: {prompt}, model: {target_model}")
    # 调用 ollama 流式生成
    save_data = {"model":target_model, "prompt": prompt, "answer": ""}
    for chunk in ollama.generate(model="gemma3n:e4b" if target_model == "gemma3n:e4b" else target_model, prompt=prompt,
                                 stream=True):
        text = chunk.get("response", "")
        if text:
            logger.info(text)
            save_data["answer"] += text
            # SSE 数据格式必须是 "data: ...\n\n"
            yield f"data: {json.dumps({'text': text})}\n\n"
    # 告诉前端结束
    yield "data: [DONE]\n\n"

    # MongoDB 存储逻辑
    # chat_record = {
    #     "prompt": save_data["prompt"],
    #     "answer": save_data["answer"],
    #     "model": target_model,
    #     "timestamp": current_time,
    #     "uuid": str(uuid.uuid4())
    # }
    # chat_collection.insert_one(chat_record)
    # logger.info("数据已保存到MongoDB")
    # 保存到history 下面
    random_id = str(uuid.uuid4())
    if not os.path.exists(f"history/history_{subfix}"):
        os.mkdir(f"history/history_{subfix}")
    with open(f"history/history_{subfix}/history_{random_id}.md", "a") as f:
        logger.info("保存数据")
        f.write(f"# model: {save_data['model']}\n")
        f.write(f"# prompt: {save_data['prompt']}\n")
        f.write(f"# answer: \n {save_data['answer']}\n")
        logger.info("保存成功")


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
        logger.info(model.model)
        response["models"].append(model.model)
    return response


@app.get("/prompt_config")
def prompt_config():
    result = chat_collection.find({"key": {"$regex": "prompt_config"}})
    prompts = []
    for prompt in result:
        logger.info(prompt)
        prompts.append(prompt)
    return prompts


@app.post("/prompt_config")
def post_prompt_config():
    prompts = request.json.get("prompts")
    if not prompts:
        return "prompts is empty"
    chat_collection.update_one({"key": "prompt_config"}, {"$set": {"prompts": prompts}})
    return "success"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5888, debug=True, threaded=True)
