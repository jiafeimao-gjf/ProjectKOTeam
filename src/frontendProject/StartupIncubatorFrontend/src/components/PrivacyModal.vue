<template>
  <a-modal 
    v-model:open="visible" 
    title="隐私政策同意" 
    @ok="handleOk" 
    :footer="null"
    :closable="false"
    :maskClosable="false"
  >
    <div style="max-height: 300px; overflow-y: auto; margin-bottom: 20px;">
      <h3>隐私政策</h3>
      <p>我们非常重视您的隐私保护。使用本系统时，您需要了解并同意以下条款：</p>
      
      <h4>1. 信息收集</h4>
      <p>我们收集您输入的项目想法、上传的文件以及配置参数，仅用于生成项目孵化方案。</p>
      
      <h4>2. 信息使用</h4>
      <p>收集的信息将用于AI分析和生成项目方案，不会用于其他用途。</p>
      
      <h4>3. 信息存储</h4>
      <p>您的数据将存储在本地数据库中，不会传输到外部服务器。</p>
      
      <h4>4. 信息共享</h4>
      <p>我们不会将您的信息共享给任何第三方。</p>
      
      <h4>5. 数据安全</h4>
      <p>我们将采取合理措施保护您的数据安全。</p>
    </div>
    
    <a-checkbox v-model:checked="agreed">
      我已阅读并同意上述隐私政策
    </a-checkbox>
    
    <div style="margin-top: 20px; text-align: right;">
      <a-button 
        type="primary" 
        @click="handleOk" 
        :disabled="!agreed"
      >
        确认并继续
      </a-button>
    </div>
  </a-modal>
</template>

<script setup>
import { ref } from 'vue';

const visible = defineModel('visible');
const agreed = ref(false);

const handleOk = () => {
  if (agreed.value) {
    visible.value = false;
  }
};

defineExpose({
  show: () => {
    visible.value = true;
    agreed.value = false;
  }
});
</script>
