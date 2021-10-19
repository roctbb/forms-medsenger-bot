<template>
    <div>
        <h3>{{ medicine.title }}</h3>
        <p>Пожалуйста, заполните данные по приему лекарства.</p>

        <form-group48 title="Принятая доза">
            <input class="form-control form-control-sm" v-model="dose"/>
        </form-group48>

        <form-group48 title="Комментарий">
            <input class="form-control form-control-sm" v-model="comment"/>
        </form-group48>

        <button class="btn btn-success" @click="save()">Записать прием</button>

    </div>
</template>

<script>
import FormGroup48 from "../common/FormGroup-4-8";

export default {
    name: "DoseVerifier",
    components: {FormGroup48},
    props: ['data'],
    data() {
        return {
            medicine: {},
            comment: "",
            dose: ""
        }
    },
    created() {
        this.medicine = this.data
        this.dose = this.medicine.dose
    },
    methods: {
        save: function (medicine) {
            this.errors = []
            let data = {
                custom: false,
                medicine: this.medicine.id,
                params: {
                    dose: this.dose,
                    comment: this.comment
                }
            }
            this.axios.post(this.url('/api/confirm-medicine'), data).then(r => Event.fire('confirm-medicine-done')).catch(r => this.errors.push('Ошибка сохранения'));
        },
    }
}
</script>

<style scoped>

</style>
