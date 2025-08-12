<template>
  <a-form-item label="选择模板">
    <a-select 
      v-model:value="selectedTemplate" 
      :options="templateOptions" 
      @change="onTemplateChange"
      placeholder="请选择一个模板"
    >
    </a-select>
    <a-button type="primary" @click="applyTemplate" :disabled="!selectedTemplate" style="margin-top: 10px;">
      应用模板
    </a-button>
  </a-form-item>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import axios from 'axios';
import { useInputStore } from '../stores/inputStore';

const store = useInputStore();
const selectedTemplate = ref('');
const templateOptions = ref([]);

onMounted(async () => {
  try {
    const response = await axios.get('/api/templates');
    templateOptions.value = response.data.map(template => ({
      label: template.name,
      value: template.name
    }));
  } catch (error) {
    message.error('获取模板列表失败');
  }
});

const onTemplateChange = (value) => {
  selectedTemplate.value = value;
};

const applyTemplate = async () => {
  if (!selectedTemplate.value) {
    message.warning('请先选择一个模板');
    return;
  }

  try {
    const response = await axios.get('/api/templates');
    const template = response.data.find(t => t.name === selectedTemplate.value);
    if (template) {
      store.setIdea(template.content);
      message.success('模板应用成功');
    }
  } catch (error) {
    message.error('应用模板失败');
  }
};
</script>
