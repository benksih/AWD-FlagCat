# awd_platform/flag_submitter.py (更新后的版本)
from .logger import log
import httpx
from typing import List
from .state import app_state

# 创建一个全局的、可复用的HTTP客户端实例
client = httpx.AsyncClient(timeout=10.0)

async def submit_flag(flag: str):
    """
    向比赛平台提交单个Flag。
    此版本已根据您提供的截图进行适配。
    """
    config = app_state.get_config()
    url = config.submit_url
    token = config.token
    
    # 1. 准备请求头 (Headers)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': token  # 从配置中读取认证Token
    }
    
    # 2. 准备JSON格式的请求体 (Body)
    json_body = {
        "flag": flag
    }
    
    try:
        log(f"[*] [SUBMITTER] 正在向 {url} 提交Flag: {flag}")
        # 3. 发送POST请求，注意此处使用 json=... 而不是 data=...
        response = await client.post(url, json=json_body, headers=headers)
        
        # 检查响应状态码
        response.raise_for_status() # 如果是4xx或5xx状态码 (如 401 Unauthorized), 会抛出异常
        
        # 检查响应内容，判断是否成功
        response_text = response.text
        log(f"[*] [SUBMITTER] 平台返回: {response_text}")
        
        # 您可以根据实际返回内容定制更详细的成功/失败判断
        if response.status_code == 200:
            log(f"[+] [SUBMITTER] Flag '{flag}' 提交请求成功!")
        else:
            log(f"[!] [SUBMITTER] Flag '{flag}' 提交后收到意外的状态码: {response.status_code}")
            
    except httpx.HTTPStatusError as e:
        # 特别处理HTTP错误，比如Token错误(401), 请求频繁(429)等
        log(f"[!] [ERROR] 提交Flag '{flag}' 时发生HTTP错误: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        log(f"[!] [ERROR] 提交Flag '{flag}' 时发生网络错误: {e}")
    except Exception as e:
        log(f"[!] [ERROR] 提交Flag '{flag}' 时发生未知错误: {e}")