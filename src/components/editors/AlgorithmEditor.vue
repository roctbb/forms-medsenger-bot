<template>
    <div v-if="algorithm">
        <error-block :errors="errors"/>
        <div class="form">
            <card title="Описание алгоритма">
                <form-group48 title="Название">
                    <input class="form-control form-control-sm"
                           :class="this.save_clicked && !algorithm.title ? 'is-invalid' : ''"
                           v-model="algorithm.title"/>
                </form-group48>

                <form-group48 title="Описание">
                    <textarea class="form-control form-control-sm" v-model="algorithm.description"></textarea>
                </form-group48>

                <form-group48 v-if="is_admin && (empty(algorithm.id) || algorithm.is_template)"
                              title="Категория шаблона">
                    <input class="form-control form-control-sm" v-model="algorithm.template_category"/>
                </form-group48>

                <form-group48 v-if="is_admin" title="Показывать шаблон клиникам (JSON)">
                    <input class="form-control form-control-sm" type="text" v-model="algorithm.clinics"/>
                </form-group48>

                <form-group48 title="Дата отсчета">
                    <date-picker lang="ru" v-model="algorithm.attach_date" value-type="YYYY-MM-DD"></date-picker>
                </form-group48>

                <form-group48 title="Дата завершения">
                    <date-picker lang="ru" v-model="algorithm.detach_date" value-type="YYYY-MM-DD"></date-picker>
                </form-group48>
            </card>

            <card :title="'Общие условия'">
                <card v-for="(condition, condition_index) in algorithm.common_conditions"
                      additional_class="border-primary"
                      :key="condition.uid">

                    <form-group48 title="Таймаут (минуты)">
                        <input class="form-control form-control-sm" type="number" v-model="condition.reset_minutes"/>
                    </form-group48>

                    <form-group48 title="Не помечать точки">
                        <input type="checkbox" v-model="condition.skip_additions">
                    </form-group48>

                    <form-group48 title="таймаут при инициализации">
                        <input type="checkbox" v-model="condition.timeout_on_init">
                    </form-group48>

                    <h6>Критерии срабатывания</h6>

                    <div v-for="(or_block, i) in condition.criteria">
                        <div v-for="(criteria, j) in or_block">
                            <criteria class="alert alert-primary" :data="criteria" :rkey="i" :pkey="j"
                                      :condition="condition" :key="criteria.uid"/>
                        </div>
                        <p class="text-center">
                            <button class="btn btn-sm btn-default" @click="add_criteria(or_block, i)">и</button>
                        </p>
                        <div class="separator">или</div>
                    </div>
                    <p class="text-center">
                        <button class="btn btn-sm btn-default" @click="add_or_block(condition)">или</button>
                    </p>

                    <h6 style="margin-top: 10px;">Действия если условие выполняется</h6>

                    <action class="alert alert-success" v-for="(action, i) in condition.positive_actions"
                            :algorithm="algorithm" :data="action" :pkey="i" :parent="condition.positive_actions"
                            :key="action.uid"></action>
                    <p class="text-center">
                        <button class="btn btn-sm btn-default" @click="add_action(condition.positive_actions)">
                            Добавить
                        </button>
                    </p>

                    <h6 style="margin-top: 10px;">Действия если условие не выполняется</h6>

                    <action class="alert alert-danger" v-for="(action, i) in condition.negative_actions"
                            :algorithm="algorithm" :data="action" :pkey="i" :parent="condition.negative_actions"
                            :key="action.uid"></action>
                    <p class="text-center">
                        <button class="btn btn-sm btn-default" @click="add_action(condition.negative_actions)">
                            Добавить
                        </button>
                    </p>

                    <hr>

                    <button class="btn btn-sm btn-danger" @click="remove_common_condition(algorithm, condition_index)">
                        Удалить условие
                    </button>
                    <button class="btn btn-sm btn-primary" @click="duplicate_common_condition(algorithm, condition_index)">
                        Дублировать условие
                    </button>
                </card>
                <button class="btn btn-sm btn-default" @click="add_common_condition(algorithm)">Добавить условие
                </button>
            </card>

            <card v-for="(step, step_index) in algorithm.steps" :title="step.title" :key="step.uid">
                <form-group48 title="Название ступени">
                    <input class="form-control form-control-sm" v-model="step.title"/>
                </form-group48>

                <form-group48 title="Таймаут (минуты)">
                    <input class="form-control form-control-sm" type="number" v-model="step.reset_minutes"/>
                </form-group48>

                <card v-for="(condition, condition_index) in step.conditions" additional_class="border-primary"
                      :key="condition.uid">

                    <form-group48 title="Таймаут (минуты)">
                        <input class="form-control form-control-sm" type="number" v-model="condition.reset_minutes"/>
                    </form-group48>

                    <form-group48 title="Не помечать точки">
                        <input type="checkbox" v-model="condition.skip_additions">
                    </form-group48>

                    <form-group48 title="таймаут при инициализации">
                        <input type="checkbox" v-model="condition.timeout_on_init">
                    </form-group48>

                    <h6>Критерии срабатывания</h6>

                    <div v-for="(or_block, i) in condition.criteria">
                        <div v-for="(criteria, j) in or_block">
                            <criteria class="alert alert-primary" :data="criteria" :rkey="i" :pkey="j"
                                      :condition="condition" :key="criteria.uid"/>
                        </div>
                        <p class="text-center">
                            <button class="btn btn-sm btn-default" @click="add_criteria(or_block, i)">и</button>
                        </p>
                        <div class="separator">или</div>
                    </div>
                    <p class="text-center">
                        <button class="btn btn-sm btn-default" @click="add_or_block(condition)">или</button>
                    </p>

                    <h6 style="margin-top: 10px;">Действия если условие выполняется</h6>

                    <action class="alert alert-success" v-for="(action, i) in condition.positive_actions"
                            :algorithm="algorithm" :data="action" :pkey="i" :parent="condition.positive_actions"
                            :key="action.uid"></action>
                    <p class="text-center">
                        <button class="btn btn-sm btn-default" @click="add_action(condition.positive_actions)">
                            Добавить
                        </button>
                    </p>

                    <h6 style="margin-top: 10px;">Действия если условие не выполняется</h6>

                    <action class="alert alert-danger" v-for="(action, i) in condition.negative_actions"
                            :algorithm="algorithm" :data="action" :pkey="i" :parent="condition.negative_actions"
                            :key="action.uid"></action>
                    <p class="text-center">
                        <button class="btn btn-sm btn-default" @click="add_action(condition.negative_actions)">
                            Добавить
                        </button>
                    </p>

                    <hr>

                    <button class="btn btn-sm btn-danger" @click="remove_condition(step, condition_index)">Удалить
                        условие
                    </button>
                </card>

                <button class="btn btn-sm btn-default" @click="add_condition(step)">Добавить условие</button>

                <hr>

                <h6>Действие по таймауту</h6>

                <action class="alert alert-warning" v-for="(action, i) in step.timeout_actions" :algorithm="algorithm"
                        :data="action" :pkey="i" :parent="step.timeout_actions" :key="action.uid"></action>
                <button class="btn btn-sm btn-default" @click="add_action(step.timeout_actions)">Добавить</button>


                <button class="btn btn-sm btn-danger" @click="remove_step(step_index)">Удалить ступень</button>
            </card>

            <button class="btn btn-sm btn-default" @click="add_step()">Добавить ступень</button>

        </div>
        <button class="btn btn-danger" @click="go_back()">Назад</button>
        <button :disabled="button_lock" class="btn btn-success" @click="save()">Сохранить <span v-if="algorithm.is_template"> шаблон</span>
        </button>
        <button :disabled="button_lock" class="btn btn-primary" v-if="!algorithm.id && is_admin" @click="save(true)">Сохранить как шаблон
        </button>
    </div>
</template>

<script>

import Card from "../common/Card";
import FormGroup48 from "../common/FormGroup-4-8";
import ErrorBlock from "../common/ErrorBlock";
import Criteria from "./parts/Criteria";
import Action from "./parts/Action";
import * as moment from "moment/moment";
import DatePicker from 'vue2-datepicker';
import 'vue2-datepicker/index.css';
import 'vue2-datepicker/locale/ru';

export default {
    name: "AlgorithmEditor",
    components: {Action, FormGroup48, Card, ErrorBlock, Criteria, DatePicker},
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
                        this.copy(this.algorithm, old)
                        Event.fire('back-to-dashboard');
                        this.algorithm = undefined
                        this.errors = []
                    }
                }
            })

        },
        create_empty_algorithm: function () {
            return {
                steps: [this.create_step()],
                common_conditions: [],
            };
        },
        add_or_block: function (condition) {
            condition.criteria.push([this.create_empty_criteria()])
            this.criteria_save_clicked.push([false]);
        },
        add_criteria: function (block, i) {
            block.push(this.create_empty_criteria())
        },
        add_common_condition: function (algorithm) {
            if (!algorithm.common_conditions) {
                algorithm.common_conditions = [];
            }
            algorithm.common_conditions.push(this.create_condition());
        },
        remove_common_condition: function (algorithm, index) {
            algorithm.common_conditions.splice(index, 1);
        },
        duplicate_common_condition: function (algorithm, index) {
            let tmp = this.create_condition()
            this.copy(tmp, algorithm.common_conditions[index])
            tmp.uid = this.uuidv4()
            algorithm.common_conditions.push(tmp)
        },
        add_condition: function (step, type) {
            step.conditions.push(this.create_condition());
        },
        add_step: function () {
            this.algorithm.steps.push(this.create_step());
        },

        create_step: function () {
            return {
                title: 'ступень',
                reset_minutes: 60,
                conditions: [this.create_condition()],
                timeout_actions: [],
                uid: this.uuidv4()
            }
        },

        create_condition: function () {
            return {
                criteria: [[this.create_empty_criteria()]],
                positive_actions: [this.create_empty_action()],
                negative_actions: [],
                uid: this.uuidv4()
            }
        },
        create_empty_criteria: function () {
            return {
                category: this.category_list[0].name,
                left_mode: 'value',
                right_mode: 'value',
                sign: 'equal',
                uid: this.uuidv4()
            }
        },
        add_action: function (parent) {
            parent.push(this.create_empty_action())
        },
        create_empty_action: function () {
            return {
                type: 'patient_message',
                params: {},
                uid: this.uuidv4()
            }
        },
        check: function () {
            this.errors = [];
            if (!this.algorithm.title) {
                this.errors.push('Укажите название алгоритма')
            }

            let prepare_criteria = (criteria) => {
                criteria.left_offset = parseInt(criteria.left_offset)
                criteria.right_offset = parseInt(criteria.right_offset)

                if (criteria.left_mode != 'time' && criteria.left_mode != 'init') {
                    if (criteria.left_dimension == 'hours') {
                        if (!this.empty(criteria.left_hours)) criteria.left_hours = parseInt(criteria.left_hours)
                    } else if (criteria.left_dimension == 'times') {
                        if (!this.empty(criteria.left_times)) criteria.left_times = parseInt(criteria.left_times)
                    } else {
                        if (!this.empty(criteria.left_for)) criteria.left_for = parseInt(criteria.left_for)
                    }

                    if (criteria.left_mode == 'count') criteria.check_value = parseInt(criteria.check_value)

                    if (criteria.right_dimension == 'hours') {
                        if (!this.empty(criteria.right_hours)) criteria.right_hours = parseInt(criteria.right_hours)
                    } else {
                        if (!this.empty(criteria.right_times)) criteria.right_times = parseInt(criteria.right_times)
                    }

                    if (!this.empty(criteria.value)) {
                        let category = this.get_category(criteria.category)
                        if (category.type == 'integer') criteria.value = parseInt(criteria.value)
                        if (category.type == 'float') criteria.value = parseFloat(criteria.value)
                    }

                    if (!this.empty(criteria.multiplier)) {
                        criteria.multiplier = parseFloat(criteria.multiplier.toString().replace(',', '.'))
                    } else {
                        criteria.multiplier = 1
                    }

                }
                if (criteria.left_mode == 'time') {
                    if (criteria.right_dimension == 'hours') {
                        if (!this.empty(criteria.right_hours)) criteria.right_hours = parseInt(criteria.right_hours)
                    } else {
                        if (!this.empty(criteria.right_times)) criteria.right_times = parseInt(criteria.right_times)
                    }

                    if (criteria.sign == 'equal') {
                        criteria.category = 'exact_time'
                    } else {
                        criteria.category = 'time'
                    }
                }
                if (criteria.left_mode == 'init') {
                    criteria.category = 'init'
                }

                return criteria
            }
            let prepare_action = (action) => {
                if (action.type == 'record') {
                    let category = this.get_category(action.params.category)

                    if (category.type == 'integer') action.params.value = parseInt(action.params.value)
                    if (category.type == 'float') action.params.value = parseFloat(action.params.value)
                }
                if (action.type == 'order') {
                    action.params.agent_id = parseInt(action.params.agent_id)
                    if (action.params.order_params && (typeof action.params.order_params === 'string' || action.params.order_params instanceof String)) {
                        action.params.order_params = JSON.parse(action.params.order_params);
                    }

                }
                if (action.type == 'script') {
                    if (action.params.script_params) {
                        action.params.script_params.forEach((param) => {
                            if ( (typeof param.value === 'string' || param.value instanceof String))
                            param.value =  parseFloat(param.value)
                        })
                    }
                }
                return action;
            }

            let criteria_validator = (criteria) => {
                let category = this.get_category(criteria.category)

                if (criteria.left_mode == 'time') {
                    if (moment(criteria.value, 'YYYY-MM-DD', true).isValid() && !this.empty(criteria.right_hours)) return false;
                    return true;
                }
                if (criteria.left_mode != 'value' && this.empty(criteria.left_hours)) {
                    return true;
                }

                if (!['value', 'category_value'].includes(criteria.right_mode) && this.empty(criteria.right_hours)) {
                    return true;
                }
                if (criteria.right_mode == 'value' && this.empty(criteria.value)) {
                    return true;
                }

                if (['value', 'category_value'].includes(criteria.right_mode) &&
                    (criteria.ask_value && (this.empty(criteria.value_name) || this.empty(criteria.value_code))))
                    return true;

                return false;
            }

            if (this.algorithm.common_conditions) {
                this.algorithm.common_conditions.forEach(condition => {
                    condition.criteria = condition.criteria.map((L) => L.map(prepare_criteria))
                    condition.positive_actions = condition.positive_actions.map(prepare_action)
                    condition.negative_actions = condition.negative_actions.map(prepare_action)
                })
            }

            this.algorithm.steps.forEach(step => {
                if (step.timeout_actions) {
                    step.timeout_actions = step.timeout_actions.map(prepare_action)
                } else {
                    step.timeout_actions = []
                }

                step.conditions.forEach(condition => {

                    condition.criteria = condition.criteria.map((L) => L.map(prepare_criteria))
                    condition.positive_actions = condition.positive_actions.map(prepare_action)
                    condition.negative_actions = condition.negative_actions.map(prepare_action)
                })
            })

            if (!this.algorithm.steps.length) {
                this.errors.push('Добавьте хотя бы одну ступень.')
            }

            let has_errors = this.algorithm.steps.some(step => {
                step.conditions.some(condition => condition.criteria.filter((L) => L.filter(criteria_validator).length > 0).length);
            });

            if (has_errors) {
                this.errors.push('Проверьте правильность условий.')
            }


            let action_validator = (action) => {
                if (action.type == 'record' && this.empty(action.params.value)) return true;
                if ((action.type == 'patient_message' || action.type == 'doctor_message') && this.empty(action.params.text)) return true;
                if (action.params.add_deadline && !action.params.action_deadline) return true;
                if (action.params.add_action && this.empty(action.params.action_name)) return true;

                return false;
            }

            has_errors = this.algorithm.steps.some(step => {
                step.conditions.some(condition => condition.positive_actions.filter(action_validator).length > 0);
            }) || this.algorithm.steps.some(step => {
                step.conditions.some(condition => condition.negative_actions.filter(action_validator).length);
            }) || this.algorithm.steps.some(step => step.timeout_actions.filter(action_validator).length);

            if (has_errors) {
                this.errors.push('Проверьте правильность действий.')
            }

            if (this.errors.length != 0) {
                return false;
            } else {
                return true;
            }
        },
        show_validation: function () {
            this.save_clicked = true
            /*
            for (let i = 0; i < this.actions_save_clicked.length; i++) {
                this.$set(this.actions_save_clicked, i, true)
            }
            for (let i = 0; i < this.criteria_save_clicked.length; i++) {
                for (let j = 0; j < this.criteria_save_clicked[i].length; j++) {
                    this.$set(this.criteria_save_clicked[i], j, true)
                }
            } */
        },
        save: function (is_template) {
            this.show_validation()
            if (this.check()) {
                this.errors = []

                if (is_template || this.algorithm.is_template) {
                    this.algorithm.contract_id = undefined
                    this.algorithm.is_template = true;
                }

                if (!this.button_lock) {
                    this.button_lock = true
                    this.axios.post(this.direct_url('/api/settings/algorithm'), this.algorithm).then(this.process_save_answer).catch(this.process_save_error);
                }
            }
        },
        process_save_answer: function (response) {
            let is_new = this.empty(this.algorithm.id)

            this.algorithm.id = response.data.id
            if (!this.algorithm.is_template) {
                this.algorithm.patient_id = response.data.patient_id
                this.algorithm.contract_id = response.data.contract_id
            }

            if (is_new) Event.fire('algorithm-created', response.data)
            else Event.fire('back-to-dashboard', response.data)
            this.button_lock = false
            this.algorithm = undefined
        },
        process_save_error: function (response) {
            this.button_lock = false
            this.errors.push('Ошибка сохранения')
        },
        remove_action: function (index) {
            index[1].splice(index[0], 1);
        },
        remove_criteria: function (index) {
            index[2].criteria[index[0]].splice(index[1], 1);

            if (!index[2].criteria[index[0]].length) {
                index[2].criteria.splice(index[0], 1);
            }
        },
        remove_condition: function (step, index) {
            step.conditions.splice(index, 1);
        },
        remove_step: function (index) {
            this.algorithm.steps.splice(index, 1);
        }
    },
    data() {
        return {
            errors: [],
            algorithm: undefined,
            backup: "",
            save_clicked: false,
            button_lock: false,
            actions_save_clicked: [],
            criteria_save_clicked: []
        }
    },
    mounted() {
        Event.listen('attach-algorithm', (algorithm) => {
            this.algorithm = {}
            this.copy(this.algorithm, algorithm)

            this.algorithm.attach_date = moment().format('YYYY-MM-DD')
            if (algorithm.attach_date && algorithm.detach_date) {
                let attach = moment(algorithm.attach_date, "YYYY-MM-DD")
                let detach = moment(algorithm.detach_date, "YYYY-MM-DD")
                let len = moment.duration(detach.diff(attach)).asDays()

                this.algorithm.detach_date = moment().add(len, 'days').format('YYYY-MM-DD')
            }

            this.algorithm.id = undefined
            this.algorithm.is_template = false;
            this.algorithm.template_id = algorithm.id;

            if (!this.empty(this.algorithm.setup)) {

                if (this.algorithm.steps && this.algorithm.steps.length != 0) {
                    this.algorithm.steps.map(step => step.conditions.map(condition => {
                        condition.criteria.forEach((block) => {
                            block.forEach(c => {
                                if (c.ask_value == true) {
                                    c.value = algorithm.setup[c.value_code]
                                }
                            })
                        })
                    }))
                }

                if (this.algorithm.common_conditions && this.algorithm.common_conditions.length != 0) {
                    this.algorithm.common_conditions.map(condition => {
                        condition.criteria.forEach((block) => {
                            block.forEach(c => {
                                if (c.ask_value == true) {
                                    c.value = algorithm.setup[c.value_code]
                                }
                            })
                        })
                    })
                }

                this.algorithm.setup = undefined
            }

            this.save()
        });

        Event.listen('home', (form) => {
            this.errors = []
            this.algorithm = undefined
            this.$forceUpdate()
        });

        Event.listen('navigate-to-create-algorithm-page', () => {
            this.algorithm = this.create_empty_algorithm()
            this.backup = JSON.stringify(this.algorithm)
        });

        Event.listen('navigate-to-edit-algorithm-page', algorithm => {
            this.algorithm = algorithm

            this.backup = JSON.stringify(algorithm)
            this.$forceUpdate()
        });

        Event.listen('remove-criteria', (i) => this.remove_criteria(i));
        Event.listen('remove-action', (i) => this.remove_action(i));
    }
}
</script>

<style scoped>
.separator {
    margin-top: 10px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    text-align: center;
}

.separator::before,
.separator::after {
    content: '';
    flex: 1;
    border-bottom: 1px dotted #aaa;
}

.separator:not(:empty)::before {
    margin-right: .25em;
}

.separator:not(:empty)::after {
    margin-left: .25em;
}
</style>
