 
<template>
  <div>
    <el-collapse   class="demo-collapse" v-model="activeNames">
      <config-section @on_save="on_save_form" v-for="(value, key) in configs" :key="key" :sub-item="false" :section-key="key" :section-data="value" />
    </el-collapse>
  </div>
</template>
  
<script>
import { ref, defineComponent  } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { system } from '/system_admin/admin/api/api.js'
import   ConfigSection  from "/system_admin/admin/pages/_component_configs.vue";

 
 
export default {
  components: { ConfigSection },
  setup() {
    const activeNames = ref(['1'])
    const configs = ref({ general: { app: { apps: [] } }, database: {}, authencation: {} })
    return {
      activeNames, configs
    }
  },
  mounted() {
    this.getConfigs()
  },
  methods: {
    async getConfigs() {
      const configs = await system.get_configs()

      this.configs = configs
    },
    handleChange(val) {
      console.log(val)
    },
    async save_configs(param){
      const ret = await system.save_configs(param.key,param.data)
      if(ret=='OK'){
        ElMessage(ret+'! The change will be applied upon restarting the application.')
      }else{
        ElMessage(ret  )
      }
      
    },
    async on_save_form(param){
      ElMessageBox.confirm(`Are you sure to change config "${param.key}"?<br/>`, '更改配置', {
        confirmButtonText: 'OK',
        cancelButtonText: 'Cancel',
        type: 'warning',
      })
        .then(() => {
           this.save_configs(param)
        })

      
    }
  }
}


</script>
<style>
.demo-collapse {
  padding: 15px;
  margin: 15PX;
}
.demo-collapse .el-collapse-item.is-active{
  border: 1px solid #409EFF;
    border-radius: 10px;
}
.demo-collapse .el-collapse-item.is-active .el-button{
  display: flex;
}
.demo-collapse .el-collapse-item .el-button{
  display: none;
}
.demo-collapse .el-collapse-item.is-active .el-collapse-item__header{
  border-color: #79bbff;
  border:1px solid #79bbff;
  border-radius: 10px;
}
.demo-collapse .el-collapse-item__content {
    padding-bottom: 25px; 
    padding-left:30px;
    padding-right:30px; 
}
.demo-collapse .el-collapse-item__header{
  font-weight: bold;
  padding-left: 15px;
}
.demo-collapse .el-card {
  width: auto;
  margin-bottom: 4px;
  margin-top: 4px;
}
.demo-collapse .el-collapse-item__content>.el-form>.el-form-item{
  border:1px solid #EEE;
  border-radius: 4px;
  margin:4px 4px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
}
.demo-collapse .el-form-item__content>.el-card{
  width:100%;
}
.demo-collapse .el-form-item{
  margin-bottom: 3px;
}
.demo-collapse .el-form-item__label{
  width:140px;
}
.demo-collapse .el-card__header{
  padding: 5px;
  font-style: italic;
}
.demo-collapse .el-select {
  width: 100%;
}

.demo-collapse .el-collapse-item__wrap {
  margin-bottom: 20px;
}
.demo-collapse .el-input__wrapper{
  padding: 1px 1px 1px 1px;
  width: 100%;
}
.demo-collapse .el-input__inner{
  width: 100%;
  border:none;

}
</style>
  