<template>
  <div id="app1" style="height: 100%;">
    <v-form-designer ref="vfDesigner" :field-list-api="fieldListApi" :banned-widgets="testBanned"
      :designer-config="designerConfig">
      <!-- 自定义按钮插槽演示 -->
      <template #customToolButtons>
        <el-button type="text" @click="saveFormJson">保存</el-button>
      </template>
    </v-form-designer>

  </div>
</template>

<script  >
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import VForm3 from '/public/libs/vform3-builds@3.0.10/designer.umd.js'  //引入VForm 3库
import '/public/libs/vform3-builds@3.0.10/designer.style.css'  //引入VForm3样式

app.use(VForm3)
export default {
  data() {
    const vfDesigner = ref(null)
    const fieldListApi = reactive({
      URL: 'https://www.fastmock.site/mock/2de212e0dc4b8e0885fea44ab9f2e1d0/vform/listField',
      labelKey: 'fieldLabel',
      nameKey: 'fieldName'
    })
    const testBanned = ref([
      //'sub-form',
      //'alert',
    ])
    const designerConfig = reactive({
      languageMenu: true,
      externalLink: false,
      //formTemplates: false,
      //eventCollapse: false,
         
        previewFormButton: true,

      //presetCssCode: '.abc { font-size: 16px; }',
    })
    return {
      vfDesigner,fieldListApi,testBanned,designerConfig
    }
  },
  methods: {
    saveFormJson() {
      const formJson = vfDesigner.value.getFormJson()
      console.log(formJson)
      ElMessage.success('保存成功')
    }
  }
}
 
</script>

 