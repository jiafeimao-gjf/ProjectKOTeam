# 本项目说明

本项目来源是想通过 大模型能力，构建一个自动化的外包团队，或者 软件项目孵化器。

接触大模型辅助，规划功能点，利用本地部署模型，测试功能，

# 快速开始，动手本地部署体验
- 前置准备
    - ollama下载和安装，[链接](https://ollama.com/library)
    - 下载一个小模型，体验ollama端的问答
```shell
ollama run gemma3:4b
# 等待下载完成，进行终端问答
```
- node环境准备，v20+
- python环境准备


  
- clone项目
```shell
git clone https://github.com/jiafeimao-gjf/ProjectKOTeam.git
```
- vscode 打开 项目
- 前端启动
```shell
cd ProjectKOTeam

cd src/frontendProject/aiSEfrontend

npm install 
# 启动项目
npm run dev

```
- 后端启动

```shell
cd ProjectKOTeam

cd src/backendProject/llmService

# 初始化Python虚拟环境

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Linux/macOS）
source venv/bin/activate

# 激活虚拟环境（Windows）
venv\Scripts\activate


# 安装依赖包

pip install ollama flask pymongo


# 终端启动项目
python app.py
```

# 项目介绍
## 前端项目：src/frontendProject/aiSEfrontend

> 基于vite 初始化的项目，UI由copilot辅助开发而成。

### 单独对话功能：

采用一问一答的模式，支持选择本地下载的模型进行问答。

![](images/本地agent助手问答.png)

### 多模型自主对话功能：

采用一问一答的模式，支持选择不同的本地下载的模型进行问答。

![](images/本地agent助手问答.png)

### 软件开发链式回答功能V1：

结合预置prompt，和提问的问题，支持选择本地下载的模型进行问答，大模型会进行多轮回答，尽可能完善项目开发相关文档输出和代码输出。

![](images/软件项目链式分析.png)

### 自定义链式回答的功能：

结合预置prompt，和提问的问题，支持选择本地下载的模型进行问答，大模型会进行多轮回答，尽可能完善答案。

![](images/自定义链式思考内容生成.png)

### 软件开发链式回答功能V2：

结合更完备的预置prompt，和提问的问题，支持选择本地下载的模型进行问答，大模型会进行多轮回答，尽可能完善项目开发相关文档输出和代码输出。

![](images/全流程项目设计和开发.png)


## 后端项目：src/backendProject/llmService

后端集成ollama模型部署和调用功能，支持问答历史保存文件、插入到mangodb。

### 接口说明

- /chat_start接口：post请求接受prompt 和 model参数，返回带有uuid的/chat url，用于流式接收答案
- /chat：流式接口，用于回答和答案保存

### 大模型调用说明
- 简单集成ollama，支持制定模型进行答案生成。
- 也可以集成其他大模型调用，例如云厂商提供的大模型调用。

```python
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

```