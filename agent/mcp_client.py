"""
MCP 客户端 - 类似 Cline 的交互式火车票查询助手
支持调用 12306 MCP Server 和大模型 API
"""

import os
import asyncio
import json
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

# 加载环境变量
load_dotenv()


class MCPClient:
    """MCP 客户端类"""
    
    def __init__(self):
        # 大模型配置（从环境变量读取）
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL")
        self.model = os.getenv("LLM_MODEL")
        
        # MCP Server 配置
        self.python_path = os.getenv("PYTHON_PATH")
        self.mcp_server_path = os.getenv("MCP_SERVER_PATH")
        
        # 初始化 OpenAI 客户端
        if self.api_key:
            self.llm_client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            self.llm_client = None
            print("警告: 未设置 LLM_API_KEY，将只使用 MCP 工具调用")
    
    async def connect_mcp_server(self):
        """连接到 MCP Server"""
        transport = StdioTransport(
            command=self.python_path,
            args=[self.mcp_server_path]
        )
        print("[INFO] 正在启动 MCP Server...")
        
        self.mcp_client = Client(transport)
        await self.mcp_client.__aenter__()
        print("[INFO] 已连接到 12306 MCP Server")
    
    async def disconnect(self):
        """断开 MCP Server 连接"""
        if hasattr(self, 'mcp_client'):
            await self.mcp_client.__aexit__(None, None, None)
            print("[INFO] 已断开 MCP Server 连接")
    
    async def call_mcp_tool(self, tool_name: str, arguments: dict):
        """调用 MCP 工具"""
        try:
            result = await self.mcp_client.call_tool(
                name=tool_name,
                arguments=arguments
            )
            return result
        except Exception as e:
            return f"调用工具出错: {str(e)}"
    
    def chat_with_llm(self, messages: list, tools: Optional[list] = None):
        """与大模型对话"""
        if not self.llm_client:
            return "错误: 未配置大模型 API"
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0,
                max_tokens=2048,
                tools=tools if tools else None
            )
            return response.choices[0].message
        except Exception as e:
            return f"大模型调用出错: {str(e)}"
    
    def get_mcp_tools_schema(self):
        """获取 MCP 工具的模式定义，用于大模型 function calling"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "check_tick",
                    "description": "查询指定日期、出发站和到达站的火车票余票信息。支持相对日期如'今天'、'明天'、'后天'等。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "查询日期，格式为YYYY-MM-DD，或支持'今天'、'明天'、'后天'等相对日期"
                            },
                            "start": {
                                "type": "string",
                                "description": "出发站名称（如：北京、上海、广州）或电报码（如：BJP、SHH）"
                            },
                            "end": {
                                "type": "string",
                                "description": "到达站名称（如：北京、上海、广州）或电报码（如：BJP、SHH）"
                            }
                        },
                        "required": ["date", "start", "end"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_date",
                    "description": "获取当前日期，用于处理相对日期查询",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_station_code_tool",
                    "description": "根据车站名称查询对应的电报码",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "station_name": {
                                "type": "string",
                                "description": "车站名称，如：北京、上海、广州"
                            }
                        },
                        "required": ["station_name"]
                    }
                }
            }
        ]
    
    async def process_query(self, user_input: str):
        """处理用户查询"""
        # 构建系统提示
        system_prompt = """你是一个火车票查询助手。你可以帮助用户查询12306火车票信息。

你可以使用以下工具：
1. check_tick - 查询火车票余票信息
2. check_date - 获取当前日期
3. get_station_code_tool - 查询车站电报码

当用户询问火车票信息时，请使用工具查询并整理结果，以清晰的格式回答用户。
如果用户没有指定具体日期，可以询问或默认使用明天。
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # 获取工具定义
        tools = self.get_mcp_tools_schema()
        
        # 第一次调用大模型
        response = self.chat_with_llm(messages, tools)
        
        if isinstance(response, str):  # 出错
            return response
        
        # 处理工具调用
        while response.tool_calls:
            # 添加助手消息到对话
            messages.append({
                "role": "assistant",
                "content": response.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in response.tool_calls
                ]
            })
            
            # 执行工具调用
            for tool_call in response.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                print(f"🔧 调用工具: {tool_name}({arguments})")
                
                # 调用 MCP 工具
                result = await self.call_mcp_tool(tool_name, arguments)
                
                # 添加工具结果到对话
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": str(result)
                })
            
            # 再次调用大模型
            response = self.chat_with_llm(messages, tools)
            if isinstance(response, str):
                return response
        
        # 返回最终回复
        return response.content
    
    async def interactive_chat(self):
        """交互式对话模式"""
        print("\n" + "="*60)
        print("12306 火车票查询助手")
        print("="*60)
        print("-" * 60)
        print("提示: 输入 'quit' 或 'exit' 退出")
        print("示例: 明天北京到上海有票吗")
        print("="*60 + "\n")
        
        # 连接到 MCP Server
        await self.connect_mcp_server()
        
        try:
            while True:
                # 获取用户输入
                user_input = input("\n👤 你: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("👋 再见！")
                    break
                
                # 处理查询
                print("\n🤖 助手: 正在查询...")
                try:
                    response = await self.process_query(user_input)
                    print(f"\n🤖 助手:\n{response}")
                except Exception as e:
                    print(f"\n❌ 出错: {str(e)}")
        
        finally:
            # 断开连接
            await self.disconnect()


async def main():
    """主函数"""
    client = MCPClient()
    await client.interactive_chat()


if __name__ == "__main__":
    asyncio.run(main())
