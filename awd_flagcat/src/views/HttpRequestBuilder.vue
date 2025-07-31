// src/views/HttpRequestBuilder.vue
<template>
  <div>
    <h4>HTTP 请求配置</h4>
    <el-form :model="httpConfig" label-position="top">
      <el-form-item label="请求方法 & 路径">
        <el-input v-model="httpConfig.path" placeholder="/index.php">
          <template #prepend>
            <el-select v-model="httpConfig.method" style="width: 100px">
              <el-option label="GET" value="GET" />
              <el-option label="POST" value="POST" />
            </el-select>
          </template>
        </el-input>
      </el-form-item>
      
      <el-form-item label="URL 参数 (用于GET)">
        <div v-for="(param, index) in httpConfig.params" :key="index" class="param-row">
          <el-input v-model="param.key" placeholder="Key" />
          <el-input v-model="param.value" placeholder="Value" />
          <el-button @click="removeRow(httpConfig.params, index)" :icon="Delete" circle plain />
        </div>
        <el-button @click="addRow(httpConfig.params)" :icon="Plus" round>添加参数</el-button>
      </el-form-item>

      <el-form-item label="表单数据 (用于POST)">
        <div v-for="(item, index) in httpConfig.data" :key="index" class="param-row">
          <el-input v-model="item.key" placeholder="Key" />
          <el-input v-model="item.value" placeholder="Value" />
          <el-button @click="removeRow(httpConfig.data, index)" :icon="Delete" circle plain />
        </div>
        <el-button @click="addRow(httpConfig.data)" :icon="Plus" round>添加数据</el-button>
      </el-form-item>

      <el-form-item label="Flag 正则表达式">
        <el-input v-model="httpConfig.flag_regex" placeholder="例如: flag{[a-z0-9-]+}" />
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, watchEffect } from 'vue';
import { ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElButton} from 'element-plus';
import { Plus, Delete } from '@element-plus/icons-vue';

const props = defineProps({ modelValue: { type: Object, required: true }});
const emit = defineEmits(['update:modelValue']);
const httpConfig = ref(props.modelValue);
watch(httpConfig, (newVal) => { emit('update:modelValue', newVal); }, { deep: true });

// --- 关键修复：确保参数/数据行至少有一行 ---
watchEffect(() => {
  if (httpConfig.value.params.length === 0) {
    httpConfig.value.params.push({ key: '', value: '' });
  }
  if (httpConfig.value.data.length === 0) {
    httpConfig.value.data.push({ key: '', value: '' });
  }
});

const addRow = (list: any[]) => list.push({ key: '', value: '' });
const removeRow = (list: any[], index: number) => list.splice(index, 1);
</script>

<style scoped>
.param-row { display: flex; gap: 10px; margin-bottom: 10px; }
</style>