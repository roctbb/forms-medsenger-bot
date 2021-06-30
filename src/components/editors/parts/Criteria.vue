<template>
    <div>
        <div class="form-group" v-if="criteria">
            <div class="row">
                <div class="col-md-2">
                    <select class="form-control form-control-sm" v-model="criteria.left_mode">
                        <option value="value">значение</option>
                        <option value="average" v-if="is_int()">среднее за</option>
                        <option value="sum" v-if="is_int()">сумма за</option>
                        <option value="difference" v-if="is_int()">разброс за</option>
                        <option value="time">текущая дата</option>
                        <option value="init">активация контракта</option>
                    </select>
                    <span class="text-muted"><button class="btn btn-sm btn-default" @click="remove()">Удалить</button></span>
                </div>

                <!-- not time -->

                <div class="col-md-2" v-if="criteria.left_mode != 'value' && !['time', 'init'].includes(criteria.left_mode)">
                    <input class="form-control form-control-sm"
                           v-if="criteria.left_dimension == 'hours'"
                           :class="criteria.need_validation && empty(criteria.left_hours) ? 'is-invalid' : ''"
                           v-model="criteria.left_hours">
                    <input class="form-control form-control-sm"
                           v-if="criteria.left_dimension == 'times'"
                           :class="criteria.need_validation && empty(criteria.left_times) ? 'is-invalid' : ''"
                           v-model="criteria.left_times">
                    <select class="form-control form-control-sm" v-model="criteria.left_dimension">
                        <option value="hours">часов</option>
                        <option value="times">раз</option>
                    </select>
                </div>
                <div class="col-md-3" v-if="!['time', 'init'].includes(criteria.left_mode)">
                    <select @change="category_changed()" class="form-control form-control-sm"
                            v-model="criteria.category">
                        <optgroup
                            v-for="(group, name) in group_by(category_list, 'subcategory')"
                            v-bind:label="name">
                            <option v-for="category in group" :value="category.name">{{ category.description }}
                            </option>
                        </optgroup>
                    </select>
                    <small class="text-muted">Код категории</small>
                </div>
                <div class="col-md-1" v-if="!['time', 'init'].includes(criteria.left_mode)">
                    <select class="form-control form-control-sm" v-model="criteria.sign">
                        <option value="equal">=</option>
                        <option value="contains" v-if="!is_int()">содержит</option>
                        <option value="greater" v-if="is_int()">&gt;</option>
                        <option value="less" v-if="is_int()">&lt;</option>
                        <option value="not_equal" v-if="is_int()">!=</option>
                        <option value="greater_or_equal" v-if="is_int()">&gt;=</option>
                        <option value="less_or_equal" v-if="is_int()">&lt;=</option>
                    </select>
                </div>

                <div class="col-md-2" v-if="!['time', 'init'].includes(criteria.left_mode)">
                    <select class="form-control form-control-sm" v-model="criteria.right_mode">
                        <option value="value">фиксированное значение</option>
                        <option value="category_value">значение</option>
                        <option value="average" v-if="is_int()">среднее за</option>
                        <option value="sum" v-if="is_int()">сумма за</option>
                        <option value="difference" v-if="is_int()">разброс за</option>
                    </select>
                </div>

                <div class="col-md-2" v-if="criteria.right_mode != 'value' && !['time', 'init'].includes(criteria.left_mode)">
                    <select class="form-control form-control-sm"
                            v-model="criteria.right_category">
                        <optgroup
                            v-for="(group, name) in group_by(category_list, 'subcategory')"
                            v-bind:label="name">
                            <option v-for="category in group" :value="category.name">{{ category.description }}
                            </option>
                        </optgroup>
                    </select>

                    <small class="text-muted">Код категории для сравнения</small>
                </div>

                <div class="col-md-2"
                     v-if="!['value', 'category_value'].includes(criteria.right_mode) && !['time', 'init'].includes(criteria.left_mode)">
                    <input class="form-control form-control-sm"
                           v-if="criteria.right_dimension == 'hours'"
                           :class="criteria.need_validation && empty(criteria.right_hours) ? 'is-invalid' : ''"
                           v-model="criteria.right_hours">
                    <input class="form-control form-control-sm"
                           v-if="criteria.right_dimension == 'times'"
                           :class="criteria.need_validation && empty(criteria.right_hours) ? 'is-invalid' : ''"
                           v-model="criteria.right_times">
                    <select class="form-control form-control-sm" v-model="criteria.right_dimension">
                        <option value="hours">часов</option>
                        <option value="times">раз</option>
                    </select>
                </div>
                <div class="col-md-1" v-if="!['time', 'init'].includes(criteria.left_mode)">
                    <input class="form-control form-control-sm"
                           :class="criteria.need_validation && empty(criteria.value) ? 'is-invalid' : ''"
                           v-model="criteria.value">
                    <small class="text-muted" v-if="criteria.right_mode == 'value'">значение для сравнения</small>
                    <small class="text-muted" v-else>модификатор</small>
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
                           :class="criteria.need_validation && empty(criteria.value) ? 'is-invalid' : ''"
                           v-model="criteria.value">
                </div>

                <div class="col-md-1" v-if="criteria.left_mode == 'time'">
                    +
                </div>

                <div class="col-md-1" v-if="criteria.left_mode == 'time'">
                    <input class="form-control form-control-sm"
                           :class="criteria.need_validation && empty(criteria.right_hours) ? 'is-invalid' : ''"
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

            <div v-if="is_admin && criteria.left_mode !='init' && ['value', 'category_value'].includes(criteria.right_mode)" class="row">
                <div class="col-md-4">
                    <input type="checkbox" v-model="criteria.ask_value">
                    <small class="text-muted">Запросить при подключении шаблона?</small>
                </div>
                <div class="col-md-5" v-if="criteria.ask_value">
                    <input class="form-control form-control-sm"
                           :class="criteria.need_validation && empty(criteria.value_name) ? 'is-invalid' : ''"
                           v-model="criteria.value_name">
                    <small class="text-muted">Имя поля</small>
                </div>
                <div class="col-md-3" v-if="criteria.ask_value">
                    <input class="form-control form-control-sm"
                           :class="criteria.need_validation && empty(criteria.value_code) ? 'is-invalid' : ''"
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

export default {
    name: "Criteria",
    components: {FormGroup48, Card},
    props: ['data', 'rkey', 'pkey', 'condition'],
    data() {
        return {
            mode: 'integer',
            criteria: {},
            category: undefined
        }
    },
    methods: {

        remove: function () {
            Event.fire('remove-criteria', [this.rkey, this.pkey, this.condition])
        },
        is_int: function () {
            return this.category.type != 'string'
        },
        category_changed: function () {
            this.category = this.get_category(this.criteria.category)

            if (!this.is_int()) this.criteria.left_mode = 'value';
            if (!this.is_int()) this.criteria.right_mode = 'value';

            if (!this.is_int() && !['equal', 'contains'].includes(this.criteria.sign)) this.criteria.sign = 'equal';
            if (this.is_int() && this.criteria.sign == 'contains') this.criteria.sign = 'equal';

            this.$forceUpdate()

        }

    },
    created() {
        this.mode = this.data.type;
        this.criteria = this.data;
        if (this.empty(this.criteria.left_dimension)) this.criteria.left_dimension = 'hours';
        if (this.empty(this.criteria.right_dimension)) this.criteria.right_dimension = 'hours';
        this.category = this.get_category(this.criteria.category)

    }
}
</script>

<style scoped>

</style>
