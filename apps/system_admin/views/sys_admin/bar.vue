<template>
  <el-table :data="tableData" style="width: 100%">
    <el-table-column prop="date" label="Date" width="180" />
    <el-table-column prop="name" label="Name" width="180" />
    <el-table-column prop="address" label="Address" />
  </el-table>
</template>

<script>
    const {ElTable,ElTableColumn,ref} = Vue
    
    export default {
        components: {
            ElTable,ElTableColumn
        },
        data(){
             
        },
        created() {
            console.log('bar created')
        },
        mounted() {
            console.log('bar mounted')
        },
        setup(props,context){
            const tableData = [
                      {
                        date: '2016-05-03',
                        name: 'Tom',
                        address: 'No. 189, Grove St, Los Angeles',
                      },
                      {
                        date: '2016-05-02',
                        name: 'Tom',
                        address: 'No. 189, Grove St, Los Angeles',
                      },
                      {
                        date: '2016-05-04',
                        name: 'Tom',
                        address: 'No. 189, Grove St, Los Angeles',
                      },
                      {
                        date: '2016-05-01',
                        name: 'Tom',
                        address: 'No. 189, Grove St, Los Angeles',
                      },
                    ]
                return {tableData}
        },
        updated(){
            console.log("bar.vue updated...")
        }
    }
</script>