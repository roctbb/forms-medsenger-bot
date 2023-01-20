<template>
    <div v-if="form">
        <div class="form">
            <h5 v-if="!form.id">Создание опросника</h5>
            <h5 v-if="form.id">Настройка опросника "{{ form.title }}" </h5>

            <timetable-editor :data="form.timetable" :timetable_save_clicked="this.timetable_save_clicked">&nbsp;<a
                v-if="form.id"
                class="btn btn-success btn-sm"
                @click="save()">Сохранить</a>
            </timetable-editor>
            <div v-show="!tt_only">
                <card title="Параметры опросника">
                    <form-group48 title="Название опросника">
                        <input class="form-control form-control-sm"
                               :class="this.save_clicked && !form.title ? 'is-invalid' : ''"
                               v-model="form.title"/>
                    </form-group48>

                    <form-group48 title="Описание для пациента">
                        <textarea class="form-control form-control-sm" v-model="form.patient_description"></textarea>
                    </form-group48>

                    <form-group48 title="Краткое описание для врача">
                        <textarea class="form-control form-control-sm" v-model="form.doctor_description"></textarea>
                    </form-group48>

                    <form-group48 v-if="is_admin" title="Приветственное сообщение">
                        <textarea class="form-control form-control-sm" v-model="form.init_text"></textarea>
                    </form-group48>

                    <form-group48 title="Пациент может заполнить опросник в произвольное время">
                        <input class="form-check" type="checkbox" v-model="form.show_button"/>
                    </form-group48>

                    <form-group48 v-if="form.show_button" title="Название опросника для кнопки">
                        <input class="form-control form-control-sm"
                               :class="this.save_clicked && !form.button_title ? 'is-invalid' : ''"
                               v-model="form.button_title"/>
                    </form-group48>

                    <form-group48 title="Текст для кнопки в сообщении" v-if="is_admin">
                        <input class="form-control form-control-sm" v-model="form.custom_title"/>
                    </form-group48>

                    <form-group48 title="Текст внутри сообщения" v-if="is_admin">
                        <input class="form-control form-control-sm" v-model="form.custom_text"/>
                    </form-group48>

                    <form-group48 v-if="is_admin && (empty(form.id) || form.is_template)"
                                  title="ID связанного алгоритма">
                        <input class="form-control form-control-sm" v-model="form.algorithm_id"/>
                    </form-group48>

                    <form-group48 v-if="is_admin && (empty(form.id) || form.is_template)" title="Категория шаблона">
                        <input class="form-control form-control-sm" value="Общее" v-model="form.template_category"/>
                    </form-group48>

                    <form-group48 title="Уведомить, если пациент не заполнят опросник">
                        <input class="form-check" type="checkbox" @change="warning_change()"
                               v-model="form.warning_enabled"/>
                    </form-group48>

                    <form-group48 v-if="form.warning_enabled" title="Прислать уведомление о пропусках через">
                        <input class="form-control form-control-sm"
                               :class="this.save_clicked && form.warning_days < 1 ? 'is-invalid' : ''"
                               type="number" min="1" max="200" step="1" v-model="form.warning_days"/>
                        <small class="text-muted">дней</small>
                    </form-group48>

                    <form-group48 title="Сразу же присылать ответы врачу" v-if="is_admin">
                        <input class="form-check" type="checkbox" v-model="form.instant_report"/>
                    </form-group48>

                    <form-group48 title="Отправить при подключении" v-if="is_admin">
                        <input class="form-check" type="checkbox" v-model="form.timetable.send_on_init"/>
                    </form-group48>

                    <form-group48 v-if="is_admin" title="Показывать шаблон клиникам (JSON)">
                        <input class="form-control form-control-sm" type="text" v-model="form.clinics"/>
                    </form-group48>

                    <form-group48 v-if="is_admin" title="Спрятать шаблон у клиник (JSON)">
                        <input class="form-control form-control-sm" type="text" v-model="form.exclude_clinics"/>
                    </form-group48>

                    <form-group48 title="Текст после успешного заполнения (если не сработал алгоритм)">
                        <textarea class="form-control form-control-sm" v-model="form.thanks_text"></textarea>
                    </form-group48>

                    <form-group48 title="Интегральная оценка результатов" v-if="is_admin">
                        <input class="form-check" type="checkbox" @change="add_integral_evaluation()"
                               v-model="form.has_integral_evaluation"/>
                    </form-group48>
                </card>
                <integral-evaluation :data="form.integral_evaluation" :save_clicked="save_clicked"
                                     v-if="form.has_integral_evaluation"></integral-evaluation>

                <hr>
                <fields-editor v-if="form" :form="form" :fields="form.fields"
                               :fields_save_clicked="fields_save_clicked"/>
            </div>
        </div>

        <error-block :errors="errors"/>

        <button class="btn btn-danger" @click="go_back()">Вернуться назад</button>
        <button class="btn btn-success" @click="save()">Сохранить <span v-if="form.is_template"> шаблон</span></button>
        <button v-if="!form.id && is_admin" class="btn btn-default" @click="save(true)">Сохранить как шаблон</button>
        <button v-if="!form.id && !is_admin" class="btn btn-default" @click="save(true, 'doctor')">Сохранить как шаблон
            для себя
        </button>
        <button v-if="!form.id && !is_admin" class="btn btn-default" @click="save(true, 'clinic')">Сохранить как шаблон
            для клиники
        </button>

    </div>
</template>

<style scoped>
h5 {
    margin-bottom: 10px;
}
</style>


<script>


import Card from "../common/Card";
import FormGroup48 from "../common/FormGroup-4-8";
import TimetableEditor from "./parts/TimetableEditor";
import FieldsEditor from "./parts/FieldsEditor";
import ErrorBlock from "../common/ErrorBlock";
import IntegralEvaluation from "./parts/IntegralEvaluation";

export default {
    name: "FormEditor",
    components: {IntegralEvaluation, ErrorBlock, FieldsEditor, TimetableEditor, FormGroup48, Card},
    props: {
        data: {
            required: false
        },
        patient: {
            required: false
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
                has_integral_evaluation: false,
                warning_days: 0
            };
        },
        empty_integral_evaluation: function () {
            return {
                category: 'none',
                offset: 0,
                groups_enabled: false,
                dont_send_to_doctor: false,
                results: [{
                    value: 0,
                    description: "",
                    message: ""
                }]
            }
        },
        add_integral_evaluation: function () {
            if (!this.form.integral_evaluation)
                this.form.integral_evaluation = this.empty_integral_evaluation()
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
            if (this.form.warning_days < 0) {
                this.form.warning_days = 0
            }

            if (this.form.has_integral_evaluation) {
                if (this.form.integral_evaluation) {
                    if (this.form.integral_evaluation.script_enabled) {
                        if (!this.form.integral_evaluation.script)
                            this.errors.push('Проверьте корректность скрипта интеграционной оценки')
                    } else {

                        this.form.integral_evaluation.offset = parseInt(this.form.integral_evaluation.offset)
                        this.form.integral_evaluation.results = this.form.integral_evaluation.results.map(res => {
                            return {
                                value: parseInt(res.value),
                                description: res.description,
                                message: res.message,
                                urgent: res.urgent
                            }
                        })

                        if (this.form.integral_evaluation.groups_enabled) {
                            this.form.integral_evaluation.groups = this.form.integral_evaluation.groups.map(group => {
                                return {
                                    value: parseInt(group.value.toString()),
                                    questions: group.questions.toString().split(',')
                                        .map(q => parseInt(q)).filter(q => !isNaN(q)),
                                    description: group.description,
                                    category: group.category
                                }
                            })

                            if (!this.form.integral_evaluation.dont_send_to_doctor && this.form.integral_evaluation.groups.filter(group => !group.description || isNaN(group.value)).length > 0) {
                                this.errors.push('Проверьте корректность групп интеграционной оценки')
                            }
                        }

                        if (!this.form.integral_evaluation.dont_send_to_doctor && this.form.integral_evaluation.results.filter(res => !res.description || isNaN(res.value)).length > 0) {
                            this.errors.push('Проверьте корректность результатов интеграционной оценки')
                        }
                    }
                } else {
                    this.errors.push('Проверьте корректность интеграционной оценки')
                }
            }

            let prepare_field = (field) => {
                if (['integer', 'float'].includes(field.type)) {
                    field.params.max = parseFloat(field.params.max)
                    field.params.min = parseFloat(field.params.min)
                }
                if (field.type == 'radio') {
                    if (field.params.variants) {
                        field.category = field.params.variants.map(v => v.category).join('|')
                    }
                    if (this.form.has_integral_evaluation) {
                        field.params.variants.forEach(variant =>
                            variant.weight = this.empty(variant.weight) ? 0 : parseFloat(variant.weight))
                    }
                }
                if (field.type == 'checkbox' && this.form.has_integral_evaluation)
                    field.weight = this.empty(field.weight) ? 0 : parseFloat(field.weight.toString())
                return field
            }
            this.form.fields = this.form.fields.map(prepare_field);

            let validate_field = (field) => {
                if (field.type == 'header') return false;
                if (!field.text) return true;

                if (!Object.keys(this.field_types).includes(field.type)) return true;
                if (['integer', 'float'].includes(field.type)) {
                    if (!this.empty(field.params.max) && !this.empty(field.params.min)) {
                        if (field.params.max < field.params.min) return true;
                    }

                }
                if (!this.isJsonString(field.params.custom_params)) return true;
                if (field.type == 'radio') {
                    let variant_validator = (variant) => !variant.text || !variant.category ||
                        this.empty(variant.text) || !this.isJsonString(variant.custom_params)
                    if (field.params.variants.length < 2) return true
                    if (field.params.variants.filter(variant_validator).length) return true;
                }
                if (field.type == 'scale') {
                    if (!field.params.colors.length) return true
                }
                if (!field.category) return true;
            }

            if (this.form.fields.filter(validate_field).length > 0) {

                this.errors.push('Проверьте корректность вопросов')
            }

            return this.errors.length == 0;

        },
        show_validation: function () {
            this.save_clicked = true
            for (let i of this.timetable_save_clicked.keys()) {
                this.$set(this.timetable_save_clicked, i, true)
            }
            for (let i of this.fields_save_clicked.keys()) {
                this.$set(this.fields_save_clicked, i, true)
            }
        },
        save: function (is_template, template_mode, bypass_validation) {
            this.show_validation()
            if (this.check() || bypass_validation) {
                this.errors = []

                if (is_template || this.form.is_template) {
                    this.form.contract_id = undefined
                    this.form.is_template = true;

                    if (template_mode) {
                        this.form.doctor_id = this.patient.info.doctor_id
                        if (template_mode == 'clinic') {
                            this.form.clinic_id = this.patient.info.clinic_id
                        }
                    }
                }

                this.form.categories = this.form.fields.map(f => f.category).join('|')
                this.axios.post(this.url('/api/settings/form'), this.form).then(this.process_save_answer).catch(this.process_save_error);
            }
        },
        process_save_answer: function (response) {
            let is_new = this.empty(this.form.id)


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
            this.save_clicked = false
            this.fields_save_clicked = []
            this.timetable_save_clicked = [false]
        },
        process_save_error: function (response) {
            this.errors.push('Ошибка сохранения');
        },
        warning_change: function () {
            if (this.form.warning_enabled) {
                this.form.warning_days = 7
            } else {
                this.form.warning_days = 0
            }
        }
    },
    data() {
        return {
            errors: [],
            form: undefined,
            backup: "",
            save_clicked: false,
            timetable_save_clicked: [false],
            fields_save_clicked: [],
            tt_only: false
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
            this.save(false, '', true)
        });

        Event.listen('home', (form) => {
            this.form = undefined
            this.errors = []
            this.$forceUpdate()
        });

        Event.listen('navigate-to-create-form-page', () => {
            this.tt_only = false
            this.form = this.create_empty_form()

            this.save_clicked = false
            this.timetable_save_clicked = [false]
            this.fields_save_clicked = []

            this.backup = JSON.stringify(this.form)
        });

        Event.listen('navigate-to-edit-form-page', form => {
            this.tt_only = false
            this.form = form

            this.save_clicked = false

            if (this.form.timetable.points) {
                for (let i of this.form.timetable.points.keys()) {
                    this.$set(this.timetable_save_clicked, i, false)
                }
            }

            for (let i of this.form.fields.keys()) {
                this.$set(this.fields_save_clicked, i, false)
            }


            if (this.form.warning_days > 0) {
                this.form.warning_enabled = true;
            }

            this.backup = JSON.stringify(form)
            this.$forceUpdate()
        });

        Event.listen('edit-form-tt-only', () => {
            this.tt_only = true
        })

        // Обработка добавления времени
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
