<template>
    <div v-if="examination">
        <h3>{{ examination.title }}</h3>
        <p v-html="br(examination.patient_description)"></p>
        <card>
            <form-group48 :big="true" title="Прикрепите файл обследования">
                <input type="file" class="monitoring-input" multiple ref="file" @change="submit_file"/>
            </form-group48>

            <!-- Файлы -->
            <div v-for="(file, i) in files" style="margin-bottom: 5px" class="row">
                <div class="col-1">
                    <a class="btn btn-default btn-sm" @click="remove_file(i)">Удалить</a>
                </div>
                <div class="col">
                    <img :src="images.file" height="20"/>
                    <a href="#" @click="get_file(file, 'download')">{{ file.name }} (скачать)</a>
                </div>
            </div>
            <div class="alert alert-primary" role="alert" style="margin-bottom: 0; font-size: small"
                 v-if="file_states.length">
                <span v-for="state in file_states"><span v-html="state"/><br></span>
            </div>
        </card>
        <div class="card">
            <div class="card-body">
                <form-group48 :big="true"
                              :title="'Время прохождения обследования'" :key="-1"
                              style="margin-top: 15px; margin-bottom: 15px;">
                    <date-picker v-model="fill_time" lang="ru" :minute-step="15" type="datetime" format="DD.MM.YYYY HH:mm"
                                 time-title-format="DD.MM.YYYY"
                                 :class="flags.validated && date_invalid(fill_time) ? 'is-invalid' : ''"
                                 :disabled-date="date_invalid"></date-picker>
                </form-group48>
            </div>
        </div>

        <button class="btn btn-danger" @click="go_back()" v-if="page != 'examination'">Назад</button>
        <button class="btn btn-success" @click="save()">Сохранить</button>

        <error-block :errors="errors"/>
    </div>
</template>

<script>
import Card from "../common/Card";
import FormGroup48 from "../common/FormGroup-4-8";
import ErrorBlock from "../common/ErrorBlock";
import DatePicker from 'vue2-datepicker';
import 'vue2-datepicker/index.css';
import 'vue2-datepicker/locale/ru';
import downloadjs from "downloadjs";

export default {
    name: "ExaminationPresenter",
    components: {ErrorBlock, FormGroup48, Card, DatePicker},
    props: {
        show_back_btn: {required: false}
    },
    data() {
        return {
            flags: {
                validated: false,
                lock_btn: false
            },
            errors: [],
            fill_time: new Date(),
            files: [],
            file_states: [],
            examination: undefined
        }
    },
    methods: {
        format_date: function (date) {
            let d = date.split('-')
            return `${d[2]}.${d[1]}.${d[0]}`
        },
        // файлы
        remove_file: function (i) {
            this.files.splice(i, 1)
            this.file_states.splice(i, 1)
        },
        get_file: function (file, action) {
            if (action == 'download')
                downloadjs(`data:${file.type};base64,${file.base64}`, file.name, file.type);
            this.$forceUpdate()
        },
        submit_file: function (event) {
            let files = Array.from(event.target.files)

            if (files) {
                this.file_states = []
                files.forEach((file, i) => {
                    if (file.size > 50 * 1024 * 1024) {
                        this.file_states.push('<strong>' + file.name + ':</strong> Размер файла не должен превышать 50 МБ.')
                    } else {
                        let filename = file.name;
                        let type = file.type;

                        if (!type) {
                            type = 'text/plain'
                        }

                        this.file_states.push('<strong>' + file.name + ':</strong> Готовим файл к загрузке...');

                        this.toBase64(file).then((base64) => {
                            this.files.push({
                                name: filename,
                                type: type,
                                base64: base64
                            })
                            this.file_states[i] = '<strong>' + file.name + ':</strong> Файл успешно загружен!';
                            this.$forceUpdate();
                        })
                    }
                })
            }
        },
        go_back() {
            this.$confirm({
                message: `Вы уверены? Внесенные изменения будут утеряны!`,
                button: {
                    no: 'Нет',
                    yes: 'Да'
                },
                callback: confirm => {
                    if (confirm) {
                        Event.fire('back-to-examinations-list');

                        this.files = []
                        this.file_states = []
                        this.errors = []
                    }
                }
            })
        },
        save: function () {
            this.errors = []
            this.flags.validated = true
            this.flags.lock_btn = true

            if (this.date_invalid(this.fill_time)) {
                this.errors = [`Дата прохождения обследования должна быть в периоде от ${this.format_date(this.examination.notification_date)} до ${this.format_date(this.examination.deadline_date)}`]
                this.flags.lock_btn = false
            } else {
                this.axios
                    .post(this.direct_url('/api/examination/' + this.examination.id), {
                        files: this.files,
                        date: Math.floor(+this.fill_time / 1000)
                    })
                    .then((response) => {
                        this.examination.files = this.files
                        this.examination.upload_date = this.strftime('%Y-%m-%d', this.fill_time)
                        Event.fire('examination-loaded', this.examination)
                    })
            }
        },
        date_invalid: function (date) {
            return date > new Date() || this.examination && date < this.examination.date
        }
    },
    created() {
        Event.listen('navigate-to-load-examination-page', (examination) => {
            this.examination = examination
            if (examination.upload_date) {
                this.axios.get(this.direct_url('/api/settings/get_examination_files/' + examination.id))
                .then((response) => {
                    this.files = response.data
                    this.file_states = this.files.map((f) => '<strong>' + f.name + ':</strong> Файл был загружен ранее.')
                })
            }
        })
    }
}
</script>

<style scoped>
.card {
    margin-bottom: 15px;
}
</style>
