<template>
  <a-collapse v-model:activeKey="activeKey">
    <a-collapse-panel key="1" header="历史Idea列表">
      <div v-if="loading">
        <a-spin />
      </div>
      <div v-else-if="ideas.length === 0">
        <a-empty description="暂无历史记录" />
      </div>
      <div v-else>
        <a-list :data-source="ideas" size="small">
          <template #renderItem="{ item }">
            <a-list-item>
              <a-list-item-meta :description="item.idea.substring(0, 100) + '...'">
                <template #title>
                  <a @click="loadIdea(item.id)">#{{ item.id }} {{ item.createdAt || '' }}</a>
                </template>
              </a-list-item-meta>
              <template #actions>
                <a @click="loadIdea(item.id)">加载</a>
                <a @click="deleteIdea(item.id)">删除</a>
              </template>
            </a-list-item>
          </template>
        </a-list>
      </div>
    </a-collapse-panel>
  </a-collapse>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import axios from 'axios';
import { useInputStore } from '../stores/inputStore';

const store = useInputStore();
const activeKey = ref([]);
const ideas = ref([]);
const loading = ref(false);

onMounted(() => {
  loadHistory();
});

const loadHistory = async () => {
  loading.value = true;
  try {
    const response = await axios.get('/api/history');
    ideas.value = response.data;
  } catch (error) {
    message.error('获取历史记录失败');
  } finally {
    loading.value = false;
  }
};

const loadIdea = async (id) => {
  try {
    const idea = ideas.value.find(item => item.id === id);
    if (idea) {
      store.setIdea(idea.idea);
      message.success('已加载到编辑器');
    }
  } catch (error) {
    message.error('加载失败');
  }
};

const deleteIdea = async (id) => {
  try {
    await axios.delete(`/api/history/${id}`);
    message.success('删除成功');
    loadHistory(); // 重新加载列表
  } catch (error) {
    message.error('删除失败');
  }
};
</script>
