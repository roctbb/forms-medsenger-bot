<template>
    <div class="form-group row">
        <div class="col-md-4">
            <strong>{{ title }}</strong>
        </div>
        <div class="col-md-8">
            <slot></slot>
            <span class="text-muted" v-if="description">{{ description }}</span>
        </div>
    </div>
</template>

<script>
export default {
    name: "FormGroup-4-8",
    props: ['title', 'description']
}
</script>

<style scoped>

</style>
