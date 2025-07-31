<template>
  <div class="dashboard">
    <div class="controls">
      <el-button type="primary" @click="startAttack">启动攻击</el-button>
      <el-button type="danger" @click="stopAttack">停止攻击</el-button>
      <el-tag :type="wsStatus.type" class="status-tag">{{ wsStatus.text }}</el-tag>
    </div>

    <div class="log-container">
      <h3>实时日志</h3>
      <div class="log-box" ref="logBoxRef">
        <div v-for="(log, index) in logs" :key="index" class="log-item" :class="getLogClass(log)">
          <span class="log-time">{{ new Date().toLocaleTimeString() }}:</span>
          <span class="log-message">{{ log }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue';
import { storeToRefs } from 'pinia';
// 1. 在这里重新导入 ElMessage
import { ElButton, ElTag, ElMessage } from 'element-plus';
import { useLogStore } from '../store/logStore';

const logBoxRef = ref<HTMLDivElement | null>(null);
const logStore = useLogStore();

const { logs, connectionStatus } = storeToRefs(logStore);

watch(logs, (newLogs) => {
  nextTick(() => {
    if (logBoxRef.value) {
      logBoxRef.value.scrollTop = logBoxRef.value.scrollHeight;
    }
  });
}, { deep: true });


// --- API 调用逻辑 (恢复 ElMessage) ---
const apiRequest = async (endpoint: string, method: 'POST' | 'GET' = 'POST') => {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api${endpoint}`, { method });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '请求失败');
        }
        const data = await response.json();
        // 2. 将这里的 ElMessage 调用恢复
        ElMessage.success(data.message || '操作成功！');
    } catch(error: any) {
        // 3. 将这里的 ElMessage 调用也恢复
        ElMessage.error(`操作失败: ${error.message}`);
    }
}
const startAttack = () => apiRequest('/control/start');
const stopAttack = () => apiRequest('/control/stop');


// --- 计算属性 (这部分保持不变) ---
const wsStatus = computed(() => {
  switch (connectionStatus.value) {
    case 'connected':
      return { type: 'success', text: '已连接' };
    case 'disconnected':
      return { type: 'danger', text: '已断开' };
    default:
      return { type: 'warning', text: '连接中...' };
  }
});

const getLogClass = (log: string) => {
  if (log.includes('[+]') || log.includes('成功')) return 'log-success';
  if (log.includes('[!]') || log.includes('ERROR')) return 'log-error';
  if (log.includes('[-]') || log.includes('失败')) return 'log-warning';
  return 'log-info';
}
</script>
<style scoped>
.dashboard {
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.controls {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.status-tag {
  margin-left: 20px;
}

.log-container {
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

h3 {
  padding: 10px 15px;
  margin: 0;
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
}

.log-box {
  height: calc(100vh - 125px); /* 动态计算高度 */
  overflow-y: auto;
  padding: 15px;
  background-color: #fff;
}

.log-item {
  margin-bottom: 8px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
}

.log-time {
  color: #909399;
  margin-right: 10px;
}

.log-success { color: #67c23a; }
.log-error { color: #f56c6c; }
.log-warning { color: #e6a23c; }
.log-info { color: #409eff; }
</style>