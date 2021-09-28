<template>
<div>
    <div class="row">
        <div v-for="(color, index) in colors" class="col d-flex justify-content-center"> {{ index + (from_zero ? 0 : 1) }} </div>
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
    props: ['colors', 'from_zero']
}
</script>

<style scoped>

</style>
