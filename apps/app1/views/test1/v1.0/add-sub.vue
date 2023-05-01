<template>
    <h1>页面组件</h1>
    <h1 v-text='num'></h1>
    <button @click='add'>自增</button>
    <el-button @click='sub'>自减</el-button>
  </template>
  
  <script>
  const { ref } = Vue
  module.exports = {  
    props: { },  // 接收自定义属性
    setup (props, context) {
      console.log('----setup', props)
      console.log('----setup', context)
      const num = ref(1)
      const add = () => {
        num.value++
      }
      return { num, add }
    },
    methods: {
      sub () { this.num-- }
    },
    mounted () {
      console.log('---mounted')
    }
  }
  </script>