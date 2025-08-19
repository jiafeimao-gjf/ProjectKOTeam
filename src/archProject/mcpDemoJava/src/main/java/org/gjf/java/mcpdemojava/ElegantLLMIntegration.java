import io.modelcontextprotocol.client.McpSyncClient;
import io.modelcontextprotocol.spec.McpSchema;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public class ElegantLLMIntegration {
    private final McpSyncClient mcpClient;
    private final LargeLanguageModel llm;
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final List<String> availableTools; // 可用工具列表，从MCP服务器获取

    public ElegantLLMIntegration(McpSyncClient client, LargeLanguageModel llm) {
        this.mcpClient = client;
        this.llm = llm;
        this.availableTools = initializeAvailableTools(); // 从服务器获取可用工具
    }

    // 处理用户查询的主方法
    public String processQuery(String userQuery) {
        System.out.println("用户问题: " + userQuery);

        // 1. 大模型自主判断是否需要调用工具（改进点：更智能的提示词）
        String decisionJson = llm.generate(buildToolNeedPrompt(userQuery));
        ToolDecision decision = parseDecision(decisionJson);

        if (decision.needTool()) {
            System.out.println("大模型决策：需要调用工具 - " + decision.reasoning());
            
            // 2. 选择最合适的工具（基于工具描述和能力）
            String toolSelection = llm.generate(buildToolSelectionPrompt(userQuery, decision.reasoning()));
            String toolName = extractToolName(toolSelection);
            System.out.println("选择工具: " + toolName);

            // 3. 生成符合工具要求的参数
            String toolSchema = getToolSchema(toolName); // 获取工具的参数Schema
            String paramsJson = llm.generate(buildParameterGenerationPrompt(userQuery, toolName, toolSchema));
            Map<String, Object> params = parseParameters(paramsJson);

            // 4. 调用工具并获取结果
            String toolResult = callTool(toolName, params);
            
            // 5. 生成最终回答
            return llm.generate(buildFinalAnswerPrompt(userQuery, toolResult));
        } else {
            System.out.println("大模型决策：不需要调用工具 - " + decision.reasoning());
            return llm.generate("请用自然语言详细回答用户问题：" + userQuery);
        }
    }

    // 构建更智能的工具需求判断提示词
    private String buildToolNeedPrompt(String query) {
        return """
        请分析以下用户问题是否需要调用外部工具获取信息，并以JSON格式返回决策结果：
        {
            "needTool": boolean,
            "reasoning": "详细说明判断依据，包括是否属于实时信息、是否超出你的知识截止日期、是否需要专业数据等"
        }
        
        用户问题：%s
        你的知识截止日期：2023年10月
        注意：如果问题涉及2023年10月之后的事件、实时变化的数据（天气、股价等）、需要最新统计的信息，必须调用工具。
        如果是常识性问题、历史事实（2023年10月前）、不需要实时数据的问题，可以不调用工具。
        """.formatted(query);
    }

    // 构建工具选择提示词
    private String buildToolSelectionPrompt(String query, String reasoning) {
        return """
        根据以下信息，从可用工具中选择最适合回答用户问题的工具，只需返回工具名称：
        
        用户问题：%s
        决策依据：%s
        可用工具及功能：
        %s
        """.formatted(query, reasoning, formatToolsForLLM());
    }

    // 构建参数生成提示词
    private String buildParameterGenerationPrompt(String query, String toolName, String schema) {
        return """
        请为工具"%s"生成符合以下JSON Schema的调用参数，用于回答用户问题：%s
        
        参数Schema：%s
        
        要求：
        1. 严格遵循Schema格式，包含所有必填字段
        2. 参数值需从用户问题中提取或合理推断
        3. 只返回JSON内容，不添加其他说明
        """.formatted(toolName, query, schema);
    }

    // 构建最终回答提示词
    private String buildFinalAnswerPrompt(String query, String toolResult) {
        return """
        请基于以下信息，用自然语言流畅、准确地回答用户问题：
        
        用户问题：%s
        工具返回的相关信息：%s
        
        要求：
        1. 只使用提供的工具信息进行回答
        2. 不要编造信息，如果信息不足请说明
        3. 语言简洁明了，符合中文表达习惯
        """.formatted(query, toolResult);
    }

    // 从MCP服务器获取可用工具列表
    private List<String> initializeAvailableTools() {
        try {
            McpSchema.ListToolsResult result = mcpClient.listTools();
            return result.tools().stream()
                    .map(tool -> tool.name() + ": " + tool.description())
                    .toList();
        } catch (Exception e) {
            System.err.println("获取工具列表失败: " + e.getMessage());
            return List.of();
        }
    }

    // 格式化工具信息供大模型阅读
    private String formatToolsForLLM() {
        StringBuilder sb = new StringBuilder();
        for (String tool : availableTools) {
            sb.append("- ").append(tool).append("\n");
        }
        return sb.toString();
    }

    // 获取工具的参数Schema
    private String getToolSchema(String toolName) {
        try {
            McpSchema.ListToolsResult result = mcpClient.listTools();
            return result.tools().stream()
                    .filter(t -> t.name().equals(toolName))
                    .findFirst()
                    .map(McpSchema.Tool::parameters)
                    .orElse("{}");
        } catch (Exception e) {
            return "{}";
        }
    }

    // 解析大模型的决策结果
    private ToolDecision parseDecision(String json) {
        try {
            return objectMapper.readValue(json, ToolDecision.class);
        } catch (Exception e) {
            System.err.println("解析决策结果失败: " + e.getMessage());
            return new ToolDecision(false, "解析决策失败，默认不调用工具");
        }
    }

    // 提取工具名称
    private String extractToolName(String toolSelection) {
        // 实际实现中可以更健壮，处理可能的格式问题
        return toolSelection.trim();
    }

    // 解析参数JSON
    private Map<String, Object> parseParameters(String json) {
        try {
            return objectMapper.readValue(json, Map.class);
        } catch (Exception e) {
            System.err.println("解析参数失败: " + e.getMessage());
            return Map.of();
        }
    }

    // 调用MCP工具
    private String callTool(String toolName, Map<String, Object> params) {
        try {
            McpSchema.CallToolRequest request = new McpSchema.CallToolRequest(
                    toolName,
                    params,
                    UUID.randomUUID().toString(),
                    Map.of("timeout", "15000")
            );

            McpSchema.CallToolResult result = mcpClient.callTool(request);
            return ((McpSchema.TextContent) result.content().get(0)).text();
        } catch (Exception e) {
            System.err.println("工具调用失败: " + e.getMessage());
            return "工具调用失败，无法获取相关信息";
        }
    }

    // 工具决策数据类
    private static class ToolDecision {
        private final boolean needTool;
        private final String reasoning;

        public ToolDecision(boolean needTool, String reasoning) {
            this.needTool = needTool;
            this.reasoning = reasoning;
        }

        public boolean needTool() { return needTool; }
        public String reasoning() { return reasoning; }
    }

    // 大模型接口
    public interface LargeLanguageModel {
        String generate(String prompt);
    }

    // 主方法示例
    public static void main(String[] args) {
        // 初始化MCP客户端和大模型（实际项目中替换为真实实现）
        McpSyncClient mcpClient = createMockMcpClient();
        LargeLanguageModel llm = createMockLLM();

        // 处理用户查询
        ElegantLLMIntegration integration = new ElegantLLMIntegration(mcpClient, llm);
        String response = integration.processQuery("2024年巴黎奥运会的开幕时间是什么时候？");
        System.out.println("\n最终回答: " + response);

        mcpClient.closeGracefully();
    }

    // 创建模拟MCP客户端
    private static McpSyncClient createMockMcpClient() {
        return new McpSyncClient() {
            @Override
            public McpSchema.ListToolsResult listTools() {
                // 模拟可用工具
                McpSchema.Tool searchTool = new McpSchema.Tool(
                        "internet_search",
                        "搜索互联网获取最新信息",
                        """
                        {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "搜索关键词"},
                                "language": {"type": "string", "description": "语言，默认中文"}
                            },
                            "required": ["query"]
                        }
                        """
                );
                return new McpSchema.ListToolsResult(List.of(searchTool));
            }

            @Override
            public McpSchema.CallToolResult callTool(McpSchema.CallToolRequest request) {
                // 模拟搜索结果
                return new McpSchema.CallToolResult(
                        List.of(new McpSchema.TextContent(
                                "2024年巴黎奥运会于2024年7月26日开幕，8月11日闭幕"
                        ))
                );
            }

            @Override public void closeGracefully() {}
            // 其他必要方法实现...
        };
    }

    // 创建模拟大模型
    private static LargeLanguageModel createMockLLM() {
        return prompt -> {
            System.out.println("\n大模型处理提示: " + prompt.substring(0, 80) + "...");
            
            // 模拟不同提示的返回结果
            if (prompt.contains("是否需要调用外部工具")) {
                return """
                {
                    "needTool": true,
                    "reasoning": "用户问题涉及2024年奥运会的开幕时间，我的知识截止到2023年10月，无法提供准确信息，需要调用工具获取最新数据"
                }
                """;
            } else if (prompt.contains("选择最适合回答用户问题的工具")) {
                return "internet_search";
            } else if (prompt.contains("生成符合以下JSON Schema的调用参数")) {
                return """
                {
                    "query": "2024年巴黎奥运会 开幕时间",
                    "language": "zh-CN"
                }
                """;
            } else {
                return "2024年巴黎奥运会的开幕时间是2024年7月26日，闭幕时间为8月11日。这是第33届夏季奥林匹克运动会，将在法国巴黎举办。";
            }
        };
    }
}
    