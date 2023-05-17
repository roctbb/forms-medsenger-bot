<template>
    <div v-if="reminder">
        <div class="form">
            <card title="Описание напоминания">

                <form-group48 title="Кому прислать напоминание">
                    <select class="form-control form-control-sm" v-model="reminder.type">
                        <option value="patient">пациенту</option>
                        <option value="doctor">врачу</option>
                    </select>
                </form-group48>

                <form-group48 title="Текст напоминания">
                    <textarea class="form-control form-control-sm"
                              :class="this.validated && empty(reminder.text) ? 'is-invalid' : ''"
                              v-model="reminder.text"></textarea>
                </form-group48>

                <form-group48 title="Дата начала">
                    <date-picker v-model="reminder.attach_date"
                                 :class="this.validated && !reminder.is_template && empty(reminder.attach_date) ? 'is-invalid' : ''"
                                 value-type="YYYY-MM-DD"></date-picker>
                </form-group48>

                <form-group48 title="Дата завершения">
                    <date-picker v-model="reminder.detach_date"
                                 :class="this.validated && !reminder.is_template && empty(reminder.detach_date) ? 'is-invalid' : ''"
                                 value-type="YYYY-MM-DD"></date-picker>
                </form-group48>

                <form-group48 title="Спрятать действия" v-if="is_admin">
                    <input class="form-check" type="checkbox"
                           v-model="reminder.hide_actions"/>
                </form-group48>

                <form-group48 title="Привязать приказ агенту" v-if="is_admin">
                    <input class="form-check" type="checkbox"
                           v-model="reminder.has_order"/>
                </form-group48>

                <div v-if="reminder.has_order" class="form-group form-group-sm row">
                    <div class="col-md-3">
                        <input class="form-control form-control-sm" type="number" v-model="reminder.order_agent_id">
                        <small class="text-muted">ID агента</small>
                    </div>

                    <div class="col-md-3">
                        <input class="form-control form-control-sm" type="text" v-model="reminder.order">
                        <small class="text-muted">order</small>
                    </div>

                    <div class="col-md-6">
                        <textarea class="form-control form-control-sm" v-model="reminder.order_params"></textarea>
                        <small class="text-muted">JSON параметры</small>
                    </div>
                </div>

            </card>

            <timetable-editor source="reminder" :data="reminder.timetable" :timetable_save_clicked="timetable_validated"/>
        </div>

        <button v-if="show_button" class="btn btn-danger" @click="go_back()">Назад</button>
        <button :disabled="button_lock" class="btn btn-success" @click="save()">Сохранить <span
            v-if="reminder.is_template"> шаблон</span></button>
        <button :disabled="button_lock" v-if="!reminder.id && is_admin" class="btn btn-default" @click="save(true)">
            Сохранить как шаблон
        </button>

        <error-block :errors="errors"></error-block>
    </div>
</template>

<script>
import Card from "../common/Card";
import FormGroup48 from "../common/FormGroup-4-8";
import ErrorBlock from "../common/ErrorBlock";
import TimetableEditor from "./parts/TimetableEditor";
import DatePicker from 'vue2-datepicker';
import 'vue2-datepicker/index.css';
import 'vue2-datepicker/locale/ru';

import * as moment from "moment/moment";

export default {
    name: "ReminderEditor",
    components: {FormGroup48, Card, ErrorBlock, DatePicker, TimetableEditor},
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
            let attach_date = moment().format('YYYY-MM-DD')
            let detach_date = moment().add(7, 'days').format('YYYY-MM-DD')
            let timetable = this.empty_timetable()
            timetable.points[0].hour = 10
            timetable.points[0].minute = '00'
            return {
                type: 'patient',
                text: '',
                timetable: timetable,
                attach_date: attach_date,
                detach_date: detach_date,
                has_order: false
            }
        },
        check: function () {
            this.errors = [];

            if (this.empty(this.reminder.text) && !this.reminder.has_order) {
                this.errors.push('Заполните текст напоминания')
            }

            if (this.reminder.attach_date > this.reminder.detach_date) {
                this.errors.push('Дата завершения не может быть раньше даты начала')
            }

            if (!this.verify_timetable(this.reminder.timetable)) {
                this.errors.push('Проверьте корректность расписания')
            }

            if (this.reminder.has_order) {
                if (this.empty(this.reminder.order)) {
                    this.errors.push('Укажите приказ')
                }
            }

            return this.errors.length == 0;
        },
        show_validation: function () {
            this.validated = true
            for (let i of this.timetable_validated.keys()) {
                this.$set(this.timetable_validated, i, true)
            }
        },
        save: function (is_template) {
            this.validated = true
            this.show_validation()

            if (this.check()) {
                this.errors = []

                if (is_template || this.reminder.is_template) {
                    this.reminder.contract_id = undefined
                    this.reminder.is_template = true;
                }

                if (!this.button_lock) {
                    this.button_lock = true
                    this.axios.post(this.direct_url('/api/settings/reminder'), this.reminder).then(this.process_save_answer).catch(this.process_save_error);
                }
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

            this.button_lock = false
            this.reminder = undefined
            this.validated = false
            this.timetable_validated = [false]
        },
        process_save_error: function (response) {
            this.button_lock = false
            this.errors.push('Ошибка сохранения');
        },
    },
    data() {
        return {
            errors: [],
            reminder: undefined,
            backup: "",
            validated: false,
            timetable_validated: [false],
            show_button: false,
            button_lock: false
        }
    },
    created() {
    },
    mounted() {
        Event.listen('attach-reminder', (reminder) => {
            this.reminder = {}

            this.copy(this.reminder, reminder)
            this.reminder.id = undefined

            this.reminder.attach_date = moment().format('YYYY-MM-DD')
            let len = 7
            if (reminder.attach_date && reminder.detach_date) {
                let attach = moment(reminder.attach_date, "YYYY-MM-DD")
                let detach = moment(reminder.detach_date, "YYYY-MM-DD")
                len = moment.duration(detach.diff(attach)).asDays()
            }
            this.reminder.detach_date = moment().add(len, 'days').format('YYYY-MM-DD')

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
    computed: {}
}
</script>

<style scoped>

</style>
