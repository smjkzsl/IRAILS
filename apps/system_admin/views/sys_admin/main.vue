<template>
    <foo/>
</template>
<script>
    import foo from './foo.vue'

    export default {
        components: {
            foo,
        },
        created() {
            console.log('main created')
        },
        mounted() {
            console.log('main mounted')
        },
        
    }
</script>           