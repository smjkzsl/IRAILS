<template>
    <el-collapse-item v-if="!subItem && !isEmpty(sectionData)">
        <template #title>

            <div class="form-tool-bar">
                <span :style="sectionKey == 'general' ? 'color:blue;' : 'color:inherit;'">
                    {{ capitalizeFirstLetter(sectionKey) }}
                    <el-icon>
                        <Postcard />
                    </el-icon>
                </span>
                
                <el-button     @click="submit($event,sectionKey, sectionData)" type="primary">保存<el-icon>
                        <FolderChecked />
                    </el-icon></el-button>
                 
            </div>
        </template>
        <el-form :ref="sectionKey" v-model="sectionData" v-if="!isEmpty(sectionData)">

            <template v-for="(value, key) in sectionData">
                <el-form-item :label="key" v-if="typeof value != 'object'">
                    <template v-if="Array.isArray(value)">
                        <el-select  @change="dataChanged" v-model="sectionData[key]" multiple filterable allow-create :placeholder="key">
                            <el-option v-for="(option, optionIndex) in value" :key="optionIndex" :label="option"
                                :value="option"></el-option>
                        </el-select>
                    </template>
                    <template v-else-if="typeof value === 'boolean'">
                        <el-checkbox  @change="dataChanged" v-model="sectionData[key]"></el-checkbox>
                    </template>

                    <template v-else>
                        <el-input  @change="dataChanged" v-model="sectionData[key]"></el-input>
                    </template>
                </el-form-item>
                <el-card v-if="typeof value === 'object'">
                    <template #header>
                        <div class="card-header">
                            <span>{{ key }}</span>

                        </div>
                    </template>
                    <config-section :section-key="key" :section-data="value" :sub-item="true" />
                </el-card>
            </template>
        </el-form>
    </el-collapse-item>

    <template v-if="subItem" v-for="(value, key) in sectionData">
        <el-form-item :label="key">
            <template v-if="Array.isArray(value)">
                <el-select  @change="dataChanged" v-model="sectionData[key]" multiple filterable allow-create>
                    <el-option v-for="(option, optionIndex) in value" :key="optionIndex" :placeholder="key" :label="option"
                        :value="option"></el-option>
                </el-select>
            </template>
            <template v-else-if="typeof value === 'boolean'">
                <el-checkbox  @change="dataChanged" v-model="sectionData[key]"></el-checkbox>
            </template>
            <template v-else-if="typeof value === 'object'">
                <el-card v-if="typeof value === 'object'">
                    <template #header>
                        <div class="card-header">
                            <span>{{ key }}</span>

                        </div>
                    </template>
                    <config-section :section-key="key" :section-data="value" :sub-item="true" />
                </el-card>
            </template>
            <template v-else>
                <el-input @change="dataChanged"  v-model="sectionData[key]"></el-input>
            </template>
        </el-form-item>
    </template>
</template>
  
<script>

import { defineEmits,ref ,nextTick  } from 'vue'
import { Grid, Postcard, Check,FolderChecked } from 'element_icon'


export default {
    name: "ConfigSection",
    emits: ['on_save'],
    props: ["sectionData", "sectionKey", "subItem",],
    setup() { 
        let data_changed = ref(false)
        return {data_changed}
    },
     
    methods: {
        capitalizeFirstLetter(str) {
            return str.charAt(0).toUpperCase() + str.slice(1);
        },
        isEmpty(obj) {
            if (typeof obj == 'undefined' || !obj) {
                return true
            }
            return Object.keys(obj).length === 0;
        },
        submit(event,key, data) {
            this.$emit('on_save', { 'key': key, 'data': data })
            event.stopPropagation();

        },
        async dataChanged  ()  { 
            console.log(this.data_changed)
           this.data_changed = true
           await nextTick()
           
        }
         
    }
};

</script>
<style scoped>
.form-tool-bar {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 5px;
}

.el-button {
    right: 100px;
    position: absolute;
    margin-top: 10px;
     
}
.button-show{
    display: flex;
}
.button-hide{
    display:none;
}
</style>