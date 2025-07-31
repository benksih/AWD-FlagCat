<template>
  <div class="page-container">
    <h2>目标配置</h2>
    <p>在此处粘贴目标地址，每行一个。支持域名和IP，可带端口。</p>
    <el-input
      v-model="ipsText"
      :rows="15"
      type="textarea"
      placeholder="192.168.1.1:8080&#10;team1.game.com:1337&#10;192.168.1.3"
    />
    <el-button type="primary" @click="submitTargets" style="margin-top: 20px;">更新目标列表</el-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElInput, ElButton, ElMessage } from 'element-plus';

const ipsText = ref('');

const submitTargets = async () => {
  // 将文本按行分割，并过滤掉空行
  const ips = ipsText.value.split('\n').filter(ip => ip.trim() !== '');
  if (ips.length === 0) {
    ElMessage.warning('目标列表不能为空');
    return;
  }

  try {
    const response = await fetch('http://127.0.0.1:8000/api/targets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ips: ips }),
    });
     if (response.ok) {
      ElMessage.success('目标列表已更新！');
    } else {
      const errorData = await response.json();
      ElMessage.error(`更新失败: ${errorData.detail}`);
    }
  } catch (error) {
     ElMessage.error('更新目标时出错');
  }
};
</script>

<style scoped>
.page-container { padding: 20px; }
</style>