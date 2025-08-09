# app.py
import logging
import os
import time
import uuid

import ollama

from flask import Flask, Response, request
import ollama
import json


# from .log.log_utils import logger
def get_logger(name):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return logging.getLogger(name)


logger = get_logger(__name__)

app = Flask(__name__)

# 获取格式化时间 2025-08-09 23:59:59
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
postfix = time.strftime("%Y%m%d%H%M%S", time.localtime())

def ollama_stream(prompt, target_model, postfix):
    logger.info(f"ollama_stream: {prompt}, model: {target_model}")
    # 调用 ollama 流式生成
    save_data = {"prompt": prompt, "answer": ""}
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
    # 保存到history 下面
    random_id = str(uuid.uuid4())
    if not os.path.exists(f"history/history_{postfix}"):
        os.mkdir(f"history/history_{postfix}")
    with open(f"history/history_{postfix}/history_{random_id}.md", "a") as f:
        logger.info("保存数据")

        f.write(f"# prompt: {save_data['prompt']}\n")
        f.write(f"# answer: \n {save_data['answer']}\n")
        logger.info("保存成功")


@app.route("/chat")
def chat():
    # 获取query里面的prompt
    prompt = request.args.get("prompt")
    if not prompt:
        return "prompt is empty"
    model = request.args.get("model")
    if not model:
        return "model is empty"

    global current_time
    global postfix
    # current_time 时间距离当前时间超过5分钟，更新 current_time
    if time.time() - time.mktime(time.strptime(current_time, "%Y-%m-%d %H:%M:%S")) > 300:
        postfix = time.strftime("%Y%m%d%H%M%S", time.localtime())
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    return Response(
        ollama_stream(prompt, model, current_time),
        mimetype="text/event-stream",  # SSE 必须用这个 MIME
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 关闭 Nginx 等的缓冲
        }
    )


@app.route("/models")
def models():
    models = ollama.list()
    response = {"models": []}
    for model in models.models:
        logger.info(model.model)
        response["models"].append(model.model)
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5888, debug=True, threaded=True)
