<template>
    <card class="col-lg-3 col-md-4" :class="is_expired ? 'text-muted' : ''"
          :image="is_expired ? images.expired_examination : images.examination">
        <strong class="card-title">
            {{ examination.title }}
        </strong>
        <small v-if="examination.doctor_description"> {{ examination.doctor_description }}<br></small>
        <small v-if="!examination.no_expiration"><i>Срок действия: {{ examination.expiration_days }} дн.</i><br></small>
        <small v-else><i>Бессрочно</i><br></small>
        <small v-if="examination.upload_date" class="text-muted">
            <img :src="images.file" height="20"/>
            <a href="#" @click="get_files()">Скачать файлы ({{ format_date(examination.upload_date) }})</a><br>
        </small>
        <div v-if="!examination.is_template">
            <small v-if="examination.deadline_date && !is_expired && !examination.upload_date">
                До крайнего срока осталось <b>{{ days_left }} дн.</b><br>
            </small>

            <small v-if="examination.attach_date && !is_expired" class="text-muted">
                Назначено {{ format_date(examination.attach_date) }}<br>
            </small>

            <div v-if="examination.contract_id == current_contract_id && !is_expired">
                <a href="#" @click="edit_examination()">Редактировать</a>
                <a href="#" @click="delete_examination()">Отменить</a>
            </div>
            <div v-else-if="examination.contract_id !== current_contract_id">
                <small>Добавлено в другом контракте.</small>
            </div>

            <small v-if="!empty(examination.template_id)" class="text-muted">ID шаблона: {{
                    examination.template_id
                }}</small>
        </div>
        <div v-else>
            <a href="#" @click="attach_examination()">Назначить</a>
            <a href="#" v-if="is_admin" @click="edit_examination()">Редактировать</a><br>
            <a href="#" v-if="is_admin" @click="delete_examination()">Удалить</a>
            <small class="text-muted" v-if="is_admin">ID: {{ examination.id }}</small>
        </div>
    </card>
</template>

<script>
import Card from "../../common/Card";
import * as moment from "moment/moment";
import downloadjs from "downloadjs";

export default {
    name: "ExaminationCard",
    components: {Card},
    props: {
        examination: {required: true},
        patient: {required: true}
    },
    computed: {
        is_expired() {
            if (this.examination.is_template || this.examination.no_expiration) return false
            return moment(this.examination.deadline_date + ' 23:59', 'YYYY-MM-DD hh:mm') < moment()
        },
        days_left() {
            let len = moment(this.examination.deadline_date, 'YYYY-MM-DD').diff(moment())
            return Math.ceil(moment.duration(len).asDays())
        }
    },
    methods: {
        format_date: function (date) {
            let d = date.split('-')
            return `${d[2]}.${d[1]}.${d[0]}`
        },
        attach_examination: function () {
            Event.fire('attach-examination-from-card', this.examination)
        },
        edit_examination: function () {
            Event.fire('edit-examination', this.examination)
        },
        delete_examination: function () {
            this.$confirm({
                message: `Вы уверены, что хотите удалить обследование?`,
                button: {
                    no: 'Нет',
                    yes: 'Да, удалить'
                },
                callback: confirm => {
                    if (confirm) {
                        this.axios.post(this.direct_url('/api/settings/delete_examination'), this.examination)
                            .then((response) => Event.fire('examination-deleted', response.data.deleted_id));
                    }
                }
            })
        },
        get_files: function () {
            this.axios.get(this.direct_url('/api/settings/get_examination_files/' + this.examination.id))
                .then((response) => {
                    response.data.forEach((file, i) => {
                        let filename = `${this.patient.info.name}_${this.examination.title}(${this.examination.upload_date})`
                        downloadjs(`data:${file.type};base64,${file.base64}`, filename, file.type);
                    })
                })
        }
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
