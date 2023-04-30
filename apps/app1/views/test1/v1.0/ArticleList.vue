 
<template>
  <div> {{ article }} </div>
</template>

<script setup>
// API call
const getArticleInfo = async () => {
  await new Promise(resolve => setTimeout(resolve, 1000))
  const article = {
    title: 'Vue3 中使用 defineAsyncComponent 延迟加载组件',
    author: 'lio'
  }
  return article
}

const article = await getArticleInfo()
</script>