<template>
    <div class="form-group row" v-if="criteria">
        <div class="col-md-2">
            <select class="form-control" v-model="criteria.left_mode">
                <option value="value">значение</option>
                <option value="average" v-if="is_int()">среднее за</option>
                <option value="sum" v-if="is_int()">сумма за</option>
                <option value="difference" v-if="is_int()">разброс за</option>
            </select>
            <span class="text-muted"><button class="btn btn-sm btn-default" @click="remove()">Удалить</button></span>
        </div>
        <div class="col-md-1" v-if="criteria.left_mode != 'value'">
            <input class="form-control" v-model="criteria.left_days">
            <span class="text-muted">дней</span>
        </div>
        <div class="col-md-4">
            <select @change="category_changed()" class="form-control" v-model="criteria.category">
                <option
                    v-for="category in category_list"
                    :value="category.name">{{ category.description }}
                </option>
            </select>
            <span class="text-muted">Код категории</span>
        </div>
        <div class="col-md-1">
            <select class="form-control" v-model="criteria.sign">
                <option value="equal">=</option>
                <option value="contains" v-if="!is_int()">содержит</option>
                <option value="greater" v-if="is_int()">&gt;</option>
                <option value="less" v-if="is_int()">&lt;</option>
                <option value="not_equal" v-if="is_int()">!=</option>
                <option value="greater_or_equal" v-if="is_int()">&gt;=</option>
                <option value="less_or_equal" v-if="is_int()">&lt;=</option>
            </select>
        </div>

        <div class="col-md-2">
            <select class="form-control" v-model="criteria.right_mode">
                <option value="value">значение</option>
                <option value="average" v-if="is_int()">среднее за</option>
                <option value="sum" v-if="is_int()">сумма за</option>
                <option value="difference" v-if="is_int()">разброс за</option>
            </select>
        </div>
        <div class="col-md-1" v-if="criteria.right_mode != 'value'">
            <input class="form-control" v-model="criteria.right_days">
            <span class="text-muted">дней</span>
        </div>
        <div class="col-md-2" v-if="criteria.right_mode == 'value'">
            <input class="form-control" v-model="criteria.value">
        </div>
    </div>
</template>

<script>

import Card from "../../common/Card";
import FormGroup48 from "../../common/FormGroup-4-8";

export default {
    name: "Criteria",
    components: {FormGroup48, Card},
    props: ['data', 'rkey', 'pkey'],
    data() {
        return {
            mode: 'integer',
            criteria: {},
            category: undefined
        }
    },
    methods: {

        remove: function () {
            Event.fire('remove-criteria', [this.rkey, this.pkey])
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
        this.category = this.get_category(this.criteria.category)

    }
}
</script>

<style scoped>

</style>
