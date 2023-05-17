<template>
    <card class="col-lg-6 col-md-6" :class="medicine.canceled_at ? 'text-muted' : ''"
          :image="medicine.canceled_at ? images.canceled_medicine : images.medicine">

        <strong class="card-title">{{ medicine.title }}</strong>
        <small v-if="medicine.dose"><strong>Дозировка: </strong>{{ medicine.dose }}<br></small>
        <small v-if="medicine.rules"><strong>Правила приема: </strong>{{ medicine.rules }}<br></small>
        <br>

        <small><i>{{ tt_description(medicine.timetable) }}</i></small>
        <br>

        <small v-if="medicine.sent">
            Подтверждено {{ medicine.done }} раз(а) / отправлено {{ medicine.sent }} раз(а) за последний месяц
        </small>
        <small v-else-if="!medicine.is_template">Пока не отправлялось<br></small>
        <br>

        <small v-if="medicine.canceled_at"><strong>Отменено: </strong>{{ medicine.canceled_at }}<br></small>
        <!--История предписаний-->
        <div v-if="medicine.prescription_history">
            <input class="btn btn-link btn-sm text-muted shadow-none" type="button"
                   data-toggle="collapse" style="padding: 0" aria-expanded="false" value="История предписаний"
                   :data-target="`#collapse-medicine-${medicine.id}`"
                   :aria-controls="`collapse-medicine-${medicine.id}`">
            <div class="collapse" :id="`collapse-medicine-${medicine.id}`">
                <div class="card card-body"
                     style="background-color: transparent; border-color: transparent; padding: 0;">
                    <table class="table table-hover" style="font-size: small">
                        <colgroup>
                            <col span="1" style="width: 15%;">
                            <col span="1" style="width: 25%;">
                            <col span="1" style="width: 60%;">
                        </colgroup>
                        <thead>
                        <tr class="table-info">
                            <th scope="col">Дата</th>
                            <th scope="col">Состояние</th>
                            <th scope="col">Комментарий</th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr v-for="record in medicine.prescription_history.records">
                            <th scope="row" style="text-align: left;">{{ record.date }}</th>
                            <td>{{ record.description }}</td>
                            <td>
                                <textarea class="form-control form-control-sm" v-model="record.comment"
                                          :disabled="medicine.contract_id != current_contract_id">
                                </textarea>
                            </td>
                        </tr>
                        </tbody>
                    </table>

                    <div v-if="medicine.contract_id == current_contract_id">
                        <button class="btn btn-success btn-sm" :disabled="flags.lock_btn" @click="save_history()">
                            Сохранить
                        </button>
                        <br>
                        {{ response }}
                    </div>

                </div>
            </div>
        </div>

        <!--действия-->
        <div v-if="!medicine.is_template">
            <div v-if="medicine.contract_id == current_contract_id && !medicine.canceled_at">
                <a href="#" @click="edit_medicine()">Редактировать</a>
                <a href="#" @click="delete_medicine()">Отменить</a>
            </div>
            <div v-else-if="medicine.contract_id == current_contract_id && medicine.canceled_at">
                <a href="#" @click="resume_medicine()">Возобновить</a>
            </div>
            <div v-else>
                <small>Добавлен в другом контракте.</small>
            </div>
            <div v-if="medicine.is_created_by_patient">
                <small>Добавлен пациентом.</small>
            </div>
            <br>
            <small v-if="!empty(medicine.template_id)" class="text-muted">
                ID шаблона: {{medicine.template_id }}
            </small>
        </div>
        <div v-else>
            <a href="#" v-if="!is_attached" @click="attach_medicine()">Подключить</a>
            <small v-else class="text-muted">Препарат назначен<br></small>
            <a href="#" v-if="is_admin || patient.info.doctor_id == medicine.doctor_id"
               @click="edit_medicine()">Редактировать</a>
            <a href="#" v-if="is_admin || patient.info.doctor_id == medicine.doctor_id"
               @click="delete_medicine()">Удалить</a>
            <br>
            <small class="text-muted">ID: {{ medicine.id }}</small>
            <small class="text-muted" v-if="is_admin && medicine.doctor_id">Doctor ID: {{ medicine.doctor_id }}</small>
            <small class="text-muted" v-if="is_admin && medicine.clinic_id">Clinic ID: {{ medicine.doctor_id }}</small>
        </div>
    </card>
</template>

<script>
import Card from "../../common/Card";

export default {
    name: "MedicineCard",
    props: {
        medicine: {required: true},
        patient: {required: false}
    },
    components: {Card},
    data() {
        return {
            flags: {
                lock_btn: false
            },
            response: ''
        }
    },
    computed: {
        is_attached() {
            return (this.patient.medicines.filter(m => m.template_id == this.medicine.id).length +
                this.patient.canceled_medicines.filter(m => m.template_id == this.medicine.id).length) != 0
        },
    },
    methods: {
        save_history: function () {
            this.flags.lock_btn = true
            this.$forceUpdate()

            this.axios.post(this.direct_url('/api/settings/medicine_history'), this.medicine).then(r => {
                this.response = 'Данные успешно сохранены.'
                this.flags.lock_btn = false
                this.$forceUpdate()
            }).catch(r => {
                this.response = 'Ошибка сохранения'
                this.flags.lock_btn = false
                this.$forceUpdate()
            });
        },
        edit_medicine: function () {
            Event.fire('edit-medicine', this.medicine)
        },
        delete_medicine: function () {
            this.$confirm({
                message: `Вы уверены, что хотите отменить препарат ` + this.medicine.title + `?`,
                button: {
                    no: 'Нет',
                    yes: 'Да, отменить'
                },
                callback: confirm => {
                    if (confirm) {
                        if (!this.medicine.prescription_history)
                            this.medicine.prescription_history = {
                                records: []
                            }
                        this.medicine.prescription_history.records.push({
                            description: 'Отменен',
                            comment: '',
                            date: new Date().toLocaleDateString()
                        })
                        this.$forceUpdate()

                        this.axios.post(this.direct_url('/api/settings/delete_medicine'), this.medicine)
                            .then((response) => Event.fire('medicine-deleted', response.data.deleted_id));
                    }
                }
            })
        },
        resume_medicine: function () {
            this.$confirm({
                message: `Вы уверены, что хотите возобновить препарат ` + this.medicine.title + `?`,
                button: {
                    no: 'Нет',
                    yes: 'Да, возобновить'
                },
                callback: confirm => {
                    if (confirm) {
                        this.medicine.prescription_history.records.push({
                            description: 'Возобновлен',
                            comment: '',
                            date: new Date().toLocaleDateString()
                        })
                        this.$forceUpdate()
                        this.axios.post(this.direct_url('/api/settings/resume_medicine'), this.medicine)
                            .then((response) => Event.fire('medicine-resumed', response.data.resumed_id));
                    }
                }
            })
        },
        attach_medicine: function () {
            Event.fire('attach-medicine-from-card', this.medicine)
        },
    }
}
</script>

<style scoped>
p {
    margin-top: 5px;
    margin-bottom: 5px;
}

h5 {
    margin-bottom: 10px;
    margin-top: 10px;
    font-size: 1.15rem;
}

small {
    font-size: 90%;
}

.card a {
    font-size: 90% !important;
}

</style>
