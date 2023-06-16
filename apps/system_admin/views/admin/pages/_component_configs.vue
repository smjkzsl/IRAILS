<template>
    <el-collapse-item v-if="!subItem && !isEmpty(sectionData)" :title="capitalizeFirstLetter(sectionKey)">
        <el-form :ref="sectionKey" v-model="sectionData" v-if="!isEmpty(sectionData)">
            <div class="form-tool-bar">
                <el-button @click="submit(sectionKey)" type="primary">保存</el-button>
            </div>
            <template v-for="(value, key) in sectionData">
                <el-form-item :label="key" v-if="typeof value != 'object'">
                    <template v-if="Array.isArray(value)">
                        <el-select v-model="sectionData[key]" multiple filterable allow-create :placeholder="key">
                            <el-option v-for="(option, optionIndex) in value" :key="optionIndex" :label="option"
                                :value="option"></el-option>
                        </el-select>
                    </template>
                    <template v-else-if="typeof value === 'boolean'">
                        <el-checkbox v-model="sectionData[key]"></el-checkbox>
                    </template>

                    <template v-else>
                        <el-input v-model="sectionData[key]"></el-input>
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
                <el-select v-model="sectionData[key]" multiple filterable allow-create>
                    <el-option v-for="(option, optionIndex) in value" :key="optionIndex" :placeholder="key" :label="option"
                        :value="option"></el-option>
                </el-select>
            </template>
            <template v-else-if="typeof value === 'boolean'">
                <el-checkbox v-model="sectionData[key]"></el-checkbox>
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
                <el-input v-model="sectionData[key]"></el-input>
            </template>
        </el-form-item>
    </template>
</template>
  
<script>

import { defineEmits } from 'vue'

export default {
    name: "ConfigSection",
    emits: ['on_save'],
    props: ["sectionData", "sectionKey", "subItem"],
    setup() {

    },
    methods: {
        capitalizeFirstLetter(str) {
            return str.charAt(0).toUpperCase() + str.slice(1);
        },
        isEmpty(obj) {
            if(typeof obj=='undefined' || !obj){
                return true
            }
            return Object.keys(obj).length === 0;
        },
        submit(key) {
            this.$emit('on_save', { 'key': key, 'data': this.sectionData[key] })

        }
    }
};

</script>
<style>
.form-tool-bar {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 5px;
}
</style>