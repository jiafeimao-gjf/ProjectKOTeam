# fsm_controller.py
# 该模块实现了一个基于有限状态机的AI软件开发流程控制器
# 使用 transitions 库实现状态机功能
import os
import random

from transitions import Machine
import logging
from typing import Dict, Any

from src.backendProject.AISE.ollama_utils import ollama_sync

# 配置日志系统，设置日志级别为INFO
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 模拟外部组件（可替换为真实 LLM 或工具）
class LLMDriver:
    """使用本地 Ollama 模型的大模型驱动器"""
    # 默认使用的模型名称，可以根据需要更改为其他模型（如 llama3, qwen2, mistral 等）
    DEFAULT_MODEL = "gemma3n:e4b"  # 可改为 llama3, qwen2, mistral 等

    @staticmethod
    def ollama_generate(prompt: str, context: dict) -> str:
        """
        调用本地 Ollama 模型生成响应
        
        Args:
            prompt (str): 输入给模型的提示词
            context (dict): 上下文信息，包含模型配置等
            
        Returns:
            str: 模型生成的响应文本
        """
        # 从上下文中获取模型名称，如果不存在则使用默认模型
        model = context.get("model", LLMDriver.DEFAULT_MODEL)  # 支持上下文指定模型
        # 调用 ollama_sync 函数与模型交互
        answer = ollama_sync(prompt, model)

        return answer


class Validator:
    """验证器类，用于验证各个阶段的输出是否符合要求"""

    @staticmethod
    def validate_requirement(output: str) -> bool:
        """
        验证需求分析阶段的输出是否包含必要关键词
        
        Args:
            output (str): 需求分析阶段的输出文本
            
        Returns:
            bool: 如果包含所有必要关键词则返回True，否则返回False
        """
        # 检查输出是否包含"功能"、"角色"、"用例"等关键词
        return all(keyword in output.lower() for keyword in ["功能", "角色", "用例"])

    @staticmethod
    def validate_design(output: str) -> bool:
        """
        验证系统设计阶段的输出是否包含必要关键词
        
        Args:
            output (str): 系统设计阶段的输出文本
            
        Returns:
            bool: 如果包含所有必要关键词则返回True，否则返回False
        """
        # 检查输出是否包含"模块"、"api"、"数据库"等关键词
        return all(keyword in output.lower() for keyword in ["模块", "api", "数据库"])

    @staticmethod
    def validate_code(output: str) -> bool:
        """
        验证代码实现阶段的输出是否包含Python代码的基本结构
        
        Args:
            output (str): 代码实现阶段的输出文本
            
        Returns:
            bool: 如果包含代码结构则返回True，否则返回False
        """
        # 检查输出是否包含Python代码的基本结构（def/class/function）
        return "def " in output or "class " in output or "function" in output

    @staticmethod
    def run_tests() -> bool:
        """
        模拟执行测试
        
        Returns:
            bool: 测试是否通过（模拟实现，有2/3概率通过）
        """
        import random
        # 随机选择测试结果（模拟实现，有2/3概率通过）
        success = random.choice([True, True, False])
        logger.info(f"🧪 测试执行结果: {'✅ 通过' if success else '❌ 失败'}")
        return success


# 主控制器类，实现基于有限状态机的AI软件开发流程控制
def save_file(project_name, prompt, result, state):
    if not os.path.exists(f"se_history_{project_name}"):
        os.mkdir(f"se_history_{project_name}")
    with open(f"se_history_{project_name}/history_{state}.md", "a+", encoding="utf-8") as f:
        f.write(f"# prompt: {prompt}\n")
        f.write(f"# answer: \n {result}\n")


class AISOftwareFSM:
    """AI软件开发流程状态机控制器"""

    def __init__(self):
        """
        初始化状态机控制器，设置初始状态和状态转移规则
        """
        # 项目上下文，用于在不同阶段之间传递信息
        self.project_context: Dict[str, Any] = {
            "user_input": "",  # 用户输入的需求
            "requirements": "",  # 需求分析结果
            "design": "",  # 系统设计结果
            "code": "",  # 代码实现结果
            "tests": "",  # 测试代码
            "test_report": "",  # 测试报告
            "documentation": "",  # 项目文档
            "model": "gemma3:12b"  # 使用的模型
        }

        # 定义状态机的所有状态
        self.states = [
            'idle',  # 空闲状态
            'requirement_analysis',  # 需求分析阶段
            'system_design',  # 系统设计阶段
            'code_implementation',  # 编码实现阶段
            'test_generation',  # 测试生成阶段
            'testing_validation',  # 测试验证阶段
            'documentation',  # 文档生成阶段
            'success',  # 成功完成状态
            'error_intervention'  # 错误干预状态
        ]

        # 定义状态转移规则，每个转移包含触发条件、源状态和目标状态
        self.transitions = [
            {'trigger': 'start_analysis', 'source': 'idle', 'dest': 'requirement_analysis'},  # 启动分析
            {'trigger': 'to_design', 'source': 'requirement_analysis', 'dest': 'system_design'},  # 进入设计
            {'trigger': 'to_coding', 'source': 'system_design', 'dest': 'code_implementation'},  # 进入编码
            {'trigger': 'to_test_gen', 'source': 'code_implementation', 'dest': 'test_generation'},  # 进入测试生成
            {'trigger': 'to_testing', 'source': 'test_generation', 'dest': 'testing_validation'},  # 进入测试验证
            {'trigger': 'to_document', 'source': 'testing_validation', 'dest': 'documentation'},  # 进入文档生成
            {'trigger': 'finish', 'source': 'documentation', 'dest': 'success'},  # 完成流程
            {'trigger': 'fail_to_intervention', 'source': '*', 'dest': 'error_intervention'},  # 进入错误干预
            {'trigger': 'recover_from_intervention', 'source': 'error_intervention', 'dest': 'requirement_analysis'},
            # 从错误干预恢复到需求分析
            {'trigger': 'recover_to_design', 'source': 'error_intervention', 'dest': 'system_design'},  # 从错误干预恢复到系统设计
            {'trigger': 'recover_to_coding', 'source': 'error_intervention', 'dest': 'code_implementation'},
            # 从错误干预恢复到编码实现
            {'trigger': 'recover_to_test_gen', 'source': 'error_intervention', 'dest': 'test_generation'},
            # 从错误干预恢复到测试生成
            {'trigger': 'recover_to_document', 'source': 'error_intervention', 'dest': 'documentation'},  # 从错误干预恢复到文档生成
            {'trigger': 'manual_finish', 'source': 'error_intervention', 'dest': 'success'},  # 手动完成流程
        ]

        # 初始化状态机，设置初始状态为'idle'，禁用自动状态转移
        self.machine = Machine(model=self, states=self.states, transitions=self.transitions,
                               initial='idle', auto_transitions=False)

        # 绑定状态进入时的回调函数
        self.machine.on_enter_requirement_analysis('on_enter_requirement_analysis')  # 进入需求分析状态
        self.machine.on_enter_system_design('on_enter_system_design')  # 进入系统设计状态
        self.machine.on_enter_code_implementation('on_enter_code_implementation')  # 进入编码实现状态
        self.machine.on_enter_test_generation('on_enter_test_generation')  # 进入测试生成状态
        self.machine.on_enter_testing_validation('on_enter_testing_validation')  # 进入测试验证状态
        self.machine.on_enter_documentation('on_enter_documentation')  # 进入文档生成状态
        self.machine.on_enter_error_intervention('on_enter_error_intervention')  # 进入错误干预状态
        self.machine.on_enter_success('on_enter_success')  # 进入成功完成状态

    def set_project_name(self, project_name):
        self.project_context["project_name"] = project_name

    def run(self, user_input: str):
        """
        启动整个AI软件开发流程
        
        Args:
            user_input (str): 用户输入的需求描述
        """
        # 保存用户输入到项目上下文
        self.project_context['user_input'] = user_input
        logger.info("🚀 启动 AI 软件开发流程")
        # 触发状态机开始分析
        self.start_analysis()

    # === 状态进入回调函数 ===

    def on_enter_requirement_analysis(self):
        """
        进入需求分析阶段时的回调函数
        负责调用LLM进行需求分析，并验证分析结果
        """
        logger.info("🔍 进入【需求分析】阶段")
        # 构造提示词，要求LLM将用户需求转化为结构化软件需求文档
        prompt = """
        你是一个资深需求分析师。请将以下用户需求转化为结构化软件需求文档：
        {user_input}
        输出格式：JSON，包含字段：功能列表、用户角色、用例描述、非功能需求。
        """.format(user_input=self.project_context['user_input'])
        try:
            # 调用LLM生成需求分析结果
            result = LLMDriver.ollama_generate(prompt, self.project_context)
            # 保存需求分析结果到项目上下文
            self.project_context['requirements'] = result
            # 调用保存文件函数
            save_file(self.project_context["project_name"], prompt, result, "需求分析结果")
            # 验证需求分析结果是否符合要求
            if Validator.validate_requirement(result):
                logger.info("✅ 需求分析完成，验证通过")
                # 验证通过，进入系统设计阶段
                self.to_design()
            else:
                logger.warning("❌ 需求验证失败，进入人工干预")
                # 验证失败，进入错误干预状态
                self.fail_to_intervention()
        except Exception as e:
            # 处理异常情况，进入错误干预状态
            logger.error(f"需求分析失败: {e}")
            self.fail_to_intervention()

    def on_enter_system_design(self):
        """
        进入系统设计阶段时的回调函数
        负责调用LLM进行系统设计，并验证设计结果
        """
        logger.info("🏗️ 进入【系统设计】阶段")
        # 构造提示词，要求LLM根据需求分析结果设计系统架构
        prompt = f"""
        根据以下需求设计系统架构：
        {self.project_context['requirements']}
        请输出：模块划分、API 接口定义、数据库 schema。
        """
        try:
            # 调用LLM生成系统设计结果
            result = LLMDriver.ollama_generate(prompt, self.project_context)
            # 保存系统设计结果到项目上下文
            self.project_context['design'] = result
            # 调用保存文件函数
            save_file(self.project_context["project_name"], prompt, result, "系统设计结果")
            # 验证系统设计结果是否符合要求
            if Validator.validate_design(result):
                logger.info("✅ 系统设计完成，验证通过")
                # 验证通过，进入编码实现阶段
                self.to_coding()
            else:
                logger.warning("❌ 设计验证失败")
                # 验证失败，进入错误干预状态
                self.fail_to_intervention()
        except Exception as e:
            # 处理异常情况，进入错误干预状态
            logger.error(f"设计失败: {e}")
            self.fail_to_intervention()

    def on_enter_code_implementation(self):
        """
        进入编码实现阶段时的回调函数
        负责调用LLM进行代码生成，并验证代码格式
        """
        logger.info("💻 进入【编码实现】阶段")
        # 构造提示词，要求LLM根据系统设计生成Python代码
        prompt = f"""
        根据以下设计生成 Python 代码：
        {self.project_context['design']}
        要求：使用 Flask + SQLite，模块化结构。
        """
        try:
            # 调用LLM生成代码实现
            result = LLMDriver.ollama_generate(prompt, self.project_context)
            # 保存代码实现到项目上下文
            self.project_context['code'] = result
            # 调用保存文件函数
            save_file(self.project_context["project_name"], prompt, result, "编码实现结果")
            # 验证代码实现是否符合要求
            if Validator.validate_code(result):
                logger.info("✅ 代码生成完成，语法检查通过")
                # 验证通过，进入测试生成阶段
                self.to_test_gen()
            else:
                logger.warning("❌ 代码格式不合规")
                # 验证失败，进入错误干预状态
                self.fail_to_intervention()
        except Exception as e:
            # 处理异常情况，进入错误干预状态
            logger.error(f"代码生成失败: {e}")
            self.fail_to_intervention()

    def on_enter_test_generation(self):
        """
        进入测试生成阶段时的回调函数
        负责调用LLM生成单元测试代码
        """
        logger.info("🧪 进入【测试生成】阶段")
        # 构造提示词，要求LLM为生成的代码编写单元测试
        prompt = f"""
        为以下代码生成单元测试：
        {self.project_context['code']}
        使用 pytest 框架。
        """
        try:
            # 调用LLM生成测试代码
            result = LLMDriver.ollama_generate(prompt, self.project_context)
            # 保存测试代码到项目上下文
            self.project_context['tests'] = result
            # 调用保存文件函数
            save_file(self.project_context["project_name"], prompt, result, "测试生成结果")
            logger.info("✅ 测试代码生成")
            # 进入测试验证阶段
            self.to_testing()
        except Exception as e:
            # 处理异常情况，进入错误干预状态
            logger.error(f"测试生成失败: {e}")
            self.fail_to_intervention()

    def on_enter_testing_validation(self):
        """
        进入测试验证阶段时的回调函数
        负责执行测试并验证测试结果
        """
        logger.info("⚙️ 进入【测试执行与验证】阶段")
        try:
            # 执行测试
            test_passed = Validator.run_tests()
            if test_passed:
                logger.info("✅ 所有测试通过")
                # 测试通过，进入文档生成阶段
                self.to_document()
            else:
                logger.warning("❌ 测试失败，返回编码阶段修复")
                # 测试失败，记录测试报告并返回编码实现阶段
                self.project_context['test_report'] = "测试失败，需修复"
                self.to_coding()  # 自动回退到编码
        except Exception as e:
            # 处理异常情况，进入错误干预状态
            logger.error(f"测试执行异常: {e}")
            self.fail_to_intervention()

    def on_enter_documentation(self):
        """
        进入文档生成阶段时的回调函数
        负责调用LLM生成项目文档
        """
        logger.info("📄 进入【文档生成】阶段")
        # 构造提示词，要求LLM生成项目文档
        prompt = f"""
        生成项目文档，包括：
        - README
        - API 文档
        - 部署说明
        基于以下内容：
        需求: {self.project_context['requirements']}
        设计: {self.project_context['design']}
        代码: {self.project_context['code']}...
        """
        try:
            # 调用LLM生成项目文档
            result = LLMDriver.ollama_generate(prompt, self.project_context)
            # 保存项目文档到项目上下文
            self.project_context['documentation'] = result
            # 调用保存文件函数
            save_file(self.project_context["project_name"], prompt, result, "文档生成结果")
            logger.info("✅ 文档生成完成")
            # 文档生成完成，进入成功完成状态
            self.finish()
        except Exception as e:
            # 处理异常情况，进入错误干预状态
            logger.error(f"文档生成失败: {e}")
            self.fail_to_intervention()

    def on_enter_error_intervention(self):
        """
        进入错误干预状态时的回调函数
        提示用户需要人工干预处理错误
        """
        logger.warning("🛑 进入【人工干预】状态")
        logger.info("请检查问题并调用 recover_* 方法恢复流程")
        msg = input("请输入修复信息：")
        self.project_context['intervention_info'] = msg
        if msg == "exit":
            self.fail()
        elif msg == "recover":
            self.to_coding()
        # 实际中可阻塞等待用户输入或 API 调用

    def on_enter_success(self):
        """
        进入成功完成状态时的回调函数
        输出最终项目摘要信息
        """
        logger.info("🎉 流程成功完成！")
        logger.info("最终项目上下文已保存。")
        # 可导出为文件、ZIP 包等
        print("\n=== 最终项目摘要 ===")
        print(f"用户需求: {self.project_context['user_input']}")
        print(f"状态: 成功交付")

    def get_context(self) -> Dict[str, Any]:
        """
        获取当前项目上下文（用于调试或前端展示）
        
        Returns:
            Dict[str, Any]: 当前项目上下文的副本
        """
        return self.project_context.copy()


# ======================
# 使用示例
# ======================
if __name__ == "__main__":
    # 创建状态机实例
    fsm = AISOftwareFSM()

    # 用户输入需求
    user_request = "开发一个待办事项应用，支持增删改查，使用 Python Flask 和 SQLite。"
    fsm.set_project_name("todo_app")

    # 启动流程
    fsm.run(user_request)

    # 模拟流程结束后查看上下文
    # context = fsm.get_context()
    # print(json.dumps(context, indent=2, ensure_ascii=False))
