<template>
    <div v-if="medicine">
        <h5>Назначить новое лекарство</h5>
        <error-block :errors="errors"/>
        <div class="form row">
            <div class="col-lg-6">
                <card title="Описание лекарства">
                    <form-group48 title="Название">
                        <vue-typeahead-bootstrap
                            :inputClass="this.save_clicked && !medicine.title ? 'is-invalid form-control form-control-sm' : 'form-control form-control-sm'"
                            v-model="medicine.title" ref="typeahead"
                            :data="suggestions" :serializer="s => s.title"
                            @hit="medicine.title = $event.title; medicine.dose = $event.dose; medicine.rules = $event.rules; $forceUpdate()"/>
                    </form-group48>

                    <form-group48 title="Дозировка">
                        <textarea class="form-control form-control-sm" v-model="medicine.dose"></textarea>
                    </form-group48>

                    <form-group48 title="Правила приема">
                        <textarea class="form-control form-control-sm" v-model="medicine.rules"></textarea>
                    </form-group48>

                    <form-group48 title="Разрешить пациенту регулировать дозировку">
                        <input class="form-check" type="checkbox" v-model="medicine.verify_dose"/>
                    </form-group48>

                    <form-group48 title="Уведомить, если пациент не отмечает прием">
                        <input class="form-check" type="checkbox" @change="warning_change()"
                               v-model="medicine.warning_enabled"/>
                    </form-group48>

                    <form-group48 v-if="medicine.warning_enabled" title="Прислать уведомление о пропусках через">
                        <input class="form-control form-control-sm"
                               :class="this.save_clicked && medicine.warning_days < 0 ? 'is-invalid' : ''"
                               type="number" min="1" max="200" step="1" v-model="medicine.warning_days"/>
                        <small class="text-muted">дней</small>
                    </form-group48>

                    <form-group48 v-if="is_admin && (empty(medicine.id) || medicine.is_template)"
                                  title="Категория шаблона">
                        <input class="form-control form-control-sm" value="Общее" v-model="medicine.template_category"/>
                    </form-group48>

                    <form-group48 v-if="is_admin && (empty(medicine.id) || medicine.is_template)" title="Показывать шаблон клиникам (JSON)">
                        <input class="form-control form-control-sm" type="text" v-model="medicine.clinics"/>
                    </form-group48>

                    <form-group48 v-if="is_admin && (empty(medicine.id) || medicine.is_template)" title="Спрятать шаблон у клиник (JSON)">
                        <input class="form-control form-control-sm" type="text" v-model="medicine.exclude_clinics"/>
                    </form-group48>
                </card>
            </div>
            <div class="col-lg-6">
                <timetable-editor source="medicine" :data="medicine.timetable"
                                  :timetable_save_clicked="timetable_save_clicked"/>
            </div>
        </div>
        <button v-if="show_button" class="btn btn-danger" @click="go_back()">Назад</button>
        <button :disabled="button_lock" class="btn btn-success" @click="save()">Сохранить <span
            v-if="medicine.is_template"> шаблон</span></button>
        <button :disabled="button_lock" v-if="!medicine.id && is_admin" class="btn btn-default"
                @click="save(true)">Сохранить как шаблон
        </button>
        <button :disabled="button_lock" v-if="!medicine.id && !is_admin" class="btn btn-default"
                @click="save(true, 'doctor')">
            Сохранить как шаблон для себя
        </button>
        <button :disabled="button_lock" v-if="!medicine.id && !is_admin" class="btn btn-default"
                @click="save(true, 'clinic')">
            Сохранить как шаблон для клиники
        </button>
    </div>
</template>

<script>

import Card from "../common/Card";
import FormGroup48 from "../common/FormGroup-4-8";
import TimetableEditor from "./parts/TimetableEditor";
import ErrorBlock from "../common/ErrorBlock";
import * as moment from "moment/moment";
import VueTypeaheadBootstrap from 'vue-typeahead-bootstrap';

export default {
    name: "MedicineEditor",
    components: {VueTypeaheadBootstrap, TimetableEditor, FormGroup48, Card, ErrorBlock},
    props: {
        data: {
            required: false,
        },
        patient: {
            required: false
        }
    },
    methods: {
        loadSuggetions: function () {
            this.axios.get(this.direct_url('/api/medicine-template'))
                .then(response => {
                    this.suggestions = response.data;
                })
                .catch(error => {
                    console.log(error);
                });
        },
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
                        this.copy(this.medicine, old)
                        Event.fire('back-to-dashboard');

                        this.medicine = undefined
                        this.errors = []
                    }
                }
            })
        },
        create_empty_medicine: function () {
            return {
                title: "",
                timetable: {
                    mode: 'daily',
                    points: [{'hour': '', 'minute': 0}]
                }
            };
        },

        check: function () {
            this.errors = [];
            if (this.empty(this.medicine.title)) {
                this.errors.push('Укажите название лекарства')
            }

            this.medicine.warning_days = parseInt(this.medicine.warning_days)
            if (this.medicine.warning_days < 0) {
                this.medicine.warning_days = 0
            }

            if (!this.verify_timetable(this.medicine.timetable)) {
                this.errors.push('Проверьте корректность расписания')
            }

            return this.errors.length == 0;
        },
        show_validation: function () {
            this.save_clicked = true
            for (let i of this.timetable_save_clicked.keys()) {
                this.$set(this.timetable_save_clicked, i, true)
            }
        },
        save: function (is_template, template_mode) {
            this.show_validation()
            if (this.check()) {
                this.errors = []

                if (is_template || this.medicine.is_template) {
                    this.medicine.contract_id = undefined
                    this.medicine.is_template = true;

                    if (template_mode) {
                        this.medicine.doctor_id = this.patient.info.doctor_id
                        if (template_mode == 'clinic') {
                            this.medicine.clinic_id = this.patient.info.clinic_id
                        }
                    }

                } else {
                    if (!this.medicine.prescription_history) {
                        this.medicine.prescription_history = {
                            records: [{
                                description: this.medicine.id ? 'Изменены параметры' : 'Назначено',
                                comment: this.med_description(this.medicine),
                                date: new Date().toLocaleDateString()
                            }]
                        }
                    } else if (this.medicine.id) {
                        this.medicine.prescription_history.records.push({
                            description: 'Изменены параметры',
                            comment: this.med_description(this.medicine),
                            date: new Date().toLocaleDateString()
                        })
                    }
                }

                if (!this.button_lock) {
                    this.button_lock = true
                    this.axios.post(this.direct_url('/api/settings/medicine'), this.medicine).then(this.process_save_answer).catch(this.process_save_error);
                }
            }
        },
        process_save_answer: function (response) {
            let is_new = this.empty(this.medicine.id)
            this.medicine.id = response.data.id

            if (!this.medicine.is_template) {
                this.medicine.prescribed_at = moment(new Date()).format("DD.MM.YYYY")
                this.medicine.patient_id = response.data.patient_id
                this.medicine.contract_id = response.data.contract_id
            }

            if (is_new) Event.fire('medicine-created', {
                medicine: this.medicine,
                close_window: !this.show_button
            })
            else Event.fire('back-to-dashboard', this.medicine)

            this.button_lock = false
            this.medicine = undefined
            this.timetable_save_clicked = [false]
            this.save_clicked = false
        },
        process_save_error: function (response) {
            this.button_lock = false
            this.errors.push('Ошибка сохранения');
        },
        warning_change: function () {
            if (this.medicine.warning_enabled) {
                this.medicine.warning_days = 7
            } else {
                this.medicine.warning_days = 0
            }
        }
    },
    data() {
        return {
            errors: [],
            medicine: undefined,
            backup: "",
            save_clicked: false,
            button_lock: false,
            timetable_save_clicked: [false],
            show_button: false,
            suggestions: []
        }
    },
    created() {
        this.medicine = undefined;
    },
    mounted() {
        this.loadSuggetions()

        Event.listen('attach-medicine', (medicine) => {
            this.medicine = {}
            this.copy(this.medicine, medicine)
            this.medicine.id = undefined
            this.medicine.is_template = false;
            this.medicine.template_id = medicine.id;
            if (this.$refs.typeahead)
                this.$refs.typeahead.inputValue = medicine.title;
            this.backup = JSON.stringify(this.medicine)

            this.save()
        });

        Event.listen('home', (form) => {
            this.errors = []
            this.medicine = undefined
            this.$forceUpdate()
        });

        Event.listen('create-medicine-editor', () => {
            this.show_button = false
            this.medicine = this.create_empty_medicine()
            this.backup = JSON.stringify(this.medicine)
        });

        Event.listen('navigate-to-create-medicine-page', () => {
            this.show_button = true
            this.medicine = this.create_empty_medicine()
            this.backup = JSON.stringify(this.medicine)
        });

        Event.listen('navigate-to-edit-medicine-page', medicine => {
            this.show_button = true
            this.medicine = medicine
            if (this.$refs.typeahead)
                this.$refs.typeahead.inputValue = medicine.title;

            if (this.medicine.warning_days > 0) {
                this.medicine.warning_enabled = true;
            }

            if (this.medicine.timetable.points) {
                for (let i of this.medicine.timetable.points.keys()) {
                    this.$set(this.timetable_save_clicked, i, false)
                }
            }

            this.backup = JSON.stringify(medicine)
            this.$forceUpdate()
        });

        Event.listen('add-time-point', () => {
            this.timetable_save_clicked.push(false)
        });

        Event.listen('remove-time-point', (index) => {
            this.timetable_save_clicked.splice(index, 1);
        });

        Event.listen('clear-time-points', (index) => {
            this.timetable_save_clicked = [];
        });
    }
}
</script>

<style scoped>

</style>
