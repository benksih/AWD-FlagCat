# awd_platform/logger.py
import asyncio
from .websocket_manager import manager

def log(message: str):
    """
    统一的日志记录函数。
    它会同时在控制台打印并尝试通过WebSocket广播。
    """
    # 1. 在服务器控制台打印日志
    print(message)
    
    # 2. 通过WebSocket广播
    # asyncio.create_task 会在后台发送消息，不会阻塞当前函数的执行
    asyncio.create_task(manager.broadcast(message))