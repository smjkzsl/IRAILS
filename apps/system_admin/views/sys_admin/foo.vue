<template>
    <bar/>
</template>
<script>
    import bar from './bar.vue'

    export default {
        components: {
            bar,
        },
        created() {
            console.log('foo created')
        },
        mounted() {
            console.log('foo mounted')
        },
        setup(){
            console.log("foo.vue setup...")
        },
        updated(){
            console.log("foo.vue updated...")
        }
    }
</script>