<template>
    <el-collapse-item :title="sectionKey">
        <el-form>
            <template v-for="(value, key) in sectionData">
                <el-form-item :label="key">
                    <template v-if="Array.isArray(value)">
                        <el-select v-model="sectionData[key]" multiple>
                            <el-option v-for="(option, optionIndex) in value" :key="optionIndex" :label="option"
                                :value="option"></el-option>
                        </el-select>
                    </template>
                    <template v-else-if="typeof value === 'boolean'">
                        <el-checkbox v-model="sectionData[key]"></el-checkbox>
                    </template>
                    <template v-else-if="typeof value === 'object'"> 
                        <config-section :section-key="key" :section-data="value" /> 
                    </template>
                    <template v-else>
                        <el-input v-model="sectionData[key]"></el-input>
                    </template>
                </el-form-item>
            </template>
        </el-form>
    </el-collapse-item>
</template>
  
<script>
export default {
    name: "ConfigSection",

    props: ["sectionData", "sectionKey"],
};

</script>
  