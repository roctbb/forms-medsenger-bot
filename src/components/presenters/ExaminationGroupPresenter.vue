<template>
    <div v-if="examination_group">
        <h4>{{ examination_group.title }}</h4>
        <h6>{{ examination_group.category }}</h6>
        Дата, к которой необходимо пройти обследования: <br>
        <date-picker lang="ru" v-model="date" type="date" value-type="timestamp"/>
        <br>
        <hr>
        Выберите обследования для назначения
        <div class="row" v-for="examination in examination_group.examination_templates">
            <div class="col-1">
                <input class="form-check" type="checkbox" v-model="examination.attach">
            </div>
            <div class="col" style="margin-top: 5px">
                <span>{{ examination.title }}</span><br>
                <span class="text-muted">{{ examination.doctor_description }}</span>
            </div>
        </div>
        <hr>
        <button class="btn btn-primary" @click="attach_examinations">Назначить</button>
    </div>
</template>

<script>
import ActionDone from "./ActionDone";
import FormGroup48 from "../common/FormGroup-4-8";
import ErrorBlock from "../common/ErrorBlock";
import DatePicker from 'vue2-datepicker';
import * as moment from "moment/moment";

export default {
    name: "ExaminationGroupPresenter",
    components: {ActionDone, ErrorBlock, FormGroup48, DatePicker},
    props: {
        data: {
            required: false
        }
    },
    data() {
        return {
            examination_group: undefined,
            date: undefined,
            errors: []
        }
    },
    methods: {
        attach_examinations: function () {
            this.axios
                .post(this.direct_url('/api/settings/examination-group'), {
                    deadline: this.date / 1000,
                    examinations: this.examination_group.examination_templates.filter((e) => e.attach).map((e) => e.id)
                })
                .then((response) => Event.fire('action-done'))
        }
    },
    created() {
        this.examination_group = this.data
        this.date = +moment().add(14, "days")
    }
}
</script>

<style scoped>
.btn {
    margin-bottom: 5px;
}
</style>
