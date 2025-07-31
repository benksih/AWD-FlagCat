// src/store/configStore.ts
import { ref } from 'vue'
import { defineStore } from 'pinia'
import { ElMessage } from 'element-plus'

const defaultConfig = {
  submit_url: '', token: '', concurrency: 10, round_interval: 60,
  attack_mode: 'python_script', selected_exploit: 'example_exp.py',
  http_attack_config: {
    method: 'GET', path: '/', params: [], data: [],
    flag_regex: 'flag\\{[a-zA-Z0-9-_]+\\}'
  }
};

export const useConfigStore = defineStore('config', () => {
  const config = ref(JSON.parse(JSON.stringify(defaultConfig)));
  const isLoading = ref(true);

  async function fetchConfig() {
    isLoading.value = true;
    try {
      const response = await fetch('http://127.0.0.1:8000/api/config');
      if (response.ok) {
        const loadedConfig = await response.json();
        // 深度合并，防止后端缺少新字段时出错
        config.value = { 
          ...defaultConfig, 
          ...loadedConfig, 
          http_attack_config: { 
            ...defaultConfig.http_attack_config, 
            ...loadedConfig.http_attack_config 
          }
        };
      } else { ElMessage.error('获取当前配置失败'); }
    } catch (error) { ElMessage.error('无法连接到后端服务'); }
    finally { isLoading.value = false; }
  }

  async function saveConfig() {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config.value),
      });
      if (response.ok) {
        ElMessage.success('配置已保存！');
      } else {
        const errorData = await response.json();
        ElMessage.error(`保存失败: ${errorData.detail}`);
      }
    } catch (error) { ElMessage.error('保存配置时出错'); }
  }

  return { config, isLoading, fetchConfig, saveConfig }
})