<template>
  <div class="toolbar">
    <span style="position: absolute;left:10px;font-weight: bold;font-size: x-large;">Irails</span>
    <Suspense><el-dropdown>

        <span>{{ user.username }} <el-icon style="padding: 5px;margin-top:3px;">
            <setting />
          </el-icon></span>


        <template #dropdown>
          <el-dropdown-menu> 
            <el-dropdown-item @click="exit_login">Exit</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </Suspense>
  </div>
</template>
<script>
import { ElDropdown, ElDropdownMenu, ElDropdownItem } from 'element_ui'
import { ElIcon } from 'element_icon'
import { user } from './api/api.js'

export default {
  components: {
    ElDropdown, ElIcon, ElDropdownMenu, ElDropdownItem
  },
  methods:{
    async exit_login(){
      console.log("exit_login")
      await user.exit_login()
      window.location.href = "/"
    }
  },
  created() {
    console.log('headers created')
  },
  async mounted() {
    console.log('headers mounted')

    this.user = await user.getCurrentUser()
  },
  data() {
    return {
      user: {username:''}
    }
  },

  updated() {
    console.log("headers.vue updated...")
  }
}
</script>
<style scoped>
.toolbar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  right: 60px;
}
</style>