<template>
    <div>
        <a class="btn btn-danger btn-sm" @click="go_back()">назад</a>
        <ul>
            <li v-for="error in errors">{{ error }}</li>
        </ul>
        <div class="form">
            <card title="Параметры анкеты">
                <form-group-4-8 title="Название анкеты">
                    <input class="form-control" v-model="form.title"/>
                </form-group-4-8>

                <form-group-4-8 title="Краткое описание для врача">
                    <textarea class="form-control" v-model="form.doctor_description"></textarea>
                </form-group-4-8>

                <form-group-4-8 title="Описание для пациента">
                    <textarea class="form-control" v-model="form.patient_description"></textarea>
                </form-group-4-8>

                <form-group-4-8 title="Пациент может заполнить анкету в произвольное время">
                    <input class="form-check" type="checkbox" v-model="form.show_button" />
                </form-group-4-8>

                <form-group-4-8 v-if="form.show_button" title="Название анкеты для кнопки">
                    <input class="form-control" v-model="form.button_title"/>
                </form-group-4-8>
            </card>

            <card title="Расписание">
                <form-group-4-8 title="Режим">
                    <select @change="clear_time_points()" class="form-control"
                            v-model="form.timetable.mode">
                        <option value="manual">Заполняется вручную</option>
                        <option value="daily">Ежедневно</option>
                        <option value="weekly">Еженедельно</option>
                        <option value="monthly">Ежемесячно</option>
                    </select>
                </form-group-4-8>


                <div v-if="form.timetable.mode != 'manual'">
                    <hr>

                    <div class="form-group row" v-for="(timepoint, i) in form.timetable.points">
                        <div class="col-md-3">
                            <div v-if="form.timetable.mode == 'weekly'">
                                <small class="text-muted">День недели</small>
                                <select class="form-control" v-model="timepoint.day">
                                    <option v-for="(day, i) in weekdays"
                                            v-bind:value="i">{{ day }}
                                    </option>
                                </select>
                            </div>
                            <div v-if="form.timetable.mode == 'monthly'">
                                <small class="text-muted">День</small>
                                <input type="number" min="1" max="31" class="form-control"
                                       v-model="timepoint.day"/>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <small class="text-muted">Часы</small>
                            <input type="number" min="0" max="23" class="form-control"
                                   v-model="timepoint.hour"/>
                        </div>
                        <div class="col-md-3">
                            <small class="text-muted">Минуты</small>
                            <input type="number" min="0" max="59" class="form-control"
                                   v-model="timepoint.minute"/>
                        </div>
                        <div class="col-md-3">
                            <a href="#" @click="remove_time_point(i)" v-if="form.timetable.points.length > 1">Удалить</a>
                        </div>
                    </div>

                    <a href="#" class="btn btn-primary btn-sm" @click="add_time_point()">Добавить</a>

                </div>
            </card>

            <hr>

            <div class="card" v-for="(field, i) in form.fields">
                <div class="card-body">
                    <form-group-4-8 title="Текст вопроса">
                        <input class="form-control" v-model="field.text"/>
                    </form-group-4-8>

                    <form-group-4-8 title="Тип">
                        <select @change="clear_params(field)" class="form-control" v-model="field.type">
                            <option v-for="type in Object.entries(field_types)" :value="type[0]">{{ type[1] }}</option>
                        </select>
                    </form-group-4-8>


                    <div class="form-group row">
                        <div class="col-md-4">
                            <strong>Код категории</strong>
                        </div>
                        <div class="col-md-8">
                            <input class="form-control" v-model="field.category"/>
                        </div>
                    </div>

                    <div v-if="field.type == 'integer'">
                        <hr>
                        <div class="form-group row">
                            <div class="col-md-4">
                                <strong>Ограничения</strong>
                            </div>
                            <div class="col-md-3">
                                От <input type="number" pattern="\d*" class="form-control" v-model="field.params.min"/>
                            </div>
                            <div class="col-md-3">
                                до <input type="number" pattern="\d*" class="form-control" v-model="field.params.max"/>
                            </div>
                        </div>
                    </div>

                    <div v-if="field.type == 'float'">
                        <hr>
                        <div class="form-group row">
                            <div class="col-md-4">
                                <strong>Ограничения</strong>
                            </div>
                            <div class="col-md-3">
                                От <input type="number" step="0.01" class="form-control" v-model="field.params.min"/>
                            </div>
                            <div class="col-md-3">
                                до <input type="number" step="0.01" class="form-control" v-model="field.params.max"/>
                            </div>
                        </div>
                    </div>

                    <div v-if="field.type == 'radio'">
                        <hr>

                        <strong>Варианты ответа</strong>

                        <div class="form-group row" v-for="(variant, j) in field.params.variants">
                            <div class="col-md-4">
                                <small class="text-mutted">Код категории</small><br>
                                <input type="text" class="form-control" v-model="variant.category"/>
                            </div>
                            <div class="col-md-6">
                                <small class="text-mutted">Текст варианта</small><br>
                                <input type="text" class="form-control" v-model="variant.text"/>
                            </div>
                            <a href="#" v-if="field.params.variants.length > 1" @click="remove_variant(field, j)">Удалить
                                вариант</a>
                        </div>
                        <a class="btn btn-primary btn-sm" @click="add_variant(field)">Добавить вариант</a>

                    </div>

                    <a class="btn btn-danger btn-sm" @click="remove_field(i)">Удалить вопрос</a>
                </div>
            </div>

            <p class="text-center"><a href="#" class="btn btn-primary btn-sm" @click="add_field()">Добавить поле</a></p>
        </div>

        <button class="btn btn-success btn-lg" @click="save()">Сохранить</button>
    </div>
</template>

<script>

import Card from "../common/Card";
import FormGroup48 from "../common/FormGroup-4-8";

const axios = require('axios');

export default {
    name: "FormEditor",
    components: {FormGroup48, Card},
    props: {
        data: {
            required: false,
        }
    },
    methods: {
        go_back: function () {
            Event.fire('back-to-dashboard');
        },
        create_empty_form: function () {
            return {
                fields: [],
                timetable: {
                    mode: 'daily',
                    points: [{
                        hour: '',
                        minute: ''
                    }]
                }
            };
        },
        clear_params: function (field) {
            field.params = {};

            if (field.type == 'radio') {
                field.params.variants = [{text: '', category: ''}]
            }
        },
        clear_time_points: function () {
            this.form.timetable.points = []
            this.add_time_point();
        },
        add_field: function () {
            this.form.fields.push({
                type: 'integer',
                params: {}
            });
        },
        add_variant: function (field) {
            field.params.variants.push({text: '', category: ''});
            this.$forceUpdate()
        },
        remove_variant: function (field, index) {
            field.params.variants.splice(index, 1);
            this.$forceUpdate()
        },
        remove_field: function (index) {
            this.form.fields.splice(index, 1);
        },
        add_time_point: function () {
            if (this.form.timetable.mode == 'manual') {
                return;
            }
            if (this.form.timetable.mode == 'daily') {
                this.form.timetable.points.push({
                    hour: '',
                    minute: ''
                })
            } else {
                this.form.timetable.points.push({
                    day: '',
                    hour: '',
                    minute: ''
                })
            }
        },
        remove_time_point: function (index) {
            this.form.timetable.points.splice(index, 1);
        },
        check: function () {
            this.errors = [];
            if (!this.form.title) {
                this.errors.push('Укажите название анкеты')
            }
            if (this.form.show_button && !this.form.button_title) {
                this.errors.push('Укажите название для кнопки')
            }
            if (this.form.timetable.mode != 'manual') {
                let prepare_point = (point) => {
                    point.hour = parseInt(point.hour);
                    point.minute = parseInt(point.minute);
                    if (point.day) point.day = parseInt(point.day);
                    return point
                }
                this.form.timetable.points = this.form.timetable.points.map(prepare_point);

                let general_validate = (point) => {
                    if (!point.hour || !point.minute) return true;
                    if (point.hour < 0 || point.hour > 23) return true;
                    if (point.minute < 0 || point.minute > 59) return true;
                    return false;
                }
                let validate_point = general_validate;
                if (this.form.timetable.mode == 'weekly') {
                    validate_point = (point) => {
                        if (general_validate(point)) return true;
                        if (!point.day || point.day < 0 || point.day > 6) return true;
                        return false;
                    }
                }
                if (this.form.timetable.mode == 'monthly') {
                    validate_point = (point) => {
                        if (general_validate(point)) return true;
                        if (!point.day || point.day < 1 || point.day > 31) return true;
                        return false;
                    }
                }

                if (this.form.timetable.points.filter(point => validate_point(point)).length > 0) {
                    console.log(this.form.timetable.points.filter(point => validate_point(point)))
                    this.errors.push('Проверьте корректность расписания')
                }
            }

            if (this.form.fields.length == 0) {
                this.errors.push('Добавьте хотя бы один вопрос')
            }

            if (this.errors.length != 0) {
                return false;
            } else {
                return true;
            }

        },
        save: function () {
            if (this.check())
            {
                axios.post(this.url('/api/create_form')).then(this.process_load_answer).catch(this.process_save_error);
            }
        },
        process_save_answer: function (response) {
            this.form.patient_id = response.data.patient_id
            this.form.contract_id = response.data.contract_id
            Event.fire('form-created', this.form)
            this.go_back();
        },
        process_save_error: function (response)
        {
            this.errors.push('Ошибка сохранения');
        }
    },
    data() {
        return {
            errors: [],
            form: {}
        }
    },
    created() {
        if (!this.data) {
            this.form = this.create_empty_form()
        } else {
            this.form = this.data;
        }

    }
}
</script>

<style scoped>

</style>
