// src/views/Settings.vue
<template>
  <div class="page-container">
    <h4>Flag 提交接口设置</h4>
    <el-form :model="config" label-width="120px" style="max-width: 600px">
      <el-form-item label="平台URL">
        <el-input v-model="config.submit_url" placeholder="请输入提交Flag的URL"></el-input>
      </el-form-item>
      <el-form-item label="认证Token">
        <el-input v-model="config.token" placeholder="请输入平台认证Token" show-password></el-input>
      </el-form-item>
      <el-divider>通用设置</el-divider>
      <el-form-item label="攻击并发数">
        <el-slider v-model="config.concurrency" :min="1" :max="100" show-input></el-slider>
      </el-form-item>
      <el-form-item label="每轮间隔(秒)">
        <el-slider v-model="config.round_interval" :min="10" :max="300" show-input></el-slider>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="configStore.saveConfig">保存设置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useConfigStore } from '../store/configStore';
import { ElForm, ElFormItem, ElInput, ElButton, ElSlider, ElDivider } from 'element-plus';

const configStore = useConfigStore();
const { config } = storeToRefs(configStore);
</script>

<style scoped>
.page-container { padding: 20px; }
h4 { margin-top: 0; }
</style>