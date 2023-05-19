<template>
    <div v-if="examination">
        <div class="form">
            <card title="Параметры обследования">
                <form-group48 title="Название обследования">
                    <input class="form-control form-control-sm"
                           :class="this.flags.validated && empty(examination.title) ? 'is-invalid' : ''"
                           v-model="examination.title"/>
                </form-group48>

                <form-group48 title="Категория шаблона" v-if="is_admin">
                    <input class="form-control form-control-sm"
                           v-model="examination.template_category"/>
                </form-group48>

                <form-group48 title="Описание для пациента">
                    <textarea class="form-control form-control-sm" v-model="examination.patient_description"></textarea>
                </form-group48>

                <form-group48 title="Описание для врача">
                    <textarea class="form-control form-control-sm" v-model="examination.doctor_description"></textarea>
                </form-group48>

                <form-group48 title="Крайняя дата загрузки" v-if="!examination.is_template">
                    <date-picker v-model="examination.deadline_date"
                                 :class="this.flags.validated && is_valid_date ? 'is-invalid' : ''"
                                 value-type="YYYY-MM-DD"></date-picker>
                </form-group48>

                <form-group48 title="Обследование действительно">
                    <input class="form-control form-control-sm"
                           :class="this.flags.validated && examination.expiration_days < 1 ? 'is-invalid' : ''"
                           type="number" min="1" max="365" step="1" v-model="examination.expiration_days"/>
                    <small class="text-muted">дней</small>
                </form-group48>
            </card>

        </div>

        <button :disabled="flags.btn_lock" class="btn btn-danger" @click="go_back()">Назад</button>
        <button :disabled="flags.btn_lock" class="btn btn-success" @click="save()">Сохранить <span
            v-if="examination.is_template"> шаблон</span></button>
        <button :disabled="flags.btn_lock" v-if="!examination.id && is_admin" class="btn btn-default"
                @click="save(true)">
            Сохранить как шаблон
        </button>

        <error-block :errors="errors"></error-block>
    </div>
</template>

<script>
import Card from "../common/Card";
import FormGroup48 from "../common/FormGroup-4-8";
import ErrorBlock from "../common/ErrorBlock";
import DatePicker from 'vue2-datepicker';
import 'vue2-datepicker/index.css';
import 'vue2-datepicker/locale/ru';

import * as moment from "moment/moment";

export default {
    name: "ExaminationEditor",
    components: {FormGroup48, Card, ErrorBlock, DatePicker},
    props: {
        data: {
            required: false,
        }
    },
    data() {
        return {
            errors: [],
            flags: {
                validated: false,
                show_button: false,
                btn_lock: false
            },
            examination: undefined,
            backup: "",
        }
    },
    computed: {
        is_valid_date() {
            if (this.examination.is_template) return true
            return moment(this.examination.deadline_date, 'YYYY-MM-DD') > moment()
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
                        this.copy(this.examination, old)
                        Event.fire('back-to-dashboard');

                        this.examination = undefined
                        this.errors = []
                    }
                }
            })
        },
        create_empty_examination: function () {
            return {
                text: '',
                template_category: '',
                doctor_description: '',
                patient_description: '',
                expiration_days: 14,
                deadline_date: moment().add(1, 'month').format('YYYY-MM-DD')
            }
        },
        check: function () {
            this.errors = [];

            if (this.empty(this.examination.title)) {
                this.errors.push('Заполните название обследования')
            }

            if (!this.is_valid_date) {
                this.errors.push('Крайний срок сдачи не может быть раньше текущей даты')
            }

            if (this.examination.expiration_days < 1) {
                this.errors.push('Обследование не может быть действительно менее 1 дня')
            }

            return this.errors.length == 0;
        },
        show_validation: function () {
            this.flags.validated = true
        },
        save: function (is_template) {
            this.show_validation()

            if (this.check()) {
                this.errors = []

                if (is_template || this.examination.is_template) {
                    this.examination.contract_id = undefined
                    this.examination.is_template = true;
                }

                if (!this.flags.btn_lock) {
                    this.flags.btn_lock = true
                    this.examination.expiration_days = parseInt(this.examination.expiration_days)
                    this.axios.post(this.direct_url('/api/settings/examination'), this.examination).then(this.process_save_answer).catch(this.process_save_error);
                }
            }
        },
        process_save_answer: function (response) {
            let is_new = this.empty(this.examination.id)
            this.examination.id = response.data.id

            if (!this.examination.is_template) {
                this.examination.patient_id = response.data.patient_id
                this.examination.contract_id = response.data.contract_id
            }

            if (is_new) Event.fire('examination-created', this.examination)
            else Event.fire('back-to-dashboard', this.examination)

            this.examination = undefined
            this.flags.btn_lock = false
            this.flags.validated = false
        },
        process_save_error: function (response) {
            this.flags.btn_lock = false
            this.errors.push('Ошибка сохранения');
        },
    },
    created() {
    },
    mounted() {
        Event.listen('attach-examination', (examination) => {
            this.examination = {}

            this.copy(this.examination, examination)
            this.examination.id = undefined

            this.examination.attach_date = moment().format('YYYY-MM-DD')

            this.examination.is_template = false;
            this.examination.template_id = examination.id;

            this.save()
        });

        Event.listen('home', () => {
            this.errors = []
            this.examination = undefined
            this.flags.btn_lock = false
            this.flags.validated = false
            this.$forceUpdate()
        });

        Event.listen('navigate-to-create-examination-page', () => {
            this.examination = this.create_empty_examination()
            this.backup = JSON.stringify(this.examination)
        });

        Event.listen('navigate-to-edit-examination-page', (examination) => {
            this.examination = examination
            this.backup = JSON.stringify(examination)
            this.$forceUpdate()
        });
    }
}
</script>

<style scoped>

</style>
