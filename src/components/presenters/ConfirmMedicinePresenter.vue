<template>
    <div>
        <div style="margin-bottom: 15px;">
            <h5>Записать прием лекарства</h5>
            <div v-if="!custom && medicines.length">
                <div style="margin-top: 15px;" class="alert alert-info" role="alert">
                    <p>Напоминания о плановом приеме лекарств приходят согласно расписанию.
                        Если Вы уже отметили прием препарата с помощью кнопки в чате, повторно записывать прием не нужно.</p>
                </div>

                <p>Выберите лекарство, прием которого Вы хотите записать.</p>
                <div class="row" v-if="!mobile">
                    <card v-for="(medicine, i) in medicines" :key="medicine.id" :image="images.medicine" class="col-lg-6 col-md-7">
                        <h6>{{ medicine.title }}</h6>
                        <small><strong>Назначенная дозировка: </strong> {{ medicine.dose ? medicine.dose : '-' }}</small><br>
                        <small><strong>Правила приема: </strong> {{ medicine.rules ? medicine.rules : '-' }}</small><br>
                        <small><i>{{ tt_description(medicine.timetable) }}</i></small><br>
                        <button class="btn btn-success btn-sm" @click="save(medicine)">Записать прием</button>
                    </card>
                </div>
                <div style="padding-bottom: 10px;" v-else>
                    <card v-for="(medicine, i) in medicines" :key="medicine.id" :image="images.medicine">
                        <h6>{{ medicine.title }}</h6>
                        <small><strong>Назначенная дозировка: </strong> {{ medicine.dose ? medicine.dose : '-' }}</small><br>
                        <small><strong>Правила приема: </strong> {{ medicine.rules ? medicine.rules : '-' }}</small><br>
                        <small><i>{{ tt_description(medicine.timetable) }}</i></small><br>
                        <button class="btn btn-success btn-sm" @click="save(medicine)">Записать прием</button>
                    </card>
                </div>
                <button class="btn btn-primary" @click="custom = true">Другое лекарство</button>
            </div>
            <div v-else>
                <div>
                    <form-group48 title="Название лекарства">
                        <input class="form-control form-control-sm"
                               :class="save_clicked && empty(custom_medicine.title) ? 'is-invalid' : ''"
                               v-model="custom_medicine.title"/>
                    </form-group48>

                    <form-group48 title="Принятая доза">
                        <input class="form-control form-control-sm"
                               :class="save_clicked && empty(custom_medicine.dose) ? 'is-invalid' : ''"
                               v-model="custom_medicine.dose"/>
                    </form-group48>

                    <form-group48 title="Комментарий">
                        <textarea class="form-control monitoring-input" v-model="custom_medicine.comment"/>
                    </form-group48>
                </div>
                <button class="btn btn-danger btn-sm" @click="custom = false" v-if="medicines.length">Назад</button>
                <button class="btn btn-success btn-sm" @click="custom_save()">Записать прием</button>
            </div>
        </div>
        <error-block :errors="errors"/>

    </div>
</template>

<script>
import ActionDone from "./ActionDone";
import FormGroup48 from "../common/FormGroup-4-8";
import Card from "../common/Card";
import ErrorBlock from "../common/ErrorBlock";

export default {
    name: "ConfirmMedicinePresenter",
    components: {ActionDone, ErrorBlock, FormGroup48, Card},
    props: {
        data: {
            required: false
        }
    },
    data() {
        return {
            medicines: {},
            custom_medicine: {},
            save_clicked: false,
            custom: false,
            errors: []
        }
    },
    methods: {
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
            this.save_clicked = true
            if (this.empty(this.custom_medicine.title) || this.empty(this.custom_medicine.dose))
                this.errors.push('Заполните пустые поля')
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
    mounted() {
        this.medicines = this.data
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
