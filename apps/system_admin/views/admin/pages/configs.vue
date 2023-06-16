 
<template>
  <div>
    <el-collapse   class="demo-collapse" v-model="activeNames">
      <config-section @on_save="on_save_form" v-for="(value, key) in configs" :key="key" :sub-item="false" :section-key="key" :section-data="value" />
    </el-collapse>
  </div>
</template>
  
<script>
import { ref, defineComponent } from 'vue'
import { system } from 'api/api.js'
import   ConfigSection  from "./_component_configs.vue";

 
 
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
    on_save_form(param){
      console.log(param.key,param.data)
    }
  }
}


</script>
<style>
.demo-collapse {
  padding: 15px;
  margin: 15PX;
}

.demo-collapse .el-card {
  width: auto;
  margin-bottom: 4px;
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
  