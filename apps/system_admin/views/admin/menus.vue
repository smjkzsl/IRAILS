 

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
// import applist_page from './pages/apps.vue'
import VueRouter from "/public/libs/vue-router@4.2.1/dist/vue-router.global.js"
import {system} from './api/api.js'
import {ref} from 'vue'


 
import { Menu as IconMenu, Message, Setting } from 'element_icon'

const router = VueRouter.createRouter({
        history: VueRouter.createWebHashHistory(),
        routes: [],
      })
app.use(router)


export default {
  components: {
    IconMenu, Message, Setting
  },
  created() {
    console.log('menus created')
  },
  mounted() {
    console.log('menus mounted')
    this.getPages()
  },
  methods:{
    async getPages(){
      let data = await system.getPagesList() 
      console.log(data)
      let _routes = []
      for(var item in data){
        let _name = item
        let url = data[_name]
        const menuItem = {
          name: _name,
          path: '/' + _name ,
          // icon: route.meta.icon,
          label: _name,
          // 设置 component 属性为一个函数，该函数会动态地加载路由对应的组件
          component: () => import(url),
        };
        router.addRoute(menuItem)
        router.replace(router.currentRoute.value.fullPath)

        
         
      } 
      debugger
      this.routes = router.getRoutes()
      console.log(router.getRoutes())
    },
  },
  setup() {
    
    const routes = ref(router.options.routes)
    return { 
      routes
    }

  },
  updated() {
    console.log("menus.vue updated...")
  }
}
</script>
 