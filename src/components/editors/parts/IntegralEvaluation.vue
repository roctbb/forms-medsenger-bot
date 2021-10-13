<template>
    <div v-if="integral_evaluation">
        <card title="Интегральная оценка">
            <form-group48 title="Сдвиг">
                <input class="form-control form-control-sm"
                       :class="save_clicked && empty(integral_evaluation.offset) ? 'is-invalid' : ''"
                       v-model="integral_evaluation.offset"/>
            </form-group48>
            <h6>Результаты</h6>
            <div v-for="(result, i) in integral_evaluation.results">
                <div class="row">
                    <div class="col-md-2">
                        <small class="text-mutted">Значение</small><br>
                        <input type="number" class="form-control form-control-sm"
                               :class="save_clicked && empty(result.value) ? 'is-invalid' : ''"
                               v-model="result.value"/>
                    </div>
                    <div class="col-md-7">
                        <small class="text-mutted">Описание результата, если сумма выше значения</small><br>
                        <input type="text"
                               :class="save_clicked && empty(result.description) ? 'is-invalid' : ''"
                               class="form-control form-control-sm" v-model="result.description"/>
                    </div>

                    <div class="col-md-2"><br>
                        <a class="btn btn-default btn-sm" v-if="integral_evaluation.results.length > 1"
                           @click="remove_result(i)">Удалить</a>
                    </div>
                </div>
            </div>
            <br>
            <a class="btn btn-primary btn-sm" @click="add_result()">Добавить</a>
        </card>
    </div>
</template>

<script>
import Card from "../../common/Card";
import FormGroup48 from "../../common/FormGroup-4-8";

export default {
    name: "IntegralEvaluation",
    components: {FormGroup48, Card},
    props: ['data', 'save_clicked'],
    methods: {
        add_result: function () {
            this.integral_evaluation.results.push({value: 0, description: ""})
            this.$forceUpdate()
        },
        remove_result: function (i) {
            this.integral_evaluation.results.splice(i, 1);
            this.$forceUpdate()
        },
    },
    data() {
        return {
            mode: 'integer',
            integral_evaluation: {},
            backup: {}
        }
    },
    mounted() {
        this.integral_evaluation = this.data
        console.log('data', this.data)
    }
}
</script>

<style scoped>

</style>
