<template>
    <div class="form-group row" v-if="action">
        <div class="col-md-3">
            <select class="form-control form-control-sm" @change="clear_params()" v-model="mode">
                <option value="doctor_message">сообщение врачу</option>
                <option value="patient_message">сообщение пациенту</option>
                <option value="record">запись в карту</option>
                <option value="medicine">прием лекарства</option>
                <option value="form">отправка опросника</option>
                <option value="attach_form">подключение опросника</option>
                <option value="detach_form">отключение опросника</option>
                <option value="attach_algorithm">подключение алгоритма</option>
                <option value="detach_algorithm">отключение алгоритма</option>
                <option value="attach_medicine">назначение лекарства</option>
                <option value="detach_medicine">отмена лекарства</option>
                <!-- назначение/отключения мониторинга/лекарства/алгоритма / order -->
            </select>
            <small class="text-muted"><button class="btn btn-sm btn-default" @click="remove()">Удалить</button></small>
        </div>

        <div class="col-md-2" v-if="['doctor_message', 'patient_message'].includes(action.type)">
            <input type="checkbox" v-model="action.params.is_urgent">
            <small class="text-muted">Срочное?</small>
        </div>

        <div class="col-md-2" v-if="action.type == 'doctor_message'">
            <input type="checkbox" v-model="action.params.need_answer">
            <small class="text-muted">Нужен ответ?</small>
        </div>

        <div class="col-md-5" v-if="['doctor_message', 'patient_message'].includes(action.type)">
            <textarea class="form-control form-control-sm" v-model="action.params.text"></textarea>
            <small class="text-muted">Текст сообщения</small>
        </div>

        <div class="col-md-4" v-if="action.type == 'record'">
            <select class="form-control form-control-sm" v-model="action.params.category">
                <option
                    v-for="category in category_list"
                    :value="category.name">{{ category.description }}
                </option>
            </select>
            <small class="text-muted">Код категории</small>
        </div>

        <div class="col-md-3" v-if="action.type == 'record'">
            <input type="text" class="form-control form-control-sm" v-model="action.params.value">
            <small class="text-muted">Значение</small>
        </div>
        <div class="col-md-4" v-if="action.type == 'medicine'">
            <textarea class="form-control form-control-sm" v-model="action.params.medicine_rules"></textarea>
            <small class="text-muted">Комментарий, доза, количество</small>
        </div>

        <div class="col-md-3" v-if="action.type == 'medicine'">
            <input type="text" class="form-control form-control-sm" v-model="action.params.medicine_name">
            <small class="text-muted">Название препарата</small>
        </div>

        <div class="col-md-3" v-if="['form', 'attach_form', 'detach_form', 'attach_algorithm', 'detach_algorithm', 'attach_medicine', 'detach_medicine'].includes(action.type)">
            <input type="text" class="form-control form-control-sm" v-model="action.params.template_id">
            <small class="text-muted">ID шаблона</small>
        </div>

        <div class="col-md-12" v-if="['doctor_message', 'patient_message'].includes(action.type)">
            <input type="checkbox" v-model="action.params.send_report">
            <small class="text-muted">Приложить показатели?</small>
        </div>

        <div class="col-md-12" v-if="['doctor_message', 'patient_message'].includes(action.type)">
            <input type="checkbox" v-model="action.params.add_action">
            <small class="text-muted">Приложить действие?</small>

            <div class="row" v-if="action.params.add_action">
                <div class="col-md-4">
                    <input type="text" class="form-control form-control-sm" v-model="action.params.action_link">
                    <small class="text-muted">Имя действия</small>
                </div>

                <div class="col-md-4">
                    <input type="text" class="form-control form-control-sm" v-model="action.params.action_name">
                    <small class="text-muted">Текст для кнопки</small>
                </div>
            </div>
        </div>


        <div class="col-md-12">
            <input type="checkbox" v-model="action.params.is_negative">
            <small class="text-muted">Выполнить если критерии не выполняются.</small>
        </div>

    </div>
</template>

<script>

import Card from "../../common/Card";
import FormGroup48 from "../../common/FormGroup-4-8";

export default {
    name: "Action",
    components: {FormGroup48, Card},
    props: ['data', 'pkey'],
    data() {
        return {
            action: {},
            backup: {},
            mode: 'patient_message'
        }
    },
    methods: {

        remove: function () {
            Event.fire('remove-action', this.pkey)
        },
        clear_params: function () {
            this.backup[this.action.type] = JSON.stringify(this.action.params)
            this.action.type = this.mode
            if (this.backup[this.mode]) {
                this.action.params = JSON.parse(this.backup[this.mode])
            } else {
                this.action.params = {};
            }

        },
    },
    created() {
        this.action = this.data;
        if (this.data.type)
        {
            this.mode = this.action.type
        }
    }
}
</script>

<style scoped>

</style>
