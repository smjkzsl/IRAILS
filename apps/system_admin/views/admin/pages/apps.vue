 
<template>
  <div class="app-lists">
    <div class="headers">
      <el-text class="mx-1" type="primary">Filter:</el-text>
      <el-radio-group v-model="states" @change="filter_change">
        <el-radio-button label="installed" />
        <el-radio-button label="uninstalled" />
        <el-radio-button label="all" />
      </el-radio-group>
    </div>
    <Suspense>

      <el-container>

        <el-table :data="applist" :border="parentBorder" style="width: 100%">
          <el-table-column type="expand">
            <template #default="props">
              <div m="2">
                <h3>Routes (count {{ props.row.routes.length }})<el-text v-if="!props.row.is_installed">(Not Installed)</el-text></h3>
                <el-table v-if="props.row.is_installed" :data="props.row.routes" :border="childBorder">
                  <el-table-column label="Controller" prop="function" :formatter="get_controller" width="150" />
                  <el-table-column label="Path" prop="path" width="450">
                    <template #default="scope">
                      <el-link   v-if="scope.row.methods.indexOf('GET')>-1" target="_blank" :href="scope.row.path"  >
                        {{ scope.row.path }} <el-icon class="el-icon--right"><icon-view /></el-icon>
                      </el-link>
                      <span v-else-if="scope.row.methods.indexOf('GET')==-1">{{ scope.row.path }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="Methods" prop="methods" width="110" />
                  <el-table-column label="Title" prop="doc.title" />
                  <el-table-column label="Nav" prop="doc.nav" width="80" />
                  <el-table-column label="Auth Type" prop="auth" :formatter="format_auth" width="120" />
                </el-table>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="App Name" prop="app_name" width="150" />
          <el-table-column label="Version" prop="version" width="80" />
          <el-table-column label="Author" prop="author" width="150" />
          <el-table-column label="License" prop="license" width="100" />
          <el-table-column label="Title" prop="title" />
          <el-table-column label="Category" prop="category" width="120" />
          <el-table-column label="Description" prop="description" width="350" />
          <el-table-column fixed="right" label="Operations" width="140">
            <template #default="scope">
              <el-button link type="primary" size="small" v-if="scope.row.is_installed"
                @click="uninstall(scope.$index, scope.row)">Uninstall</el-button>
              <el-button link type="primary" v-if="!scope.row.is_installed" size="small"
                @click="install(scope.$index, scope.row)">Install</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-container>
      <!-- 在 #fallback 插槽中显示 “正在加载中” -->
      <template #fallback>
        Loading...
      </template>
    </Suspense>
  </div>
</template>
<script>
import { ElTable, ElTableColumn, ref, toRaw } from 'vue'
import { system } from 'api/api.js'
import { ElMessageBox, ElMessage } from 'element-plus'
import { Edit, View as IconView } from 'element_icon'

export default {
  components: {
    ElTable, ElTableColumn ,IconView
  },
  methods: {
    filter_change(value) {

      this.states = value
      this.getData()
    },
    async install(index, row) {


      ElMessageBox.confirm(`Are you sure to install "${row.app_name}"?`, '安装', {
        confirmButtonText: 'OK',
        cancelButtonText: 'Cancel',
        type: 'info',
      })
        .then(() => {
          console.log(row.app_name)

          this.install_app(row.app_name)
          this.getData()
        })
    },
    async uninstall(index, row) {
      ElMessageBox.confirm(`Are you sure to uninstall "${row.app_name}"?`, '警告', {
        confirmButtonText: 'OK',
        cancelButtonText: 'Cancel',
        type: 'warning',
      })
        .then(() => {
          console.log(row.app_name)

          this.uninstall_app(row.app_name)
          this.getData()
        })



    },
    async install_app(app_name) {
      let ret = await system.install_app(app_name)
      ElMessage(ret)
      this.getData()
    },
    async uninstall_app(app_name) {
      let ret = await system.uninstall_app(app_name)
      ElMessage(ret)
    },
    async getData() {

      const t = this.states || 'installed'
      const res = await system.getAppList(t);
      console.log(res);

      this.applist = res

    },
    format_auth(row) {

      if (!row.auth) {
        return 'inherit'
      }
      return row.auth
    },
    get_controller(row) {
      var ar = row.function.split(".")
      return ar[0]

    }
  },
  mounted() {
    this.getData()
  },
  setup(props, context) {
    const applist = Vue.ref([])
    const parentBorder = ref(true)
    const childBorder = ref(false)
    const states = ref('installed')
    return {
      applist, parentBorder, childBorder, states
    }
  },
  updated() {
    console.log("apps.vue updated...")
  }
}
</script>
<style  >
.el-table__expanded-cell {
  background: #fffbfb;
  padding: 0px 5px 5px 50px !important;
}

.el-table h3 {
  font-style: italic;
  border-bottom: 1px solid #AAA;
}

.app-lists .headers {
  padding: 10px;
}

.mx-1 {
  margin-right: 15px;
}
</style>