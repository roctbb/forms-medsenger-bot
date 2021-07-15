<template>
    <div @click="blur()">
        <error-block :errors="errors"/>
        <h3>{{ this.form.title }}</h3>
        <p v-html="br(form.patient_description)"></p>
        <form-group48 v-for="(field, i) in form.fields" v-if="!field.show_if || answers[field.show_if]" :required="field.required"
                      :title="field.text" :key="i"
                      :description="field.description">
            <input type="number" min="field.params.min" max="field.params.max" step="1" class="form-control monitoring-input"
                   :class="save_clicked && field.required &&
                       (!answers[field.uid] && answers[field.uid] !== 0 || answers[field.uid] < field.params.min || answers[field.uid] > field.params.max) ? 'is-invalid' : ''"
                   v-if="field.type == 'integer'" :required="field.required" v-model="answers[field.uid]"/>
            <input type="number" min="field.params.min" max="field.params.max" step="0.01" class="form-control monitoring-input"
                   :class="save_clicked && field.required &&
                       (!answers[field.uid] && answers[field.uid] !== 0 || answers[field.uid] < field.params.min || answers[field.uid] > field.params.max) ? 'is-invalid' : ''"
                   v-if="field.type == 'float'" :required="field.required" v-model="answers[field.uid]"/>
            <input type="text" class="form-control monitoring-input" v-if="field.type == 'text'" :required="field.required"
                   :class="save_clicked && field.required && !answers[field.uid] && answers[field.uid] !== 0 ? 'is-invalid' : ''"
                   v-model="answers[field.uid]"/>
            <textarea class="form-control monitoring-input" v-if="field.type == 'textarea'" :required="field.required"
                      :class="save_clicked && field.required && !answers[field.uid] && answers[field.uid] !== 0 ? 'is-invalid' : ''"
                      v-model="answers[field.uid]"></textarea>
            <div v-if="field.type == 'checkbox'" style="width: 100%;"><input type="checkbox"
                                                                             v-model="answers[field.uid]"/></div>

            <div v-if="field.type == 'radio'">
                <div class="form-check" v-for="(variant, j) in field.params.variants">
                    <input class="form-check-input monitoring-input" type="radio"
                           :id="'radio_' + i + '_' + j" :name="'radio_' + i"
                           v-model="answers[field.uid]" :value="j">
                    <label class="form-check-label" :for="'radio_' + i + '_' + j">{{ variant.text }}</label>
                </div>
            </div>

            <div v-if="field.type == 'date'">
                <date-picker :required="field.required" v-model="answers[field.uid]" value-type="YYYY-MM-DD"></date-picker>
            </div>

            <div v-if="field.type == 'time'">
                <date-picker :required="field.required" v-model="answers[field.uid]" value-type="H:m" type="time"></date-picker>
            </div>


        </form-group48>

        <button @click="save()" class="btn btn-success" :disabled="submitted">Отправить ответ</button>


    </div>
</template>

<script>
import FormGroup48 from "../common/FormGroup-4-8";
import ErrorBlock from "../common/ErrorBlock";
import ActionDone from "./ActionDone";
import DatePicker from 'vue2-datepicker';
import 'vue2-datepicker/index.css';
import 'vue2-datepicker/locale/ru';

export default {
    name: "FormPresenter",
    components: {ActionDone, FormGroup48, ErrorBlock, DatePicker},
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
            submitted: false,
            save_clicked: false
        }
    },
    methods: {
        save: function () {
            this.errors = []
            this.save_clicked = true

            if (this.check()) {
                this.submitted = true
                this.axios.post(this.url('/api/form/' + this.form.id), this.answers).then(r => Event.fire('form-done')).catch(r => {
                    this.errors.push('Ошибка сохранения')
                    this.submitted = false
                });
            } else {
                this.errors.push('Проверьте правильность заполнения опросника')
            }
        },
        check: function () {
            let prepare_field = (field, i) => {
                if (this.empty(this.answers[field.uid])) {
                    return;
                }
                if (field.type == 'integer') {
                    this.answers[field.uid] = parseInt(this.answers[field.uid])
                }
                if (field.type == 'float') {
                    this.answers[field.uid] = parseFloat(this.answers[field.uid])
                }
                if (field.show_if && !this.answers[field.show_if]) {
                    this.answers[field.uid] = undefined;
                }
            }

            this.form.fields.map(prepare_field)

            let validate_field = (field, i) => {
                if (field.required && this.empty(this.answers[field.uid])) return true;
                if (field.type == 'integer' || field.type == 'float') {
                    if (this.answers[field.uid] < field.params.min || this.answers[field.uid] > field.params.max) return true
                }
                return false
            }

            return this.form.fields.filter(validate_field).length == 0
        },
        set_default: function () {
            let prepare_field = (field, i) => {
                if (field.type == 'radio') {
                    this.answers[field.uid] = 0
                }
            }

            this.form.fields.map(prepare_field)
        }
    },
    created() {
        this.form = this.data
        this.set_default()
    },
    mounted() {
        window.document.querySelector('input.monitoring-input').focus()
    }
}
</script>

<style scoped>

</style>
