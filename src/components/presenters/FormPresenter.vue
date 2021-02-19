<template>
    <div>
        <div v-if="!submitted">
            <error-block :errors="errors"/>
            <h3>{{ this.form.title }}</h3>
            <p> {{ this.form.patient_description }}</p>
            <form-group48 v-for="(field, i) in form.fields" :title="field.text" :key="i" :description="field.description">
                <input type="number" min="field.params.min" max="field.params.max" step="1" class="form-control" v-if="field.type == 'integer'" :required="field.required" v-model="answers[field.uid]"/>
                <input type="number" min="field.params.min" max="field.params.max" step="0.01" class="form-control" v-if="field.type == 'float'" :required="field.required" v-model="answers[field.uid]"/>
                <input type="text" class="form-control" v-if="field.type == 'text'" :required="field.required" v-model="answers[field.uid]"/>
                <textarea class="form-control" v-if="field.type == 'textarea'" :required="field.required" v-model="answers[field.uid]"></textarea>
                <div v-if="field.type == 'checkbox'" style="width: 100%;"><input type="checkbox" v-model="answers[field.uid]"/></div>

                <div v-if="field.type == 'radio'">
                    <div class="form-check" v-for="(variant, j) in field.params.variants">
                        <input class="form-check-input" type="radio" :name="'radio_' + i" v-model="answers[field.uid]" :value="j" :checked="j==0">
                        <label class="form-check-label">{{ variant.text }}</label>
                    </div>
                </div>
            </form-group48>

            <a @click="save()" class="btn btn-success">Отправить ответ</a>
        </div>
        <ActionDone v-else></ActionDone>
    </div>
</template>

<script>
import FormGroup48 from "../common/FormGroup-4-8";
import ErrorBlock from "../common/ErrorBlock";
import ActionDone from "./ActionDone";

export default {
    name: "FormPresenter",
    components: {ActionDone, FormGroup48, ErrorBlock},
    props: {
        data: {
            required: false,
        }
    },
    data() {
        return {
            form: {},
            answers: {},
            errors: [],
            submitted: false
        }
    },
    methods: {
        save: function () {
            this.errors = []
            if (this.check()) {
                this.axios.post(this.url('/api/form/' + this.form.id), this.answers).then(r => this.submitted = true).catch(r => this.errors.push('Ошибка сохранения'));
            } else {
                this.errors.push('Проверьте правильность заполнения анкеты')
            }
        },
        check: function () {
            let prepare_field = (field, i) => {
                if (field.type == 'integer') {
                    this.answers[field.uid] = parseInt(this.answers[field.uid])
                }
                if (field.type == 'float') {
                    this.answers[field.uid] = parseFloat(this.answers[field.uid])
                }
            }

            this.form.fields.map(prepare_field)

            let validate_field = (field, i) => {
                if (field.required && this.ne(this.answers[field.uid])) return true;
                if (field.type == 'integer' || field.type == 'integer') {
                    if (this.answers[field.uid] < field.params.min || this.answers[field.uid] > field.params.max) return true
                }
                return false
            }

            return this.form.fields.filter(validate_field).length == 0
        }
    },
    created() {
        this.form = this.data

        let prepare_answer = (field, i) => {
            if (field.type == 'radio') {
                this.answers[field.uid] = 0
            }
        }

        this.form.fields.map(prepare_answer);
    }
}
</script>

<style scoped>

</style>
