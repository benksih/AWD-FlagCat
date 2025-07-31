# awd_platform/websocket_manager.py
import asyncio
from typing import List
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """处理新的WebSocket连接"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """处理断开的WebSocket连接"""
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """向所有连接的客户端广播消息"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # 如果发送失败（例如客户端已关闭），则默默地忽略
                pass

# 创建一个全局实例
manager = WebSocketManager()