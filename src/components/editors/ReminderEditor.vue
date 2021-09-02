<template>
    <div v-if="reminder">
        <div class="form">
            <card title="Описание напоминания">

                <form-group48 title="Кому прислать напоминание">
                    <select class="form-control form-control-sm" v-model="reminder.type">
                        <option value="patient">пациенту</option>
                        <option value="doctor">врачу</option>
                        <option value="both">всем</option>
                    </select>
                </form-group48>

                <form-group48 title="Разные напоминания" v-if="reminder.type == 'both'">
                    <input class="form-check" type="checkbox" v-model="reminder.different_text"/>
                </form-group48>

                <form-group48 :title="'Текст напоминания' + (reminder.type == 'both' && !reminder.different_text ? '' : ' для пациента')"
                              v-if="reminder.type != 'doctor'">
                    <textarea class="form-control form-control-sm"
                              :class="this.save_clicked && empty(reminder.patient_text) ? 'is-invalid' : ''"
                              v-model="reminder.patient_text"></textarea>
                </form-group48>

                <form-group48 title="Текст напоминания для врача"
                              v-if="reminder.type == 'doctor' || reminder.type == 'both' && reminder.different_text">
                    <textarea class="form-control form-control-sm"
                              :class="this.save_clicked && empty(reminder.doctor_text) ? 'is-invalid' : ''"
                              v-model="reminder.doctor_text"></textarea>
                </form-group48>

                <form-group48 title="Дата напоминания">
                    <date-picker v-model="reminder.date" type="datetime" format="DD.MM.YYYY в HH:mm"></date-picker>
                </form-group48>

            </card>
        </div>

        <button v-if="show_button" class="btn btn-danger" @click="go_back()">Назад</button>
        <button class="btn btn-success" @click="save()">Сохранить <span
            v-if="reminder.is_template"> шаблон</span></button>
        <button v-if="!reminder.id && is_admin" class="btn btn-primary" @click="save(true)">
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
    name: "ReminderEditor",
    components: {FormGroup48, Card, ErrorBlock, DatePicker},
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
                        this.copy(this.reminder, old)
                        Event.fire('back-to-dashboard');

                        this.reminder = undefined
                        this.errors = []
                    }
                }
            })
        },
        create_empty_reminder: function () {
            return {
                type: 'patient',
                different_text: false,
                patient_text: '',
                doctor_text: '',
                date: new Date(moment().add(1, "day").format('YYYY-MM-DD hh:mm')),
                reminder_date: ''
            }
        },
        check: function () {
            this.errors = [];

            if (this.reminder.type == 'both' && !this.reminder.different_text)
                this.reminder.doctor_text = this.reminder.patient_text

            if (this.reminder.type == 'patient' && this.empty(this.reminder.patient_text) ||
                this.reminder.type == 'doctor' && this.empty(this.reminder.doctor_text) ||
                this.reminder.type == 'both' && this.empty(this.reminder.patient_text) && !this.reminder.different_text) {
                this.errors.push('Заполните текст напоминания')
            }

            if (this.reminder.type == 'both' && this.reminder.different_text) {
                if (this.empty(this.reminder.patient_text))
                    this.errors.push('Заполните текст напоминания для пациента')
                if (this.empty(this.reminder.doctor_text))
                    this.errors.push('Заполните текст напоминания для врача')
            }

            this.reminder.reminder_date = moment(this.reminder.date).format('DD.MM.YYYY HH:mm')
            if (+new Date() >= +this.reminder.date) {
                this.errors.push('Установлена некорректная дата')
            }
            return this.errors.length == 0;
        },
        save: function (is_template) {
            this.save_clicked = true

            if (this.check()) {
                this.errors = []

                if (is_template || this.reminder.is_template) {
                    this.reminder.contract_id = undefined
                    this.reminder.is_template = true;
                }

                this.axios.post(this.url('/api/settings/reminder'), this.reminder).then(this.process_save_answer).catch(this.process_save_error);
            }
        },
        process_save_answer: function (response) {
            let is_new = this.empty(this.reminder.id)
            this.reminder.id = response.data.id

            if (!this.reminder.is_template) {
                this.reminder.patient_id = response.data.patient_id
                this.reminder.contract_id = response.data.contract_id
            }

            if (is_new) Event.fire('reminder-created', {
                reminder: this.reminder,
                close_window: !this.show_button
            })
            else Event.fire('back-to-dashboard', this.reminder)

            this.reminder = undefined
            this.save_clicked = false
        },
        process_save_error: function (response) {
            console.log(response)
            this.errors.push('Ошибка сохранения');
        },
    },
    data() {
        return {
            errors: [],
            reminder: undefined,
            backup: "",
            save_clicked: false,
            show_button: false
        }
    },
    created() {
    },
    mounted() {
        Event.listen('attach-reminder', (reminder) => {
            this.reminder = {}
            this.copy(this.reminder, reminder)
            this.reminder.id = undefined
            this.reminder.is_template = false;
            this.reminder.template_id = reminder.id;
            this.save()
        });

        Event.listen('home', (form) => {
            this.errors = []
            this.reminder = undefined
            this.$forceUpdate()
        });

        Event.listen('navigate-to-create-reminder-page', () => {
            this.show_button = true
            this.reminder = this.create_empty_reminder()
            this.backup = JSON.stringify(this.reminder)
        });

        Event.listen('navigate-to-edit-reminder-page', reminder => {
            this.show_button = true
            this.reminder = reminder
            this.reminder.date = new Date(this.reminder.date)

            this.backup = JSON.stringify(reminder)
            this.$forceUpdate()
        });
    },
    computed: {
    }
}
</script>

<style scoped>

</style>
