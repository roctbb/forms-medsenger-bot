<template>
    <div>
        <h3>Записать прием лекарства</h3>
        <error-block :errors="errors"/>
        <h5>Назначенные лекарства</h5>
        <p>Нажмите на название лекартсва, прием которого Вы хотите записать.</p>
        <div v-for="(medicine, i) in data" style="padding-bottom: 15px;">
            <button class="btn btn-success" @click="save(medicine.id)">{{ medicine.title }}</button>
        </div>
        <h5>Другое лекарство</h5>
        <div>
            <form-group48 title="Название лекарства">
                <input class="form-control form-control-sm"
                       :class="save_clicked && empty(custom_medicine) ? 'is-invalid' : ''"
                       v-model="custom_medicine"/>
            </form-group48>
        </div>
        <button class="btn btn-primary" @click="custom_save()">Записать прием</button>

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
            custom_medicine: '',
            save_clicked: false,
            errors: []
        }
    },
    methods: {
        save: function (medicine_id) {
            this.errors = []
            let data = { 'custom': false, 'medicine': medicine_id}
            this.axios.post(this.url('/api/confirm-medicine'), data).then(r => Event.fire('confirm-medicine-done')).catch(r => this.errors.push('Ошибка сохранения'));
        },
        custom_save: function () {
            this.errors = []
            this.save_clicked = true
            if (this.empty(this.custom_medicine))
                this.errors.push('Заполните поле')
            else {
                this.errors = []
                let data = { 'custom': true, 'medicine': this.custom_medicine}
                this.axios.post(this.url('/api/confirm-medicine'), data).then(r => Event.fire('confirm-medicine-done')).catch(r => this.errors.push('Ошибка сохранения'));
                console.log('save custom medicine')
            }
        },
        created() {
            this.medicines = this.data
        }
    }
}
</script>

<style scoped>

</style>
