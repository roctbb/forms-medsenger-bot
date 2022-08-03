<template>
    <div v-if="integral_evaluation">
        <card title="Интегральная оценка">
            <form-group48 title="Оценивать с помощью скрипта">
                <input type="checkbox" class="form-check" v-model="integral_evaluation.script_enabled" @change="$forceUpdate()">
            </form-group48>

            <div v-if="integral_evaluation.script_enabled">
                <form-group48 title="Код">
                    <textarea class="form-control form-control-sm" v-model="integral_evaluation.script"></textarea>
                </form-group48>
            </div>
            <div v-else>
                <form-group48 title="Код категории">
                    <select class="form-control form-control-sm"
                            :class="save_clicked && empty(integral_evaluation.category) ? 'is-invalid' : ''"
                            v-model="integral_evaluation.category">
                        <option value="none">Не сохранять ответ</option>

                        <optgroup
                            v-for="(group, name) in group_by(category_list.filter(c => ['float', 'integer'].includes(c.type)), 'subcategory')"
                            v-bind:label="name">
                            <option v-for="category in group" :value="category.name">{{ category.description }}
                            </option>
                        </optgroup>
                    </select>
                </form-group48>

                <form-group48 title="Сдвиг">
                    <input type="number" class="form-control form-control-sm"
                           :class="save_clicked && empty(integral_evaluation.offset) ? 'is-invalid' : ''"
                           v-model="integral_evaluation.offset"/>
                </form-group48>

                <form-group48 title="Не отправлять результат врачу">
                    <input type="checkbox" class="form-check" v-model="integral_evaluation.dont_send_to_doctor">
                </form-group48>

                <form-group48 title="Группы вопросов">
                    <input type="checkbox" class="form-check" v-model="integral_evaluation.groups_enabled"
                           @change="enable_groups()">
                </form-group48>

                <div v-if="integral_evaluation.groups_enabled">
                    <div v-for="(group, i) in integral_evaluation.groups">
                        <div class="row">
                            <div class="col-md-4">
                                <small class="text-mutted">Название группы</small><br>
                                <input type="text"
                                       :class="save_clicked && empty(group.description) ? 'is-invalid' : ''"
                                       class="form-control form-control-sm" v-model="group.description"/>
                            </div>

                            <div class="col-md-3">
                                <small class="text-mutted">Категория</small><br>
                                <select class="form-control form-control-sm"
                                        v-model="group.category">
                                    <option value="none">Не сохранять ответ</option>

                                    <optgroup
                                        v-for="(group, name) in group_by(category_list.filter(c => ['float', 'integer'].includes(c.type)), 'subcategory')"
                                        v-bind:label="name">
                                        <option v-for="category in group" :value="category.name">{{
                                                category.description
                                            }}
                                        </option>
                                    </optgroup>
                                </select>
                            </div>

                            <div class="col-md-3">
                                <small class="text-mutted">Номера вопросов</small><br>
                                <input type="text"
                                       :class="save_clicked && empty(group.questions) ? 'is-invalid' : ''"
                                       class="form-control form-control-sm" v-model="group.questions"/>
                            </div>

                            <div class="col-md-1">
                                <small class="text-mutted">Значение</small><br>
                                <input type="number" class="form-control form-control-sm"
                                       :class="save_clicked && empty(group.value) ? 'is-invalid' : ''"
                                       v-model="group.value"/>
                            </div>
                            <div class="col-md-1"><br>
                                <a class="btn btn-default btn-sm" v-if="integral_evaluation.groups.length > 1"
                                   @click="remove_group(i)">Удалить</a>
                            </div>

                        </div>
                    </div>
                    <br>
                    <a class="btn btn-primary btn-sm" @click="add_group()">Добавить</a>
                    <br>
                </div>

                <h6>Результаты</h6>

                <div v-for="(result, i) in integral_evaluation.results">
                    <div class="row">
                        <div class="col-md-2">
                            <small class="text-mutted">Критичность</small><br>
                            <input type="checkbox" class="form-check" v-model="result.urgent"/>
                        </div>
                        <div class="col-md-2">
                            <small class="text-mutted">Значение</small><br>
                            <input type="number" class="form-control form-control-sm"
                                   :class="save_clicked && empty(result.value) ? 'is-invalid' : ''"
                                   v-model="result.value"/>
                        </div>
                        <div class="col-md-3">
                            <small class="text-mutted">Описание результата, если сумма выше значения</small><br>
                            <input type="text"
                                   :class="save_clicked && empty(result.description) ? 'is-invalid' : ''"
                                   class="form-control form-control-sm" v-model="result.description"/>
                        </div>

                        <div class="col-md-3">
                            <small class="text-mutted">Сообщение для пациента</small><br>
                            <input type="text" class="form-control form-control-sm" v-model="result.message"/>
                        </div>

                        <div class="col-md-2"><br>
                            <a class="btn btn-default btn-sm" v-if="integral_evaluation.results.length > 1"
                               @click="remove_result(i)">Удалить</a>
                        </div>
                    </div>
                </div>
                <br>
                <a class="btn btn-primary btn-sm" @click="add_result()">Добавить</a>
                <br>
                <form-group48 title="Сообщение пациенту, если результат критичен"
                              :description="'Будет отправлено, у результата стоит галочка' + integral_evaluation.groups_enabled ? ' или сумма в группе превышает ее значение' : ''">
                    <textarea class="form-control form-control-sm"
                              v-model="integral_evaluation.warning_text"></textarea>
                </form-group48>
                <form-group48 title="Сообщение пациенту, если все в порядке">
                    <textarea class="form-control form-control-sm"
                              v-model="integral_evaluation.ok_text"></textarea>
                </form-group48>
            </div>
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
            this.integral_evaluation.results.push({value: 0, description: "", message: "", urgent: false})
            this.$forceUpdate()
        },
        remove_result: function (i) {
            this.integral_evaluation.results.splice(i, 1);
            this.$forceUpdate()
        },
        add_group: function () {
            this.integral_evaluation.groups.push({value: 0, description: "", questions: [], category: 'none'})
            this.$forceUpdate()
        },
        remove_group: function (i) {
            this.integral_evaluation.groups.splice(i, 1);
            this.$forceUpdate()
        },
        enable_groups: function () {
            if (!this.integral_evaluation.groups) {
                this.integral_evaluation.groups = []
                this.add_group()
            }
        }
    },
    data() {
        return {
            integral_evaluation: {},
            backup: {}
        }
    },
    mounted() {
        this.integral_evaluation = this.data
    }
}
</script>

<style scoped>

</style>
