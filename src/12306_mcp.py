"""
12306 火车票查询 MCP Server
使用 FastMCP 框架实现 Model Context Protocol
"""

import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
from pydantic import Field
from fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("12306 Ticket Query")

# 常用车站电报码映射表
STATION_CODES = {
    "北京": "BJP",
    "北京南": "VNP",
    "北京西": "BXP",
    "上海": "SHH",
    "上海虹桥": "AOH",
    "上海南": "SNH",
    "天津": "TJP",
    "天津西": "TXP",
    "广州": "GZQ",
    "广州南": "IZQ",
    "深圳": "SZQ",
    "深圳北": "IOQ",
    "杭州": "HZH",
    "杭州东": "HGH",
    "南京": "NJH",
    "南京南": "NKH",
    "武汉": "WHN",
    "武汉站": "WHN",
    "成都": "CDW",
    "成都东": "ICW",
    "重庆": "CQW",
    "重庆北": "CUW",
    "西安": "XAY",
    "西安北": "EAY",
    "郑州": "ZZF",
    "郑州东": "ZAF",
    "长沙": "CSQ",
    "长沙南": "CWQ",
    "济南": "JNK",
    "济南西": "JGK",
    "青岛": "QDK",
    "青岛北": "QHK",
    "沈阳": "SYT",
    "沈阳北": "SBT",
    "大连": "DLT",
    "哈尔滨": "HBB",
    "哈尔滨西": "VAB",
    "长春": "CCT",
    "昆明": "KMM",
    "昆明南": "KOM",
    "贵阳": "GIW",
    "贵阳北": "KQW",
    "南宁": "NNZ",
    "南宁东": "NFZ",
    "兰州": "LZJ",
    "乌鲁木齐": "WAR",
    "拉萨": "LSO",
    "呼和浩特": "HHC",
    "太原": "TYV",
    "石家庄": "SJP",
    "合肥": "HFH",
    "合肥南": "ENH",
    "南昌": "NCG",
    "南昌西": "NXG",
    "福州": "FZS",
    "福州南": "FYS",
    "厦门": "XMS",
    "厦门北": "XKS",
}


def get_station_code(station_name: str) -> Optional[str]:
    """根据车站名称获取电报码"""
    return STATION_CODES.get(station_name)


def parse_date(date_str: str) -> str:
    """
    解析日期字符串，支持相对日期
    例如：今天、明天、后天、3天后 等
    """
    today = datetime.now().date()
    
    date_str = date_str.strip()
    
    if date_str in ["今天", "今日"]:
        return today.strftime("%Y-%m-%d")
    elif date_str in ["明天", "明日"]:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif date_str in ["后天", "后日"]:
        return (today + timedelta(days=2)).strftime("%Y-%m-%d")
    elif date_str in ["大后天"]:
        return (today + timedelta(days=3)).strftime("%Y-%m-%d")
    elif "天后" in date_str:
        try:
            days = int(date_str.replace("天后", "").strip())
            return (today + timedelta(days=days)).strftime("%Y-%m-%d")
        except ValueError:
            pass
    
    # 如果已经是标准格式，直接返回
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        pass
    
    return date_str


@mcp.tool(
    title="查询火车票",
    description="查询指定日期、出发站和到达站的火车票余票信息"
)
def check_tick(
    date: str = Field(
        description="查询日期，格式为YYYY-MM-DD，或支持'今天'、'明天'、'后天'等相对日期"
    ),
    start: str = Field(
        description="出发站名称（如：北京、上海、广州）或电报码（如：BJP、SHH）"
    ),
    end: str = Field(
        description="到达站名称（如：北京、上海、广州）或电报码（如：BJP、SHH）"
    )
) -> str:
    """
    查询指定日期、出发站和到达站的火车票余票信息
    
    Args:
        date: 查询日期，支持YYYY-MM-DD格式或相对日期（今天/明天/后天）
        start: 出发站名称或电报码
        end: 到达站名称或电报码
    
    Returns:
        格式化的火车票查询结果表格
    """
    # 解析日期
    parsed_date = parse_date(date)
    
    # 解析车站代码
    start_code = get_station_code(start) or start
    end_code = get_station_code(end) or end
    
    url = 'https://kyfw.12306.cn/otn/leftTicket/queryG?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
        parsed_date, start_code, end_code)
    
    headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "If-Modified-Since": "0",
        "Referer": "https://kyfw.12306.cn/otn/leftTicket/init",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    
    cookies = {
        "_uab_collina": "",
        "JSESSIONID": "",
        "BIGipServerotn": "",
        "BIGipServerpassport": "",
        "guidesStatus": "",
        "highContrastMode": "",
        "cursorStatus": "",
        "route": "",
        "_jc_save_fromStation": "",
        "_jc_save_toStation": "",
        "_jc_save_fromDate": "",
        "_jc_save_toDate": "",
        "_jc_save_wfdc_flag": ""
    }
    
    try:
        session = requests.session()
        res = session.get(url, headers=headers, cookies=cookies, timeout=10)
        data = res.json()
        
        if data.get("data") is None or data.get("data").get("result") is None:
            return f"查询失败：无法获取{start}到{end}的票务信息，请检查车站名称或日期是否正确。"
        
        result = data["data"]["result"]
        
        if not result:
            return f"未找到 {parsed_date} 从 {start} 到 {end} 的车次信息。"
        
        lis = []
        for index in result:
            index_list = index.replace('有', 'Yes').replace('无', 'No').split('|')
            train_number = index_list[3]  # 车次
            
            time_1 = index_list[8]   # 出发时间
            time_2 = index_list[9]   # 到达时间
            duration = index_list[10]  # 历时
            can_book = index_list[11]  # 是否可以预定
            
            # 获取座位信息
            if 'G' in train_number or 'D' in train_number or 'C' in train_number:
                # 高铁/动车/城际
                business_seat = index_list[25] if len(index_list) > 25 else "--"  # 商务座
                first_class = index_list[31] if len(index_list) > 31 else "--"    # 一等座
                second_class = index_list[30] if len(index_list) > 30 else "--"   # 二等座
                
                dit = {
                    '车次': train_number,
                    '出发时间': time_1,
                    '到达时间': time_2,
                    '历时': duration,
                    '商务座': business_seat,
                    '一等座': first_class,
                    '二等座': second_class,
                    '可预订': '是' if can_book == 'Y' else '否'
                }
            else:
                # 普通列车
                soft_sleeper = index_list[23] if len(index_list) > 23 else "--"   # 软卧
                hard_sleeper = index_list[28] if len(index_list) > 28 else "--"   # 硬卧
                hard_seat = index_list[29] if len(index_list) > 29 else "--"      # 硬座
                
                dit = {
                    '车次': train_number,
                    '出发时间': time_1,
                    '到达时间': time_2,
                    '历时': duration,
                    '软卧': soft_sleeper,
                    '硬卧': hard_sleeper,
                    '硬座': hard_seat,
                    '可预订': '是' if can_book == 'Y' else '否'
                }
            
            lis.append(dit)
        
        # 使用 pandas 格式化输出
        df = pd.DataFrame(lis)
        
        output = f"\n{'='*60}\n"
        output += f"查询日期: {parsed_date}\n"
        output += f"出发站: {start} ({start_code})\n"
        output += f"到达站: {end} ({end_code})\n"
        output += f"{'='*60}\n"
        output += df.to_string(index=False)
        output += f"\n{'='*60}\n"
        output += f"共找到 {len(lis)} 个车次\n"
        
        return output
        
    except requests.exceptions.Timeout:
        return "查询超时，请稍后重试。"
    except requests.exceptions.RequestException as e:
        return f"网络请求错误: {str(e)}"
    except Exception as e:
        return f"查询出错: {str(e)}"


@mcp.tool(
    title="获取当前日期",
    description="返回当前的日期信息，用于处理相对日期查询"
)
def check_date() -> str:
    """
    获取当前日期
    
    Returns:
        当前日期，格式为YYYY-MM-DD
    """
    today = datetime.now().date()
    return today.strftime("%Y-%m-%d")


@mcp.tool(
    title="查询车站代码",
    description="根据车站名称查询对应的电报码"
)
def get_station_code_tool(
    station_name: str = Field(description="车站名称，如：北京、上海、广州")
) -> str:
    """
    查询车站对应的电报码
    
    Args:
        station_name: 车站名称
    
    Returns:
        车站电报码或提示信息
    """
    code = get_station_code(station_name)
    if code:
        return f"{station_name} 的电报码是: {code}"
    else:
        return f"未找到 {station_name} 的电报码，请尝试使用标准车站名称或直接使用电报码查询。"


@mcp.resource("station://list", description="常用车站列表及电报码")
def station_list() -> str:
    """
    返回常用车站及其电报码列表
    """
    output = "常用车站及电报码列表:\n\n"
    output += f"{'车站名称':<12} {'电报码':<8}\n"
    output += "-" * 25 + "\n"
    
    for station, code in sorted(STATION_CODES.items()):
        output += f"{station:<12} {code:<8}\n"
    
    return output


@mcp.resource("help://usage", description="使用帮助文档")
def usage_help() -> str:
    """
    返回12306查询助手的使用说明
    """
    help_text = """
12306 火车票查询助手使用说明
==============================

可用工具:
---------
1. check_tick - 查询火车票
   参数:
   - date: 日期 (支持格式: 2025-04-01 或 今天/明天/后天)
   - start: 出发站名称或电报码
   - end: 到达站名称或电报码

2. check_date - 获取当前日期
   无参数

3. get_station_code_tool - 查询车站电报码
   参数:
   - station_name: 车站名称

可用资源:
---------
- station://list - 常用车站列表
- help://usage - 本帮助文档

使用示例:
---------
查询明天北京到上海的火车票:
  check_tick(date="明天", start="北京", end="上海")

查询2025年4月15日广州到深圳的火车票:
  check_tick(date="2025-04-15", start="广州", end="深圳")

查询车站代码:
  get_station_code_tool(station_name="成都")

注意事项:
---------
- 车站名称支持常用城市名，系统会自动转换为电报码
- 日期支持相对描述（今天/明天/后天/N天后）
- 查询结果包含车次、时间、座位余票等信息
"""
    return help_text


@mcp.prompt("ticket_query", description="火车票查询提示模板")
def ticket_query_prompt(
    date: str = Field(description="查询日期"),
    start: str = Field(description="出发站"),
    end: str = Field(description="到达站")
) -> str:
    """
    生成火车票查询的提示模板
    """
    return f"""请帮我查询火车票信息:

出发站: {start}
到达站: {end}
日期: {date}

请使用 check_tick 工具查询，并将结果以清晰的格式展示给我。
如果查询失败，请说明可能的原因（如日期格式错误、车站名称不正确等）。
"""


if __name__ == "__main__":
    # 运行 MCP 服务器，使用 STDIO 传输
    mcp.run()
    # mcp.run(transport="sse", host="127.0.0.1", port=9000)
