<template>
    <div>
        <div class="form-group" v-if="criteria">
            <div class="row">
                <div class="col-md-2">
                    <select class="form-control form-control-sm" v-model="criteria.left_mode">
                        <option value="value">текущее значение</option>
                        <option value="category_value">последнее значение</option>
                        <option value="count" v-if="is_int() && !is_date()">количество за</option>
                        <option value="average" v-if="is_int() && !is_date()">среднее за</option>
                        <option value="sum" v-if="is_int() && !is_date()">сумма за</option>
                        <option value="difference" v-if="is_int() && !is_date()">разброс за</option>
                        <option value="time">текущая дата</option>
                        <option value="init">активация контракта</option>
                        <option value="step_init">переход к ступени</option>
                    </select>
                    <span class="text-muted"><button class="btn btn-sm btn-default"
                                                     @click="remove()">Удалить</button></span>
                </div>

                <!-- not time -->
                <div class="col-md-1"
                     v-if="!['value', 'category_value'].includes(criteria.left_mode) && !['time', 'init', 'step_init'].includes(criteria.left_mode)">
                    <input class="form-control form-control-sm"
                           type="number" min="0"
                           v-if="criteria.left_dimension == 'hours'"
                           :class="this.save_clicked && empty(criteria.left_hours) ? 'is-invalid' : ''"
                           v-model="criteria.left_hours">
                    <input class="form-control form-control-sm"
                           type="number" min="0"
                           v-else-if="criteria.left_dimension == 'times'"
                           :class="this.save_clicked && empty(criteria.left_times) ? 'is-invalid' : ''"
                           v-model="criteria.left_times">
                    <input class="form-control form-control-sm"
                           type="number" min="0"
                           :class="this.save_clicked && empty(criteria.left_for) ? 'is-invalid' : ''"
                           v-model="criteria.left_for" v-else>
                    <select class="form-control form-control-sm" v-model="criteria.left_dimension">
                        <option value="days">дней</option>
                        <option value="hours">часов</option>
                        <option value="times">раз</option>
                    </select>
                    <small class="text-muted">с отступом</small>
                    <input class="form-control form-control-sm"
                           type="number" min="0"
                           :class="this.save_clicked && empty(criteria.left_offset) ? 'is-invalid' : ''"
                           v-model="criteria.left_offset">
                    <select class="form-control form-control-sm" v-model="criteria.left_offset_dimension">
                        <option value="days">дней</option>
                        <option value="hours">часов</option>
                        <option value="times">раз</option>
                    </select>
                </div>
                <div class="col-md-1" v-if="criteria.left_mode == 'count'">
                    <select class="form-control form-control-sm" v-model="criteria.left_sign">
                        <option value="equal" v-if="!is_date()">=</option>
                        <option value="contains" v-if="!is_int() && !is_date()">содержит</option>
                        <option value="greater" v-if="is_int()">&gt;</option>
                        <option value="less" v-if="is_int()">&lt;</option>
                        <option value="not_equal" v-if="is_int()">!=</option>
                        <option value="greater_or_equal" v-if="is_int()">&gt;=</option>
                        <option value="less_or_equal" v-if="is_int()">&lt;=</option>
                    </select>
                </div>
                <div class="col-md-1" v-if="criteria.left_mode == 'count'">
                    <input class="form-control form-control-sm"
                           :class="this.save_clicked && empty(criteria.check_value) ? 'is-invalid' : ''"
                           v-model="criteria.check_value">
                    <small data-v-554d70e7="" class="text-muted">значение</small>
                </div>


                <div class="col-md-3" v-if="!['time', 'init', 'step_init'].includes(criteria.left_mode)">
                    <select @change="category_changed()" class="form-control form-control-sm"
                            v-model="criteria.category">
                        <optgroup label="Авто">
                            <option value="exact_date">Текущая дата</option>
                            <option value="contract_start_date">Дата начала консультирования</option>
                            <option value="contract_end_date">Дата завершения консультирования</option>
                            <option value="algorithm_attach_date">Дата отсчета алгоритма</option>
                            <option value="algorithm_detach_date">Дата завершения алгоритма</option>
                        </optgroup>
                        <optgroup
                            v-for="(group, name) in group_by(category_list, 'subcategory')"
                            v-bind:label="name">
                            <option v-for="category in group" :value="category.name">{{ category.description }}
                            </option>
                        </optgroup>
                    </select>
                    <small class="text-muted">Код категории</small>
                </div>
                <div class="col-md-1" v-if="!['time', 'init', 'step_init'].includes(criteria.left_mode)">
                    <select class="form-control form-control-sm" v-model="criteria.sign">
                        <option value="equal" v-if="!is_date()">=</option>
                        <option value="contains" v-if="!is_int() && !is_date()">содержит</option>
                        <option value="greater" v-if="is_int()">&gt;</option>
                        <option value="less" v-if="is_int()">&lt;</option>
                        <option value="not_equal" v-if="is_int()">!=</option>
                        <option value="greater_or_equal" v-if="is_int()">&gt;=</option>
                        <option value="less_or_equal" v-if="is_int()">&lt;=</option>

                        <option value="date_equal" v-if="is_date()">=</option>
                        <option value="date_greater" v-if="is_date()">&gt;</option>
                        <option value="date_less" v-if="is_date()">&lt;</option>
                        <option value="date_not_equal" v-if="is_date()">!=</option>
                        <option value="date_greater_or_equal" v-if="is_date()">&gt;=</option>
                        <option value="date_less_or_equal" v-if="is_date()">&lt;=</option>
                    </select>
                </div>

                <div class="col-md-2" v-if="!['time', 'init', 'step_init'].includes(criteria.left_mode)">
                    <select class="form-control form-control-sm" v-model="criteria.right_mode">
                        <option value="value">фиксированное значение</option>
                        <option value="category_value">значение</option>
                        <option value="count" v-if="is_int() && !is_date()">количество за</option>
                        <option value="average" v-if="is_int()">среднее за</option>
                        <option value="sum" v-if="is_int()">сумма за</option>
                        <option value="difference" v-if="is_int()">разброс за</option>
                    </select>
                </div>

                <div class="col-md-2"
                     v-if="criteria.right_mode != 'value' && !['time', 'init', 'step_init'].includes(criteria.left_mode)">
                    <select class="form-control form-control-sm"
                            v-model="criteria.right_category">
                        <optgroup label="Авто">
                            <option value="exact_date">Текущая дата</option>
                            <option value="contract_start_date">Дата начала консультирования</option>
                            <option value="contract_end_date">Дата завершения консультирования</option>
                            <option value="algorithm_attach_date">Дата отсчета алгоритма</option>
                            <option value="algorithm_detach_date">Дата завершения алгоритма</option>
                        </optgroup>
                        <optgroup
                            v-for="(group, name) in group_by(category_list, 'subcategory')"
                            v-bind:label="name">
                            <option v-for="cat in group"
                                    v-if="category.type != 'date' && cat.type != 'date' || category.type == cat.type"
                                    :value="cat.name">{{ cat.description }}
                            </option>
                        </optgroup>
                    </select>

                    <small class="text-muted">Код категории для сравнения</small>
                </div>

                <div class="col-md-2"
                     v-if="!['value', 'category_value'].includes(criteria.right_mode) && !['time', 'init', 'step_init'].includes(criteria.left_mode)">
                    <input class="form-control form-control-sm"
                           v-if="criteria.right_dimension == 'hours'"
                           :class="this.save_clicked && empty(criteria.right_hours) ? 'is-invalid' : ''"
                           v-model="criteria.right_hours">
                    <input class="form-control form-control-sm"
                           v-if="criteria.right_dimension == 'times'"
                           :class="this.save_clicked && empty(criteria.right_times) ? 'is-invalid' : ''"
                           v-model="criteria.right_times">
                    <select class="form-control form-control-sm" v-model="criteria.right_dimension">
                        <option value="hours">часов</option>
                        <option value="times">раз</option>
                    </select>
                    <small class="text-muted">с отступом</small>
                    <input class="form-control form-control-sm"
                           :class="this.save_clicked && empty(criteria.right_offset) ? 'is-invalid' : ''"
                           v-model="criteria.right_offset">
                    <select class="form-control form-control-sm" v-model="criteria.right_offset_dimension">
                        <option value="days">дней</option>
                        <option value="hours">часов</option>
                        <option value="times">раз</option>
                    </select>
                </div>
                <div class="col-md-1" v-if="!['time', 'init', 'step_init'].includes(criteria.left_mode)">

                    <input v-if="category.type != 'date' || criteria.right_mode != 'value'"
                           class="form-control form-control-sm"
                           :class="this.save_clicked && empty(criteria.value) ? 'is-invalid' : ''"
                           v-model="criteria.value">
                    <date-picker v-else v-model="criteria.value" value-type="YYYY-MM-DD"></date-picker>
                    <small class="text-muted" v-if="criteria.right_mode == 'value'">значение для сравнения</small>
                    <small class="text-muted" v-else>модификатор</small>
                </div>
                <div class="col-md-1"
                     v-if="!['time', 'init', 'step_init'].includes(criteria.left_mode) && criteria.right_mode != 'value'">

                    <input class="form-control form-control-sm"
                           :class="this.save_clicked && empty(criteria.multiplier) ? 'is-invalid' : ''"
                           v-model="criteria.multiplier">
                    <small class="text-muted">мультипликатор</small>
                </div>

                <!-- time -->

                <div class="col-md-1" v-if="criteria.left_mode == 'time'">
                    <select class="form-control form-control-sm" v-model="criteria.sign">
                        <option value="equal">=</option>
                        <option value="greater">&gt;</option>
                        <option value="less">&lt;</option>
                    </select>
                </div>

                <div class="col-md-2" v-if="criteria.left_mode == 'time'">
                    <input class="form-control form-control-sm"
                           :class="this.save_clicked && empty(criteria.value) ? 'is-invalid' : ''"
                           v-model="criteria.value">
                </div>

                <div class="col-md-1" v-if="criteria.left_mode == 'time'">
                    +
                </div>

                <div class="col-md-1" v-if="criteria.left_mode == 'time'">
                    <input class="form-control form-control-sm"
                           :class="this.save_clicked && empty(criteria.right_hours) ? 'is-invalid' : ''"
                           v-model="criteria.right_hours">
                    <small class="text-muted">часов</small>
                </div>
            </div>

            <div v-if="is_admin" class="row">
                <div class="col-md-12">
                    <input type="checkbox" v-model="criteria.hide_in_description">
                    <small class="text-muted">Не выводить в показателях?</small>
                </div>
            </div>

            <div
                v-if="is_admin && criteria.left_mode !='init' && ['value', 'category_value'].includes(criteria.right_mode)"
                class="row">
                <div class="col-md-4">
                    <input type="checkbox" v-model="criteria.ask_value">
                    <small class="text-muted">Запросить при подключении шаблона?</small>
                </div>
                <div class="col-md-5" v-if="criteria.ask_value">
                    <input class="form-control form-control-sm"
                           :class="this.save_clicked && empty(criteria.value_name) ? 'is-invalid' : ''"
                           v-model="criteria.value_name">
                    <small class="text-muted">Имя поля</small>
                </div>
                <div class="col-md-3" v-if="criteria.ask_value">
                    <input class="form-control form-control-sm"
                           :class="this.save_clicked && empty(criteria.value_code) ? 'is-invalid' : ''"
                           v-model="criteria.value_code">
                    <small class="text-muted">Код (для сценариев)</small>
                </div>
            </div>
        </div>
    </div>
</template>


<script>

import Card from "../../common/Card";
import FormGroup48 from "../../common/FormGroup-4-8";
import DatePicker from 'vue2-datepicker';
import 'vue2-datepicker/index.css';
import 'vue2-datepicker/locale/ru';

export default {
    name: "Criteria",
    components: {FormGroup48, Card, DatePicker},
    props: ['data', 'rkey', 'pkey', 'save_clicked', 'condition'],
    data() {
        return {
            criteria: {},
            category: undefined
        }
    },
    methods: {
        remove: function () {
            Event.fire('remove-criteria', [this.rkey, this.pkey, this.condition])
        },
        is_date: function () {
            return this.category.type == 'date'
        },
        is_int: function () {
            return this.category.type != 'string' && this.category.type != 'date'
        },
        category_changed: function () {
            if (this.criteria.category == 'exact_date') {
                this.category = {
                    type: "date",
                    description: "Текущая дата"
                }
            } else {
                this.category = this.get_category(this.criteria.category)
            }

            if (!this.is_int()) this.criteria.left_mode = 'value';
            if (!this.is_int()) this.criteria.right_mode = 'value';

            if (!this.is_int() && !['equal', 'contains'].includes(this.criteria.sign)) this.criteria.sign = 'equal';
            if (this.is_int() && this.criteria.sign == 'contains') this.criteria.sign = 'equal';

            this.$forceUpdate()

        }

    },
    created() {
        this.criteria = this.data;
        if (this.empty(this.criteria.left_dimension)) this.criteria.left_dimension = 'hours';
        if (this.empty(this.criteria.right_dimension)) this.criteria.right_dimension = 'hours';
        if (this.empty(this.criteria.left_offset_dimension)) {
            this.criteria.left_offset_dimension = 'hours';
            this.criteria.left_offset = 0
        }
        if (this.empty(this.criteria.right_offset_dimension)) {
            this.criteria.right_offset_dimension = 'hours';
            this.criteria.right_offset = 0
        }
        if (this.empty(this.criteria.multiplier))
            this.criteria.multiplier = '1'
        this.category = this.get_category(this.criteria.category)

    },
    mounted() {
        this.category = this.get_category(this.criteria.category)
    }
}
</script>

<style scoped>

</style>
