<template>
  <div class="input-module">
    <a-card title="AI项目快速自动孵化器 - 输入模块">
      <a-row :gutter="16">
        <a-col :span="24">
          <InputTextArea />
        </a-col>
      </a-row>
      
      <a-row :gutter="16" style="margin-top: 20px;">
        <a-col :span="12">
          <FileUploader />
        </a-col>
        <a-col :span="12">
          <ParamConfigPanel />
        </a-col>
      </a-row>
      
      <a-row :gutter="16" style="margin-top: 20px;">
        <a-col :span="12">
          <TemplateSelector />
        </a-col>
        <a-col :span="12">
          <HistoryList />
        </a-col>
      </a-row>
      
      <a-row :gutter="16" style="margin-top: 20px;">
        <a-col :span="24" style="text-align: center;">
          <a-button type="primary" size="large" @click="showPreview">
            预览并提交
          </a-button>
        </a-col>
      </a-row>
    </a-card>
    
    <PreviewConfirm v-model:visible="previewVisible" @submitted="onSubmitted" />
    <PrivacyModal ref="privacyModal" v-model:visible="privacyVisible" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import InputTextArea from './InputTextArea.vue';
import FileUploader from './FileUploader.vue';
import ParamConfigPanel from './ParamConfigPanel.vue';
import TemplateSelector from './TemplateSelector.vue';
import HistoryList from './HistoryList.vue';
import PreviewConfirm from './InputModule.vue';
import PrivacyModal from './PrivacyModal.vue';

const previewVisible = ref(false);
const privacyVisible = ref(true);
const privacyModal = ref(null);

// onMounted(() => {
//   // 页面加载时显示隐私政策弹窗
//   setTimeout(() => {
//     if (privacyModal.value) {
//       privacyModal.value.show();
//     }
//   }, 500);
// });

const showPreview = () => {
  previewVisible.value = true;
};

const onSubmitted = (id) => {
  message.success(`提交成功，ID: ${id}`);
};
</script>

<style scoped>
.input-module {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
</style>
