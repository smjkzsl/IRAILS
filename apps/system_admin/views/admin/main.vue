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

      <el-container>
        <el-main>
          <router-view></router-view>
        </el-main>

        <el-footer>Footer</el-footer></el-container>
    </el-container>



  </el-container>
</template>

<script>
import { ref } from 'vue'

import { Menu as IconMenu, Message, Setting } from 'element_icon'
import table_content from './pages/table_content.vue'
import menus from './menus.vue'
import headers from './headers.vue'
// 1. 定义路由组件.
// 也可以从其他文件导入
const Home = {
  template: '<div>Home</div>'
}
const About = {
  template: '<div>About</div>'
}

// 2. 定义一些路由
// 每个路由都需要映射到一个组件。
// 我们后面再讨论嵌套路由。
const routes = [{
  path: '/',
  component: table_content
}, {
  path: '/about',
  component: About
},]
// 3. 创建路由实例并传递 `routes` 配置
// 你可以在这里输入更多的配置，但我们在这里
// 暂时保持简单
const router = VueRouter.createRouter({
  // 4. 内部提供了 history 模式的实现。为了简单起见，我们在这里使用 hash 模式。
  history: VueRouter.createWebHashHistory(),
  routes, // `routes: routes` 的缩写
})
app.use(router)
export default {
  components: {
    table_content, IconMenu, Message, Setting, menus, headers
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
  background-color: var(--el-color-primary-light-7);
  color: var(--el-text-color-primary);
}

.layout-container-demo .el-aside {
  color: var(--el-text-color-primary);
  background: var(--el-color-primary-light-8);
  position: absolute;
  left: 0;
  top: 60px;
  bottom: 0;
}

.layout-container-demo .el-menu {
  border-right: none;
  background: transparent;
}

.layout-container-demo .el-main {
  padding: 0;
  position: absolute;
  left: 200px;
  top: 60px;
  bottom: 0;
  width: 100%;

}
</style>
