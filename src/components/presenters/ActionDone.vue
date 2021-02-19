<template>
    <div>
        <h3>Действие подтверждено!</h3>

        <button class="btn btn-success">Закрыть окно</button>
    </div>
</template>

<script>
export default {
    name: "ActionDone",
    methods: {
        close: function () {
            window.parent.postMessage('close-modal-success', '*');
        }
    }
}
</script>

<style scoped>

</style>
