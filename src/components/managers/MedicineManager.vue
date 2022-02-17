<template>
    <div v-if="state == 'main'">
        <h5>Лекарства</h5>

        <div class="row">
            <card v-for="(medicine, i) in patient.medicines" :key="'medicine' + medicine.id" :image="images.medicine"
                  class="col-lg-3 col-md-4">
                <h6>{{ medicine.title }}</h6>
                <small>{{ medicine.rules }}</small><br>
                <small><i>{{ tt_description(medicine.timetable) }}</i></small><br>
                <small v-if="medicine.sent">Подтверждено {{ medicine.done }} раз(а) / отправлено {{ medicine.sent }}
                    раз(а) за последний месяц</small>
                <small v-else>Пока не отправлялось</small><br>
                <div v-if="medicine.contract_id == current_contract_id">
                    <a href="#" @click="edit_medicine(medicine)">Редактировать</a>
                    <a href="#" @click="delete_medicine(medicine)">Отменить</a>
                </div>
                <div v-else>
                    <small>Добавлен в другом контракте.</small>
                </div>

                <small v-if="!empty(medicine.template_id)" class="text-muted">ID шаблона: {{
                        medicine.template_id
                    }}</small>

            </card>

            <card v-for="(medicine, i) in patient.canceled_medicines" :key="'canceled_medicine' + medicine.id"
                  :image="images.canceled_medicine"
                  class="col-lg-3 col-md-4 text-muted">
                <h6>{{ medicine.title }}</h6>
                <small>{{ medicine.rules }}</small><br>
                <small><i>{{ tt_description(medicine.timetable) }}</i></small><br>
                <small>Назначено: {{ medicine.prescribed_at }}</small><br>
                <small>Отменено: {{ medicine.canceled_at }}</small><br>
                <div v-if="medicine.contract_id == current_contract_id">
                    <a href="#" @click="resume_medicine(medicine)">Возобновить</a>
                </div>

            </card>
        </div>

        <button class="btn btn-primary btn-sm" @click="create_medicine()">Назначить лекарство
        </button>

    </div>

</template>

<script>
import Card from "../common/Card";
import ErrorBlock from "../common/ErrorBlock";
import * as moment from "moment/moment";

export default {
    name: "MedicineManager",
    components: {ErrorBlock, Card},
    props: {
        patient: {
            required: true
        },
        templates: {
            required: true
        }
    },
    data: function () {
        return {
            loaded: false,
            state: 'main',
            errors: [],
            lock_btn: false,
            search_query: ''
        }
    },
    methods: {
        attach_medicine: function (medicine) {
            Event.fire('attach-medicine', medicine)
        },
        create_medicine: function () {
            Event.fire('navigate-to-create-medicine-page')
        },
        edit_medicine: function (medicine) {
            Event.fire('edit-medicine', medicine)
        },
        delete_medicine: function (medicine) {
            this.$confirm(
                {
                    message: `Вы уверены, что хотите отменить препарат ` + medicine.title + `?`,
                    button: {
                        no: 'Нет',
                        yes: 'Да, удалить'
                    },
                    callback: confirm => {
                        if (confirm) {
                            this.axios.post(this.url('/api/settings/delete_medicine'), medicine).then(this.process_delete_medicine_answer);
                        }
                    }
                }
            )
        },
        process_delete_medicine_answer: function (response) {
            if (response.data.deleted_id) {
                let medicine = this.patient.medicines.find(m => m.id == response.data.deleted_id)
                if (medicine) {
                    medicine.canceled_at = moment(new Date()).format("DD.MM.YYYY")
                    this.patient.canceled_medicines.push(medicine);
                }

                this.patient.medicines = this.patient.medicines.filter(m => m.id != response.data.deleted_id)
                this.templates.medicines = this.templates.medicines.filter(m => m.id != response.data.deleted_id)
            }
        },
        resume_medicine: function (medicine) {
            this.$confirm(
                {
                    message: `Вы уверены, что хотите возобновить препарат ` + medicine.title + `?`,
                    button: {
                        no: 'Нет',
                        yes: 'Да, возобновить'
                    },
                    callback: confirm => {
                        if (confirm) {
                            this.axios.post(this.url('/api/settings/resume_medicine'), medicine).then(this.process_resume_medicine_answer);
                        }
                    }
                }
            )
        },
        process_resume_medicine_answer: function (response) {
            if (response.data.resumed_id) {
                let medicine = this.patient.canceled_medicines.find(m => m.id == response.data.resumed_id)
                if (medicine) {
                    medicine.canceled_at = null
                    this.patient.medicines.push(medicine);
                }

                this.patient.canceled_medicines = this.patient.canceled_medicines.filter(m => m.id != response.data.resumed_id)
            }
        }
    },

    mounted() {
        Event.listen('home', () => {
            this.state = 'main'
        });
    }

}
</script>

<style scoped>

</style>
