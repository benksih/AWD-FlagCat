// src/store/logStore.ts

import { defineStore } from 'pinia'
import { ref } from 'vue'

// 定义一个名为 'log' 的 store
export const useLogStore = defineStore('log', () => {
  // --- State (状态) ---
  const logs = ref<string[]>([])
  const connectionStatus = ref<'connecting' | 'connected' | 'disconnected'>('connecting')
  let ws: WebSocket | null = null

  // --- Actions (方法) ---
  const connectWebSocket = () => {
    // 防止重复连接
    if (ws && ws.readyState < 2) {
        return;
    }

    ws = new WebSocket('ws://127.0.0.1:8000/ws/logs')

    ws.onopen = () => {
      connectionStatus.value = 'connected'
      // ElMessage 调用已被移除
    }

    ws.onmessage = (event) => {
      logs.value.push(event.data)
    }

    ws.onclose = () => {
      connectionStatus.value = 'disconnected'
      // ElMessage 调用已被移除
      // 依然保留重连逻辑
      setTimeout(connectWebSocket, 3000)
    }

    ws.onerror = (error) => {
      console.error('WebSocket Error:', error)
      // ElMessage 调用已被移除
      ws?.close()
    }
  }

  const disconnectWebSocket = () => {
    if (ws) {
      ws.onclose = null // 禁用重连逻辑
      ws.close()
    }
  }

  // --- 返回 state 和 actions ---
  return { logs, connectionStatus, connectWebSocket, disconnectWebSocket }
})