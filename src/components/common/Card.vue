<template>
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{{ title }}</h5>
            <slot></slot>
        </div>
    </div>
</template>

<script>
export default {
    name: "Card",
    props: ['title']
}
</script>

<style scoped>
    .card {
        margin-bottom: 15px;
    }
</style>
