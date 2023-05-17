<template>
    <div>
        <h3>{{ medicine.title }}</h3>
        <p>Пожалуйста, заполните данные по приему лекарства.</p>

        <card>
            <form-group48 title="Принятая доза" required="true">
                <input class="form-control form-control-sm"
                       :class="validated && empty(dose) ? 'is-invalid' : ''"
                       v-model="dose"/>
            </form-group48>

            <form-group48 title="Комментарий">
                <input class="form-control form-control-sm" v-model="comment"/>
            </form-group48>
        </card>

        <button class="btn btn-danger btn" @click="back()" v-if="mode == 'medicines-list'">Назад</button>
        <button class="btn btn-success" @click="save()">Записать прием</button>

    </div>
</template>

<script>
import FormGroup48 from "../common/FormGroup-4-8";
import Card from "../common/Card";

export default {
    name: "DoseVerifier",
    components: {Card, FormGroup48},
    props: ['data'],
    data() {
        return {
            medicine: {},
            validated: false,
            comment: '',
            dose: '',
            mode: window.PAGE
        }
    },
    created() {
        this.medicine = this.data
        this.dose = this.medicine.dose
    },
    methods: {
        back: function () {
            Event.fire('back-to-medicine-list')
        },
        save: function () {
            this.errors = []
            this.validated = true
            if (this.empty(this.dose))
                this.errors.push('Пожалуйста, заполните обязательные поля')
            else {
                let data = {
                    custom: false,
                    medicine: this.medicine.id,
                    params: {
                        dose: this.dose,
                        comment: this.comment
                    }
                }
                this.axios.post(this.direct_url('/api/confirm-medicine'), data).then(r => Event.fire('confirm-medicine-done')).catch(r => this.errors.push('Ошибка сохранения'));
            }
        },
    }
}
</script>

<style scoped>

</style>
