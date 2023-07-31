<template>

    <el-container>
        <!-- Add / Update Dialog -->
        <el-dialog :append-to-body="true" v-model="dialogVisible" :title="dialogTitle">
            <el-form :model="dialogForm" label-width="120px">
                <el-form-item v-for="(column, index) in managed_columns" :label="column.description" :key="index">
                    
                    <el-input v-if="column.type.includes('VARCHAR')" v-model="dialogForm[column.key]"></el-input>
                    <el-checkbox v-else-if="column.type === 'BOOLEAN'" v-model="dialogForm[column.key]"></el-checkbox>
                    <el-input v-else :disabled="column.primary_key===true || column.key=='id'" v-model="dialogForm[column.key]"></el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click="dialogVisible = false">Cancel</el-button>
                <el-button type="primary" @click="dialogConfirm">Confirm</el-button>
            </div>
        </el-dialog>    

        <!-- Left Side Model List --> 
        <el-aside width="150px">
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
            <el-table :data="activeModelData"  >
                <el-table-column v-for="(column, index) in managed_columns" :prop="column.key"
                    :label="column.description" :key="index">
                    <template #default="{ row }">
                        <span>{{ row[column.key] }}</span>
                    </template>
                    
                </el-table-column>
                <el-table-column label="">
                    <template #default="scope">
                        <el-button size="small" type="text" @click="handleUpdate(scope.row)">update</el-button>
                        <el-button size="small" type="text" @click="handleDelete(scope.row)">delete</el-button>
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
import { modelManager, system } from 'api/api.js';
import {ref} from 'vue'
import {ElMessage} from 'element-plus'
export default {
    methods: {
        async handleAdd() {
            if(this.activeModel && this.activeModel.columns){ 
                this.dialogForm = this.defaultForm();
                this.dialogTitle = 'Add New Entry - ' + this.activeModel.module;
                this.dialogVisible = true;
                this.dialogAction = 'add';
            }else{
                ElMessage("Please choose the model to Add")
            }
        },
        async handleUpdate(row) {
            this.dialogForm = Object.assign({}, row);
            this.dialogTitle = 'Update Entry - ' + this.activeModel.module + '('+ row.id +')';
            this.dialogVisible = true;
            this.dialogAction = 'update';
        },
        async dialogConfirm() {
            if (this.dialogAction === 'add') {
                // Implement API call to add new data
            } else if (this.dialogAction === 'update') {
                // Implement API call to update existing data
            }
            this.dialogVisible = false;
            this.fetchModelData();
        },
        defaultForm() {
            let form = {};
            this.managed_columns.forEach(column => {
                form[column.key] = '';
            });
            return form;
        },
        findInApp(moduleName) {
            let ret = null
         
            for (var index in  this.appList) {
                var app = this.appList[index]
                if (moduleName == app.app_name) {
                    ret = app
                    break
                }
            }
            return ret
        },
        async getMetaDatas() {
            this.models = await modelManager.getModelMeta();
            this.appList = await system.getAppList()
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
                 
                let _module = this.findInApp(moduleName )
                if (_module) {
                    moduleName = '【'+_module.title+'】'
                    if (!this.modelGroups[moduleName]) {
                        this.modelGroups[moduleName] = [];
                    }
                    this.modelGroups[moduleName].push(newModel);
                }

            }
            console.log(this.modelGroups)
            // Initialize activeModelIndex to the first model in the list
            if (this.modelArray.length > 0) {
                this.activeModelIndex = this.modelArray[0].module;
            }


        },
        async fetchModelData() {
            if (this.working) {
                return
            }
            this.working = true

            let moduleName = ""
            const _arr = this.activeModel.module.split(".")
            if (_arr.length > 2) {
                moduleName = _arr.slice(0, -2).join('.');
            } else {
                moduleName = _arr[0]
            }
            const model_name = _arr.pop(0)

            const result = await modelManager.fetchModelData(moduleName, model_name, this.currentPage, this.pageSize);
            if (result) {
                this.activeModelData = result.data;
                this.currentPage = result.currentPage;
                this.pageSize = result.pageSize;
                this.total = result.total;
            }
            this.working = false
        },
        handleSelect(index) {

            this.activeModelIndex = index;
            this.activeModel = this.models[this.activeModelIndex];
            // Fetch data of active model
            this.fetchModelData()
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
    computed:{
        managed_columns(){
            if(this.activeModel && this.activeModel.columns){
                return this.activeModel.columns.filter((col)=>
                {
                    if (col.info && col.info.manager===true){
                        return true
                    }else if(col.info && col.info.manager===false){
                        return false
                    }else{
                        return true
                    }
                })
            }else{
                return []
            }
            
        },
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
            appList: [],
            working: false,
            dialogVisible: ref(false),
            dialogForm: {},
            dialogTitle: '',
            dialogAction: '',

        };
    },

}; 
</script>
