 

<template>
  <el-menu class="el-menu" :default-openeds="['1']">
    <el-sub-menu class="el-menu" index="1">
      <template #title>
        <el-icon>
          <setting />
        </el-icon>系统管理
      </template>
      <router-link v-for="route in routes" :key="route.path" :to="route.path">
        <el-menu-item :index="route.path">{{ route.name }}</el-menu-item>
      </router-link>
    </el-sub-menu>
  </el-menu>
</template> 

 
<script>
import applist_page from './pages/apps.vue'
// 1. 定义路由组件.
// 也可以从其他文件导入

const About = {
  template: '<div>About</div>'
}

// 2. 定义一些路由
// 每个路由都需要映射到一个组件。
// 我们后面再讨论嵌套路由。
const routes = [{
  path: '/',
  name: 'AppList',
  component: applist_page
}, {
  path: '/about',
  name: 'About',
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
import { Menu as IconMenu, Message, Setting } from 'element_icon'
export default {
  components: {
    IconMenu, Message, Setting
  },
  created() {
    console.log('menus created')
  },
  mounted() {
    console.log('menus mounted')
  },
  setup() {
    return {
      routes
    }

  },
  updated() {
    console.log("menus.vue updated...")
  }
}
</script>
 