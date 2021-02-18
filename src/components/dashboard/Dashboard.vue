<template>
    <div>
        <h2>Пациент: {{ patient.info.name }}</h2>
        <strong>Опросники</strong>
        <ul>
            <li v-for="(form, i) in patient.forms">{{ form.title }}<br><small>{{ form.doctor_description }}</small><br>
            <a href="#" @click="edit_form(form)">Редактировать</a>
            <a href="#" @click="delete_form(form)">Удалить</a></li>
        </ul>

        <button class="btn btn-primary btn-sm" @click="create_form()">Добавить</button>

        <hr>

        <strong>Лекарства</strong>
        <ul>
            <li v-for="(medicine, i) in patient.medicines">{{ medicine.title }}<br>
            <a href="#" @click="edit_medicine(medicine)">Редактировать</a>
            <a href="#" @click="delete_medicine(medicine)">Удалить</a></li>
        </ul>

        <button class="btn btn-primary btn-sm" @click="create_medicine()">Добавить</button>
    </div>
</template>

<script>
const axios = require('axios');

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
        },
        edit_form: function (form) {
            Event.fire('edit-form', form)
        },
        delete_form: function (form) {
            axios.post(this.url('/api/settings/delete_form'), form).then(this.process_delete_form_answer);
        },
        process_delete_form_answer: function (response) {
            if (response.data.deleted_id)
            {
                this.patient.forms = this.patient.forms.filter(f => f.id != response.data.deleted_id)
            }
        },
        create_medicine: function () {
            Event.fire('navigate-to-create-medicine-page')
        },
        edit_medicine: function (medicine) {
            Event.fire('edit-medicine', medicine)
        },
        delete_medicine: function (medicine) {
            axios.post(this.url('/api/settings/delete_medicine'), medicine).then(this.process_delete_medicine_answer);
        },
        process_delete_medicine_answer: function (response) {
            if (response.data.deleted_id)
            {
                this.patient.medicines = this.patient.medicines.filter(m => m.id != response.data.deleted_id)
            }
        },
    },
}
</script>

<style scoped>

</style>
