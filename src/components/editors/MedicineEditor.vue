<template>
    <div v-if="medicine">
        <div>
            <h5>Назначить новое лекарство</h5>
            <error-block :errors="errors"/>
            <div class="form row">
                <div class="col-lg-6">
                    <card title="Описание лекарства">
                        <form-group48 title="Название" v-if="search_mode == 'full'">
                            <autocomplete :search="search_hil" placeholder="Поиск лекарств"
                                          :defaultValue="medicine.title"
                                          aria-label="Введите название препарата" :getResultValue="m => m.title"
                                          auto-select
                                          @submit="sub_er"></autocomplete>
                        </form-group48>

                        <form-group48 title="Название" v-if="search_mode == 'prefilled'">
                            <vue-typeahead-bootstrap
                                :inputClass="this.save_clicked && !medicine.title ? 'is-invalid form-control form-control-sm' : 'form-control form-control-sm'"
                                v-model="medicine.title" ref="typeahead"
                                :data="suggestions" :serializer="s => s.title"
                                @hit="medicine.title = $event.title; medicine.dose = $event.dose; medicine.rules = $event.rules; $forceUpdate()"/>
                        </form-group48>


                        <form-group48 v-if="medicine.medicine_database_id">
                            <a class="btn btn-sm btn-info" target="_blank" :href="database_medicine_description.href">Vidal</a>
                            <a class="btn btn-sm btn-info" @click="display_medicine_description()">Дозировка и
                                применение</a>
                        </form-group48>

                        <form-group48 title="Дозировка">
                            <input v-model="medicine.dose" class="form-control form-control-sm">
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

                        <form-group48 v-if="medicine.warning_enabled"
                                      title="Прислать уведомление о пропусках через">
                            <input class="form-control form-control-sm"
                                   :class="this.save_clicked && medicine.warning_days < 0 ? 'is-invalid' : ''"
                                   type="number" min="1" max="200" step="1" v-model="medicine.warning_days"/>
                            <small class="text-muted">дней</small>
                        </form-group48>

                        <form-group48 v-if="is_admin && (empty(medicine.id) || medicine.is_template)"
                                      title="Категория шаблона">
                            <input class="form-control form-control-sm" value="Общее"
                                   v-model="medicine.template_category"/>
                        </form-group48>

                        <form-group48 v-if="is_admin && (empty(medicine.id) || medicine.is_template)"
                                      title="Показывать шаблон клиникам (JSON)">
                            <input class="form-control form-control-sm" type="text" v-model="medicine.clinics"/>
                        </form-group48>

                        <form-group48 v-if="is_admin && (empty(medicine.id) || medicine.is_template)"
                                      title="Спрятать шаблон у клиник (JSON)">
                            <input class="form-control form-control-sm" type="text"
                                   v-model="medicine.exclude_clinics"/>
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

        <modal height="auto" :width="mobile ? '95%' : '80%'" name="med_stat" :scrollable="true">
            <div class="container">
                <div v-if="show_medicine_description">
                    <div v-for="medicine_field in medicine_info_fields">
                        <form-group48 v-if="database_medicine_description[medicine_field]" :title="ru_ru[medicine_field]">
                            {{ database_medicine_description[medicine_field] }}
                        </form-group48>
                        <hr/>
                    </div>

                    <button class="btn btn-danger my-2" @click="hide_medicine_description()">Назад</button>
                </div>
            </div>
        </modal>
    </div>

</template>

<script>

import Card from "../common/Card";
import FormGroup48 from "../common/FormGroup-4-8";
import TimetableEditor from "./parts/TimetableEditor";
import ErrorBlock from "../common/ErrorBlock";
import * as moment from "moment/moment";
import VueTypeaheadBootstrap from 'vue-typeahead-bootstrap';
import Autocomplete from '@trevoreyre/autocomplete-vue'
import '@trevoreyre/autocomplete-vue/dist/style.css'
import da from "vue2-datepicker/locale/es/da";
import tr from "vue2-datepicker/locale/es/tr";

export default {
    name: "MedicineEditor",
    components: {VueTypeaheadBootstrap, TimetableEditor, FormGroup48, Card, ErrorBlock, Autocomplete},
    props: {
        data: {
            required: false,
        },
        patient: {
            required: false
        }
    },
    computed: {
        medicine_info_fields: function () {
            return Object.keys(this.database_medicine_description).filter(key => this.database_medicine_description[key])
        },
        search_mode: function () {
            if (this.suggestions && this.suggestions.length > 0) {
                return 'prefilled'
            } else {
                return 'full'
            }
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
        hide_medicine_description: function () {
            this.$modal.hide('med_stat')
            this.show_medicine_description = false
        },
        display_medicine_description: function () {
            this.$modal.show('med_stat')
            this.show_medicine_description = true
        },
        search_hil(input) {
            this.medicine.title = input
            this.database_medicine_description = null
            this.show_medicine_description = false
            this.medicine.medicine_database_id = undefined

            return new Promise((resolve, reject) => {
                const url = `https://medicines.services.ai.medsenger.ru/search?name=${encodeURI(input)}`

                if (input.length < 3) {
                    resolve([])
                }

                this.axios.get(url).then(response => {
                    resolve(response.data);
                }).catch(error => {
                    console.log("error", error);
                    reject();
                })

            })
        },
        sub_er(medicine) {
            this.medicine.medicine_database_id = medicine.id
            const url = `https://medicines.services.ai.medsenger.ru/medicine/${encodeURI(medicine.id)}`
            this.axios.get(url).then(response => {
                let data = response.data
                this.database_medicine_description = data
                this.medicine.title = data.name
                this.database_medicine_description.name = null
                this.database_medicine_description.id = null
                this.database_medicine_description.name_l = null
            }).catch(error => {
                console.log("error", error);
            })
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
            ru_ru: {
                "id": "Системный id:",
                "atx": "ATX-код:",
                "pharm": "Отпускается:",
                "influence": "Действие:",
                "hepata": "Противопоказания связаные с печенью:",
                "old": "Применение пожилым:",
                "storage_conditions": "Условия хранения:",
                "child": "Применения детям:",
                "indication": "Против чего:",
                "renal": "Противопоказания связаные с почками:",
                "contra": "Противопаказания:",
                "preg_lact": "Противопоказания при беремености:",
                "dosage": "Доза:",
                "insteraction": "Взаимодействие с другимим перпаратами",
                "side_effects": "Побочные эффекты:",
                "storage_time": "Время хранения:",
                "over_doasge": "При передозировке:",
                "kinetics": "Действие внутри:",
                "special": "Особое:",
                "owner": "Компания-владелец:",
                "href": "Ссылка на vidal.ru"
            },
            database_medicine_description: undefined,
            respon: [],
            errors: [],
            medicine: undefined,
            backup: "",
            save_clicked: false,
            button_lock: false,
            timetable_save_clicked: [false],
            show_button: false,
            suggestions: [],
            show_medicine_description: false,
            selected_db_medicine: undefined
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
            if (this.medicine.warning_days > 0) {
                this.medicine.warning_enabled = true;
            }

            if (this.medicine.timetable.points) {
                for (let i of this.medicine.timetable.points.keys()) {
                    this.$set(this.timetable_save_clicked, i, false)
                }
            }

            if (medicine.medicine_database_id) {
                this.sub_er({"id": medicine.medicine_database_id})
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
    },
}
</script>

<style scoped>

</style>
