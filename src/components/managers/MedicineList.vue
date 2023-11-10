<template>
    <div v-if="mode == 'list'">
        <div style="margin-top: 15px;" class="alert alert-info" role="alert">
            Напоминания о плановом приеме препаратов приходят согласно расписанию. Если Вы уже отметили прием препарата
            с помощью кнопки в чате, повторно записывать прием не нужно.
        </div>
        <div v-if="medicines.length || patient_medicines.length">
            <h4>Назначения врача</h4>
            <div class="row">
                <card v-for="(medicine, i) in medicines" :key="medicine.id" :image="images.medicine"
                      class="col-lg-4 col-md-4">
                    <h5>{{ medicine.title }}</h5>
                    <small><strong>Назначенная дозировка: </strong> {{
                            medicine.dose ? medicine.dose : '-'
                        }}</small><br>
                    <small><strong>Правила приема: </strong> {{ medicine.rules ? medicine.rules : '-' }}</small><br>
                    <small><i>{{ tt_description(medicine.timetable) }}</i></small><br>
                    <button class="btn btn-success btn-sm my-2" @click="save(medicine)" v-if="medicine">Записать прием
                    </button>
                    <div v-if="medicine.timetable.mode !='manual'">
                        <a href="#" v-if="!medicine.notifications_disabled" @click="disable_notifications(medicine)">Отключить
                            уведомления</a>
                        <strong v-if="medicine.notifications_disabled"><small>Уведомления выключены! </small></strong>
                        <a href="#" v-if="medicine.notifications_disabled" @click="enable_notifications(medicine)">Включить
                            уведомления?</a>
                    </div>
                    <div v-else>
                        <small><strong>Принимается при необходимости.</strong></small>
                    </div>
                </card>
            </div>
            <h4>Другие препараты</h4>
            <div class="row">
                <card v-for="(medicine, i) in patient_medicines" :key="medicine.id" :image="images.medicine"
                      class="col-lg-4 col-md-4">
                    <h5>{{ medicine.title }}</h5>
                    <small><strong>Дозировка: </strong> {{ medicine.dose ? medicine.dose : '-' }}</small><br>
                    <small><i>{{ tt_description(medicine.timetable) }}</i></small><br>
                    <button class="btn btn-success btn-sm my-2" @click="save(medicine)" v-if="medicine">Записать прием
                    </button>
                    <div v-if="medicine.timetable.mode !='manual'">
                        <a href="#" v-if="!medicine.notifications_disabled" @click="disable_notifications(medicine)">Отключить
                            уведомления</a>
                        <strong v-if="medicine.notifications_disabled"><small>Уведомления выключены! </small></strong>
                        <a href="#" v-if="medicine.notifications_disabled" @click="enable_notifications(medicine)">Включить
                            уведомления?</a>
                    </div>
                    <div v-else>
                        <small><strong>Принимается при необходимости.</strong></small>
                    </div>
                    <a href="#" @click="edit_medicine(medicine)">Редактировать</a>
                    <a href="#" @click="delete_medicine(medicine)">Удалить</a>
                </card>
            </div>
        </div>
        <button class="btn btn-primary" @click="mode = 'add-medicine'">Добавить препарат в список</button>
        <button class="btn btn-primary" @click="mode = 'add-record'">Записать прием препарата</button>
    </div>

    <div v-else>
        <h4 v-if="mode == 'add-record'">Записать прием препарата</h4>
        <h4 v-else>Добавить препарат в список</h4>

        <card>
            <form-group48 title="Название препарата" required="true">
                <autocomplete :search="search_hil" placeholder="Поиск лекарств"
                              :defaultValue="custom_medicine.title"
                              aria-label="Введите название препарата" :getResultValue="m => m.title"
                              auto-select
                              @submit="sub_er"></autocomplete>
            </form-group48>

            <form-group48 :title="mode == 'add-record' ? 'Принятая доза' : 'Дозировка'" required="true">
                <input class="form-control form-control-sm"
                       :class="validated && empty(custom_medicine.dose) ? 'is-invalid' : ''"
                       v-model="custom_medicine.dose"/>
            </form-group48>

            <form-group48 title="Комментарий" v-if="mode == 'add-record'">
                <textarea class="form-control monitoring-input" v-model="custom_medicine.comment"/>
            </form-group48>
        </card>
        <timetable-editor v-if="mode != 'add-record'" source="patient-medicine" :data="custom_medicine.timetable"
                          :timetable_save_clicked="timetable_save_clicked"/>

        <button class="btn btn-warning btn" @click="clear()">Назад</button>
        <button class="btn btn-success btn" @click="custom_save()" :disabled="button_lock">
            {{ mode == 'add-record' ? 'Записать прием' : 'Сохранить' }}
        </button>
        <error-block :errors="errors"/>
    </div>

</template>

<script>
import Card from "../common/Card";
import FormGroup48 from "../common/FormGroup-4-8";
import ErrorBlock from "../common/ErrorBlock";
import TimetableEditor from "../editors/parts/TimetableEditor";
import * as moment from "moment/moment";
import Autocomplete from "@trevoreyre/autocomplete-vue";

export default {
    name: "MedicineList",
    components: {TimetableEditor, ErrorBlock, FormGroup48, Card, Autocomplete},
    props: {
        data: {
            required: false
        }
    },
    data() {
        return {
            medicines: {},
            patient_medicines: [],
            custom_medicine: {},
            validated: false,
            mode: 'list',
            save_clicked: false,
            timetable_save_clicked: [],
            button_lock: false,
            errors: []
        }
    },
    methods: {
        search_hil: function (input) {
            this.custom_medicine.title = input

            return new Promise((resolve, reject) => {
                const url = `https://medicines.services.ai.medsenger.ru/search?title=${encodeURI(input)}`

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
        sub_er: function (custom_medicine) {
            this.custom_medicine.title = custom_medicine.title
        },
        disable_notifications: function (medicine) {
            this.$confirm({
                message: `Вы уверены, что хотите отключить напоминания для препарата ${medicine.title}?`,
                button: {
                    no: 'Нет',
                    yes: 'Да'
                },
                callback: confirm => {
                    if (confirm) {
                        this.axios.post(this.direct_url('/api/medicine/' + medicine.id + '/disable_notifications')).then(answer => medicine.notifications_disabled = answer.data.notifications_disabled);
                    }
                }
            })
        },
        enable_notifications: function (medicine) {
            this.axios.post(this.direct_url('/api/medicine/' + medicine.id + '/enable_notifications')).then(answer => medicine.notifications_disabled = answer.data.notifications_disabled);
        },
        edit_medicine: function (medicine) {
            this.custom_medicine = medicine
            if (this.custom_medicine.timetable.points) {
                for (let i of this.custom_medicine.timetable.points.keys()) {
                    this.$set(this.timetable_save_clicked, i, false)
                }
            }
            this.mode = 'add-medicine'
            this.$forceUpdate()
        },
        delete_medicine: function (medicine) {
            this.$confirm(
                {
                    message: `Вы уверены, что хотите удалить препарат ` + medicine.title + `?`,
                    button: {
                        no: 'Нет',
                        yes: 'Да, отменить'
                    },
                    callback: confirm => {
                        if (confirm) {
                            if (!medicine.prescription_history)
                                medicine.prescription_history = {
                                    records: []
                                }
                            medicine.prescription_history.records.push({
                                description: 'Отменен пациентом',
                                comment: '',
                                date: new Date().toLocaleDateString()
                            })
                            medicine.deleted_by_patient = true
                            this.axios.post(this.direct_url('/api/settings/delete_medicine'), medicine)
                                .then(response => {
                                    if (response.data.deleted_id) {
                                        let medicine = this.medicines.find(m => m.id == response.data.deleted_id)
                                        if (medicine) {
                                            medicine.canceled_at = moment(new Date()).format("DD.MM.YYYY")
                                        }
                                        this.medicines = this.medicines.filter(m => m.id != response.data.deleted_id)
                                    }
                                });
                        }
                    }
                }
            )
        },
        save: function (medicine) {
            this.errors = []

            if (medicine.verify_dose) {
                Event.fire('verify-dose', medicine)
            } else {
                let data = {
                    custom: false,
                    medicine: medicine.id,
                    params: null
                }

                this.$confirm({
                    message: `Записать прием препарата ${medicine.title}?`,
                    button: {
                        no: 'Нет',
                        yes: 'Да'
                    },
                    callback: confirm => {
                        if (confirm) {
                            this.axios.post(this.direct_url('/api/confirm-medicine'), data).then(r => Event.fire('confirm-medicine-done')).catch(r => this.errors.push('Ошибка сохранения'));
                        }
                    }
                })
            }
        },
        custom_save: function () {
            this.errors = []
            this.validated = true
            if (this.empty(this.custom_medicine.title) || this.empty(this.custom_medicine.dose) ||
                this.mode == 'add-medicine' && !this.verify_timetable(this.custom_medicine.timetable)) {
                this.errors.push('Пожалуйста, заполните обязательные поля')
                this.save_clicked = true
                for (let i of this.timetable_save_clicked.keys()) {
                    this.$set(this.timetable_save_clicked, i, true)
                }
            } else {
                this.errors = []
                this.save_clicked = false
                if (this.mode == 'add-record') {
                    let data = {
                        custom: true,
                        medicine: this.custom_medicine.title,
                        params: {
                            dose: this.custom_medicine.dose,
                            comment: this.custom_medicine.comment
                        }
                    }
                    this.axios.post(this.direct_url('/api/confirm-medicine'), data)
                        .then(r => Event.fire('confirm-medicine-done'))
                        .catch(r => this.errors.push('Ошибка сохранения'));

                } else {
                    if (!this.button_lock) {
                        this.button_lock = true
                        this.custom_medicine.prescription_history = {
                            records: [{
                                description: this.custom_medicine.id ? 'Пациент изменил параметры' : 'Добавлен пациентом',
                                comment: this.med_description(this.custom_medicine),
                                date: new Date().toLocaleDateString()
                            }]
                        }
                        this.custom_medicine.edited_by_patient = true
                        this.axios.post(this.direct_url('/api/settings/medicine'), this.custom_medicine)
                            .then(r => {
                                if (!this.custom_medicine.id) {
                                    this.patient_medicines.push(this.custom_medicine)
                                }
                                this.clear()
                                this.button_lock = false
                            })
                            .catch(r => {
                                this.errors.push('Ошибка сохранения')
                                this.button_lock = false
                            });
                    }
                }
            }
        },
        clear: function () {
            this.custom_medicine = {
                title: '',
                dose: '',
                comment: '',
                is_created_by_patient: true,
                edited_by_patient: true,
                timetable: {
                    mode: 'manual',
                    points: []
                }
            }
            this.timetable_save_clicked = []
            this.save_clicked = false
            this.mode = 'list'
        }
    },
    created() {
        this.medicines = this.data.medicines.filter(medicine => medicine.contract_id == this.current_contract_id)
        this.medicines.sort((a, b) => {
            return a.title < b.title ? -1 : a.title > b.title ? 1 : 0
        })

        this.patient_medicines = this.data.patient_medicines
        this.patient_medicines.sort((a, b) => {
            return a.title < b.title ? -1 : a.title > b.title ? 1 : 0
        })
        this.clear()

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
small {
    font-size: 90%;
}

.card a {
    font-size: 90%;
}
</style>
