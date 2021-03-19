<template>
    <div v-if="form">
        <error-block :errors="errors"/>
        <div class="form">
            <card title="Параметры опросника">
                <form-group48 title="Название опросника">
                    <input class="form-control form-control-sm" v-model="form.title"/>
                </form-group48>

                <form-group48 title="Краткое описание для врача">
                    <textarea class="form-control form-control-sm" v-model="form.doctor_description"></textarea>
                </form-group48>

                <form-group48 title="Описание для пациента">
                    <textarea class="form-control form-control-sm" v-model="form.patient_description"></textarea>
                </form-group48>

                <form-group48 title="Пациент может заполнить опросник в произвольное время">
                    <input class="form-check" type="checkbox" v-model="form.show_button"/>
                </form-group48>

                <form-group48 v-if="form.show_button" title="Название опросника для кнопки">
                    <input class="form-control form-control-sm" v-model="form.button_title"/>
                </form-group48>

                <form-group48 v-if="is_admin && (empty(form.id) || form.is_template)" title="ID связанного алгоритма">
                    <input class="form-control form-control-sm" v-model="form.algorithm_id"/>
                </form-group48>

                <form-group48 v-if="is_admin && (empty(form.id) || form.is_template)" title="Категория шаблона">
                    <input class="form-control form-control-sm" value="Общее" v-model="form.template_category"/>
                </form-group48>

                <form-group48 title="Уведомить, если пациент не заполнят опросник">
                    <input class="form-check" type="checkbox" @change="warning_change()" v-model="form.warning_enabled"/>
                </form-group48>

                <form-group48 v-if="form.warning_enabled" title="Прислать уведомление о пропусках через">
                    <input class="form-control form-control-sm" type="number" min="1" max="200" step="1" v-model="form.warning_days"/>
                    <small class="text-muted">дней</small>
                </form-group48>
            </card>

            <timetable-editor v-bind:data="form.timetable"/>

            <hr>
            <fields-editor v-bind:data="form.fields"/>
        </div>

        <button class="btn btn-danger" @click="go_back()">Вернуться назад</button>
        <button class="btn btn-success" @click="save()">Сохранить <span v-if="form.is_template"> шаблон</span></button>
        <button v-if="!form.id && is_admin" class="btn btn-primary" @click="save(true)">Сохранить как шаблон</button>
    </div>
</template>

<script>

import Card from "../common/Card";
import FormGroup48 from "../common/FormGroup-4-8";
import TimetableEditor from "./parts/TimetableEditor";
import FieldsEditor from "./parts/FieldsEditor";
import ErrorBlock from "../common/ErrorBlock";

export default {
    name: "FormEditor",
    components: {ErrorBlock, FieldsEditor, TimetableEditor, FormGroup48, Card},
    props: {
        data: {
            required: false,
        }
    },
    methods: {
        go_back: function () {
            this.$confirm({
                message: `Вы уверены? Внесенные изменения будут утеряны!`,
                button: {
                    no: 'Нет',
                    yes: 'Да'
                },
                callback: confirm => {
                    if (confirm) {
                        let old = JSON.parse(this.backup)
                        this.copy(this.form, old)
                        Event.fire('back-to-dashboard');
                        this.form = undefined
                        this.errors = []
                    }
                }
            })

        },
        create_empty_form: function () {
            return {
                fields: [],
                timetable: this.empty_timetable(),
                warning_days: 0
            };
        },

        check: function () {
            this.errors = [];
            if (!this.form.title) {
                this.errors.push('Укажите название опросника')
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

            this.form.warning_days = parseInt(this.form.warning_days)
            if (this.form.warning_days < 0)
            {
                this.form.warning_days = 0
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
                    if (this.empty(field.params.max) || this.empty(field.params.min)) return true;
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
        save: function (is_template) {
            if (this.check()) {
                this.errors = []

                if (is_template || this.form.is_template) {
                    this.form.contract_id = undefined
                    this.form.is_template = true;
                }

                this.form.categories = this.form.fields.map(f => f.category).join('|')
                this.axios.post(this.url('/api/settings/form'), this.form).then(this.process_save_answer).catch(this.process_save_error);
            }
        },
        process_save_answer: function (response) {
            let is_new = this.empty(this.form.id)
            console.log(response)

            this.form.id = response.data.id
            if (is_new) {
                if (!this.form.is_template) {
                    this.form.patient_id = response.data.patient_id
                    this.form.contract_id = response.data.contract_id
                }
                Event.fire('form-created', this.form)
            } else {
                Event.fire('back-to-dashboard', this.form)
            }

            this.form = undefined
        },
        process_save_error: function (response) {
            this.errors.push('Ошибка сохранения');
        },
        warning_change: function ()
        {
            if (this.form.warning_enabled)
            {
                this.form.warning_days = 7
            }
            else {
                this.form.warning_days = 0
            }
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
        Event.listen('attach-form', (form) => {
            this.form = {}
            this.copy(this.form, form)
            this.form.id = undefined
            this.form.is_template = false;
            this.form.contract_id = undefined;
            this.form.template_id = form.id;
            this.save()
        });

        Event.listen('home', (form) => {
            this.form = undefined
            this.errors = []
            this.$forceUpdate()
        });

        Event.listen('navigate-to-create-form-page', () => {
            this.form = this.create_empty_form()
            console.log("create", this.form)
            this.backup = JSON.stringify(this.form)
        });

        Event.listen('navigate-to-edit-form-page', form => {
            this.form = form

            if (this.form.warning_days > 0)
            {
                this.form.warning_enabled = true;
            }

            this.backup = JSON.stringify(form)
            this.$forceUpdate()
        });
    }
}
</script>

<style scoped>

</style>
