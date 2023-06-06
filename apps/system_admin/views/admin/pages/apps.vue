 
<template>
  <Suspense>
    <el-container>
      
      <el-table :data="applist" :border="parentBorder" style="width: 100%">
        <el-table-column type="expand">
          <template #default="props">
            <div m="2"> 
              <h3>Routes</h3>
              <el-table :data="props.row.routes" :border="childBorder">
                <el-table-column label="Controller" prop="function" :formatter="get_controller" width="150" />
                <el-table-column label="Path" prop="path" width="450" />
                <el-table-column label="Methods" prop="methods" width="110" />
                <el-table-column label="Title" prop="doc.title" />
                <el-table-column label="Nav" prop="doc.nav" width="80"/>
                <el-table-column label="Auth Type" prop="auth" :formatter="format_auth" width="120" /> 
              </el-table>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="App Name" prop="app_name" width="150"/>
        <el-table-column label="Version" prop="version" width="80" />
        <el-table-column label="Author" prop="author" width="150" />
        <el-table-column label="License" prop="license" width="100" />
        <el-table-column label="Title" prop="title" />
        <el-table-column label="Category" prop="category" width="120"/>
        <el-table-column label="Description" prop="description" width="350" />
      </el-table>
    </el-container>
    <!-- 在 #fallback 插槽中显示 “正在加载中” -->
    <template #fallback>
      Loading...
    </template>
  </Suspense>
</template>
<script>
const { ElTable, ElTableColumn, ref } = Vue
import { system } from 'api/api.js'

export default {
  components: {
    ElTable, ElTableColumn
  },
  methods: {
    // 获取应用列表数据的方法
    async getData() {

      const res = await system.getAppList();
      console.log(res);

      this.applist = res

    },
    format_auth(row){
       
      if( !row.auth){
        return 'inherit'
      }
      return row.auth
    },
    get_controller(row){
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
    return {
      applist,parentBorder,childBorder
    }
  },
  updated() {
    console.log("bar.vue updated...")
  }
}
</script>
<style  >
.el-table__expanded-cell {
    background: #fffbfb;
    padding: 0px 5px 5px 50px !important;
}
.el-table h3{
  font-style: italic;
    border-bottom: 1px solid #AAA;
}
</style>