<template>
    <div v-if="!custom && medicines.length">
        <h3>Назначенные лекарства</h3>
        <div style="margin-top: 15px;" class="alert alert-info" role="alert">
            <p>Напоминания о плановом приеме лекарств приходят согласно расписанию.
                Если Вы уже отметили прием препарата с помощью кнопки в чате, повторно записывать прием не нужно.</p>
        </div>
        <div class="row">
            <card v-for="(medicine, i) in medicines" :key="medicine.id"
                  :image="images.medicine" class="col-lg-4 col-md-5 text-muted">
                <h6>{{ medicine.title }}</h6>
                <small><strong>Назначенная дозировка: </strong> {{ medicine.dose ? medicine.dose : '-' }}</small><br>
                <small><strong>Правила приема: </strong> {{ medicine.rules ? medicine.rules : '-' }}</small><br>
                <small><i>{{ tt_description(medicine.timetable) }}</i></small>
                <small v-if="medicine.notifications_disabled"><strong>Уведомления выключены</strong></small>
                <br><br>
                <button class="btn btn-success btn-sm" @click="save(medicine)" v-if="medicine">Записать прием</button>
                <div v-if="medicine.timetable.mode !='manual'">
                    <a href="#" v-if="!medicine.notifications_disabled" @click="disable_notifications(medicine)">Отключить
                        уведомления</a>
                    <a href="#" v-if="medicine.notifications_disabled" @click="enable_notifications(medicine)">Включить
                        уведомления</a>
                </div>
                <div v-else>
                    <strong>Принимается при необходимости.</strong>
                </div>
            </card>
        </div>
        <button class="btn btn-primary" @click="custom = true">Другое лекарство</button>
    </div>

    <div v-else>
        <h3>Записать прием лекарства</h3>

        <card>
            <form-group48 title="Название лекарства" required="true">
                <input class="form-control form-control-sm"
                       :class="validated && empty(custom_medicine.title) ? 'is-invalid' : ''"
                       v-model="custom_medicine.title"/>
            </form-group48>

            <form-group48 title="Принятая доза" required="true">
                <input class="form-control form-control-sm"
                       :class="validated && empty(custom_medicine.dose) ? 'is-invalid' : ''"
                       v-model="custom_medicine.dose"/>
            </form-group48>

            <form-group48 title="Комментарий">
                <textarea class="form-control monitoring-input" v-model="custom_medicine.comment"/>
            </form-group48>
        </card>

        <button class="btn btn-danger btn" @click="custom = false" v-if="medicines.length">Назад</button>
        <button class="btn btn-success btn" @click="custom_save()">Записать прием</button>
        <error-block :errors="errors"/>
    </div>

</template>

<script>
import Card from "../common/Card";
import FormGroup48 from "../common/FormGroup-4-8";
import ErrorBlock from "../common/ErrorBlock";

export default {
    name: "MedicineList",
    components: {ErrorBlock, FormGroup48, Card},
    props: {
        data: {
            required: false
        }
    },
    data() {
        return {
            medicines: {},
            custom_medicine: {},
            validated: false,
            custom: false,
            errors: []
        }
    },
    methods: {
        disable_notifications: function (medicine) {
            this.$confirm({
                message: `Вы уверены, что хотите отключить напоминания для препарата ${medicine.title}?`,
                button: {
                    no: 'Нет',
                    yes: 'Да'
                },
                callback: confirm => {
                    if (confirm) {
                        this.axios.post(this.url('/api/medicine/' + medicine.id + '/disable_notifications')).then(answer => medicine.notifications_disabled = answer.data.notifications_disabled);
                    }
                }
            })
        },
        enable_notifications: function (medicine) {
            this.axios.post(this.url('/api/medicine/' + medicine.id + '/enable_notifications')).then(answer => medicine.notifications_disabled = answer.data.notifications_disabled);
        },
        save: function (medicine) {
            this.errors = []

            if (medicine.verify_dose) {
                Event.fire('verify-dose', medicine)
            } else {
                let data = {
                    custom: false,
                    medicine: medicine.id,
                    params: null
                }
                this.axios.post(this.url('/api/confirm-medicine'), data).then(r => Event.fire('confirm-medicine-done')).catch(r => this.errors.push('Ошибка сохранения'));
            }
        },
        custom_save: function () {
            this.errors = []
            this.validated = true
            if (this.empty(this.custom_medicine.title) || this.empty(this.custom_medicine.dose))
                this.errors.push('Пожалуйста, заполните обязательные поля')
            else {
                this.errors = []
                let data = {
                    custom: true,
                    medicine: this.custom_medicine.title,
                    params: {
                        dose: this.custom_medicine.dose,
                        comment: this.custom_medicine.comment
                    }
                }
                this.axios.post(this.url('/api/confirm-medicine'), data).then(r => Event.fire('confirm-medicine-done')).catch(r => this.errors.push('Ошибка сохранения'));
            }
        }

    },
    created() {
        this.medicines = this.data.filter(medicine => medicine.contract_id == this.current_contract_id)
        this.medicines.sort((a, b) => {
            return a.title < b.title ? -1 : a.title > b.title ? 1 : 0
        })

        this.custom_medicine = {
            title: '',
            dose: '',
            comment: ''
        }
    }
}
</script>

<style scoped>

</style>
