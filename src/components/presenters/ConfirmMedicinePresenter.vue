<template>
    <div>
        <div v-if="data.length" style="margin-bottom: 15px;">
            <h5>Назначенные лекарства</h5>
            <p>Выберите лекарство, прием которого Вы хотите записать.</p>
            <div class="row">
                <div class="col-4" v-for="(medicine, i) in data" style="padding-bottom: 10px;">
                    <button class="btn btn-primary btn-block" @click="save(medicine)">{{ medicine.title }}</button>
                </div>
            </div>
        </div>
        <h5>Другое лекарство</h5>
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
                <input class="form-control form-control-sm" v-model="custom_medicine.comment"/>
            </form-group48>
        </div>
        <button class="btn btn-success" @click="custom_save()">Записать прием</button>
        <error-block :errors="errors"/>

    </div>
</template>

<script>
import ActionDone from "./ActionDone";
import FormGroup48 from "../common/FormGroup-4-8";
import ErrorBlock from "../common/ErrorBlock";

export default {
    name: "ConfirmMedicinePresenter",
    components: {ActionDone, ErrorBlock, FormGroup48},
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
            errors: []
        }
    },
    methods: {
        save: function (medicine) {
            this.errors = []
            console.log(medicine)
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
        },
        created() {
            this.medicines = this.data
            this.custom_medicine = {
                title: '',
                dose: '',
                comment: ''
            }
        }
    }
}
</script>

<style scoped>

</style>
