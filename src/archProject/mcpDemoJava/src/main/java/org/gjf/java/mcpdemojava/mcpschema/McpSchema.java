package org.gjf.java.mcpdemojava.mcpschema;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;

public class McpSchema {
    public static final String MCP_SCHEMA_VERSION = "1.0.0";

    public static class ListToolsResult {
        public List<Tool> tools;
        public String version;

        public List<Tool> tools() {
            return new ArrayList<>(tools);
        }

        public ListToolsResult(List<Tool> tools) {
            this.tools = tools;
            this.version = MCP_SCHEMA_VERSION;
        }
    }


    public static class Tool {
        public String name;
        public String description;
        public String parameters;
        public Tool(String name, String description, String parameters) {
            this.name = name;
            this.description = description;
            this.parameters = parameters;
        }

        public String parameters()  {
            return parameters;
        }
    }

    public static class CallToolRequest {
        public String toolName;
        public Map<String, Object> params;
        public Map<String, String> extras;
        public String parameters;
        public CallToolRequest(String toolName,  Map<String, Object> params,String parameters,Map<String, String> extras) {
            this.toolName = toolName;
            this.params = params;
            this.parameters = parameters;
        }
    }

    public static class CallToolResult {
        public List<TextContent> contents;
        public CallToolResult(List<TextContent> contents) {
            this.contents = contents;
        }
    }

    public static class TextContent{
        public String content;
        public String text;

        public TextContent(String string) {
            content = string;
        }



    }
}
