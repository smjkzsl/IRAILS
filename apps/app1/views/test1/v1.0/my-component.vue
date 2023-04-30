<template>
    <div class="hello" @click="clickme">click me to change:Hello {{who}} From my-component.vue</div>
    
</template>

<script>
var that;
       
module.exports = { 
    data: function() { 
        return {
            who: 'irails',
            visible: false
        }
    },
    methods:{ 
        clickme:function(evt){
            console.log('clickme',evt)
             
            this.who="我啊"
        }
    }
}
</script>

<style scoped>
.hello {
    background-color: #ffe;
    color:blue;
}
</style>