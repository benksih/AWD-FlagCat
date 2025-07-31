# awd_platform/attack_logic.py (最终版)
import asyncio
import importlib.util
import re
from pathlib import Path
from typing import List
import httpx

from .state import app_state
from .models import Target, TargetStatus
from .logger import log
from .flag_submitter import submit_flag

# 创建一个全局可复用的HTTP客户端
http_client = httpx.AsyncClient(verify=False, timeout=10.0)

async def run_python_script_attack(target: Target) -> List[str]:
    """动态加载并执行选定的Python EXP脚本"""
    selected_exploit = app_state.get_config().selected_exploit
    exp_path = Path(__file__).parent / "exploits" / selected_exploit
    if not exp_path.exists():
        log(f"[!] [ERROR] 攻击脚本 '{selected_exploit}' 不存在，跳过对 {target.ip} 的攻击。")
        return []
    try:
        spec = importlib.util.spec_from_file_location(exp_path.stem, exp_path)
        exp_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(exp_module)
        if hasattr(exp_module, 'attack'):
            flags = await exp_module.attack(target.ip)
            return flags if flags else []
        else:
            log(f"[!] [ERROR] 脚本 {exp_path.name} 中未找到 'attack' 函数")
            return []
    except Exception as e:
        log(f"[!] [ERROR] 执行EXP {exp_path.name} 针对 {target.ip} 时出错: {e}")
        return []

async def run_simple_http_attack(target: Target) -> List[str]:
    """根据配置执行简单的HTTP GET/POST攻击（新版：支持带端口的目标地址）"""
    config = app_state.get_config().http_attack_config
    
    # --- 关键改动：智能解析主机和端口 ---
    # target.ip 字段现在被我们用作 "address" 字段
    address = target.ip.strip() 
    
    # 简单的协议头处理，如果用户输入了 http:// 则移除
    if address.startswith("http://"):
        address = address[7:]
    
    # 解析主机和端口
    host, port = address, 80  # 默认端口为80
    if ':' in address:
        parts = address.rsplit(':', 1)
        # 确保端口是数字
        if parts[1].isdigit():
            host, port = parts[0], int(parts[1])

    url = f"http://{host}:{port}{config.path}"
    # --- 解析逻辑结束 ---
    
    try:
        params = {p.key: p.value for p in config.params if p.key}
        data = {d.key: d.value for d in config.data if d.key}
        
        log(f"[*] [HTTP] {config.method} -> {url} | params: {params} | data: {data}")

        if config.method.upper() == "GET":
            response = await http_client.get(url, params=params)
        else: # POST
            response = await http_client.post(url, params=params, data=data)
        
        response.raise_for_status()
        
        found_flags = re.findall(config.flag_regex, response.text)
        if found_flags:
            log(f"[+] [HTTP] 在 {target.ip} 的响应中找到 {len(found_flags)} 个Flag: {found_flags}")
        
        return found_flags
        
    except httpx.RequestError as e:
        log(f"[-] [HTTP] 请求 {target.ip} 时网络错误: {e}")
        return []
    except Exception as e:
        log(f"[!] [ERROR] HTTP攻击 {target.ip} 时发生未知错误: {e}")
        return []
async def attack_worker(target: Target, semaphore: asyncio.Semaphore):
    """单个攻击任务的工作单元，现在能根据模式选择攻击方式"""
    async with semaphore:
        ip = target.ip
        log(f"[*] [SCHEDULER] 开始处理目标: {ip}")
        
        app_state.targets[ip].status = "ATTACKING"
        app_state.targets[ip].last_attack_time = asyncio.get_event_loop().time()
        
        attack_mode = app_state.get_config().attack_mode
        flags = []
        try:
            if attack_mode == "python_script":
                flags = await run_python_script_attack(target)
            elif attack_mode == "http_request":
                flags = await run_simple_http_attack(target)
            
            if flags:
                app_state.targets[ip].status = "SUCCESS"
                app_state.targets[ip].success_flags_count += len(flags)
                # --- 关键修复：添加提交Flag的逻辑 ---
                log(f"[+] [SCHEDULER] 在 {ip} 发现 {len(flags)} 个Flag，准备提交...")
                submit_tasks = [submit_flag(flag) for flag in flags]
                await asyncio.gather(*submit_tasks) # 并发提交所有获取到的Flag
                # --- 修复结束 ---
            else:
                app_state.targets[ip].status = "FAILED"
        except Exception as e:
            app_state.targets[ip].status = "ERROR"
            log(f"[!] [ERROR] {ip}: 攻击时发生未知异常: {e}")

async def main_attack_loop():
    """
    程序的核心，一个无限循环，负责调度每一轮的攻击。
    """
    log("[*] [SYSTEM] 主攻击循环已启动...")
    while app_state.attack_running:
        log("\n" + "="*20 + " 开始新一轮攻击 " + "="*20)
        
        config = app_state.get_config()
        targets = app_state.get_all_targets()
        
        if not targets:
            log("[*] [SCHEDULER] 目标列表为空，暂停10秒...")
            await asyncio.sleep(10)
            continue

        # 创建一个信号量来控制并发数
        semaphore = asyncio.Semaphore(config.concurrency)
        
        # 创建所有攻击任务
        tasks = [attack_worker(target, semaphore) for target in targets]
        
        # 等待本轮所有任务完成
        await asyncio.gather(*tasks, return_exceptions=True)
        
        log("="*20 + f" 本轮攻击结束，等待 {config.round_interval} 秒 " + "="*20 + "\n")
        await asyncio.sleep(config.round_interval)

    log("[*] [SYSTEM] 主攻击循环已停止。")