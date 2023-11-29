 

<template>
  <el-menu :collapse="isCollapse" class="el-menu" unique-opened :default-openeds="['.']">
    <el-sub-menu v-for="route in routes" :key="route.path" class="el-menu" :index="route.path">
      <template #title>
        <component :is="route.icon" style="margin-right:5px; width: 1.5em; height: 1.5em; color:#123456"></component>
        {{ route.label }}
      </template>
      <router-link v-for="menu in route.children" :key="menu.path" :to="menu.path">

        <el-menu-item v-if="menu.name != 'profile.vue'" :index="menu.path">
          <component :is="menu.icon" style="margin-right:5px; width: 1.5em; height: 1.5em; color:#123456"></component>
          {{ menu.label }}
        </el-menu-item>
      </router-link>
    </el-sub-menu>
  </el-menu>
</template> 
 
 
<script>
// import applist_page from './pages/apps.vue'
import VueRouter from "vue-router_global"
import { system } from './api/api.js'

import { ref } from 'vue'
 
import { Menu as IconMenu, Message, Setting } from 'element_icon'

const router = VueRouter.createRouter({
  history: VueRouter.createWebHashHistory(),
  routes: [],
})
app.use(router)
window.router=router


export default {
  components: {
    IconMenu, Message, Setting
  },
  props: {
    isCollapse: Boolean
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
      var compare = (a, b) => a.file == 'home.vue' ? -1 : 0
      for (var _dir in data) {
        data[_dir].sort(compare)
      }
      let _routes = []

      for (var _dir in data) {
        let _icon = _routes.length == 0 ? 'Setting' : 'Folder'

        let dir_name = _dir == '.' ? '项目设置' : _dir
        dir_name = dir_name == 'general' ? '通用管理' : dir_name
        let menus = {
          path: '/' + dir_name,
          icon: _icon,
          label: dir_name,
          children: [],

        };
        let isHome = false

        for (var _i in data[_dir]) {
          let icon = data[_dir][_i].icon ? data[_dir][_i].icon : 'Document'
          let _file = data[_dir][_i].file
          isHome = _file == 'home.vue'
          let url = `pages/${_dir}/${_file}` // data[_name]['file_path']
          let _path = `${_dir}/${_file}`.replace(".vue", "")
          _path = '/' + (isHome ? '' : _path)

          menus.children.push({
            name: _file,
            path: _path,
            icon: icon,
            label: data[_dir][_i].title,

            component: () => import(url),// 设置 component 属性为一个函数，该函数会动态地加载路由对应的组件
          })

        }
        _routes.push(menus)
        router.addRoute(menus)

      }
      router.replace('/')
      this.routes = _routes

      console.log('ROUTERS', router.getRoutes())
    },
  },
  setup(props) {
    console.log('menus.vue has props', props)
    const routes = ref(router.options.routes)
    return {
      routes, props
    }

  },
  updated() {
    console.log("menus.vue updated...")
  }
}
</script>
<style scoped>
.el-sub-menu a {
  border-bottom: none;
  text-decoration: none;
}

.el-menu-item {
  padding-left: 70px !important;
}
</style>
 