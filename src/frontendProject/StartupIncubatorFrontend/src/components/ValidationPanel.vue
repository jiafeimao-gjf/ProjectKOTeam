<template>
  <a-modal 
    v-model:open="visible" 
    title="输入预览与确认" 
    @ok="handleOk" 
    @cancel="handleCancel"
    okText="确认提交"
    cancelText="取消"
  >
    <a-form :model="formState" layout="vertical">
      <a-form-item label="项目Idea">
        <a-textarea 
          v-model:value="formState.idea" 
          :auto-size="{ minRows: 4, maxRows: 10 }"
          readonly
        />
      </a-form-item>
      
      <a-form-item label="参数配置">
        <a-descriptions :column="1" size="small">
          <a-descriptions-item label="AI模型">
            {{ formState.params.model }}
          </a-descriptions-item>
          <a-descriptions-item label="语言">
            {{ formState.params.language }}
          </a-descriptions-item>
          <a-descriptions-item label="详细程度">
            {{ formState.params.detail }}
          </a-descriptions-item>
        </a-descriptions>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { message } from 'ant-design-vue';
import axios from 'axios';
import { useInputStore } from '../stores/inputStore';

const store = useInputStore();
const visible = defineModel('visible');
const emit = defineEmits(['submitted']);

const formState = reactive({
  idea: store.idea,
  params: store.params
});

const handleOk = async () => {
  try {
    const response = await axios.post('/api/submit-idea', {
      idea: formState.idea,
      params: formState.params
    });
    
    message.success('提交成功');
    emit('submitted', response.data.id);
    visible.value = false;
  } catch (error) {
    message.error('提交失败');
  }
};

const handleCancel = () => {
  visible.value = false;
};
</script>
