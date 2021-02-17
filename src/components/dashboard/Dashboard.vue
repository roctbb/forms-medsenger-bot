<template>
    <div>
        <h2>Пациент: {{ patient.info.name }}</h2>
        <strong>Опросники</strong>
        <ul>
            <li v-for="form in patient.forms">{{ form.title }}<br><small>{{ form.doctor_description }}</small></li>
        </ul>

        <button class="btn btn-primary btn-sm" @click="create_form()">Добавить</button>
    </div>
</template>

<script>
export default {
    name: "Dashboard",
    props: {
        patient: {
            required: true
        }
    },
    methods: {
        create_form: function () {
            Event.fire('navigate-to-create-form-page')
        }
    },
}
</script>

<style scoped>

</style>
