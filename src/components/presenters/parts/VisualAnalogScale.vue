<template>
<div style="margin-bottom: 20px">
    <div class="row" v-if="params.left_label || params.right_label">
        <div  :class="`col-5 d-flex justify-content-start`" v-if="params.left_label">
            <small>{{ params.left_label }}</small>
        </div>
        <div  :class="`col-5 offset-2 d-flex justify-content-end`" v-if="params.right_label">
            <small>{{ params.right_label }}</small>
        </div>
    </div>
    <div class="row" v-if="!isNaN(params.start_from)">
        <div v-for="(color, index) in params.colors" class="col d-flex justify-content-center">
            {{ params.abs ? Math.abs((params.reversed ? -1 : 1) * index + params.start_from) : (params.reversed ? -1 : 1) * index + params.start_from }}
        </div>
    </div>
    <div class="row">
        <div v-for="(color, index) in params.colors" class="col" style="height: 20px; border: 1px solid #444;" :style="'background-color: ' + color"></div>
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
