<template>
    <el-container>
        <!-- Left Side Model List -->


        <el-aside width="200px">
            <el-menu :default-openeds="[activeModelIndex]" @select="handleSelect">
                <el-sub-menu v-for="(group, moduleName) in modelGroups" :index="moduleName" :key="moduleName">
                    <template #title>{{ moduleName }}</template>
                    <el-menu-item-group>
                        <el-menu-item v-for="(model, index) in group" :index="model.module" :key="model.module">
                            {{ model.module.split('.').pop() }}
                        </el-menu-item>
                    </el-menu-item-group>
                </el-sub-menu>
            </el-menu>
        </el-aside>

        <!-- Right Side Model Data Table -->
        <el-main>
            <el-button type="primary" @click="handleAdd">新增</el-button>
            <el-table :data="activeModelData" style="width: 100%">
                <el-table-column v-for="(column, index) in activeModel.columns" :prop="column.key"
                    :label="column.description" :key="index">
                    <template #default="{ row }">
                        <span>{{ row[column.key] }}</span>
                    </template>
                    <template #append>
                        <el-button size="mini" type="text" @click="handleUpdate(row)">update</el-button>
                        <el-button size="mini" type="text" @click="handleDelete(row)">delete</el-button>
                    </template>
                </el-table-column>
            </el-table>
            <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page="currentPage"
                :page-sizes="[10, 20, 30, 40]" :page-size="pageSize" layout="total, sizes, prev, pager, next, jumper"
                :total="total">
            </el-pagination>
        </el-main>

    </el-container>
</template>

<script>
import { modelManager } from 'api/api.js';
export default {
    methods: {
        async getMetaDatas() {
            this.models = await modelManager.getModelMeta();
            // Convert models object to array and group by module
            for (let _model in this.models) {
                let newModel = this.models[_model];
                newModel.module = _model;
                this.modelArray.push(newModel);
                let _arr = _model.split('.')
                let moduleName = ""
                if (_arr.length > 2) {
                    moduleName = _arr.slice(2, 3).join('.');
                } else {
                    moduleName = _arr[0]
                }
                if (!this.modelGroups[moduleName]) {
                    this.modelGroups[moduleName] = [];
                }
                this.modelGroups[moduleName].push(newModel);
            }
            console.log(this.modelGroups)
            // Initialize activeModelIndex to the first model in the list
            if (this.modelArray.length > 0) {
                this.activeModelIndex = this.modelArray[0].module;
            }


        },
        async fetchModelData() {
            if(this.working){
                return
            }
            this.working=true

            let moduleName=""
            const _arr = this.activeModel.module.split(".")
            if (_arr.length > 2) {
                    moduleName = _arr.slice(0, -2).join('.');
                } else {
                    moduleName = _arr[0]
                } 
            const model_name = _arr.pop(0)
            debugger
            const response = await modelManager.fetchModelData(moduleName,model_name, this.currentPage, this.pageSize);
            if (response) {
                this.activeModelData = response.data;
                this.currentPage = response.currentPage;
                this.pageSize = response.pageSize;
                this.total = response.total;
            }
            this.working = false
        },
        handleSelect(index) {

            this.activeModelIndex = index;
            this.activeModel = this.models[this.activeModelIndex];
            // Fetch data of active model
            this.fetchModelData()
        },

        handleAdd() {
            // Implement add functionality
        },
        handleUpdate(row) {
            // Implement update functionality
        },
        handleDelete(row) {
            // Implement delete functionality
        },// Pagination methods
        handleSizeChange(val) {
            this.pageSize = val;
            this.fetchModelData();
        },
        handleCurrentChange(val) {
            this.currentPage = val;
            this.fetchModelData();
        },
    },
    created() {
        this.getMetaDatas()
    },
    data() {
        return {
            models: {},
            activeModel: {},
            activeModelIndex: "", // Default active model index, to be initialized later
            activeModelData: [], // Data of active model
            modelArray: [], // Array to hold models
            modelGroups: {}, // Grouped models
            currentPage: 1,
            pageSize: 20,
            total: 0,

            working:false,
        };
    },

}; 
</script>
