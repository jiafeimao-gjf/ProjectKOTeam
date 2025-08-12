<template>
  <a-collapse v-model:activeKey="activeKey">
    <a-collapse-panel key="1" header="参数配置">
      <a-form :model="formState" layout="vertical">
        <a-form-item label="AI模型">
          <a-select v-model:value="formState.model" :options="modelOptions" />
        </a-form-item>
        
        <a-form-item label="语言">
          <a-select v-model:value="formState.language" :options="langOptions" />
        </a-form-item>
        
        <a-form-item label="详细程度">
          <a-slider 
            v-model:value="formState.detailLevel" 
            :marks="detailMarks" 
            :min="1" 
            :max="5" 
          />
        </a-form-item>
        
        <a-form-item>
          <div>预计时间: {{ estimatedTime }} 分钟</div>
        </a-form-item>
      </a-form>
    </a-collapse-panel>
  </a-collapse>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { useInputStore } from '../stores/inputStore';

const store = useInputStore();
const activeKey = ref(['1']);

const formState = reactive({
  model: 'Grok',
  language: '中文',
  detailLevel: 2,
});

const modelOptions = [
  { label: 'Grok', value: 'Grok' },
  { label: 'GPT-4', value: 'GPT-4' },
  { label: 'Claude', value: 'Claude' },
];

const langOptions = [
  { label: '中文', value: '中文' },
  { label: 'English', value: 'English' },
  { label: '日本語', value: '日本語' },
];

const detailMarks = {
  1: '简单',
  2: '较详细',
  3: '详细',
  4: '很详细',
  5: '极详细'
};

const estimatedTime = computed(() => formState.detailLevel * 1.5);
</script>
