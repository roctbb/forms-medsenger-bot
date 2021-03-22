<template>
    <div v-if="algorithm">
        <error-block :errors="errors"/>
        <div class="form">
            <card title="Описание алгоритма">
                <form-group48 title="Название">
                    <input class="form-control form-control-sm" v-model="algorithm.title"/>
                </form-group48>

                <form-group48 title="Описание">
                    <textarea class="form-control form-control-sm" v-model="algorithm.description"></textarea>
                </form-group48>

                <form-group48 v-if="is_admin && (empty(algorithm.id) || algorithm.is_template)" title="Категория шаблона">
                    <input class="form-control form-control-sm" value="Общее" v-model="algorithm.template_category"/>
                </form-group48>
            </card>

            <card title="Критерий срабатывания">
                <div v-for="(or_block, i) in algorithm.criteria">
                    <div v-for="(criteria, j) in or_block">
                        <criteria :data="criteria" :rkey="i" :pkey="j" :key="criteria.uid"/>
                    </div>
                    <button class="btn btn-sm btn-primary" @click="add_criteria(or_block)">и</button>
                    <div class="separator">или</div>
                </div>
                <button class="btn btn-sm btn-primary" @click="add_or_block()">или</button>
            </card>

            <card title="Действия">
                <action v-for="(action, i) in algorithm.actions" :data="action" :pkey="i" :key="action.uid"></action>
                <button class="btn btn-sm btn-primary" @click="add_action()">Добавить</button>
            </card>

        </div>
        <button class="btn btn-danger" @click="go_back()">Назад</button>
        <button class="btn btn-success" @click="save()">Сохранить <span v-if="algorithm.is_template"> шаблон</span>
        </button>
        <button class="btn btn-primary" v-if="!algorithm.id && is_admin" @click="save(true)">Сохранить как шаблон
        </button>
    </div>
</template>

<script>

import Card from "../common/Card";
import FormGroup48 from "../common/FormGroup-4-8";
import ErrorBlock from "../common/ErrorBlock";
import Criteria from "./parts/Criteria";
import Action from "./parts/Action";

export default {
    name: "AlgorithmEditor",
    components: {Action, FormGroup48, Card, ErrorBlock, Criteria},
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
                criteria: [],
                actions: []
            };
        },
        add_or_block: function () {
            this.algorithm.criteria.push([this.create_empty_criteria()])
        },
        add_criteria: function (block) {
            block.push(this.create_empty_criteria())
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
        add_action: function () {
            this.algorithm.actions.push(this.create_empty_action())
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
                if (!this.empty(criteria.left_days)) criteria.left_days = parseInt(criteria.left_days)

                if (!this.empty(criteria.right_hours)) criteria.right_hours = parseInt(criteria.right_hours)


                if (!this.empty(criteria.value)) {
                    let category = this.get_category(criteria.category)
                    if (category.type == 'integer') criteria.value = parseInt(criteria.value)
                    if (category.type == 'float') criteria.value = parseFloat(criteria.value)
                }

                return criteria
            }

            let criteria_validator = (criteria) => {
                let category = this.get_category(criteria.category)
                if (criteria.left_mode != 'value' && this.empty(criteria.left_days)) return true;
                if (criteria.right_mode != 'value' && this.empty(criteria.right_hours)) return true;

                if (criteria.right_mode == 'value' && this.empty(criteria.value)) return true;
                return false;
            }

            this.algorithm.criteria = this.algorithm.criteria.map((L) => L.map(prepare_criteria))

            if (!this.algorithm.criteria.length) {
                this.errors.push('Добавьте хотя бы одно условие.')
            }

            console.log(this.algorithm.criteria.filter((L) => L.filter(criteria_validator)))
            if (this.algorithm.criteria.filter((L) => L.filter(criteria_validator).length > 0).length) {
                this.errors.push('Проверьте правильность условий.')
            }

            let prepare_action = (action) => {
                if (action.type == 'record') {
                    let category = this.get_category(action.params.category)

                    if (category.type == 'integer') action.params.value = parseInt(action.params.value)
                    if (category.type == 'float') action.params.value = parseFloat(action.params.value)
                }
                return action;
            }

            let action_validator = (action) => {
                if (action.type == 'record' && this.empty(action.params.value)) return true;
                if ((action.type == 'patient_message' || action.type == 'doctor_message') && this.empty(action.params.text)) return true;
                return false;
            }

            this.algorithm.actions = this.algorithm.actions.map(prepare_action)

            if (!this.algorithm.actions.length) {
                this.errors.push('Добавьте хотя бы одно действие.')
            }

            if (this.algorithm.actions.filter(action_validator).length) {
                this.errors.push('Проверьте правильность действий.')
            }

            if (this.errors.length != 0) {
                return false;
            } else {
                return true;
            }
        },
        save: function (is_template) {
            if (this.check()) {
                this.algorithm.categories = this.algorithm.criteria.map(block => block.map(c => c.category).join('|')).join('|')
                this.errors = []

                if (is_template || this.algorithm.is_template) {
                    this.algorithm.contract_id = undefined
                    this.algorithm.is_template = true;
                }

                this.axios.post(this.url('/api/settings/algorithm'), this.algorithm).then(this.process_save_answer).catch(this.process_save_error);
            }
        },
        process_save_answer: function (response) {
            let is_new = this.empty(this.algorithm.id)

            this.algorithm.id = response.data.id
            if (!this.algorithm.is_template) {
                this.algorithm.patient_id = response.data.patient_id
                this.algorithm.contract_id = response.data.contract_id
            }

            if (is_new) Event.fire('algorithm-created', this.algorithm)
            else Event.fire('back-to-dashboard', this.algorithm)

            this.algorithm = undefined
        },
        process_save_error: function (response) {
            this.errors.push('Ошибка сохранения');
        },
        remove_action: function (index) {
            this.algorithm.actions.splice(index, 1);
        },
        remove_criteria: function (index) {
            this.algorithm.criteria[index[0]].splice(index[1], 1);

            if (!this.algorithm.criteria[index[0]].length) {
                this.algorithm.criteria.splice(index[0], 1);
            }
        }
    },
    data() {
        return {
            errors: [],
            algorithm: undefined,
            backup: ""
        }
    },
    mounted() {
        Event.listen('attach-algorithm', (algorithm) => {
            this.algorithm = {}
            this.copy(this.algorithm, algorithm)
            this.algorithm.id = undefined
            this.algorithm.is_template = false;
            this.algorithm.template_id = algorithm.id;

            if (!this.empty(this.algorithm.setup))
            {
                this.algorithm.criteria.forEach((block) => {
                    block.forEach(c => {
                        if (c.ask_value == true)
                        {
                            c.value = algorithm.setup[c.uid]
                        }
                    })
                })

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
