<template>
    <div>
        <div style="margin-top: 15px;" class="alert alert-info" role="alert">
            Напоминания о загрузке обследования приходят заблаговременно.
        </div>
        <div v-if="examinations.length">
            <div v-if="!mobile">
                <div class="row font-weight-bold" style="padding: 0 1.25rem;">
                    <span class="col-4">Обследование</span>
                    <span class="col-2">Пройти после</span>
                    <span class="col-2">Загрузить до</span>
                </div>

                <div v-for="examination in examinations">
                    <card :class="!examination.expired ? '' : 'text-muted'"
                          :image="!examination.expired ? images.examination : images.expired_examination">
                        <div class="row">
                            <span class="col-4">
                                <b :style="!examination.expired ? 'color: #006c88' : ''">{{ examination.title }}</b><br>
                                {{ examination.patient_description }}
                            </span>
                            <span class="col-2">
                                {{ format_date(examination.notification_date) }} <br>
                                <small v-if="!examination.active && !examination.expired">
                                    Осталось {{ days_left(examination.notification_date) }} дн.
                                </small>
                            </span>
                            <span class="col-2">
                                {{ format_date(examination.deadline_date) }} <br>
                                <small v-if="!examination.expired">Осталось {{ days_left(examination.deadline_date) }} дн.</small>
                            </span>
                            <div class="col">
                                <button class="btn btn-sm btn-primary" v-if="examination.active"
                                        @click="load_examination(examination)">
                                    Загрузить
                                </button>
                                <span
                                    v-else-if="examination.expired && !examination.upload_date">Срок загрузки истек<br></span>
                                <span v-else-if="!examination.upload_date">Загрузка сейчас недоступна<br></span>
                                <div v-if="examination.upload_date">
                                    <small>
                                        Срок действия
                                        <span
                                            v-if="days_left(examination.upload_date, examination.expiration_days) >= 0">истечет через {{
                                                days_left(examination.upload_date, examination.expiration_days)
                                            }} дн. </span>
                                        <span v-else>истек</span>
                                    </small>
                                    <br>
                                    <img :src="images.file" height="20"/>
                                    <a href="#" @click="get_files(examination)">Скачать файлы
                                        ({{ format_date(examination.upload_date) }})</a>
                                </div>
                            </div>
                        </div>
                    </card>
                </div>
            </div>

            <div v-else>
                <div v-for="examination in examinations">
                    <card :class="!examination.expired ? '' : 'text-muted'"
                          :image="!examination.expired ? images.examination : images.expired_examination">
                        <span :style="!examination.expired ? 'color: #006c88' : ''">{{ examination.title }}</span><br>
                        {{ examination.patient_description }}<br>
                        <span>Пройти после <b>{{ format_date(examination.notification_date) }}</b></span>
                        <i v-if="!examination.active && !examination.expired">(осталось
                            {{ days_left(examination.notification_date) }} дн.)</i>
                        <br>
                        <span>Загрузить до <b>{{ format_date(examination.deadline_date) }}</b></span>
                        <i v-if="!examination.expired">(осталось {{ days_left(examination.deadline_date) }} дн.)</i>
                        <br>
                        <button class="btn btn-sm btn-primary" v-if="examination.active"
                                @click="load_examination(examination)">
                            Загрузить
                        </button>
                        <span
                            v-else-if="examination.expired && !examination.upload_date"><br>Срок загрузки истек<br></span>
                        <span v-else-if="examination.upload_date"><br>Загрузка сейчас недоступна<br></span>
                        <div v-if="examination.upload_date">
                            <span>
                                Срок действия
                                <span v-if="days_left(examination.upload_date, examination.expiration_days) >= 0">истечет через {{
                                        days_left(examination.upload_date, examination.expiration_days)
                                    }} дн. </span>
                                <span v-else>истек</span>
                            </span><br>
                            <img :src="images.file" height="20"/>
                            <a href="#" @click="get_files(examination)">Скачать файлы
                                ({{ format_date(examination.upload_date) }})</a>
                        </div>
                        <br>
                    </card>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import Card from "../common/Card";
import downloadjs from "downloadjs";
import * as moment from "moment/moment";

export default {
    name: "ExaminationsList",
    components: {Card},
    props: {
        data: {required: true}
    },
    data() {
        return {
            flags: {
                lock_btn: false
            },
            examinations: [],
            errors: []
        }
    },
    methods: {
        format_date: function (date) {
            let d = date.split('-')
            return `${d[2]}.${d[1]}.${d[0]}`
        },
        days_left: function (date, add_days = 0) {
            let len = moment(date, 'YYYY-MM-DD').add(add_days, 'days').diff(moment())
            return Math.ceil(moment.duration(len).asDays())
        },
        load_examination: function (examination) {
            if (examination.record_id && !examination.files) {
                this.axios.get(this.direct_url('/api/examination/' + examination.id))
                    .then((response) => {
                        examination.files = response.data.files
                        Event.fire('navigate-to-load-examination-page', examination)
                    });
            } else {
                Event.fire('navigate-to-load-examination-page', examination)
            }
        },
        get_files: function (examination) {
            this.axios.get(this.direct_url('/api/settings/get_examination_files/' + examination.id))
                .then((response) => {
                    response.data.forEach((file) => {
                        let filename = `${this.data.info.name}_${examination.title}(${examination.upload_date})`
                        downloadjs(`data:${file.type};base64,${file.base64}`, filename, file.type);
                    })
                })
        }
    },
    created() {
        let today = new Date()
        today.setHours(23, 59, 59)

        this.examinations = this.data.examinations.concat(this.data.expired_examinations)
        this.examinations = this.examinations.map((examination) => {
            examination.date = new Date(examination.notification_date)
            examination.expired = new Date(examination.deadline_date) < today
            examination.active = examination.date < today && new Date(examination.deadline_date) > today
            return examination
        })

        Event.listen('examination-loaded', (examination) => {
            let ex = this.examinations.filter((e) => e.id == examination.id)[0]
            ex.upload_date = examination.upload_date
        })
    }
}
</script>

<style scoped>
.card-body {
    padding: 10px !important;
}
</style>
