<template>
  <div>
    <h4>攻击方法</h4>
    <el-radio-group v-model="config.attack_mode" @change="save" style="margin-bottom: 20px;">
      <el-radio-button label="python_script">Python 脚本</el-radio-button>
      <el-radio-button label="http_request">HTTP 请求</el-radio-button>
    </el-radio-group>
    
    <el-divider />

    <div v-if="config.attack_mode === 'python_script'">
      <Exploits />
    </div>
    <div v-else-if="config.attack_mode === 'http_request'">
      <HttpRequestBuilder v-model="config.http_attack_config" @change="save" />
    </div>

  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useConfigStore } from '../store/configStore';
import { ElRadioGroup, ElRadioButton, ElDivider } from 'element-plus';
import Exploits from './Exploits.vue';
import HttpRequestBuilder from './HttpRequestBuilder.vue';

const configStore = useConfigStore();
const { config } = storeToRefs(configStore);

// 每次修改后自动保存
const save = () => {
  configStore.saveConfig();
}
</script>