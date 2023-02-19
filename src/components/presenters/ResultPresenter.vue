<template>
    <div>
        <h3 style="text-align: center; margin-bottom: 15px;">{{result.result}}</h3>

        <div :class="`alert alert-${result.urgent ? 'danger' : 'info'}`">
            <p style="text-align: center" v-html="result.message"></p>
        </div>

        <p v-if="result.action" style="text-align: center">
            <a class="btn btn-success" :href="result.url">{{result.action}}</a>
        </p>
    </div>
</template>

<script>
export default {
    name: "ResultPresenter",
    props: ['result']
}
</script>

<style scoped>

</style>
