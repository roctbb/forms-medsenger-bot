<template>
    <modal height="auto" :width="mobile ? '95%' : '600px'" name="examination-settings" @before-open="beforeOpen">
        <div class="container">
            <h5>Настройка параметров обследования {{ examination.title }}</h5>
            <error-block :errors="errors"></error-block>
            <form-group48 title="Крайний срок загрузки">
                <date-picker v-model="examination.deadline_date"
                             :class="this.flags.validated && is_valid_date ? 'is-invalid' : ''"
                             value-type="YYYY-MM-DD"></date-picker>
            </form-group48>

            <button class="btn btn-danger btn-sm" @click="close()">Не назначать обследование</button>
            <button class="btn btn-success btn-sm" @click="attach()">Назначить</button>
        </div>

    </modal>
</template>

<script>

import FormGroup48 from "../../common/FormGroup-4-8";
import ErrorBlock from "../../common/ErrorBlock";
import DatePicker from 'vue2-datepicker';
import 'vue2-datepicker/index.css';
import 'vue2-datepicker/locale/ru';
import * as moment from "moment/moment";

export default {
    name: "ExaminationSettings",
    components: {ErrorBlock, FormGroup48, DatePicker},
    data() {
        return {
            examination: {},
            errors: [],
            flags: {
                validated: false,
            },
        }
    },
    computed: {
        is_valid_date() {
            return moment(this.examination.deadline_date, 'YYYY-MM-DD') > moment()
        }
    },
    methods: {
        close: function () {
            this.$modal.hide('examination-settings')
        },
        attach: function () {
            if (this.check()) {
                Event.fire('attach-examination', this.examination)
                this.close()
            }
        },
        check: function () {
            this.flags.validated = true
            if (!this.is_valid_date) {
                this.errors.push('Крайний срок сдачи не может быть раньше текущей даты')
                return false
            }
            return true
        },
        beforeOpen(event) {
            this.examination = event.params.examination;
            this.examination.deadline_date = moment().add(14, 'days').format('YYYY-MM-DD')
            this.errors = []
        }
    }
}
</script>

<style scoped>
.container {
    padding-top: 15px;
    padding-bottom: 15px;
}

</style>
