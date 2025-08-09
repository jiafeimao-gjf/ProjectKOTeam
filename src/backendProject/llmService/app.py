# app.py
import logging
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


def ollama_stream(prompt):
    # 调用 ollama 流式生成
    save_data = {"prompt":prompt,"answer": ""}
    for chunk in ollama.generate(model="gpt-oss:20b", prompt=prompt, stream=True):
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
    with open(f"history_{random_id}.md", "a") as f:
        logger.info("保存数据")

        f.write(f"# prompt: {save_data['prompt']}\n")
        f.write(f"# answer: \n {save_data['answer']}\n")
        logger.info("保存成功")




@app.route("/chat")
def chat():
    # 获取query里面的prompt
    prompt = request.args.get("prompt")
    return Response(
        ollama_stream(prompt),
        mimetype="text/event-stream",  # SSE 必须用这个 MIME
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 关闭 Nginx 等的缓冲
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5888, debug=True, threaded=True)
