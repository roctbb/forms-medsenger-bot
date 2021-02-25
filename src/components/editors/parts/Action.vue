<template>
    <div class="form-group row" v-if="action">
        <div class="col-md-3">
            <select class="form-control" @change="clear_params()" v-model="mode">
                <option value="doctor_message">сообщение врачу</option>
                <option value="patient_message">сообщение пациенту</option>
                <option value="record">запись в карту</option>
                <!-- назначение/отключения мониторинга/лекарства/алгоритма / order -->
            </select>
            <span class="text-muted"><button class="btn btn-sm btn-default" @click="remove()">Удалить</button></span>
        </div>

        <div class="col-md-2" v-if="['doctor_message', 'patient_message'].includes(action.type)">
            <input type="checkbox" v-model="action.params.is_urgent">
            <span class="text-muted">Срочное?</span>
        </div>

        <div class="col-md-2" v-if="action.type == 'doctor_message'">
            <input type="checkbox" v-model="action.params.need_answer">
            <span class="text-muted">Нужен ответ?</span>
        </div>

        <div class="col-md-5" v-if="['doctor_message', 'patient_message'].includes(action.type)">
            <textarea class="form-control" v-model="action.params.text"></textarea>
            <span class="text-muted">Текст сообщения</span>
        </div>

        <div class="col-md-4" v-if="action.type == 'record'">
            <select class="form-control" v-model="action.params.category">
                <option
                    v-for="category in category_list"
                    :value="category.name">{{ category.description }}
                </option>
            </select>
            <span class="text-muted">Код категории</span>
        </div>

        <div class="col-md-3" v-if="action.type == 'record'">
            <input type="text" class="form-control" v-model="action.params.value">
            <span class="text-muted">Значение</span>
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
    }
}
</script>

<style scoped>

</style>
