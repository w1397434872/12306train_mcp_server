# MCP Server 12306 Train

[![PyPI version](https://badge.fury.io/py/mcp-server-12306train-ylg.svg)](https://pypi.org/project/mcp-server-12306train-ylg/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 的 12306 火车票查询服务器，支持自然语言查询火车票余票信息。

## 功能特点

- 🔍 **智能查询** - 支持自然语言查询，如"明天北京到上海有票吗"
- 📅 **相对日期** - 支持"今天"、"明天"、"后天"等相对日期描述
- 🚄 **车次信息** - 查询高铁、动车、普通列车等多种车次
- 💺 **余票信息** - 实时显示商务座、一等座、二等座、软卧、硬卧、硬座余票
- 🏷️ **车站代码** - 内置常用车站电报码，支持中文车站名自动转换
- 🔌 **MCP 协议** - 基于 MCP 协议，可与 Claude、Cline 等 AI 助手集成

## 安装

```bash
pip install mcp-server-12306train-ylg
```

## 使用方法

### 1. 作为 MCP Server 运行

#### 使用 Claude Desktop

在 Claude Desktop 配置文件中添加：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "12306": {
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "python",
      "args": [
        "D:\\12306查票助手智能体\\src\\12306_mcp.py"
      ]
    }
}



#uv启动
{
  "mcpServers": {
    "12306": {
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "uvx",
      "args": [
        "mcp-server-12306train-ylg"
      ]
    }
}


```

#### 使用 Cline (VS Code 插件)

在 Cline 的 MCP 设置中添加：

```json
{
  "mcpServers": {
    "12306": {
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "python",
      "args": [
        "D:\\12306查票助手智能体\\src\\12306_mcp.py"
      ]
    }
}



#uv启动
{
  "mcpServers": {
    "12306": {
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "uvx",
      "args": [
        "mcp-server-12306train-ylg"
      ]
    }
}

```

### READM

### 2. 直接运行

```bash
python -m mcp_server_12306train_ylg
```

### 3. 在代码中使用

```python
from mcp_server_12306train_ylg import mcp

# 启动服务器
mcp.run()
```

### 4. 使用 MCP 客户端智能体

项目包含一个完整的 MCP 客户端示例 (`agent/`)，可以像 Cline 一样调用 MCP Server 并集成大模型 API：

#### 配置环境变量

在 `agent/.env` 文件中配置：

```env
# 大模型 API 配置
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus

# MCP Server 配置
PYTHON_PATH=D:/adaconda/envs/agent/python.exe
MCP_SERVER_PATH=d:/12306查票助手智能体/src/12306_mcp.py
```

#### 运行客户端

```bash
cd agent
python mcp_client.py
```

#### 客户端功能

- 🤖 **AI 对话** - 集成大模型 API，支持自然语言交互
- 🔧 **自动工具调用** - 大模型自动判断何时调用 MCP 工具
- 💬 **交互式聊天** - 类似 Cline 的交互体验
- 🔑 **环境变量配置** - 所有配置通过 `.env` 文件管理

#### 使用示例

```
============================================================
12306 火车票查询助手
============================================================
提示: 输入 'quit' 或 'exit' 退出
示例: 明天北京到上海有票吗
============================================================

[INFO] 正在启动 MCP Server...
[INFO] 已连接到 12306 MCP Server

你: 明天西安到兰州有票吗

助手: 正在查询...

助手:
查询日期: 2025-04-02
出发站: 西安 (XAY)
到达站: 兰州 (LZJ)
============================================================
   车次  出发时间  到达时间    历时 商务座 一等座 二等座 可预订
  G352  15:54    18:23    02:29   Yes   Yes   Yes    是
  G466  12:56    15:37    02:41   Yes   Yes   Yes    是
  ...
============================================================
共找到 15 个车次
```

## 可用工具

### check_tick

查询指定日期、出发站和到达站的火车票余票信息。

**参数：**

- `date` (string): 查询日期，格式为 YYYY-MM-DD，或支持"今天"、"明天"、"后天"等相对日期
- `start` (string): 出发站名称（如：北京、上海）或电报码（如：BJP、SHH）
- `end` (string): 到达站名称或电报码

**示例：**

```
查询明天北京到上海的火车票
check_tick(date="明天", start="北京", end="上海")
```

### check_date

获取当前日期，用于处理相对日期查询。

### get_station_code_tool

根据车站名称查询对应的电报码。

**参数：**

- `station_name` (string): 车站名称，如：北京、上海、广州

## 支持的车站

内置常用车站电报码：

| 车站名称 | 电报码 |
| -------- | ------ |
| 北京     | BJP    |
| 北京南   | VNP    |
| 上海     | SHH    |
| 上海虹桥 | AOH    |
| 广州     | GZQ    |
| 广州南   | IZQ    |
| 深圳     | SZQ    |
| 深圳北   | IOQ    |
| 杭州     | HZH    |
| 南京     | NJH    |
| 武汉     | WHN    |
| 成都     | CDW    |
| 重庆     | CQW    |
| 西安     | XAY    |
| 郑州     | ZZF    |
| 长沙     | CSQ    |
| ...      | ...    |

完整列表请使用 `get_station_code_tool` 查询。

## 查询示例

### 示例 1: 查询明天北京到上海的火车票

```
用户: 明天北京到上海有票吗？

助手: 正在查询...

查询日期: 2025-04-02
出发站: 北京 (BJP)
到达站: 上海 (SHH)
============================================================
   车次  出发时间  到达时间    历时 商务座 一等座 二等座 可预订
   G1    06:30    11:24    04:54    No   Yes   Yes    是
   G3    06:52    11:33    04:41    No   Yes   Yes    是
   G5    07:42    12:32    04:50    No   Yes   Yes    是
  ...
============================================================
共找到 53 个车次
```

### 示例 2: 查询车站代码

```
用户: 成都的车站代码是什么？

助手: 成都 的电报码是: CDW
```

## 技术栈

- [FastMCP](https://github.com/PrefectHQ/fastmcp) - MCP 框架
- [Pydantic](https://docs.pydantic.dev/) - 数据验证
- [Requests](https://requests.readthedocs.io/) - HTTP 请求
- [Pandas](https://pandas.pydata.org/) - 数据格式化

## 项目结构

```
mcp-server-12306train-ylg/
├── src/
│   └── mcp_server_12306train_ylg/
│       ├── __init__.py
│       └── 12306_mcp.py          # MCP Server 主程序
├── agent/                         # MCP 客户端智能体示例
│   ├── mcp_client.py             # 客户端主程序
│   ├── .env                      # 环境变量配置
│   └── .env.example              # 环境变量示例
├── README.md
├── pyproject.toml
└── LICENSE
```

## 注意事项

1. 本工具仅供学习交流使用，请勿用于商业用途
2. 查询结果仅供参考，实际购票请以 12306 官网为准
3. 频繁查询可能会被 12306 限制，请合理使用
4. 车站电报码数据可能不完整，如遇查询失败请尝试使用标准车站名称

## 许可证

[MIT License](LICENSE)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v0.1.0 (2025-04-03)

- 初始版本发布
- 支持火车票余票查询
- 支持相对日期查询
- 支持常用车站代码自动转换
- 基于 MCP 协议，可与 AI 助手集成

## 联系方式

- 作者: ylg
- PyPI: https://pypi.org/project/mcp-server-12306train-ylg/
- GitHub: [你的 GitHub 仓库地址]

---

**免责声明**: 本项目与 12306 官方网站无关，仅作为技术学习交流使用。使用本项目产生的任何后果由使用者自行承担。
