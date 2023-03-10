<template>
    <div @click="blur()">

        <button style="margin-bottom: 10px;" @click="back()" class="btn btn-danger btn-sm"
                v-if="is_preview && mobile">Назад
        </button>

        <h3>{{ this.form.title }}</h3>
        <p v-html="br(form.patient_description)"></p>

        <div class="card" v-for="block in blocks">
            <div class="card-body">

                <div v-for="(field, i) in block"
                     v-if="show_field(field)">
                    <h5 v-if="field.type == 'header' && field.text">{{ field.text }}</h5>
                    <p v-html="br(field.description)" v-if="field.type == 'header' && field.description"></p>

                    <form-group48 v-if="field.type != 'header'"
                                  :check="field.type == 'checkbox'"
                                  :big="true"
                                  :required="field.required"
                                  :title="field.text" :key="i"
                                  :description="field.description" :errors="field_errors[field.uid]"
                                  style="margin-top: 15px; margin-bottom: 15px;">
                        <input type="number" :min="field.params.min" :max="field.params.max" step="1"
                               class="form-control monitoring-input" @input="fieldTransformer(field)"
                               :class="save_clicked && field.required &&
                       (!answers[field.uid] && answers[field.uid] !== 0 || answers[field.uid] < field.params.min || answers[field.uid] > field.params.max) ? 'is-invalid' : ''"
                               v-if="field.type == 'integer'" :required="field.required" v-model="answers[field.uid]"/>


                        <input type="number" :min="field.params.min" :max="field.params.max" step="0.01"
                               class="form-control monitoring-input" @input="fieldTransformer(field)"
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
                        <textarea class="form-control monitoring-input" v-if="field.type == 'textarea'"
                                  :required="field.required"
                                  :class="save_clicked && field.required && !answers[field.uid] && answers[field.uid] !== 0 ? 'is-invalid' : ''"
                                  v-model="answers[field.uid]"></textarea>
                        <div v-if="field.type == 'checkbox'" style="width: 100%;">
                            <input type="checkbox" v-model="answers[field.uid]"/>
                        </div>

                        <div v-if="field.type == 'radio'">
                            <div class="form-check" v-for="(variant, j) in field.params.variants">
                                <input class="form-check-input monitoring-input" type="radio"
                                       :id="'radio_' +  field.uid + '_' + j" :name="'radio_' +  field.uid + '_' + j"
                                       v-model="answers[field.uid]" :value="j" @change="$forceUpdate()">
                                <label class="form-check-label" :for="'radio_' +  field.uid + '_' + j">{{
                                        variant.text
                                    }}</label>
                            </div>
                        </div>

                        <div v-if="field.type == 'scale'">
                            <visual-analog-scale :params="field.params" :colors="field.params.colors">
                                <div class="row">
                                    <div class="col-1 d-flex justify-content-center"
                                         v-for="(color, i) in field.params.colors">
                                        <input class="form-check-input monitoring-input" style="margin-left: 4px"
                                               type="radio"
                                               :id="'radio_' + field.uid + '_' + i" :name="'radio_' + field.uid"
                                               v-model="answers[field.uid]"
                                               :value="(field.params.reversed ? -1 : 1) * i + field.params.start_from">
                                    </div>
                                </div>
                            </visual-analog-scale>
                        </div>

                        <div v-if="field.type == 'map'">
                            <interactive-map :map="field.params.map" :uid="field.uid"/>
                        </div>

                        <div v-if="field.type == 'date'">
                            <date-picker :required="field.required" v-model="answers[field.uid]"
                                         value-type="YYYY-MM-DD"></date-picker>
                        </div>

                        <div v-if="field.type == 'time'">
                            <date-picker :required="field.required" v-model="answers[field.uid]" format="HH:mm"
                                         value-type="HH:mm"
                                         type="time"></date-picker>
                        </div>

                        <input type="range" :min="field.params.min" :max="field.params.max" step="1"
                               class="form-control monitoring-input"
                               :class="save_clicked && field.required && (!answers[field.uid] && answers[field.uid] !== 0) ? 'is-invalid' : ''"
                               v-if="field.type == 'range'" :required="field.required" v-model="answers[field.uid]"/>

                        <div v-if="field.type == 'medicine_list'">
                            <div v-for="(medicine, j) in answers[field.uid]">
                                <div class="row">
                                    <div class="form-check col-5" v-if="medicine.id">
                                        <input class="form-check-input monitoring-input" type="checkbox"
                                               style="margin: 5px -15px;"
                                               :id="'radio_' +  field.uid + '_' + j"
                                               :name="'radio_' +  field.uid + '_' + j"
                                               v-model="medicine.checked" :value="j" @change="$forceUpdate()">
                                        <label class="form-check-label" :for="'radio_' +  field.uid + '_' + j">{{
                                                medicine.title
                                            }}</label>
                                    </div>
                                    <div class="col-5" v-else>
                                        <small>Название</small>
                                        <input type="text" class="form-control monitoring-input"
                                               v-model="medicine.title"/>
                                    </div>
                                    <div :class="`col${mobile ? '' : '-5'}`">
                                        <small>Дозировка</small>
                                        <input type="text" class="form-control monitoring-input"
                                               v-model="medicine.dose"/>
                                    </div>
                                    <div v-if="!medicine.id" class="col-md-2">
                                        <a class="btn btn-default btn-sm" :style="`margin-top: ${mobile ? 5 : 27}px;`"
                                           @click="remove_medicine(field, j)">Удалить</a>
                                    </div>
                                </div>

                            </div>
                            <br>
                            <button class="btn btn-sm btn-secondary" @click="add_medicine(field)">Добавить</button>
                        </div>

                    </form-group48>

                </div>
            </div>

        </div>

        <error-block :errors="errors"/>

        <div class="card">
            <div class="card-body">
                <form-group48
                    :big="true"
                    :title="'Время заполнения'" :key="-1"
                    style="margin-top: 15px; margin-bottom: 15px;">
                    <date-picker v-model="fill_time" :minute-step="15" type="datetime" format="DD.MM.YYYY HH:mm"
                                 time-title-format="DD.MM.YYYY"
                                 :disabled-date="date_invalid"></date-picker>
                </form-group48>
            </div>
        </div>

        <button style="margin-bottom: 20px;" @click="save()" class="btn btn-success btn-lg"
                :disabled="submitted || is_preview">Отправить ответ
        </button>


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
import InteractiveMap from "./parts/InteractiveMap";

export default {
    name: "FormPresenter",
    components: {InteractiveMap, VisualAnalogScale, ActionDone, FormGroup48, ErrorBlock, DatePicker},
    props: {
        patient: {
            required: false
        },
        data: {
            required: false,
        },
        preview: {
            required: false,
        }
    },
    data() {
        return {
            form: {},
            fill_time: new Date(),
            answers: {},
            blocks: [],
            errors: [],
            field_errors: {},
            submitted: false,
            save_clicked: false,
            hexTokens: {
                C: {
                    pattern: /\.|\,/
                }
            }

        }
    },
    methods: {
        save: function () {
            this.errors = []
            this.save_clicked = true

            if (this.fill_time) {
                this.answers.timestamp = Math.floor(this.fill_time / 1000)
            } else {
                this.answers.timestamp = Math.floor(new Date() / 1000)
            }

            if (this.check()) {
                this.submitted = true
                let url = this.page == 'outsource-form' ? ('/api/outsource_form/' + this.form.id) : this.url('/api/form/' + this.form.id)
                this.axios.post(url, this.answers).then(r => {
                    if (this.page == 'outsource-form') {
                        Event.fire('outsource-form-done', r.data.result)
                    } else {
                        Event.fire('form-done')
                    }
                }).catch(r => {
                    this.errors.push('Ошибка сохранения')
                    this.submitted = false
                });
            } else {
                this.errors.push('Проверьте правильность заполнения опросника')
            }
        },
        check: function () {
            console.log(this.answers)

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

                if (field.show_if) {
                    if (!this.show_field(field)) {
                        this.answers[field.uid] = undefined;
                    }
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
                if (field.type == 'radio' && field.required) {
                    this.answers[field.uid] = 0
                }
                if (field.type == 'medicine_list') {
                    console.log(this.patient)
                    if (this.patient.patient_medicines && this.patient.patient_medicines.length) {
                        this.answers[field.uid] = Array.from(Array(this.patient.patient_medicines.length), (_, i) => {
                            let med = {
                                id: this.patient.patient_medicines[i].id,
                                title: this.patient.patient_medicines[i].title,
                                dose: this.patient.patient_medicines[i].dose,
                                checked: false
                            }
                            return med
                        })
                    } else {
                        this.answers[field.uid] = []
                        this.add_medicine(field)
                    }
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
        fieldTransformer: function (field) {
            if (field.category == 'temperature') {
                if (this.answers[field.uid] > 100) {
                    this.answers[field.uid] /= 10;
                }
            }
        },
        show_field: function (field) {
            if (field.show_if) {
                if (this.answers[field.show_if] || field.show_if.uid && this.answers[field.show_if.uid] == field.show_if.ans) {
                    let f = this.form.fields.filter(f => {
                        return field.show_if.uid && f.uid == field.show_if.uid ||
                            field.show_if == f.uid
                    })[0]
                    return this.show_field(f)
                }
                return false
            }
            return true

        },
        add_medicine: function (field) {
            this.answers[field.uid].push({
                title: '',
                dose: '',
                timetable: {mode: "manual", points: []},
                prescription_history: {
                    records: [{
                        description: 'Добавлен пациентом',
                        comment: 'При заполнении опросника ' + this.form.title,
                        date: new Date().toLocaleDateString()
                    }]
                },
                is_created_by_patient: true,
                checked: true,
                edited_by_patient: true
            })
            this.$forceUpdate()
        },
        remove_medicine: function (field, j) {
            this.answers[field.uid].splice(j, 1);
            this.$forceUpdate()
        },
        back: function () {
            Event.fire('back-to-dashboard');
        },
        load_form: function (form) {
            if (form.fields === undefined) {
                return;
            }

            this.form = form
            this.blocks = []

            this.fill_time = new Date()

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

            setTimeout(() => {
                window.document.querySelector('input.monitoring-input').focus()
            }, 300)
        },
        date_invalid: (date) => date > new Date() || date < new Date(new Date().getTime() - 7 * 24 * 3600 * 1000)
    },
    created() {
        if (this.data) {
            this.load_form(this.data)
        }
    },
    mounted() {
        Event.listen('load-form-preview', form => {
            console.log("form preview", form)
            this.is_preview = true
            this.load_form(form)
        })

        Event.listen('interactive-map-answer', data => {
            this.answers[data.uid] = data.answer
        })
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

input[type=checkbox] {
    /* Double-sized Checkboxes */
    -ms-transform: scale(1.4); /* IE */
    -moz-transform: scale(1.4); /* FF */
    -webkit-transform: scale(1.4); /* Safari and Chrome */
    -o-transform: scale(1.4); /* Opera */
    transform: scale(1.4);
    padding: 10px;
}

input[type=radio] {
    /* Double-sized Checkboxes */
    -ms-transform: scale(1.4); /* IE */
    -moz-transform: scale(1.4); /* FF */
    -webkit-transform: scale(1.4); /* Safari and Chrome */
    -o-transform: scale(1.4); /* Opera */
    transform: scale(1.4);
    padding: 10px;
}

strong {
    size: 1.02rem !important;
}

.form-check-label {
    margin-left: 0.5rem;
}

.form-check {
    padding-left: 30px;
    margin-top: 15px;
    margin-bottom: 15px;
}

.card-body {
    padding: 1rem;
}
</style>
