 

<template>
  <el-menu class="el-menu" unique-opened :default-openeds="['.']" >
    <el-sub-menu v-for="route in routes"  :key="route.path" class="el-menu" :index="route.path"  >
      <template #title>
        <el-icon>
          <setting />
        </el-icon>{{ route.label }}
      </template>
      <router-link v-for="menu in route.children"  :key="menu.path" :to="menu.path">
        <el-menu-item :index="menu.path">{{ menu.label }}</el-menu-item>
      </router-link>
    </el-sub-menu>
  </el-menu>
</template> 

 
<script>
// import applist_page from './pages/apps.vue'
import VueRouter from "/public/libs/vue-router@4.2.1/dist/vue-router.global.js"
import { system } from './api/api.js'
import { ref } from 'vue'



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
  methods: {
    async getPages() {
      let data = await system.getPagesList()
      console.log(data)
      // # {
      //   #     '.':
      //   #         ['a.vue','b.vue'],
      //   #     'system': 
      //   #         ['cc.vue','dd.vue'], 
      //   # }
      let _routes = []
      for (var _dir in data) {
         
        let dir_name = _dir=='.'?'系统':_dir
        let menus = { 
            path: '/'+dir_name ,
            // icon: route.meta.icon,
            label: dir_name, 
            children: []
            //component: () => import(url),// 设置 component 属性为一个函数，该函数会动态地加载路由对应的组件
          };
           
        for(var _i in data[_dir]){
          let _file = data[_dir][_i]
          let url = `pages/${_dir}/${_file}` // data[_name]['file_path']
          let _path = `${_dir}/${_file}`
          const menuItem = {
            name: _file,
            path: '/' + _path,
            // icon: route.meta.icon,
            label: _file.split(".")[0], 
            component: () => import(url),// 设置 component 属性为一个函数，该函数会动态地加载路由对应的组件
          };
           
          menus.children = menus.children.concat(menuItem)
          
        }
        _routes = _routes.concat(menus)
        router.addRoute(menus)
        // router.replace(router.currentRoute.value.fullPath) 
      }

      this.routes = _routes
      console.log('ROUTERS',router.getRoutes())
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
<style scoped>
.el-sub-menu a{
  border-bottom: none;
  text-decoration: none;
}
</style>
 