<template>
    <div>
        <algorithm-settings/>
        <div v-if="state == 'main'">

            <h6 v-if="patient.month_compliance[0]" class="badge badge-info">Общая комплаентность за месяц: {{ Math.round(100 * patient.month_compliance[1] / patient.month_compliance[0]) }}%</h6>

            <div style="margin-right: -15px;" v-if="params.backup && params.backup.length">
                <input class="btn btn-block btn-outline-info" type="button" data-toggle="collapse" aria-expanded="false"
                       value="Ограничения показателей" data-target="#collapse" aria-controls="collapse">
                <div class="collapse" id="collapse" style="font-size: 14px">
                    <div class="card card-body">
                        <div v-if="loaded">
                            <div v-for="(param, i) in params.backup">
                                <form-group-4-8 :title="param.name">
                                    <input class="form-control form-control-sm"
                                           :class="errors.length && isNaN(to_float(params.edited[i])) ? 'is-invalid' : ''"
                                           v-model="params.edited[i]">
                                </form-group-4-8>
                            </div>
                            <div>
                                <button class="btn btn-success btn-sm" @click="save_params()">Сохранить</button>
                            </div>
                            <div class="alert alert-success" v-if="errors.length && errors[0] == 'Сохранено'" style="margin-top: 15px">Данные успешно сохранены.</div>
                            <error-block v-else :errors="errors"></error-block>
                        </div>
                        <span v-else class="text-center text-muted">Загрузка...</span>
                    </div>
                </div>
            </div>

            <h5>Опросники</h5>

            <div class="row">
                <card v-for="(form, i) in patient.forms" :key="'form' + form.id" class="col-lg-3 col-md-4"
                      :image="images.form">
                    <h6>{{ form.title }}</h6>
                    <small>{{ form.doctor_description }}</small><br>
                    <small><i>{{ tt_description(form.timetable) }}</i></small><br>
                    <small v-if="form.sent">Заполнен {{ form.done }} раз(а) / отправлен {{ form.sent }} раз(а) за последний месяц</small>
                    <small v-else>Пока не отправлялось</small><br>
                    <div v-if="form.contract_id == current_contract_id">
                        <a href="#" @click="edit_form(form)">Редактировать</a>
                        <a href="#" @click="delete_form(form)">Удалить</a>
                        <a target="_blank" :href="preview_form_url(form)">Просмотр</a>
                    </div>
                    <div v-else>
                        <small>Добавлен в другом контракте.</small>
                    </div>
                    <div>
                        <a href="#" @click="send_now(form)">Отправить сейчас</a>
                    </div>
                    <small v-if="!empty(form.template_id)" class="text-muted">ID шаблона: {{ form.template_id }}</small>
                    <small v-else class="text-muted">ID опросника: {{ form.id }}</small>
                </card>
            </div>

            <button class="btn btn-primary btn-sm" @click="state = 'form_templates'">Выбрать или создать опросник
            </button>

            <hr>

            <h5>Лекарства</h5>

            <div class="row">
                <card v-for="(medicine, i) in patient.medicines" :key="'medicine' + medicine.id" :image="images.medicine"
                      class="col-lg-3 col-md-4">
                    <h6>{{ medicine.title }}</h6>
                    <small>{{ medicine.rules }}</small><br>
                    <small><i>{{ tt_description(medicine.timetable) }}</i></small><br>
                    <small v-if="medicine.sent">Подтверждено {{ medicine.done }} раз(а) / отправлено {{ medicine.sent }} раз(а) за последний месяц</small>
                    <small v-else>Пока не отправлялось</small><br>
                    <div v-if="medicine.contract_id == current_contract_id">
                        <a href="#" @click="edit_medicine(medicine)">Редактировать</a>
                        <a href="#" @click="delete_medicine(medicine)">Удалить</a>
                    </div>
                    <div v-else>
                        <small>Добавлен в другом контракте.</small>
                    </div>

                    <small v-if="!empty(medicine.template_id)" class="text-muted">ID шаблона: {{
                            medicine.template_id
                        }}</small>

                </card>

                <card v-for="(medicine, i) in patient.canceled_medicines" :key="'canceled_medicine' + medicine.id" :image="images.canceled_medicine"
                      class="col-lg-3 col-md-4 text-muted">
                    <h6>{{ medicine.title }}</h6>
                    <small>{{ medicine.rules }}</small><br>
                    <small><i>{{ tt_description(medicine.timetable) }}</i></small><br>
                    <small>Назначено: {{ medicine.prescribed_at }}</small><br>
                    <small>Отменено: {{ medicine.canceled_at }}</small><br>

                </card>
            </div>

            <button class="btn btn-primary btn-sm" @click="create_medicine()">Назначить лекарство
            </button>

            <button v-if="is_admin" class="btn btn-info btn-sm" @click="state = 'medicine_templates'">Управление
                шаблонами
            </button>

            <hr>

            <h5>Напоминания</h5>

            <div class="row">
                <card v-for="(reminder, i) in patient.reminders" :key="'reminder_' + reminder.id" :image="images.reminder"
                      class="col-lg-3 col-md-4">
                    <h6>Для {{ reminder.type == 'patient' ? 'пациента' : 'врача' }}</h6>
                    <small> {{ reminder.text }} </small><br>
                    <small><i>{{ tt_description(reminder.timetable) }}</i></small><br>
                    <small>Начало: {{ reminder.attach_date }}</small><br>
                    <small>Завершение: {{ reminder.detach_date }}</small><br>
                    <div v-if="reminder.contract_id == current_contract_id">
                        <a href="#" @click="edit_reminder(reminder)">Редактировать</a>
                        <a href="#" @click="delete_reminder(reminder)">Удалить</a>
                    </div>
                    <div v-else>
                        <small>Добавлен в другом контракте.</small>
                    </div>

                    <small v-if="!empty(reminder.template_id)" class="text-muted">
                        ID шаблона: {{ reminder.template_id }}</small>

                </card>
                <card v-for="(reminder, i) in patient.old_reminders" :key="'old_reminder_' + reminder.id" :image="images.old_reminder"
                      class="col-lg-3 col-md-4">
                    <h6>Для {{ reminder.type == 'patient' ? 'пациента' : 'врача' }}</h6>
                    <small> {{ reminder.text }} </small><br>
                    <small><i>{{ tt_description(reminder.timetable) }}</i></small><br>
                    <small>Начало: {{ reminder.attach_date }}</small><br>
                    <small>Завершение: {{ reminder.detach_date }}</small><br>
                    <div v-if="reminder.contract_id != current_contract_id">
                        <small>Добавлен в другом контракте.</small>
                    </div>

                    <small v-if="!empty(reminder.template_id)" class="text-muted">
                        ID шаблона: {{ reminder.template_id }}</small>

                </card>
            </div>

            <button class="btn btn-primary btn-sm" @click="create_reminder()">Создать напоминание</button>

            <button v-if="is_admin" class="btn btn-info btn-sm" @click="state = 'reminder_templates'">Управление шаблонами</button>
            <hr>

            <h5>Алгоритмы</h5>

            <div class="row">
                <card v-for="(algorithm, i) in patient.algorithms" :key="'algorithm_' + algorithm.id" :image="images.algorithm"
                      class="col-lg-3 col-md-4">
                    <h6>{{ algorithm.title }}</h6>
                    <small>{{ algorithm.description }}</small><br>
                    <small v-html="alg_description(algorithm)"></small>
                    <div v-if="algorithm.contract_id == current_contract_id">
                        <a href="#" @click="edit_algorithm(algorithm)">Редактировать</a>
                        <a href="#" @click="delete_algorithm(algorithm)">Удалить</a>
                    </div>
                    <div v-else>
                        <small>Добавлен в другом контракте.</small>
                    </div>

                    <small v-if="!empty(algorithm.template_id)" class="text-muted">ID шаблона: {{
                            algorithm.template_id
                        }}</small>

                </card>
            </div>

            <button class="btn btn-primary btn-sm" @click="state = 'algorithm_templates'">Выбрать или создать
                алгоритм
            </button>

            <div style="margin-top: 15px;" class="alert alert-info" role="alert">
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
                    <li>Посмотреть все внесенные пациентом данные можно с помощью интеллектуального агента <strong>"Медкарта"</strong>.</li>
                    <li>Посмотреть графики можно <a v-bind:href="url('graph')">здесь</a> (или с помощью кнопки <i>Действия -> Графики</i> в Medsenger).</li>
                </ul>
            </div>

        </div>
        <div v-if="state == 'form_templates'">
            <div class="alert alert-info" role="alert">
                <h4 class="alert-heading">Выбор опросника</h4>
                <p>Выберите опросник из списка ниже. В дальнейшем вы сможете изменить расписание, описание и даже сами
                    вопросы.</p>
            </div>

            <input type="text" v-model="search_query" class="form-control form-control-sm" style="margin-bottom: 5px;" placeholder="Поиск...">

            <div class="row" v-for="(group, name) in group_by(templates.forms.filter(show_form).map((form) => {
                if (!form.template_category) form.template_category = 'Общее'
                return form
            }), 'template_category')">

                <div class="col-md-12"><h5>{{ name }}</h5></div>

                <card v-for="(form, i) in group" :key="'form_template_' + form.id" class="col-lg-3 col-md-4"
                      :image="images.form">
                    <h6>{{ form.title }}</h6>
                    <small>{{ form.doctor_description }}</small><br>
                    <small><i>{{ tt_description(form.timetable) }}</i></small><br>
                    <a href="#" v-if="!is_attached(form)" @click="attach_form(form)">Подключить</a>
                    <small v-else class="text-muted">Опросник подключен</small>

                    <a href="#" v-if="is_admin" @click="edit_form(form)">Редактировать</a>
                    <a href="#" v-if="is_admin" @click="delete_form(form)">Удалить</a>
                    <a target="_blank" :href="preview_form_url(form)">Просмотр</a>

                    <div>
                        <a href="#" @click="send_now(form)">Отправить сейчас</a>
                    </div>

                    <small v-if="form.algorithm_id"><b>Связанный алгоритм:</b>
                        {{ find_algorithm(form.algorithm_id).title }}</small>

                    <br>

                    <small class="text-muted">ID: {{ form.id }}</small>
                </card>
                <div v-if="!templates.forms.length" class="col-md-12">
                    <p style="margin-bottom: 15px;">Список шаблонов пуст.</p>
                </div>
            </div>

            <button class="btn btn-primary btn-sm" @click="create_form()">Добавить свой опросник</button>
            <button class="btn btn-danger btn-sm" @click="state = 'main'">Назад</button>

        </div>
        <div v-if="state == 'medicine_templates'">
            <h3>Шаблоны лекарств</h3>

            <div class="alert alert-info" role="alert">
                <h4 class="alert-heading">Шаблоны лекарств</h4>
                <p>Выберите лекарство или создайте новое.</p>
            </div>

            <div class="row">
                <card v-for="(medicine, i) in templates.medicines" :key="'medicine_template_' + medicine.id" :image="images.medicine"
                      class="col-lg-3 col-md-4">
                    <h6>{{ medicine.title }}</h6>
                    <small>{{ medicine.rules }}</small><br>
                    <small><i>{{ tt_description(medicine.timetable) }}</i></small><br>
                    <a href="#" @click="attach_medicine(medicine)">Подключить</a>
                    <a href="#" v-if="is_admin" @click="edit_medicine(medicine)">Редактировать</a>
                    <a href="#" v-if="is_admin" @click="delete_medicine(medicine)">Удалить</a>

                    <br>

                    <small class="text-muted">ID: {{ medicine.id }}</small>
                </card>
                <div v-if="!templates.medicines.length" class="col-md-12">
                    <p style="margin-bottom: 15px;">Список шаблонов пуст.</p>
                </div>

            </div>

            <button class="btn btn-primary btn-sm" @click="create_medicine()">Добавить</button>
            <button class="btn btn-danger btn-sm" @click="state = 'main'">Назад</button>

        </div>
        <div v-if="state == 'reminder_templates'">
            <h3>Шаблоны напоминаний</h3>

            <div class="alert alert-info" role="alert">
                <p>Выберите напоминание или создайте новое.</p>
            </div>

            <div class="row">
                <card v-for="(reminder, i) in templates.reminders" :key="'reminder_template_' + reminder.id" :image="images.reminder"
                      class="col-lg-3 col-md-4">
                    <h6>Для {{ reminder.type == 'both' ? 'всех' : (reminder.type == 'patient' ? 'пациента' : 'врача') }}</h6>
                    <small>{{ reminder.type == 'doctor' ? reminder.doctor_text : reminder.patient_text }}</small><br>
                    <small><i>{{ tt_description(reminder.timetable) }}</i></small><br>
                    <small><i>в течение {{ reminder_duration(reminder) }} дн.</i></small><br>
                    <a href="#" @click="attach_reminder(reminder)">Подключить</a>
                    <a href="#" v-if="is_admin" @click="edit_reminder(reminder)">Редактировать</a>
                    <a href="#" v-if="is_admin" @click="delete_reminder(reminder)">Удалить</a>

                    <br>

                    <small v-if="!empty(reminder.template_id)" class="text-muted">
                        ID шаблона: {{ reminder.template_id }}</small>
                </card>
                <div v-if="!templates.medicines.length" class="col-md-12">
                    <p style="margin-bottom: 15px;">Список шаблонов пуст.</p>
                </div>

            </div>

            <button class="btn btn-primary btn-sm" @click="create_reminder()">Добавить</button>
            <button class="btn btn-danger btn-sm" @click="state = 'main'">Назад</button>

        </div>
        <div v-if="state == 'algorithm_templates'">

            <div class="alert alert-info" role="alert">
                <h4 class="alert-heading">Выбор алгоритма</h4>
                <p>Выберите алгоритм из списка ниже. В дальнейшем вы сможете посмотреть подробную схему его работы, но
                    изменять ее без опыта не рекомендуется.</p>
            </div>


            <div class="row" v-for="(group, name) in group_by(templates.algorithms.map((algorithms) => {
                if (!algorithms.template_category) algorithms.template_category = 'Общее'
                return algorithms
            }), 'template_category')">

                <div class="col-md-12"><h5>{{ name }}</h5></div>
                <card v-for="(algorithm, i) in group" v-if="is_admin || !algorithm.clinics || algorithm.clinics.includes(clinic_id)" :key="'algorithm_' + algorithm.id" :image="images.algorithm"
                      class="col-lg-3 col-md-4">
                    <h6>{{ algorithm.title }}</h6>
                    <small>{{ algorithm.description }}</small><br>
                    <small v-html="alg_description(algorithm)"></small>
                    <a href="#" v-if="need_filling(algorithm)" @click="setup_algorithm(algorithm)">Настроить и
                        подключить</a>
                    <a href="#" v-else @click="attach_algorithm(algorithm)">Подключить</a>
                    <a href="#" v-if="is_admin" @click="edit_algorithm(algorithm)">Редактировать</a>
                    <a href="#" v-if="is_admin" @click="delete_algorithm(algorithm)">Удалить</a>

                    <br>
                    <small class="text-muted">ID: {{ algorithm.id }}</small>

                </card>

                <div v-if="!templates.algorithms.length" class="col-md-12">
                    <p style="margin-bottom: 15px;">Список шаблонов пуст.</p>
                </div>
            </div>


            <button class="btn btn-primary btn-sm" @click="create_algorithm()">Добавить</button>
            <button class="btn btn-danger btn-sm" @click="state = 'main'">Назад</button>

        </div>

    </div>

</template>

<script>

import Card from "../common/Card";
import AlgorithmSettings from "./AlgorithmSettings";
import FormGroup48 from "../common/FormGroup-4-8";
import ErrorBlock from "../common/ErrorBlock";
import * as moment from "moment/moment";

export default {
    name: "Dashboard",
    components: {ErrorBlock, FormGroup48, AlgorithmSettings, Card},
    props: {
        patient: {
            required: true
        },
        templates: {
            required: true
        }
    },
    data: function () {
        return {
            state: 'main',
            loaded: false,
            errors: [],
            lock_btn: false,
            params: {},
            search_query: ''
        }
    },
    methods: {
        reminder_duration: function (reminder) {
            let attach = moment(reminder.attach_date, "YYYY-MM-DD")
            let detach = moment(reminder.detach_date, "YYYY-MM-DD")
            return moment.duration(detach.diff(attach)).asDays()
        },
        update_params: function () {
            this.loaded = false
            this.params = {
                backup: [],
                edited: []
            }
            this.axios.get(this.url('/params')).then(response => {
                response.data.forEach(param => {
                    if (param.name && param.value != null) {
                        this.params.backup.push(param)
                        this.params.edited.push(param.value)
                    }
                })
                this.loaded = true
            });
        },
        save_params: function () {
            this.errors = []
            this.lock_btn = true

            // check values
            this.params.edited.map((param, i) => {
                let val = this.to_float(param)
                if (!isNaN(val)) {
                    return val
                } else {
                    this.errors.push(`Пожалуйста, проверьте поле "${this.params.backup[i].name}"`)
                    return param
                }
            })

            // change values
            let changed_algorithms = new Set()
            if (!this.errors.length) {
                this.params.backup.forEach((param, i) => {
                    if (this.to_float(param.value) != this.params.edited[i]) {
                        param.locations.forEach(loc => {
                            let alg = this.patient.algorithms.filter(a => a.id == loc.algorithm)[0]

                            if (loc.common) {
                                alg.common_conditions[loc.condition]
                                    .criteria[loc.block][loc.criteria].value = this.params.edited[i]
                            } else {
                                alg.steps[loc.step].conditions[loc.condition]
                                    .criteria[loc.block][loc.criteria].value = this.params.edited[i]
                            }

                            changed_algorithms.add(alg)
                        })
                    }
                })
            }

            // save values
            if (changed_algorithms.size) {
                this.axios.post(this.url('/api/settings/algorithms'), [...changed_algorithms])
                    .then(response => this.errors = ['Сохранено'])
                    .catch(err => this.errors = ['Ошибка сохранения']);

            }

            this.lock_btn = false
        },
        find_algorithm: function (id) {
            return this.templates.algorithms.filter(t => t.id == id)[0]
        },
        is_attached: function (form) {
            return this.patient.forms.filter(f => f.template_id == form.id).length != 0
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
        preview_form_url: function (form) {
            return this.url('/preview_form/' + form.id)
        },
        send_now: function (form) {
            let alert = () => {
                this.$alert("Опросник отправлен!");
            }

            this.$confirm(
                {
                    message: `Отправить опросник ` + form.title + ` пациенту прямо сейчас?`,
                    button: {
                        no: 'Нет',
                        yes: 'Да'
                    },
                    callback: confirm => {
                        if (confirm) {
                            this.axios.get(this.url('/api/send_form/' + form.id)).then(alert);
                        }
                    }
                }
            )
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
        edit_form: function (form) {
            Event.fire('edit-form', form)
        },
        delete_form: function (form) {
            this.$confirm(
                {
                    message: `Вы уверены, что хотите удалить опросник ` + form.title + `?`,
                    button: {
                        no: 'Нет',
                        yes: 'Да, удалить'
                    },
                    callback: confirm => {
                        if (confirm) {
                            this.axios.post(this.url('/api/settings/delete_form'), form).then(this.process_delete_form_answer);
                        }
                    }
                }
            )
        },
        process_delete_form_answer: function (response) {
            if (response.data.deleted_id) {
                this.patient.forms = this.patient.forms.filter(f => f.id != response.data.deleted_id)
                this.templates.forms = this.templates.forms.filter(f => f.id != response.data.deleted_id)
            }
        },
        create_medicine: function () {
            Event.fire('navigate-to-create-medicine-page')
        },
        edit_medicine: function (medicine) {
            Event.fire('edit-medicine', medicine)
        },
        delete_medicine: function (medicine) {
            this.$confirm(
                {
                    message: `Вы уверены, что хотите отменить препарат ` + medicine.title + `?`,
                    button: {
                        no: 'Нет',
                        yes: 'Да, удалить'
                    },
                    callback: confirm => {
                        if (confirm) {
                            this.axios.post(this.url('/api/settings/delete_medicine'), medicine).then(this.process_delete_medicine_answer);
                        }
                    }
                }
            )
        },
        attach_reminder: function (reminder) {
            Event.fire('attach-reminder', reminder)
        },
        create_reminder: function () {
            Event.fire('navigate-to-create-reminder-page')
        },
        edit_reminder: function (reminder) {
            Event.fire('edit-reminder', reminder)
        },
        delete_reminder: function (reminder) {
            this.$confirm(
                {
                    message: `Вы уверены, что хотите удалить напоминание?`,
                    button: {
                        no: 'Нет',
                        yes: 'Да, удалить'
                    },
                    callback: confirm => {
                        if (confirm) {
                            this.axios.post(this.url('/api/settings/delete_reminder'), reminder).then(this.process_delete_reminder_answer);
                        }
                    }
                }
            )
        },
        process_delete_reminder_answer: function (response) {
            if (response.data.deleted_id) {
                this.patient.reminders = this.patient.reminders.filter(r => r.id != response.data.deleted_id)
                this.templates.reminders = this.templates.reminders.filter(r => r.id != response.data.deleted_id)
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
                            this.axios.post(this.url('/api/settings/delete_algorithm'), algorithm).then(this.process_delete_algorithm_answer);
                        }
                    }
                }
            )
        },
        process_delete_medicine_answer: function (response) {
            if (response.data.deleted_id) {
                let medicine = this.patient.medicines.find(m => m.id == response.data.deleted_id)
                if (medicine) {
                    medicine.canceled_at = moment(new Date()).format("DD.MM.YYYY")
                    this.patient.canceled_medicines.push(medicine);
                }

                this.patient.medicines = this.patient.medicines.filter(m => m.id != response.data.deleted_id)
                this.templates.medicines = this.templates.medicines.filter(m => m.id != response.data.deleted_id)
            }
        },
        process_delete_algorithm_answer: function (response) {
            if (response.data.deleted_id) {
                this.patient.algorithms = this.patient.algorithms.filter(m => m.id != response.data.deleted_id)
                this.templates.algorithms = this.templates.algorithms.filter(m => m.id != response.data.deleted_id)
            }
        },
        show_form: function (form) {
            if (!form.title.toLowerCase().includes(this.search_query.toLowerCase())) return false
            if (this.is_admin) return true
            if (form.clinics) {
                return form.clinics.includes(this.clinic_id);
            }
            if (form.exclude_clinics) {
                return !form.exclude_clinics.includes(this.clinic_id);
            }
            return true;
        }
    },
    mounted() {
        Event.listen('dashboard-to-main', () => {
            this.state = 'main'
            this.update_params()
        });

        Event.listen('home', () => {
            this.state = 'main'
            this.update_params()
        });

        Event.listen('back-to-dashboard', () => this.update_params())

        this.update_params()
    }
}
</script>

<style scoped>
.col-xl-2, .col-md-4 {
    padding-right: 0px;
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

</style>
