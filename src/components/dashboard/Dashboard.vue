<template>
    <div>
        <algorithm-settings/>
        <div v-if="state == 'main'">

            <h5>Опросники</h5>

            <div class="row">
                <card v-for="(form, i) in patient.forms" :key="form.id" class="col-lg-3 col-md-4"
                      :image="images.form">
                    <h6>{{ form.title }}</h6>
                    <small>{{ form.doctor_description }}</small><br>
                    <small><i>{{ tt_description(form.timetable) }}</i></small><br>
                    <div v-if="form.contract_id == current_contract_id">
                        <a href="#" @click="edit_form(form)">Редактировать</a>
                        <a href="#" @click="delete_form(form)">Удалить</a>
                        <a target="_blank" :href="preview_form_url(form)">Просмотр</a>
                    </div>
                    <div v-else>
                        <small>Добавлен в другом контракте.</small>
                    </div>

                    <small v-if="!empty(form.template_id)" class="text-muted">ID шаблона: {{ form.template_id }}</small>
                    <small v-else class="text-muted">ID опросника: {{ form.id }}</small>
                </card>
            </div>

            <button class="btn btn-primary btn-sm" @click="state = 'form_templates'">Выбрать или создать опросник
            </button>

            <hr>

            <h5>Лекарства</h5>

            <div class="row">
                <card v-for="(medicine, i) in patient.medicines" :key="medicine.id" :image="images.medicine"
                      class="col-lg-3 col-md-4">
                    <h6>{{ medicine.title }}</h6>
                    <small>{{ medicine.rules }}</small><br>
                    <small><i>{{ tt_description(medicine.timetable) }}</i></small><br>
                    <div v-if="medicine.contract_id == current_contract_id">
                        <a href="#" @click="edit_medicine(medicine)">Редактировать</a>
                        <a href="#" @click="delete_medicine(medicine)">Удалить</a>
                    </div>
                    <div v-else>
                        <small>Добавлен в другом контракте.</small>
                    </div>

                    <small v-if="!empty(medicine.template_id)" class="text-muted">ID шаблона: {{ medicine.template_id }}</small>

                </card>
            </div>

            <button class="btn btn-primary btn-sm" @click="create_medicine()">Назначить лекарство
            </button>

            <button v-if="is_admin" class="btn btn-info btn-sm" @click="state = 'medicine_templates'">Управление
                шаблонами
            </button>

            <hr>

            <h5>Алгоритмы</h5>

            <div class="row">
                <card v-for="(algorithm, i) in patient.algorithms" :key="algorithm.id" :image="images.algorithm"
                      class="col-lg-3 col-md-4">
                    <h6>{{ algorithm.title }}</h6>
                    <small>{{ algorithm.description }}</small><br>
                    <small v-html="alg_description(algorithm)"></small>
                    <div v-if="algorithm.contract_id == current_contract_id">
                        <a href="#" @click="edit_algorithm(algorithm)">Редактировать</a>
                        <a href="#" @click="delete_algorithm(algorithm)">Удалить</a>
                    </div>
                    <div v-else>
                        <small>Добавлен в другом контракте.</small>
                    </div>

                    <small v-if="!empty(algorithm.template_id)" class="text-muted">ID шаблона: {{ algorithm.template_id }}</small>

                </card>
            </div>

            <button class="btn btn-primary btn-sm" @click="state = 'algorithm_templates'">Выбрать или создать
                алгоритм
            </button>

        </div>
        <div v-if="state == 'form_templates'">
            <div class="alert alert-info" role="alert">
                <h4 class="alert-heading">Выбор опросника</h4>
                <p>Выберите опросник из списка ниже. В дальнейшем вы сможете изменить расписание, описание и даже сами
                    вопросы.</p>
            </div>

            <div class="row">
                <card v-for="(form, i) in templates.forms" :key="form.id" class="col-lg-3 col-md-4"
                      :image="images.form">
                    <h6>{{ form.title }}</h6>
                    <small>{{ form.doctor_description }}</small><br>
                    <small><i>{{ tt_description(form.timetable) }}</i></small><br>
                    <a href="#" @click="attach_form(form)">Подключить</a>
                    <a href="#" v-if="is_admin" @click="edit_form(form)">Редактировать</a>
                    <a href="#" v-if="is_admin" @click="delete_form(form)">Удалить</a>
                    <a target="_blank" :href="preview_form_url(form)">Просмотр</a>

                    <small v-if="form.algorithm_id"><br><b>Связанный алгоритм:</b> {{ find_algorithm(form.algorithm_id).title }}</small>

                    <br>

                    <small class="text-muted">ID: {{ form.id }}</small>
                </card>
                <div v-if="!templates.forms.length" class="col-md-12">
                    <p style="margin-bottom: 15px;">Список шаблонов пуст.</p>
                </div>
            </div>

            <button class="btn btn-primary btn-sm" @click="create_form()">Добавить свой опросник</button>
            <button class="btn btn-danger btn-sm" @click="state = 'main'">Назад</button>

        </div>
        <div v-if="state == 'medicine_templates'">
            <h3>Шаблоны лекарств</h3>

            <div class="alert alert-info" role="alert">
                <h4 class="alert-heading">Шаблоны лекарств</h4>
                <p>Выберите лекарство или создайте новое.</p>
            </div>

            <div class="row">
                <card v-for="(medicine, i) in templates.medicines" :key="medicine.id" :image="images.medicine"
                      class="col-lg-3 col-md-4">
                    <h6>{{ medicine.title }}</h6>
                    <small>{{ medicine.rules }}</small><br>
                    <small><i>{{ tt_description(medicine.timetable) }}</i></small><br>
                    <a href="#" @click="attach_medicine(medicine)">Подключить</a>
                    <a href="#" v-if="is_admin" @click="edit_medicine(medicine)">Редактировать</a>
                    <a href="#" v-if="is_admin" @click="delete_medicine(medicine)">Удалить</a>

                    <br>

                    <small class="text-muted">ID: {{ medicine.id }}</small>
                </card>
                <div v-if="!templates.medicines.length" class="col-md-12">
                    <p style="margin-bottom: 15px;">Список шаблонов пуст.</p>
                </div>

            </div>

            <button class="btn btn-primary btn-sm" @click="create_medicine()">Добавить</button>
            <button class="btn btn-danger btn-sm" @click="state = 'main'">Назад</button>

        </div>
        <div v-if="state == 'algorithm_templates'">

            <div class="alert alert-info" role="alert">
                <h4 class="alert-heading">Выбор алгоритма</h4>
                <p>Выберите алгоритм из списка ниже. В дальнейшем вы сможете посмотреть подробную схему его работы, но изменять ее без опыта не рекомендуется.</p>
            </div>


            <div class="row">
                <card v-for="(algorithm, i) in templates.algorithms" :key="algorithm.id" :image="images.algorithm"
                      class="col-lg-3 col-md-4">
                    <h6>{{ algorithm.title }}</h6>
                    <small>{{ algorithm.description }}</small><br>
                    <small v-html="alg_description(algorithm)"></small>
                    <a href="#" v-if="need_filling(algorithm)" @click="setup_algorithm(algorithm)">Настроить и подключить</a>
                    <a href="#" v-else @click="attach_algorithm(algorithm)">Подключить</a>
                    <a href="#" v-if="is_admin" @click="edit_algorithm(algorithm)">Редактировать</a>
                    <a href="#" v-if="is_admin" @click="delete_algorithm(algorithm)">Удалить</a>

                    <br>
                    <small class="text-muted">ID: {{ algorithm.id }}</small>

                </card>

                <div v-if="!templates.algorithms.length" class="col-md-12">
                    <p style="margin-bottom: 15px;">Список шаблонов пуст.</p>
                </div>
            </div>


            <button class="btn btn-primary btn-sm" @click="create_algorithm()">Добавить</button>
            <button class="btn btn-danger btn-sm" @click="state = 'main'">Назад</button>

        </div>

    </div>

</template>

<script>

import Card from "../common/Card";
import AlgorithmSettings from "./AlgorithmSettings";

export default {
    name: "Dashboard",
    components: {AlgorithmSettings, Card},
    props: {
        patient: {
            required: true
        },
        templates: {
            required: true
        }
    },
    data: function () {
        return {
            state: 'main'
        }
    },
    methods: {
        find_algorithm: function (id) {
            return this.templates.algorithms.filter(t => t.id == id)[0]
        },
        attach_form: function (form) {
            let attach = () => {
                Event.fire('attach-form', form)

                if (!this.empty(form.algorithm_id)) {
                    let algorithm = this.find_algorithm(form.algorithm_id);

                    if (this.need_filling(algorithm)) this.setup_algorithm(algorithm)
                    else this.attach_algorithm(algorithm)
                }
            }

            if (this.patient.forms.filter(f => f.template_id == form.id).length != 0) {
                this.$confirm({
                    message: `Пациенту уже подключен опросник на основе шаблона ` + form.title + `. Подключить еще один?`,
                    button: {
                        no: 'Нет',
                        yes: 'Да'
                    },
                    callback: confirm => {
                        if (confirm) {
                            attach()
                        }
                    }
                })
            } else {
                attach()
            }

        },
        ask_for_alg_doubling: function (title, F) {
            this.$confirm({
                message: `Пациенту уже подключен алгоритм на основе шаблона ` + title + `. Подключить еще один?`,
                button: {
                    no: 'Нет',
                    yes: 'Да'
                },
                callback: confirm => {
                    if (confirm) {
                        F()
                    }
                }
            })
        },
        setup_algorithm: function (algorithm) {
            let setup = () => {
                this.$modal.show('algorithm-settings', {algorithm: algorithm})
            }
            if (this.patient.algorithms.filter(f => f.template_id == algorithm.id).length != 0) this.ask_for_alg_doubling(algorithm.title, setup)
            else setup()
        },
        attach_algorithm: function (algorithm) {
            let attach = () => {
                Event.fire('attach-algorithm', algorithm)
            }
            if (this.patient.algorithms.filter(f => f.template_id == algorithm.id).length != 0) this.ask_for_alg_doubling(algorithm.title, attach)
            else attach()
        },
        attach_medicine: function (medicine) {
            Event.fire('attach-medicine', medicine)
        },
        create_form: function () {
            Event.fire('navigate-to-create-form-page')
        },
        edit_form: function (form) {
            Event.fire('edit-form', form)
        },
        delete_form: function (form) {
            this.$confirm(
                {
                    message: `Вы уверены, что хотите удалить опросник ` + form.title + `?`,
                    button: {
                        no: 'Нет',
                        yes: 'Да, удалить'
                    },
                    callback: confirm => {
                        if (confirm) {
                            this.axios.post(this.url('/api/settings/delete_form'), form).then(this.process_delete_form_answer);
                        }
                    }
                }
            )
        },
        preview_form_url: function (form) {
            return this.url('/form/' + form.id)
        },
        process_delete_form_answer: function (response) {
            if (response.data.deleted_id) {
                this.patient.forms = this.patient.forms.filter(f => f.id != response.data.deleted_id)
                this.templates.forms = this.templates.forms.filter(f => f.id != response.data.deleted_id)
            }
        },
        create_medicine: function () {
            Event.fire('navigate-to-create-medicine-page')
        },
        edit_medicine: function (medicine) {
            Event.fire('edit-medicine', medicine)
        },
        delete_medicine: function (medicine) {
            this.$confirm(
                {
                    message: `Вы уверены, что хотите удалить препарат ` + medicine.title + `?`,
                    button: {
                        no: 'Нет',
                        yes: 'Да, удалить'
                    },
                    callback: confirm => {
                        if (confirm) {
                            this.axios.post(this.url('/api/settings/delete_medicine'), medicine).then(this.process_delete_medicine_answer);
                        }
                    }
                }
            )
        },
        create_algorithm: function () {
            Event.fire('navigate-to-create-algorithm-page')
        },
        edit_algorithm: function (algorithm) {
            Event.fire('edit-algorithm', algorithm)
        },
        delete_algorithm: function (algorithm) {
            this.$confirm(
                {
                    message: `Вы уверены, что хотите удалить алгоритм ` + algorithm.title + `?`,
                    button: {
                        no: 'Нет',
                        yes: 'Да, удалить'
                    },
                    callback: confirm => {
                        if (confirm) {
                            this.axios.post(this.url('/api/settings/delete_algorithm'), algorithm).then(this.process_delete_algorithm_answer);
                        }
                    }
                }
            )
        },
        process_delete_medicine_answer: function (response) {
            if (response.data.deleted_id) {
                this.patient.medicines = this.patient.medicines.filter(m => m.id != response.data.deleted_id)
                this.templates.medicines = this.templates.medicines.filter(m => m.id != response.data.deleted_id)
            }
        },
        process_delete_algorithm_answer: function (response) {
            if (response.data.deleted_id) {
                this.patient.algorithms = this.patient.algorithms.filter(m => m.id != response.data.deleted_id)
                this.templates.algorithms = this.templates.algorithms.filter(m => m.id != response.data.deleted_id)
            }
        },
    },
    mounted() {
        Event.listen('dashboard-to-main', () => this.state = 'main');
        Event.listen('home', () => this.state = 'main');
    }
}
</script>

<style scoped>
.col-xl-2, .col-md-4 {
    padding-right: 0px;
}

p {
    margin-top: 5px;
    margin-bottom: 5px;
}

h5 {
    margin-bottom: 10px;
    margin-top: 10px;
}
</style>
