<template>
    <card class="col-lg-3 col-md-4" :image="images.form">
        <strong class="card-title"> {{ form.title }}</strong>
        <small v-if="!empty(form.doctor_description)">{{ form.doctor_description }}<br></small>
        <br>
        <small><i>{{ tt_description(form.timetable) }}</i><br></small>

        <small v-if="form.is_template && form.algorithm_id">
            <b>Связанный алгоритм:</b> {{ find_algorithm(form.algorithm_id).title }}
            <br>
        </small>

        <small v-if="form.sent">
            Заполнен {{ form.done }} раз(а) / отправлен {{ form.sent }} раз(а) за последний месяц
            <br>
        </small>
        <small v-else-if="!form.is_template">Пока не отправлялось<br></small>

        <!-- опросник пациента -->
        <div v-if="!form.is_template">
            <div v-if="form.contract_id == current_contract_id">
                <a href="#" @click="edit_timetable()">Изменить расписание</a>
                <a href="#" @click="edit_form()">Редактировать</a>
                <a href="#" @click="delete_form()">Удалить</a>
                <a target="_blank" v-if="!mobile" :href="preview_form_url">Просмотр</a>
                <a href="#" v-else @click="preview_form()">Просмотр</a>
            </div>
            <div v-else>
                <small>Добавлен в другом контракте.</small>
            </div>
            <div v-if="form.contract_id == current_contract_id || form.template_id">
                <a href="#" @click="send_now()">Отправить сейчас</a>
            </div>
            <br>
            <small v-if="!empty(form.template_id)" class="text-muted">ID шаблона: {{ form.template_id }}</small>
            <small v-else class="text-muted">ID опросника: {{ form.id }}</small>
        </div>

        <!-- шаблон опросника -->
        <div v-else>
            <a href="#" v-if="!is_attached" @click="attach_form()">Подключить</a>
            <small v-else class="text-muted">Опросник подключен<br></small>

            <a href="#" v-if="is_admin || patient.info.doctor_id == form.doctor_id"
               @click="edit_form()">Редактировать</a>
            <a href="#" v-if="is_admin || patient.info.doctor_id == form.doctor_id"
               @click="delete_form()">Удалить</a>
            <a target="_blank" v-if="!mobile" :href="preview_form_url">Просмотр</a>
            <a href="#" v-else @click="preview_form()">Просмотр</a>
            <a href="#" @click="send_now()">Отправить сейчас</a>
            <br>
            <small class="text-muted">ID: {{ form.id }}</small>
            <small class="text-muted" v-if="is_admin && form.doctor_id">Doctor ID: {{ form.doctor_id }}</small>
            <small class="text-muted" v-if="is_admin && form.clinic_id">Clinic ID: {{ form.doctor_id }}</small>

        </div>
    </card>
</template>

<script>
import Card from "../../common/Card";

export default {
    name: "FormCard",
    props: {
        form: {required: true},
        templates: {required: false},
        patient: {required: false}
    },
    components: {Card},
    computed: {
        preview_form_url() {
            return this.url('/preview_form/' + this.form.id)
        },
        is_attached() {
            return this.patient.forms.filter(f => f.template_id == this.form.id).length != 0
        },
    },
    methods: {
        edit_timetable: function () {
            Event.fire('edit-timetable', this.form)
        },
        edit_form: function () {
            Event.fire('edit-form', this.form)
        },
        delete_form: function () {
            this.$confirm({
                message: `Вы уверены, что хотите удалить опросник ` + this.form.title + `?`,
                button: {
                    no: 'Нет',
                    yes: 'Да, удалить'
                },
                callback: confirm => {
                    if (confirm) {
                        this.axios.post(this.url('/api/settings/delete_form'), this.form)
                            .then((response) => Event.fire('form-deleted', response.data.deleted_id));
                    }
                }
            })
        },
        preview_form: function () {
            Event.fire('preview-form', this.form)
        },
        send_now: function () {
            let alert = () => {
                window.alert("Опросник отправлен!");
            }

            let id = this.form.id

            if (this.form.contract_id != this.current_contract_id && this.form.template_id) {
                id = this.form.template_id
            }

            this.$confirm({
                message: `Отправить опросник ` + this.form.title + ` пациенту прямо сейчас?`,
                button: {
                    no: 'Нет',
                    yes: 'Да'
                },
                callback: confirm => {
                    if (confirm) {
                        this.axios.get(this.url('/api/send_form/' + id)).then(alert);
                    }
                }
            })
        },
        find_algorithm: function (id) {
            return this.templates.algorithms.filter(t => t.id == id)[0]
        },
        attach_form: function () {
            Event.fire('attach-form-from-card', this.form)
        },
    }
}
</script>

<style scoped>
p {
    margin-top: 5px;
    margin-bottom: 5px;
}

h5 {
    margin-bottom: 10px;
    margin-top: 10px;
    font-size: 1.15rem;
}

small {
    font-size: 90%;
}

.card a {
    font-size: 90% !important;
}
</style>
