<template>
  <el-container class="layout-container-demo">

    <el-header style="text-align: right; font-size: 12px">
      <headers />
    </el-header>
    <el-container>
      
      
      
       
      <el-aside ref="aside" :width="asideWidth"> 
        <el-row class="aside-header">
          <el-icon  @click="toggleLeft()"> 
            <Fold  v-if="!isCollapse"/><Expand v-if="isCollapse"/> 
          </el-icon>
        </el-row>
        <el-row>
          <menus style="width:100%;" :isCollapse="isCollapse" /> 
        </el-row> 
      </el-aside>
      
    
      <el-container class="el-main">
        
          <router-view></router-view>
         
      </el-container>
    </el-container>
    <el-container>
      <el-footer>Copyright 2023 ©  bruce chou</el-footer>
    </el-container>


  </el-container>
</template>

<script>
 

import { ref,relative,nextTick } from 'vue'

import { Menu as IconMenu, Message, Setting } from 'element_icon'

import menus from './menus.vue'
import headers from './headers.vue'

export default {
  components: {
    IconMenu, Message, Setting, menus, headers
  },
  methods:{
    async toggleLeft(){
       
      this.isCollapse=!this.isCollapse
      await nextTick()
      this.asideWidth=this.isCollapse?"100px":'200px'
    },
  },
  setup() {
    // const state = relative({aside:ref('aside')})
    let asideWidth = ref("200px")
    const isCollapse = ref(false)

    return {isCollapse,asideWidth}
  },
}

</script>
<style >
html,
body {
  margin: 0;
  height: 100%;
}

.layout-container-demo .el-header {
  position: relative;
  border-bottom: 1px solid #EEE;
}
.layout-container-demo .el-footer {
  position: relative;
  bottom: 0px;
  text-align: center;
}

.layout-container-demo .aside-header{
  position: relative;
   
  justify-content: end;
    align-items: end;
  height: 38px;
  top:0px;
  width: 100%;
  cursor:pointer;
  padding: 10px;
  font-size: 1.2em;
  border-bottom: 1px dashed #EEE;
}
.layout-container-demo .aside-header i:hover{
  color:rgb(102, 130, 231);
  
}
.layout-container-demo .el-aside {
  
  text-align: right;
  position: relative  ;
  height: calc(100vh - 120px); 
  top: 0px;
  bottom: 0px;
  border-right: 1px solid #EEE;
}
.el-aside ul,.el-menu{
  border-right: none !important;
}
 

.layout-container-demo .el-main {
  padding: 0;
  position: relative;
  height: calc(100vh - 120px); 
  left: 0px;
  top: 0px;
  bottom: 0;
  width: auto;
  /* max-width: calc(100% - 200px); */
  
}
.layout-container-demo .el-footer{
  height: 60px;
  border-top: 1px solid #EEE;
}
</style>
