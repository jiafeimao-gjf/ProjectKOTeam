import json
import os
import uuid

import ollama



# 添加MongoDB连接
# client = MongoClient('mongodb://localhost:27017/')  # 假设MongoDB本地运行
# db = client['llm_chat_history']  # 数据库名称
# chat_collection = db['chat_records']  # 集合名称

def ollama_stream(prompt, target_model, subfix, logger=None):
    return ollama_stream_inner(prompt, target_model, subfix, need_save=True, logger=logger)


def ollama_stream_inner(prompt, target_model, subfix, need_save=False, logger=None):
    """
    :param prompt: 输入的描述
    :param target_model: 输入模型
    :param subfix: 保存的后缀
    :return:
    """
    # 调用 ollama 流式生成
    save_data = {"model": target_model, "prompt": prompt, "answer": ""}

    hasThink = False
    for chunk in ollama.generate(model="gemma3n:e4b" if target_model == "gemma3n:e4b" else target_model, prompt=prompt,
                                 stream=True):
        text = chunk.get("response", "")

        if len(text) == 0:
            text = chunk.get("thinking", "")
            if not hasThink:
                save_data["answer"] += "thinking:\n\n"
                hasThink = True
        else:
            if hasThink:
                save_data["answer"] += "\n\nthinking end \n"
                hasThink = False
                text = "\n" + text

        if text:
            if logger:
                logger.info(text)
            save_data["answer"] += text
            # SSE 数据格式必须是 "data: ...\n\n"
            # yield f'{text}'
            yield f"data: {json.dumps({'text': text})}\n\n"
    # 告诉前端结束
    yield "data: [DONE]\n\n"
    # yield "[DONE]"

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
    save_to_his(need_save, save_data, subfix, logger)


def save_to_his(need_save, save_data, subfix, logger):
    if need_save:
        random_id = str(uuid.uuid4())
        if not os.path.exists(f"history/history_{subfix}"):
            os.mkdir(f"history/history_{subfix}")
        with open(f"history/history_{subfix}/history_{random_id}.md", "a") as f:
            if logger:
                logger.info(f"save_data")
            f.write(f"# model: {save_data['model']}\n")
            f.write(f"# prompt: {save_data['prompt']}\n")

            # If image_path exists, embed the image in the markdown
            if 'image_path' in save_data and save_data['image_path']:
                image_filename = save_data['image_path'].split('/')[-1]  # Extract filename from path
                f.write(f"![Uploaded Image](http://localhost:5173/api/image/{save_data['image_path']})\n\n")

            f.write(f"# answer: \n {save_data['answer']}\n")
            if logger:
                logger.info(f"save_data ok")
