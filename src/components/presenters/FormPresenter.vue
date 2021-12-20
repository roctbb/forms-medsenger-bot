<template>
    <div @click="blur()">
        <error-block :errors="errors"/>
        <h3>{{ this.form.title }}</h3>
        <p v-html="br(form.patient_description)"></p>

        <div class="card" v-for="block in blocks">
            <div class="card-body">

                <div v-for="(field, i) in block" v-if="!field.show_if || answers[field.show_if]">

                    <h5 v-if="field.type == 'header'">{{ field.text }}</h5>
                    <form-group48 v-else
                                  :check="field.type == 'checkbox'"
                                  :big="true"
                                  :required="field.required"
                                  :title="field.text" :key="i"
                                  :description="field.description" :errors="field_errors[field.uid]">
                        <input type="number" min="field.params.min" max="field.params.max" step="1"
                               class="form-control monitoring-input"
                               :class="save_clicked && field.required &&
                       (!answers[field.uid] && answers[field.uid] !== 0 || answers[field.uid] < field.params.min || answers[field.uid] > field.params.max) ? 'is-invalid' : ''"
                               v-if="field.type == 'integer'" :required="field.required" v-model="answers[field.uid]"/>
                        <input type="number" min="field.params.min" max="field.params.max" step="0.01"
                               class="form-control monitoring-input"
                               :class="save_clicked && field.required &&
                       (!answers[field.uid] && answers[field.uid] !== 0 || answers[field.uid] < field.params.min || answers[field.uid] > field.params.max) ? 'is-invalid' : ''"
                               v-if="field.type == 'float'" :required="field.required" v-model="answers[field.uid]"/>
                        <input type="text" class="form-control monitoring-input" v-if="field.type == 'text'"
                               :required="field.required"
                               :class="save_clicked && field.required && !answers[field.uid] && answers[field.uid] !== 0 ? 'is-invalid' : ''"
                               v-model="answers[field.uid]"/>
                        <input type="file" class="monitoring-input" v-if="field.type == 'file'"
                               :required="field.required"
                               v-bind:ref="'file_' + field.uid" v-on:change="submit_file(field)"/>
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

                        <div v-if="field.type == 'scale'">
                            <visual-analog-scale :params="field.params" :colors="field.params.colors">
                                <div class="row">
                                    <div class="col-1 d-flex justify-content-center" v-for="(color, i) in field.params.colors">
                                        <input class="form-check-input monitoring-input" style="margin-left: 4px" type="radio"
                                               :id="'radio_' + field.uid + '_' + i" :name="'radio_' + field.uid"
                                               v-model="answers[field.uid]"
                                               :value="(field.params.reversed ? -1 : 1) * i + field.params.start_from">
                                    </div>
                                </div>
                            </visual-analog-scale>
                        </div>

                        <div v-if="field.type == 'date'">
                            <date-picker :required="field.required" v-model="answers[field.uid]"
                                         value-type="YYYY-MM-DD"></date-picker>
                        </div>

                        <div v-if="field.type == 'time'">
                            <date-picker :required="field.required" v-model="answers[field.uid]" format="HH:mm" value-type="HH:mm"
                                         type="time"></date-picker>
                        </div>


                    </form-group48>

                </div>
            </div>

        </div>

        <button @click="save()" class="btn btn-success btn-lg" :disabled="submitted || is_preview">Отправить ответ</button>


    </div>
</template>

<script>
import FormGroup48 from "../common/FormGroup-4-8";
import ErrorBlock from "../common/ErrorBlock";
import ActionDone from "./ActionDone";
import DatePicker from 'vue2-datepicker';
import 'vue2-datepicker/index.css';
import 'vue2-datepicker/locale/ru';
import VisualAnalogScale from "./parts/VisualAnalogScale";

export default {
    name: "FormPresenter",
    components: {VisualAnalogScale, ActionDone, FormGroup48, ErrorBlock, DatePicker},
    props: {
        data: {
            required: false,
        }
    },
    data() {
        return {
            form: {},
            answers: {},
            blocks: [],
            errors: [],
            field_errors: {},
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
                console.log(this.answers)
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
                if (field.type == 'file' && this.field_errors[field.uid]) return true;
                if (field.type == 'integer' || field.type == 'float') {
                    if (!this.empty(field.params.min) && !this.empty(field.params.max)) {
                        if (this.answers[field.uid] < field.params.min || this.answers[field.uid] > field.params.max) return true
                    }
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
        },
        submit_file: function (field) {
            if (this.$refs['file_' + field.uid] && this.$refs['file_' + field.uid][0].files) {
                if (this.$refs['file_' + field.uid][0].files[0].size > 50 * 1024 * 1024) {
                    this.field_errors[field.uid] = "Размер файла не должен превышать 50 МБ.";
                } else {
                    let file = this.$refs['file_' + field.uid][0].files[0];

                    let filename = file.name;
                    let type = file.type;

                    if (!type) {
                        type = 'text/plain'
                    }

                    this.field_errors[field.uid] = "Готовим файл к загрузке...";

                    this.toBase64(file).then((base64) => {
                        console.log("file is ready")

                        this.answers[field.uid] = {
                            name: filename,
                            type: type,
                            base64: base64
                        }
                        this.field_errors[field.uid] = "";
                        this.$forceUpdate();
                    })


                }


            }
        },
    },
    created() {
        this.form = this.data
        this.blocks = []

        let block = []

        this.form.fields.forEach((item) => {
            if (item.type == 'header' && block.length != 0) {
                this.blocks.push(block)
                block = []
            }

            block.push(item)
        })
        this.blocks.push(block)

        this.set_default()
    },
    mounted() {
        setTimeout(() => {
            window.document.querySelector('input.monitoring-input').focus()
        }, 300)

    }
}
</script>

<style scoped>
.card {
    margin-bottom: 15px;
}

h5 {
    margin-bottom: 15px;
}
input[type=checkbox]
{
  /* Double-sized Checkboxes */
  -ms-transform: scale(1.5); /* IE */
  -moz-transform: scale(1.5); /* FF */
  -webkit-transform: scale(1.5); /* Safari and Chrome */
  -o-transform: scale(1.5); /* Opera */
  transform: scale(1.5);
  padding: 10px;
}
input[type=radio]
{
  /* Double-sized Checkboxes */
  -ms-transform: scale(1.5); /* IE */
  -moz-transform: scale(1.5); /* FF */
  -webkit-transform: scale(1.5); /* Safari and Chrome */
  -o-transform: scale(1.5); /* Opera */
  transform: scale(1.5);
  padding: 10px;
}

strong {
    size: 1.02rem !important;
}

.form-check-label {
    margin-left: 5px;
}
.form-check {
     margin-top: 15px;
     margin-bottom: 15px;
}
.card-body {
    padding: 1rem;
}
</style>
