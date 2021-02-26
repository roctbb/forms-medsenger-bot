<template>
    <div v-if="algorithm">
        <a class="btn btn-danger btn-sm" @click="go_back()">назад</a>
        <error-block :errors="errors"/>
        <div class="form">
            <card title="Описание алгоритма">
                <form-group48 title="Название">
                    <input class="form-control" v-model="algorithm.title"/>
                </form-group48>

                <form-group48 title="Описание">
                    <textarea class="form-control" v-model="algorithm.description"></textarea>
                </form-group48>
            </card>

            <card title="Критерий срабатывания">
                <div v-for="(or_block, i) in algorithm.criteria">
                    <div v-for="(criteria, j) in or_block">
                        <criteria :data="criteria" :rkey="i" :pkey="j" :key="criteria.uid"/>
                    </div>
                    <button class="btn btn-sm btn-primary" @click="add_criteria(or_block)">и</button>
                    <hr>
                </div>
                <button class="btn btn-sm btn-primary" @click="add_or_block()">или</button>
            </card>

            <card title="Действия">
                <action v-for="(action, i) in algorithm.actions" :data="action" :pkey="i" :key="action.uid"></action>
                <button class="btn btn-sm btn-primary" @click="add_action()">Добавить</button>
            </card>

        </div>

        <button class="btn btn-success btn-lg" @click="save()">Сохранить <span v-if="algorithm.is_template"> шаблон</span></button>
        <button class="btn btn-primary btn-lg" v-if="!algorithm.id" @click="save(true)">Сохранить как шаблон</button>
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
            let old = JSON.parse(this.backup)
            this.copy(this.algorithm, old)
            Event.fire('back-to-dashboard');
            this.algorithm = undefined
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
                if (!this.ne(criteria.left_days)) criteria.left_days = parseInt(criteria.left_days)

                if (!this.ne(criteria.right_days)) criteria.right_days = parseInt(criteria.right_days)


                if (!this.ne(criteria.value)) {
                    let category = this.get_category(criteria.category)
                    if (category.type == 'integer') criteria.value = parseInt(criteria.value)
                    if (category.type == 'float') criteria.value = parseFloat(criteria.value)
                }

                return criteria
            }

            let criteria_validator = (criteria) => {
                let category = this.get_category(criteria.category)
                if (criteria.left_mode != 'value' && this.ne(criteria.left_days)) return true;
                if (criteria.right_mode != 'value' && this.ne(criteria.right_days)) return true;

                if (criteria.right_mode == 'value' && this.ne(criteria.value)) return true;
                return false;
            }

            this.algorithm.criteria = this.algorithm.criteria.map((L) => L.map(prepare_criteria))

            if (!this.algorithm.criteria.length)
            {
                this.errors.push('Добавьте хотя бы одно условие.')
            }

            console.log(this.algorithm.criteria.filter((L) => L.filter(criteria_validator)))
            if (this.algorithm.criteria.filter((L) => L.filter(criteria_validator).length > 0).length)
            {
                this.errors.push('Проверьте правильность условий.')
            }

            let prepare_action = (action) =>
            {
                if (action.type == 'record')
                {
                    let category = this.get_category(action.params.category)

                    if (category.type == 'integer') action.params.value = parseInt(action.params.value)
                    if (category.type == 'float') action.params.value = parseFloat(action.params.value)
                }
                return action;
            }

            let action_validator = (action) => {
                if (action.type == 'record' && this.ne(action.params.value)) return true;
                if ((action.type == 'patient_message' || action.type == 'doctor_message') && this.ne(action.params.text)) return true;
                return false;
            }

            this.algorithm.actions = this.algorithm.actions.map(prepare_action)

            if (!this.algorithm.actions.length)
            {
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

                if (is_template || this.algorithm.is_template)
                {
                    this.algorithm.contract_id = undefined
                    this.algorithm.is_template = true;
                }

                this.axios.post(this.url('/api/settings/algorithm'), this.algorithm).then(this.process_save_answer).catch(this.process_save_error);
            }
        },
        process_save_answer: function (response) {
            let is_new = this.ne(this.algorithm.id)

            this.algorithm.id = response.data.id
            if (!this.algorithm.is_template)
            {
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
            this.save()
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

</style>
