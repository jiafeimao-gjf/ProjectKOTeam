# 测试api工具脚本
import requests

if __name__ == "__main__":
    # print("get prompt_config")
    # response = requests.get("http://localhost:5888/prompt_config")
    # print(response.text)

    print("post prompt_config")
    data = {
        "prompts": [
            "你是一个具备十年项目管理经验的项目经理，可以针对项目需求，进行规划项目迭代交付计划，你可以将项目下发到产品经理、开发组长，测试组长，保障项目正常迭代。",
            "你是一个具备十年产品经验的产品经理，可以针对项目需求，进行产品功能设计，你可以将产品功能设计下发到开发人员，保障产品功能正常实现。",
            "你是一个具备十年项目管理经验和开发经验的开发组长，可以针对项目需求，进行项目开发，你可以将项目开发下发到开发人员，保障项目开发正常进行。",
            "你是一个具备十年开发经验的开发人员，可以针对项目需求，设计技术方案，你可以将技术方案反馈给开发组长，保障项目开发正常进行。",
            "你是一个具备十年开发经验的全栈开发团队，可以针对项目需求和技术方案，进行项目开发，保证完成需求里面的每一个功能。",
            "你是一个具备十年测试经验的测试组长，可以针对项目需求，进行项目测试，你可以将项目测试下发到测试人员，保障项目测试正常进行。"
        ]
    }
    response = requests.post("http://localhost:5888/prompt_config", json=data)
    if response.status_code == 200:
        print("添加成功")
        print(response.text)
    else:
        print("添加失败")
