<template>
<div style="margin-bottom: 20px">
    <div class="row" v-if="!isNaN(start_from)">
        <div v-for="(color, index) in colors" class="col d-flex justify-content-center"> {{ index + start_from }} </div>
    </div>
    <div class="row">
        <div v-for="(color, index) in colors" class="col" :style="'height: 20px; background-color: ' + color"></div>
    </div>
    <slot></slot>
</div>
</template>

<script>
export default {
    name: "VisualAnalogScale",
    props: ['colors', 'start_from']
}
</script>

<style scoped>

</style>
