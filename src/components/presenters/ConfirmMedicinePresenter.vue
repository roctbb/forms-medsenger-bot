<template>
    <div>
        <h3>Записать прием лекарства</h3>
        <h5>Назначенные лекарства</h5>
        <p>Нажмите на название лекартсва, прием которого Вы хотите записать...</p>
        <div v-for="(medicine, i) in data" style="padding-top: 15px;">
            <button class="btn btn-success" @click="save(medicine.id)">{{ medicine.title }}</button>
        </div>
        <h5 style="padding-top: 15px;">Другое</h5>
        <p>Какое лекарство Вы приняли?</p>
        <div style="padding-top: 15px;">
                <input class="form-control form-control-sm"
                       :class="save_clicked && empty(custom_medicine) ? 'is-invalid' : ''"
                       v-model="custom_medicine"/>
        </div>
        <div style="padding-top: 15px;">
                <button class="btn btn-primary" @click="custom_save()">Записать прием</button>
        </div>

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
            custom_medicine: '',
            save_clicked: false,
            errors: []
        }
    },
    methods: {
        save: function (medicine_id) {
            this.errors = []
            this.axios.post(this.url('/api/confirm-medicine/' + medicine_id), medicine_id).then(r => Event.fire('confirm-medicine-done')).catch(r => this.errors.push('Ошибка сохранения'));
        },
        custom_save: function () {
            this.errors = []
            this.save_clicked = true
            if (this.empty(this.custom_medicine))
                this.errors.push('Заполните поле')
            else
                console.log('save custom medicine')
            // TODO разобраться, что тут нужно

        },
        created() {
            this.medicines = this.data
        }
    }
}
</script>

<style scoped>

</style>
