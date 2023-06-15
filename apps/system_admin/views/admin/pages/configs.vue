 
<template>
  <div>
    <el-collapse accordion class="demo-collapse" v-model="activeNames">
      <config-section v-for="(value, key) in configs" :key="key" :section-key="key" :section-data="value" />
    </el-collapse>
  </div>
</template>
  
<script>
import { ref, defineComponent } from 'vue'
import { system } from 'api/api.js'
import   ConfigSection  from "./_component_configs.vue";

debugger

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
  width: 100%;
}

.demo-collapse .el-select {
  width: 100%;
}

.demo-collapse .el-collapse-item__wrap {
  margin-bottom: 20px;
}
</style>
  