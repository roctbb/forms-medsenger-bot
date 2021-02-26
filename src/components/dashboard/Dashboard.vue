<template>
    <div>
        <h2>Пациент: {{ patient.info.name }}</h2>

        <div v-if="state == 'main'">

            <h3>Мониторинг и лечение</h3>

            <strong>Опросники</strong>
            <ul>
                <li v-for="(form, i) in patient.forms">{{ form.title }}<br><small>{{ form.doctor_description }}</small><br>
                    <a href="#" @click="edit_form(form)">Редактировать</a>
                    <a href="#" @click="delete_form(form)">Удалить</a>
                    <a target="_blank" :href="preview_form_url(form)">Просмотр</a></li>
            </ul>

            <button class="btn btn-primary btn-sm" @click="state = 'form_templates'">Выбрать или добавить свой</button>

            <hr>

            <strong>Лекарства</strong>
            <ul>
                <li v-for="(medicine, i) in patient.medicines">{{ medicine.title }}<br>
                    <a href="#" @click="edit_medicine(medicine)">Редактировать</a>
                    <a href="#" @click="delete_medicine(medicine)">Удалить</a></li>
            </ul>

           <button class="btn btn-primary btn-sm" @click="state = 'medicine_templates'">Выбрать или добавить свое</button>

            <hr>

            <strong>Алгоритмы</strong>
            <ul>
                <li v-for="(algorithm, i) in patient.algorithms">{{ algorithm.title }}<br>
                    <a href="#" @click="edit_algorithm(algorithm)">Редактировать</a>
                    <a href="#" @click="delete_algorithm(algorithm)">Удалить</a></li>
            </ul>

            <button class="btn btn-primary btn-sm" @click="state = 'algorithm_templates'">Выбрать или добавить свой</button>

        </div>
        <div v-if="state == 'form_templates'">
            <h3>Шаблоны опросников</h3>

            <ul>
                <li v-for="(form, i) in templates.forms">{{ form.title }}<br><small>{{ form.doctor_description }}</small><br>
                    <a href="#" @click="attach_form(form)">Подключить</a>
                    <a href="#" @click="edit_form(form)">Редактировать</a>
                    <a href="#" @click="delete_form(form)">Удалить</a>
                    <a target="_blank" :href="preview_form_url(form)">Просмотр</a></li>
            </ul>

            <button class="btn btn-primary btn-sm" @click="create_form()">Добавить</button>
            <button class="btn btn-danger btn-sm" @click="state = 'main'">Назад</button>

        </div>
        <div v-if="state == 'medicine_templates'">
            <h3>Шаблоны лекарств</h3>

            <ul>
                <li v-for="(medicine, i) in templates.medicines">{{ medicine.title }}<br>
                    <a href="#" @click="attach_medicine(medicine)">Подключить</a>
                    <a href="#" @click="edit_medicine(medicine)">Редактировать</a>
                    <a href="#" @click="delete_medicine(medicine)">Удалить</a></li>
            </ul>

            <button class="btn btn-primary btn-sm" @click="create_medicine()">Добавить</button>
            <button class="btn btn-danger btn-sm" @click="state = 'main'">Назад</button>

        </div>
        <div v-if="state == 'algorithm_templates'">
            <h3>Шаблоны алгоритмов</h3>

            <ul>
                <li v-for="(algorithm, i) in templates.algorithms">{{ algorithm.title }}<br>
                    <a href="#" @click="attach_algorithm(algorithm)">Подключить</a>
                    <a href="#" @click="edit_algorithm(algorithm)">Редактировать</a>
                    <a href="#" @click="delete_algorithm(algorithm)">Удалить</a></li>
            </ul>

            <button class="btn btn-primary btn-sm" @click="create_algorithm()">Добавить</button>
            <button class="btn btn-danger btn-sm" @click="state = 'main'">Назад</button>

        </div>


    </div>
</template>

<script>

export default {
    name: "Dashboard",
    props: {
        patient: {
            required: true
        },
        templates: {
            required: true
        }
    },
    data: function () {
        return {
            state: 'main'
        }
    },
    methods: {
        attach_form: function (form) {
            Event.fire('attach-form', form)
        },
        attach_algorithm: function (algorithm) {
            Event.fire('attach-algorithm', algorithm)
        },
        attach_medicine: function (medicine) {
            Event.fire('attach-medicine', medicine)
        },
        create_form: function () {
            Event.fire('navigate-to-create-form-page')
        },
        edit_form: function (form) {
            Event.fire('edit-form', form)
        },
        delete_form: function (form) {
            this.axios.post(this.url('/api/settings/delete_form'), form).then(this.process_delete_form_answer);
        },
        preview_form_url: function (form) {
            return this.url('/form/' + form.id)
        },
        process_delete_form_answer: function (response) {
            if (response.data.deleted_id) {
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
            this.axios.post(this.url('/api/settings/delete_medicine'), medicine).then(this.process_delete_medicine_answer);
        },
        create_algorithm: function () {
            Event.fire('navigate-to-create-algorithm-page')
        },
        edit_algorithm: function (algorithm) {
            Event.fire('edit-algorithm', algorithm)
        },
        delete_algorithm: function (algorithm) {
            this.axios.post(this.url('/api/settings/delete_algorithm'), algorithm).then(this.process_delete_algorithm_answer);
        },
        process_delete_medicine_answer: function (response) {
            if (response.data.deleted_id) {
                this.patient.medicines = this.patient.medicines.filter(m => m.id != response.data.deleted_id)
            }
        },
        process_delete_algorithm_answer: function (response) {
            if (response.data.deleted_id) {
                this.patient.algorithms = this.patient.algorithms.filter(m => m.id != response.data.deleted_id)
            }
        },
    },
    mounted() {
        Event.listen('dashboard-to-main', () => this.state = 'main');
    }
}
</script>

<style scoped>

</style>
