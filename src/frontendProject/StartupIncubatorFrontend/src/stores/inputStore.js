import { defineStore } from 'pinia';

export const useInputStore = defineStore('input', {
  state: () => ({
    idea: '',
    params: { model: 'Grok', language: 'en', detail: 2 },
    files: [],
  }),
  actions: {
    setIdea(val) { 
      this.idea = val; 
    },
    appendToIdea(text) { 
      this.idea += text; 
    },
  },
});
