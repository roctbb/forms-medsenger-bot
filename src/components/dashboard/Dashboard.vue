<template>
    <div>
        <algorithm-settings/>
        <examination-settings/>

        <div v-if="state == 'main'">

            <h6 v-if="parts.length == 0 && patient.month_compliance[0]" class="badge badge-info">Общая комплаентность за
                месяц: {{ Math.round(100 * patient.month_compliance[1] / patient.month_compliance[0]) }}%</h6>

            <!-- параметры -->
            <div v-if="parts.length == 0 || parts.includes('forms')">
                <params-editor/>
            </div>

            <!-- назначенные опросники -->
            <div v-if="parts.length == 0 || parts.includes('forms')">
                <h4>Опросники</h4>
                <small v-if="!patient.forms.length">Нет назначенных опросников</small>
                <div class="row">
                    <form-card :form="form" :key="'form_' + form.id" v-for="form in patient.forms"/>
                </div>

                <button class="btn btn-default btn-sm" @click="state = 'form_templates'">Добавить опросник</button>
            </div>

            <!-- назначенные препараты -->
            <div v-if="parts.length == 0 || parts.includes('meds')">
                <h4>Назначенные препараты</h4>
                <small v-if="!patient.medicines.length && !patient.canceled_medicines.length">
                    Нет назначенных препаратов
                </small>
                <div class="row">
                    <medicine-card :medicine="medicine" :key="'medicine' + medicine.id"
                                   v-for="(medicine, i) in patient.medicines"/>
                    <medicine-card :medicine="medicine" :key="'canceled_medicine' + medicine.id"
                                   v-for="(medicine, i) in patient.canceled_medicines"/>
                </div>

                <button class="btn btn-default btn-sm" @click="create_medicine()">Назначить препарат</button>
                <button v-if="is_admin" class="btn btn-info btn-sm" @click="state = 'medicine_templates'">
                    Управление шаблонами
                </button>

                <!-- добавленные пациентом препараты -->
                <h4>Препараты, добавленные пациентом</h4>
                <small
                    v-if="(!patient.patient_medicines || !patient.patient_medicines.length) &&
                     (!patient.canceled_patient_medicines || !patient.canceled_patient_medicines.length)">
                    Нет добавленных препаратов
                </small>

                <div class="row">
                    <medicine-card :medicine="medicine" :key="'medicine' + medicine.id"
                                   v-for="(medicine, i) in patient.patient_medicines"/>
                    <medicine-card :medicine="medicine" :key="'canceled_medicine' + medicine.id"
                                   v-for="(medicine, i) in patient.canceled_patient_medicines"/>
                </div>
            </div>

            <!-- назначенные обследования -->
            <div v-if="parts.length == 0 || parts.includes('examinations')">
                <h4>Обследования</h4>
                <small v-if="!patient.examinations.length">Нет назначенных обследований</small>
                <div class="row">
                    <examination-card :patient="patient" :examination="examination" :key="'examination_' + examination.id"
                                      v-for="examination in patient.examinations"/>
                    <examination-card :patient="patient" :examination="examination" :key="'examination_' + examination.id"
                                      v-for="examination in patient.expired_examinations"/>
                </div>

                <button class="btn btn-default btn-sm" @click="state = 'examination_templates'">Назначить обследование
                </button>
            </div>

            <!-- напоминания -->
            <div v-if="parts.length == 0 || parts.includes('reminders')">
                <h4>Напоминания</h4>

                <div class="row">
                    <reminder-card :reminder="reminder" :key="'reminder_' + reminder.id"
                                   v-for="(reminder, i) in patient.reminders"/>
                    <reminder-card :reminder="reminder" :key="'old_reminder_' + reminder.id"
                                   v-for="(reminder, i) in patient.old_reminders"/>
                </div>

                <button class="btn btn-default btn-sm" @click="create_reminder()">Создать напоминание</button>
                <button v-if="is_admin" class="btn btn-info btn-sm" @click="state = 'reminder_templates'">
                    Управление шаблонами
                </button>
            </div>

            <!-- алгоритмы -->
            <div v-if="parts.length == 0 || parts.includes('algorithms')">
                <h4>Алгоритмы</h4>

                <div class="row">
                    <algorithm-card :algorithm="algorithm" :key="'algorithm_' + algorithm.id"
                                    v-for="(algorithm, i) in patient.algorithms"/>
                </div>

                <button class="btn btn-default btn-sm" @click="state = 'algorithm_templates'">Добавить алгоритм</button>
            </div>

            <div style="margin-top: 15px;" class="alert alert-info" role="alert" v-if="parts.length == 0">
                <p>Этот интеллектуальный агент умеет отправлять пациенту произвольные опросники по расписанию и
                    напоминать о приеме лекарств. Вся введенная пациентом информация сохраняется в медицинской карте
                    Medsenger, ее можно посмотреть в виде списка по датам или на графиках, а в разделе "алгоритмы" можно
                    настроить уведомления для врача, указав условия их срабатывания.</p>

                <p>Опросники можно выбрать из готовых шаблонов или создать с нуля (как в Google-формах). При
                    необходимости, нажмите на кнопку <i>"Редактировать"</i> у нужного опросника чтобы скорректировать
                    расписание. К большинству опросников уже привязаны алгоритмы, от Вас потребуется только указать
                    контрольные значения (например, безопасный коридор давления). Чтобы назначить лекарство, нажмите на
                    кнопку <i>назначить лекарство</i>.</p>

                <ul>
                    <li>Посмотреть все внесенные пациентом данные можно с помощью интеллектуального агента <strong>"Медкарта"</strong>.
                    </li>
                </ul>
            </div>
        </div>

        <!-- шаблоны опросников -->
        <div v-if="state == 'form_templates'">
            <h3>Выбор опросника</h3>
            <div class="alert alert-info" role="alert">
                <p>Выберите опросник из списка ниже. В дальнейшем Вы сможете изменить расписание,
                    описание и даже сами вопросы.</p>
            </div>

            <input type="text" v-model="search_query" class="form-control form-control-sm" style="margin-bottom: 5px;"
                   placeholder="Поиск...">

            <div class="row"
                 v-for="(group, name) in group_by(templates.forms.filter(show_form).map((form) => {
                     if (!form.template_category) form.template_category = 'Общее'
                     return form
                 }), 'template_category')">

                <div class="col-md-12"><h5>{{ name }}</h5></div>
                <form-card :form="form" :patient="patient" :templates="templates"
                           v-for="form in group" :key="'form_template_' + form.id"/>

                <div v-if="!templates.forms.length" class="col-md-12">
                    <p style="margin-bottom: 15px;">Список опросников пуст.</p>
                </div>
            </div>

            <button class="btn btn-default btn-sm" @click="create_form()">Добавить свой опросник</button>
            <button class="btn btn-danger btn-sm" @click="state = 'main'">Назад</button>
        </div>

        <!-- шаблоны препаратов -->
        <div v-if="state == 'medicine_templates'">
            <h3>Шаблоны препаратов</h3>
            <div class="alert alert-info" role="alert">
                <p>Выберите препарат из списка ниже или создайте новый.
                    В дальнейшем Вы сможете изменить расписание, дозировку и правила приема.</p>
            </div>

            <div class="row">
                <medicine-card :medicine="medicine" :patient="patient" :key="'medicine_template_' + medicine.id"
                               v-for="(medicine, i) in templates.medicines.filter(show_medicine)"/>
                <div v-if="!templates.medicines.length" class="col-md-12">
                    <p style="margin-bottom: 15px;">Список шаблонов пуст.</p>
                </div>

            </div>

            <button class="btn btn-default btn-sm" @click="create_medicine()">Добавить</button>
            <button class="btn btn-danger btn-sm" @click="state = 'main'">Назад</button>
        </div>

        <!-- шаблоны обследований -->
        <div v-if="state == 'examination_templates'">
            <h3>Шаблоны обследований</h3>
            <div class="alert alert-info" role="alert">
                <p>Выберите обследование из списка ниже или создайте новое.
                    В дальнейшем Вы сможете изменить его параметры.</p>
            </div>

            <div class="row"
                 v-for="(group, name) in group_by(templates.examinations.map((examination) => {
                     if (!examination.template_category) examination.template_category = 'Общее'
                     return examination
                 }), 'template_category')">

                <div class="col-md-12"><h5>{{ name }}</h5></div>
                <examination-card :patient="patient" :examination="examination" :key="'examination_template_' + examination.id"
                                  v-for="(examination, i) in group"/>

                <div v-if="!templates.forms.length" class="col-md-12">
                    <p style="margin-bottom: 15px;">Список шаблонов пуст.</p>
                </div>
            </div>


            <button class="btn btn-default btn-sm" @click="create_examination()">Добавить</button>
            <button class="btn btn-danger btn-sm" @click="state = 'main'">Назад</button>
        </div>

        <!-- шаблоны напоминаний -->
        <div v-if="state == 'reminder_templates'">
            <h3>Шаблоны напоминаний</h3>
            <div class="alert alert-info" role="alert">
                <p>Выберите напоминание из списка ниже или создайте новое.</p>
            </div>

            <div class="row">
                <reminder-card :reminder="reminder" :key="'reminder_template_' + reminder.id"
                               v-for="(reminder, i) in templates.reminders"/>
                <div v-if="!templates.medicines.length" class="col-md-12">
                    <p style="margin-bottom: 15px;">Список шаблонов пуст.</p>
                </div>

            </div>

            <button class="btn btn-default btn-sm" @click="create_reminder()">Добавить</button>
            <button class="btn btn-danger btn-sm" @click="state = 'main'">Назад</button>
        </div>

        <!-- шаблоны алгоритмов -->
        <div v-if="state == 'algorithm_templates'">

            <div class="alert alert-info" role="alert">
                <h4 class="alert-heading">Выбор алгоритма</h4>
                <p>Выберите алгоритм из списка ниже. В дальнейшем вы сможете посмотреть подробную схему его работы, но
                    изменять ее без опыта не рекомендуется.</p>
            </div>

            <div class="row" v-for="(group, name) in group_by(templates.algorithms.filter((algorithm) => {
                return is_admin || !algorithm.clinics || algorithm.clinics.includes(clinic_id)
            }).map((algorithms) => {
                if (!algorithms.template_category) algorithms.template_category = 'Общее'
                return algorithms
            }), 'template_category')">
                <div class="col-md-12"><h5>{{ name }}</h5></div>
                <algorithm-card :algorithm="algorithm" :key="'algorithm_' + algorithm.id"
                                v-if="is_admin || !algorithm.clinics || algorithm.clinics.includes(clinic_id)"
                                v-for="(algorithm, i) in group"/>
                <div v-if="!templates.algorithms.length" class="col-md-12">
                    <p style="margin-bottom: 15px;">Список шаблонов пуст.</p>
                </div>
            </div>

            <button class="btn btn-default btn-sm" @click="create_algorithm()">Добавить</button>
            <button class="btn btn-danger btn-sm" @click="state = 'main'">Назад</button>
        </div>
    </div>
</template>

<script>

import Card from "../common/Card";
import AlgorithmSettings from "./parts/AlgorithmSettings";
import FormGroup48 from "../common/FormGroup-4-8";
import ErrorBlock from "../common/ErrorBlock";
import * as moment from "moment/moment";
import ParamsEditor from "./parts/ParamsEditor";
import FormCard from "./parts/FormCard";
import MedicineCard from "./parts/MedicineCard";
import ReminderCard from "./parts/ReminderCard";
import AlgorithmCard from "./parts/AlgorithmCard";
import ExaminationCard from "./parts/ExaminationCard";
import ExaminationSettings from "./parts/ExaminationSettings";

export default {
    name: "Dashboard",
    components: {
        ExaminationSettings,
        ExaminationCard,
        AlgorithmCard,
        ReminderCard, MedicineCard, FormCard, ParamsEditor, ErrorBlock, FormGroup48, AlgorithmSettings, Card
    },
    props: {
        patient: {required: true},
        templates: {required: true},
        parts: {required: false}
    },
    data: function () {
        return {
            state: 'main',
            lock_btn: false,
            params: {},
            search_query: ''
        }
    },
    methods: {
        change_alg_params: function (params) {
            // change values
            let changed_algorithms = new Set()

            params.backup.forEach((param, i) => {
                if (this.to_float(param.value) != params.edited[i]) {
                    param.locations.forEach(loc => {
                        let alg = this.patient.algorithms.filter(a => a.id == loc.algorithm)[0]

                        if (loc.common) {
                            alg.common_conditions[loc.condition]
                                .criteria[loc.block][loc.criteria].value = params.edited[i]
                        } else {
                            alg.steps[loc.step].conditions[loc.condition]
                                .criteria[loc.block][loc.criteria].value = params.edited[i]
                        }

                        changed_algorithms.add(alg)
                    })
                }
            })

            // save values
            if (changed_algorithms.size) {
                this.axios.post(this.direct_url('/api/settings/algorithms'), [...changed_algorithms])
                    .then(response => Event.fire('params-saved'))
                    .catch(err => Event.fire('params-not-saved'));

            }

            this.lock_btn = false
        },
        find_algorithm: function (id) {
            return this.templates.algorithms.filter(t => t.id == id)[0]
        },
        attach_form: function (form) {
            let attach = () => {
                Event.fire('attach-form', form)

                if (!this.empty(form.algorithm_id)) {
                    let algorithm = this.find_algorithm(form.algorithm_id);

                    if (this.need_filling(algorithm)) this.setup_algorithm(algorithm)
                    else this.attach_algorithm(algorithm)
                }
            }

            if (this.patient.forms.filter(f => f.template_id == form.id).length != 0) {
                this.$confirm({
                    message: `Пациенту уже подключен опросник на основе шаблона ` + form.title + `. Подключить еще один?`,
                    button: {
                        no: 'Нет',
                        yes: 'Да'
                    },
                    callback: confirm => {
                        if (confirm) {
                            attach()
                        }
                    }
                })
            } else {
                attach()
            }

        },
        ask_for_examination_doubling: function (title, F) {
            this.$confirm({
                message: `Пациенту уже назначено обследование ` + title + `. Назначить еще раз?`,
                button: {
                    no: 'Нет',
                    yes: 'Да'
                },
                callback: confirm => {
                    if (confirm) {
                        F()
                    }
                }
            })
        },

        setup_examination: function (examination) {
            let setup = () => {
                this.$modal.show('examination-settings', {examination: examination})
            }
            if (this.patient.examinations.filter(f => f.template_id == examination.id).length != 0) this.ask_for_examination_doubling(examination.title, setup)
            else setup()
        },
        ask_for_alg_doubling: function (title, F) {
            this.$confirm({
                message: `Пациенту уже подключен алгоритм на основе шаблона ` + title + `. Подключить еще один?`,
                button: {
                    no: 'Нет',
                    yes: 'Да'
                },
                callback: confirm => {
                    if (confirm) {
                        F()
                    }
                }
            })
        },
        setup_algorithm: function (algorithm) {
            let setup = () => {
                this.$modal.show('algorithm-settings', {algorithm: algorithm})
            }
            if (this.patient.algorithms.filter(f => f.template_id == algorithm.id).length != 0) this.ask_for_alg_doubling(algorithm.title, setup)
            else setup()
        },
        attach_algorithm: function (algorithm) {
            let attach = () => {
                Event.fire('attach-algorithm', algorithm)
            }
            if (this.patient.algorithms.filter(f => f.template_id == algorithm.id).length != 0) this.ask_for_alg_doubling(algorithm.title, attach)
            else attach()
        },
        attach_medicine: function (medicine) {
            Event.fire('attach-medicine', medicine)
        },
        create_form: function () {
            Event.fire('navigate-to-create-form-page')
        },
        process_delete_form: function (deleted_form_id) {
            if (deleted_form_id) {
                this.patient.forms = this.patient.forms.filter(f => f.id != deleted_form_id)
                this.templates.forms = this.templates.forms.filter(f => f.id != deleted_form_id)
            }
        },
        create_medicine: function () {
            Event.fire('navigate-to-create-medicine-page')
        },
        create_examination: function () {
            Event.fire('navigate-to-create-examination-page')
        },
        create_reminder: function () {
            Event.fire('navigate-to-create-reminder-page')
        },
        process_delete_reminder: function (deleted_reminder_id) {
            if (deleted_reminder_id) {
                let reminder = this.patient.reminders.find(r => r.id == deleted_reminder_id)

                if (reminder) {
                    reminder.canceled_at = moment(new Date()).format("DD.MM.YYYY")
                    this.patient.old_reminders.push(reminder);
                }

                this.patient.reminders = this.patient.reminders.filter(r => r.id != deleted_reminder_id)
                this.templates.reminders = this.templates.reminders.filter(r => r.id != deleted_reminder_id)
            }
        },
        create_algorithm: function () {
            Event.fire('navigate-to-create-algorithm-page')
        },
        edit_algorithm: function (algorithm) {
            Event.fire('edit-algorithm', algorithm)
        },
        delete_algorithm: function (algorithm) {
            this.$confirm(
                {
                    message: `Вы уверены, что хотите удалить алгоритм ` + algorithm.title + `?`,
                    button: {
                        no: 'Нет',
                        yes: 'Да, удалить'
                    },
                    callback: confirm => {
                        if (confirm) {
                            this.axios.post(this.direct_url('/api/settings/delete_algorithm'), algorithm).then(this.process_delete_algorithm_answer);
                        }
                    }
                }
            )
        },
        process_delete_medicine: function (deleted_medicine_id) {
            if (deleted_medicine_id) {
                let medicine = this.patient.medicines.find(m => m.id == deleted_medicine_id)

                if (medicine) {
                    medicine.canceled_at = moment(new Date()).format("DD.MM.YYYY")
                    this.patient.canceled_medicines.push(medicine);
                } else {
                    medicine = this.patient.patient_medicines.find(m => m.id == deleted_medicine_id)
                    if (medicine) {
                        medicine.canceled_at = moment(new Date()).format("DD.MM.YYYY")
                        this.patient.canceled_patient_medicines.push(medicine);
                    }
                }

                this.patient.medicines = this.patient.medicines.filter(m => m.id != deleted_medicine_id)
                this.patient.patient_medicines = this.patient.patient_medicines.filter(m => m.id != deleted_medicine_id)
                this.templates.medicines = this.templates.medicines.filter(m => m.id != deleted_medicine_id)
            }
            this.$forceUpdate()
        },
        process_resume_medicine: function (resumed_medicine_id) {
            if (resumed_medicine_id) {
                let medicine = this.patient.canceled_medicines.find(m => m.id == resumed_medicine_id)
                if (medicine) {
                    medicine.canceled_at = null
                    this.patient.medicines.push(medicine);
                } else {
                    medicine = this.patient.canceled_patient_medicines.find(m => m.id == resumed_medicine_id)
                    if (medicine) {
                        medicine.canceled_at = null
                        this.patient.patient_medicines.push(medicine);
                    }
                }

                this.patient.canceled_medicines = this.patient.canceled_medicines.filter(m => m.id != resumed_medicine_id)
                this.patient.canceled_patient_medicines = this.patient.canceled_medicines.filter(m => m.id != resumed_medicine_id)
            }
            this.$forceUpdate()
        },
        process_delete_algorithm: function (deleted_alg_id) {
            if (deleted_alg_id) {
                this.patient.algorithms = this.patient.algorithms.filter(a => a.id != deleted_alg_id)
                this.templates.algorithms = this.templates.algorithms.filter(a => a.id != deleted_alg_id)
            }
            this.$forceUpdate()
        },
        process_delete_examination: function (deleted_examination_id) {
            if (deleted_examination_id) {
                this.patient.examinations = this.patient.examinations.filter(e => e.id != deleted_examination_id)
                this.templates.examinations = this.templates.examinations.filter(e => e.id != deleted_examination_id)
            }
            this.$forceUpdate()
        },
        show_form: function (form) {
            if (!form.title.toLowerCase().includes(this.search_query.toLowerCase())) return false
            if (this.is_admin) return true
            if (form.clinic_id) {
                return form.clinic_id == this.patient.info.clinic_id
            }
            if (form.doctor_id) {
                return form.doctor_id == this.patient.info.doctor_id
            }
            if (form.clinics) {
                return form.clinics.includes(this.clinic_id);
            }
            if (form.exclude_clinics) {
                return !form.exclude_clinics.includes(this.clinic_id);
            }
            return true;
        },
        show_medicine: function (medicine) {
            if (this.is_admin) return true
            if (medicine.clinic_id) {
                return medicine.clinic_id == this.patient.info.clinic_id
            }
            if (medicine.doctor_id) {
                return medicine.doctor_id == this.patient.info.doctor_id
            }
            return true;
        },
    },
    mounted() {
        Event.listen('dashboard-to-main', () => {
            if (window.PAGE == 'settings') {
                this.state = 'main'
            }
        });
        Event.listen('home', () => this.state = 'main');

        Event.listen('change-params', (params) => this.change_alg_params(params))

        Event.listen('form-deleted', (deleted_form_id) => this.process_delete_form(deleted_form_id))
        Event.listen('attach-form-from-card', (form) => this.attach_form(form))

        Event.listen('medicine-deleted', (deleted_medicine_id) => this.process_delete_medicine(deleted_medicine_id))
        Event.listen('medicine-resumed', (resumed_medicine_id) => this.process_resume_medicine(resumed_medicine_id))
        Event.listen('attach-medicine-from-card', (medicine) => this.attach_medicine(medicine))

        Event.listen('examination-deleted', (deleted_examination_id) => this.process_delete_examination(deleted_examination_id))
        Event.listen('attach-examination-from-card', (examination) => this.setup_examination(examination))

        Event.listen('reminder-deleted', (deleted_reminder_id) => this.process_delete_reminder(deleted_reminder_id))

        Event.listen('algorithm-deleted', (deleted_algorithm_id) => this.process_delete_algorithm(deleted_algorithm_id))
        Event.listen('attach-algorithm-from-card', (algorithm) => this.attach_algorithm(algorithm))
        Event.listen('setup-algorithm-from-card', (algorithm) => this.setup_algorithm(algorithm))
    }
}
</script>

<style scoped>
.col-xl-2, .col-md-4 {
    padding-right: 0;
}

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
