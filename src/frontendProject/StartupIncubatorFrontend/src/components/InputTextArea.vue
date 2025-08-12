<template>
  <a-textarea 
    v-model:value="idea" 
    :rows="10" 
    placeholder="请输入项目idea" 
    :maxlength="5000" 
    @input="handleInput"
  />
  <div>字数: {{ wordCount }} / 5000</div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useInputStore } from '../stores/inputStore';

const store = useInputStore();
const idea = ref(store.idea);
const wordCount = computed(() => idea.value.length);

const handleInput = (e) => {
  idea.value = e.target.value;
};

watch(idea, (newVal) => {
  store.setIdea(newVal);
  localStorage.setItem('draftIdea', newVal);
}, { deep: true });

// 初始化从localStorage加载
onMounted(() => {
  idea.value = localStorage.getItem('draftIdea') || '';
});
</script>
