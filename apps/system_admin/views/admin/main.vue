<template>
  <el-container class="layout-container-demo">

    <el-header style="text-align: right; font-size: 12px">
      <headers />
    </el-header>
    <el-container>
      <el-aside width="200px">
        <el-scrollbar>
          <menus />
        </el-scrollbar>
      </el-aside>

      <el-container class="el-main">
        
          <router-view></router-view>
         
      </el-container>
    </el-container>
    <el-container>
      <el-footer>Footer</el-footer>
    </el-container>


  </el-container>
</template>

<script>
import { ref } from 'vue'

import { Menu as IconMenu, Message, Setting } from 'element_icon'

import menus from './menus.vue'
import headers from './headers.vue'

export default {
  components: {
    IconMenu, Message, Setting, menus, headers
  },
  setup() {

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

.layout-container-demo .el-aside {
 
  position: relative  ;
  height: calc(100vh - 120px); 
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
  max-width: calc(100% - 200px);
  
}
.layout-container-demo .el-footer{
  height: 60px;
  border-top: 1px solid #EEE;
}
</style>
