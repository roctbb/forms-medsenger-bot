<template>
    <div v-if="form">
        <a class="btn btn-danger btn-sm" @click="go_back()">назад</a>
        <ul>
            <li v-for="error in errors">{{ error }}</li>
        </ul>
        <div class="form">
            <card title="Параметры анкеты">
                <form-group48 title="Название анкеты">
                    <input class="form-control" v-model="form.title"/>
                </form-group48>

                <form-group48 title="Краткое описание для врача">
                    <textarea class="form-control" v-model="form.doctor_description"></textarea>
                </form-group48>

                <form-group48 title="Описание для пациента">
                    <textarea class="form-control" v-model="form.patient_description"></textarea>
                </form-group48>

                <form-group48 title="Пациент может заполнить анкету в произвольное время">
                    <input class="form-check" type="checkbox" v-model="form.show_button"/>
                </form-group48>

                <form-group48 v-if="form.show_button" title="Название анкеты для кнопки">
                    <input class="form-control" v-model="form.button_title"/>
                </form-group48>
            </card>

            <timetable-editor v-bind:data="form.timetable"/>

            <hr>
            <fields-editor v-bind:data="form.fields"/>
        </div>

        <button class="btn btn-success btn-lg" @click="save()">Сохранить</button>
    </div>
</template>

<script>

import Card from "../common/Card";
import FormGroup48 from "../common/FormGroup-4-8";
import TimetableEditor from "./parts/TimetableEditor";
import FieldsEditor from "./parts/FieldsEditor";

const axios = require('axios');

export default {
    name: "FormEditor",
    components: {FieldsEditor, TimetableEditor, FormGroup48, Card},
    props: {
        data: {
            required: false,
        }
    },
    methods: {
        go_back: function () {
            let old = JSON.parse(this.backup)
            Object.keys(old).forEach(k => {
                this.form[k] = old[k]
            })
            Event.fire('back-to-dashboard');
            this.form = undefined
        },
        create_empty_form: function () {
            return {
                fields: [],
                timetable: this.empty_timetable()
            };
        },

        check: function () {
            this.errors = [];
            if (!this.form.title) {
                this.errors.push('Укажите название анкеты')
            }
            if (this.form.show_button && !this.form.button_title) {
                this.errors.push('Укажите название для кнопки')
            }

            if (!this.verify_timetable(this.form.timetable)) {
                this.errors.push('Проверьте корректность расписания')
            }

            if (this.form.fields.length == 0) {
                this.errors.push('Добавьте хотя бы один вопрос')
            }

            let prepare_field = (field) => {
                if (['integer', 'float'].includes(field.type)) {
                    field.max = parseFloat(field.max)
                    field.min = parseFloat(field.min)
                }
                if (field.type == 'radio') {
                    if (field.params.variants) {
                        field.category = field.params.variants.map(v => v.category).join('|')
                    }
                }
                return field
            }
            this.form.fields = this.form.fields.map(prepare_field);

            let validate_field = (field) => {
                if (!field.text) return true;
                if (!Object.keys(this.field_types).includes(field.type)) return true;
                if (['integer', 'float'].includes(field.type)) {
                    if (this.ne(field.params.max) || this.ne(field.params.min)) return true;
                }
                if (field.type == 'radio') {
                    let variant_validator = (variant) => !variant.text || !variant.category
                    if (field.params.variants.length < 2) return true
                    if (field.params.variants.filter(variant_validator).length) return true;
                }
                if (!field.category) return true;
            }

            if (this.form.fields.filter(validate_field).length > 0) {
                console.log(this.form.fields.filter(validate_field))
                this.errors.push('Проверьте корректность вопросов')
            }


            if (this.errors.length != 0) {
                return false;
            } else {
                return true;
            }

        },
        save: function () {
            if (this.check()) {
                this.errors = []
                this.form.categories = this.form.fields.map(f => f.category).join('|')
                axios.post(this.url('/api/settings/form'), this.form).then(this.process_save_answer).catch(this.process_save_error);
            }
        },
        process_save_answer: function (response) {
            let is_new = this.ne(this.form.id)
            console.log(response)
            this.form.patient_id = response.data.patient_id
            this.form.id = response.data.id
            this.form.contract_id = response.data.contract_id

            if (is_new) Event.fire('form-created', this.form)
            else Event.fire('back-to-dashboard', this.form)

            this.form = undefined
        },
        process_save_error: function (response) {
            this.errors.push('Ошибка сохранения');
        }
    },
    data() {
        return {
            errors: [],
            form: undefined,
            backup: ""
        }
    },
    mounted() {
        Event.listen('navigate-to-create-form-page', () => {
            this.form = this.create_empty_form()
            console.log("create", this.form)
            this.backup = JSON.stringify(this.form)
        });

        Event.listen('navigate-to-edit-form-page', form => {
            this.form = form
            this.backup = JSON.stringify(form)
            this.$forceUpdate()
        });
    }
}
</script>

<style scoped>

</style>
