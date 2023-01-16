<template>
<div style="margin-bottom: 20px">
    <div class="row" v-if="!isNaN(params.start_from)">
        <div v-for="(color, index) in params.colors" class="col-1 d-flex justify-content-center">
            {{ params.abs ? Math.abs((params.reversed ? -1 : 1) * index + params.start_from) : (params.reversed ? -1 : 1) * index + params.start_from }}
        </div>
    </div>
    <div class="row">
        <div v-for="(color, index) in params.colors" class="col-1" style="height: 20px; border: 1px solid #444;" :style="'background-color: ' + color"></div>
    </div>
    <slot></slot>
</div>
</template>

<script>
export default {
    name: "VisualAnalogScale",
    props: ['params']
}
</script>

<style scoped>

</style>
