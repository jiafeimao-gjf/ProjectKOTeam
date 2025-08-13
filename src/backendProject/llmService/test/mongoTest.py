from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')  # 假设MongoDB本地运行
db = client['llm_chat_history']  # 数据库名称
chat_collection = db['chat_records']  # 集合名称
if __name__ == '__main__':
    # db.create_collection("chat_records")
    # 查找所有文档
    documents = chat_collection.find()
    for document in documents:
        print(document.get("prompts"))
    # # 写入
    # chat_collection.insert_one({
    #     "prompt": "你好",
    #     "answer": "你好！有什么我可以帮助你的吗？",
    #     "model": "gemma3n:e4b",
    #     "timestamp": "2025-08-09 23:59:59",
    #     "uuid": "1234567890"
    # })
    # # 查找所有文档
    # documents = chat_collection.find()
    # for document in documents:
    #     print(document)
    # # 查找 prompt 包含 "你好" 的文档
    # query = {"prompt": {"$regex": "你好"}}
    # documents = chat_collection.find(query)
    # for document in documents:
    #     print(document)
    # # 查找 model 为 "gemma3n:e4b" 的文档
    # query = {"model": "gemma3n:e4b"}
    # documents = chat_collection.find(query)
    # for document in documents:
    #     print(document)
    # # 查找 prompt 包含 "你好" 且 model 为 "gemma3n:e4b" 的文档
    # query = {"prompt": {"$regex": "你好"}, "model": "gemma3n:e4b"}
    # documents = chat_collection.find(query)
    # for document in documents:
    #     print(document)
    # # 查找 prompt 包含 "你好" 且 model 为 "gemma3n:e4b" 的文档，只返回 prompt 和 answer 字段
    # query = {"prompt": {"$regex": "你好"}, "model": "gemma3n:e4b"}
    # projection = {"prompt": 1, "answer": 1, "_id": 0}  # 1 表示包含，0 表示不包含
    # documents = chat_collection.find(query, projection)
    # for document in documents:
    #     print(document)
    # # 查找 prompt 包含 "你好" 且 model 为 "gemma3n:e4b" 的文档，只返回 prompt 和 answer 字段，按 prompt 排序
    # query = {"prompt": {"$regex": "你好"}, "model": "gemma3n:e4b"}
    # projection = {"prompt": 1, "answer": 1, "_id": 0}  # 1 表示包含，0 表示不包含
    # documents = chat_collection.find(query, projection).sort("prompt", 1)  # 1 表示升序，-1 表示降序
    # for document in documents:
    #     print(document)

    # 更新测试
    chat_collection.update_one({"prompt": "prompt_config"}, {"$set": {"prompts": ["你好", "你好"]}})
