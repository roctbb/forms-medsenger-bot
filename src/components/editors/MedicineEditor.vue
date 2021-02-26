<template>
    <div v-if="medicine">
        <a class="btn btn-danger btn-sm" @click="go_back()">назад</a>
        <error-block :errors="errors"/>
        <div class="form">
            <card title="Описание лекарства">
                <form-group48 title="Название">
                    <input class="form-control" v-model="medicine.title"/>
                </form-group48>

                <form-group48 title="Доза и правила приема">
                    <textarea class="form-control" v-model="medicine.rules"></textarea>
                </form-group48>
            </card>

            <timetable-editor v-bind:data="medicine.timetable"/>
        </div>

        <button class="btn btn-success btn-lg" @click="save()">Сохранить <span v-if="medicine.is_template"> шаблон</span></button>
        <button v-if="!medicine.id" class="btn btn-primary btn-lg" @click="save(true)">Сохранить как шаблон</button>

    </div>
</template>

<script>

import Card from "../common/Card";
import FormGroup48 from "../common/FormGroup-4-8";
import TimetableEditor from "./parts/TimetableEditor";
import ErrorBlock from "../common/ErrorBlock";

export default {
    name: "MedicineEditor",
    components: {TimetableEditor, FormGroup48, Card, ErrorBlock},
    props: {
        data: {
            required: false,
        }
    },
    methods: {
        go_back: function () {
            let old = JSON.parse(this.backup)
            this.copy(this.medicine, old)
            Event.fire('back-to-dashboard');
            this.medicine = undefined
        },
        create_empty_medicine: function () {
            return {
                timetable: this.empty_timetable()
            };
        },

        check: function () {
            this.errors = [];
            if (!this.medicine.title) {
                this.errors.push('Укажите название анкеты')
            }

            if (!this.verify_timetable(this.medicine.timetable)) {
                this.errors.push('Проверьте корректность расписания')
            }

            if (this.errors.length != 0) {
                return false;
            } else {
                return true;
            }
        },
        save: function (is_template) {
            if (this.check()) {
                this.errors = []

                if (is_template || this.medicine.is_template)
                {
                    this.medicine.contract_id = undefined
                    this.medicine.is_template = true;
                }

                this.axios.post(this.url('/api/settings/medicine'), this.medicine).then(this.process_save_answer).catch(this.process_save_error);
            }
        },
        process_save_answer: function (response) {
            let is_new = this.ne(this.medicine.id)
            this.medicine.id = response.data.id

            if (!this.algorithm.is_template) {
                this.medicine.patient_id = response.data.patient_id
                this.medicine.contract_id = response.data.contract_id
            }

            if (is_new) Event.fire('medicine-created', this.medicine)
            else Event.fire('back-to-dashboard', this.medicine)

            this.medicine = undefined
        },
        process_save_error: function (response) {
            this.errors.push('Ошибка сохранения');
        }
    },
    data() {
        return {
            errors: [],
            medicine: undefined,
            backup: ""
        }
    },
    mounted() {
        Event.listen('attach-medicine', (medicine) => {
            this.medicine = {}
            this.copy(this.medicine, medicine)
            this.medicine.id = undefined
            this.medicine.is_template = false;
            this.save()
        });

        Event.listen('navigate-to-create-medicine-page', () => {
            this.medicine = this.create_empty_medicine()
            this.backup = JSON.stringify(this.medicine)
        });

        Event.listen('navigate-to-edit-medicine-page', medicine => {
            this.medicine = medicine
            this.backup = JSON.stringify(medicine)
            this.$forceUpdate()
        });
    }
}
</script>

<style scoped>

</style>
