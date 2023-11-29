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
            <el-dropdown-item @click="gotoProfile">Profile
              <el-icon style="padding: 5px;margin-top:3px;">
                <user />
              </el-icon>

            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </Suspense>

    <button @click="toggleDark()">
      <el-icon v-if="!isDark" ><Sunny /></el-icon>
      <el-icon v-if="isDark" ><Moon /></el-icon> 
      <span class="ml-2">{{ isDark ? '暗' : '亮' }}</span>
    </button>
    <button v-if="$i18n" v-for="locale in  $i18n.availableLocales" @click="toggleLan(locale)">
      <span>{{ locale }}</span>
    </button>
  </div>
</template>
<script>
 
import { ElDropdown, ElDropdownMenu, ElDropdownItem } from 'element_ui'
import { ElIcon } from 'element_icon'
import { user } from './api/api.js'
import {ref} from 'vue'
const i18n = require('./api/i18n.js')
const {  useI18n } = require("vue-i18n_global")
export default {
  components: {
    ElDropdown, ElIcon, ElDropdownMenu, ElDropdownItem
  },
  setup() {
     
    return{
       
      isDark : VueUse.useDark()
    }
  },
  methods: {
    async exit_login() {
      console.log("exit_login")
      await user.exit_login()
      window.location.href = "/"
    },
    gotoProfile() {
      console.log("gotoProfile")

      this.$router.push("/./profile")
    },
    toggleDark (){
      console.log(this.isDark)
      this.isDark = !this.isDark
      VueUse.useToggle(this.isDark)
    },
    toggleLan(locale){
      i18n.setI18nLanguage(i18n._i18n,locale)
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
      user: { username: '' }
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