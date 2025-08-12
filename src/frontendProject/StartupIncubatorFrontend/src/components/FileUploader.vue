<template>
  <a-upload-dragger 
    v-model:fileList="fileList" 
    :multiple="true" 
    :action="uploadUrl" 
    :before-upload="beforeUpload"
    @change="handleChange"
  >
    <p class="ant-upload-drag-icon">
      <inbox-outlined></inbox-outlined>
    </p>
    <p class="ant-upload-text">拖拽或点击上传文件 (PDF/DOCX/TXT)</p>
    <p class="ant-upload-hint">支持单次上传最多5个文件，总大小不超过10MB</p>
  </a-upload-dragger>
  <div v-if="uploadedFiles.length">已上传: {{ uploadedFiles.join(', ') }}</div>
</template>

<script setup>
import { ref } from 'vue';
import { InboxOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import axios from 'axios';
import { useInputStore } from '../stores/inputStore';

const store = useInputStore();
const fileList = ref([]);
const uploadUrl = '/api/upload';
const uploadedFiles = ref([]);

const beforeUpload = (file) => {
  const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
  const maxSize = 10 * 1024 * 1024; // 10MB
  
  if (!allowedTypes.includes(file.type)) {
    message.error('不支持的文件类型，请上传PDF/DOCX/TXT格式文件');
    return false;
  }
  
  if (file.size > maxSize) {
    message.error('文件过大，请上传小于10MB的文件');
    return false;
  }
  
  return true;
};

const handleChange = async (info) => {
  if (info.file.status === 'done') {
    try {
      const response = await axios.post('/api/parse-file', { file: info.file.name });
      store.appendToIdea('\n\n' + response.data.text);
      uploadedFiles.value.push(info.file.name);
      message.success(`${info.file.name} 上传成功`);
    } catch (error) {
      message.error(`${info.file.name} 解析失败`);
    }
  } else if (info.file.status === 'error') {
    message.error(`${info.file.name} 上传失败`);
  }
};
</script>
