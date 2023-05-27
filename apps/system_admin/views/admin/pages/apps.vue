 
<template>
  <Suspense>
    <el-container>
      
      <el-table :data="applist" :border="parentBorder" style="width: 100%">
        <el-table-column type="expand">
          <template #default="props">
            <div m="2">
             
              <h3>Routes</h3>
              <el-table :data="props.row.routes" :border="childBorder">
                <el-table-column label="Path" prop="path" />
                <el-table-column label="Methods" prop="methods" />
                <el-table-column label="Title" prop="doc.title" />
                <el-table-column label="Nav" prop="doc.nav" />
                <el-table-column label="Auth Type" prop="auth" /> 
              </el-table>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="App Name" prop="app_name" />
        <el-table-column label="Version" prop="version" />
        <el-table-column label="Author" prop="author" />
        <el-table-column label="License" prop="license" />
        <el-table-column label="Title" prop="title" />
        <el-table-column label="Category" prop="category" />
        <el-table-column label="Description" prop="description" />
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
const parentBorder = ref(true)
const childBorder = ref(true)
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

    }
  },
  mounted() {
    this.getData()
  },
  setup(props, context) {
    const applist = Vue.ref([])
    return {
      applist,
    }
  },
  updated() {
    console.log("bar.vue updated...")
  }
}
</script>
<style  >
.el-table__expanded-cell {
    background: #EEE;
    padding: 0px 5px 5px 50px !important;
}
</style>