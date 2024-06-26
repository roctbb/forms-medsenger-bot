<template>
    <div>
        <div style="margin-top: 15px;" class="alert alert-info" role="alert">
            Напоминания о загрузке обследования приходят заблаговременно.
        </div>
        <div class="row">
            <input class="form-check" type="checkbox" v-model="flags.show_expired">
            <div class="col" style="margin-top: 5px">
                Показать обследования, срок загрузки которых истек
            </div>
        </div>

        <div v-if="examinations.length">
            <div v-if="!mobile">
                <div class="row font-weight-bold" style="padding: 0 1.25rem;">
                    <span class="col-4">Обследование</span>
                    <span class="col-2">Пройти после</span>
                    <span class="col-2">Загрузить до</span>
                </div>

                <div v-for="examination in filtered_examinations">
                    <card :class="!examination.expired ? '' : 'text-muted'"
                          :image="!examination.expired ? images.examination : images.expired_examination">
                        <div class="row">
                            <span class="col-4">
                                <b :style="!examination.expired ? 'color: #006c88' : ''">{{ examination.title }}</b><br>
                                {{ examination.patient_description }}
                            </span>
                            <span class="col-2">
                                {{ format_date(examination.notification_date) }} <br>
                                <small
                                    v-if="!examination.active && !examination.expired && days_left(examination.notification_date) >= 0">
                                    Осталось {{ days_left(examination.notification_date) }} дн.
                                </small>
                            </span>
                            <span class="col-2">
                                {{ format_date(examination.deadline_date) }} <br>
                                <small v-if="!examination.expired && days_left(examination.deadline_date) >= 0">Осталось {{
                                        days_left(examination.deadline_date)
                                    }} дн.</small>
                            </span>
                            <div class="col">
                                <button class="btn btn-sm btn-primary" v-if="examination.active"
                                        @click="load_examination(examination)">
                                    Загрузить
                                </button>
                                <div
                                    v-else-if="examination.expired && !examination.upload_date">Срок загрузки истек<br>
                                    <button class="btn btn-sm btn-secondary"
                                            @click="load_examination(examination)">
                                        Все равно загрузить
                                    </button>
                                    <br>
                                </div>
                                <span v-else-if="!examination.active">
                                    Срок загрузки еще не наступил или уже прошел<br>
                                    <button class="btn btn-sm btn-secondary" @click="load_examination(examination)">Все равно загрузить</button>
                                </span>
                                <div v-if="examination.upload_date">
                                    <small>
                                        <span v-if="examination.no_expiration">Действует бессрочно</span>
                                        <span
                                            v-else-if="days_left(examination.upload_date, examination.expiration_days) >= 0">
                                            Срок действия истечет через {{
                                                days_left(examination.upload_date, examination.expiration_days)
                                            }} дн.
                                        </span>
                                        <span v-else>Срок действия истек</span>
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
                <div v-for="examination in filtered_examinations">
                    <card :class="!examination.expired ? '' : 'text-muted'"
                          :image="!examination.expired ? images.examination : images.expired_examination">
                        <span :style="!examination.expired ? 'color: #006c88' : ''">{{ examination.title }}</span><br>
                        {{ examination.patient_description }}<br>
                        <span>Пройти после <b>{{ format_date(examination.notification_date) }}</b></span>
                        <i v-if="!examination.active && !examination.expired">(осталось
                            {{ days_left(examination.notification_date) }} дн.)</i>
                        <br>
                        <span>Загрузить до <b>{{ format_date(examination.deadline_date) }}</b></span>
                        <i v-if="!examination.expired && days_left(examination.deadline_date) >= 0">(осталось
                            {{ days_left(examination.deadline_date) }} дн.)</i>
                        <br>
                        <button class="btn btn-sm btn-primary" v-if="examination.active"
                                @click="load_examination(examination)">
                            Загрузить
                        </button>
                        <div
                            v-else-if="examination.expired && !examination.upload_date">
                            <br>Срок загрузки истек<br>
                            <button class="btn btn-sm btn-secondary"
                                    @click="load_examination(examination)">
                                Все равно загрузить
                            </button>

                        </div>
                        <span v-else-if="!examination.active"><br>Загрузка сейчас недоступна<br></span>
                        <div v-if="examination.upload_date">
                            <span v-if="examination.no_expiration">Действует бессрочно</span>
                            <span v-else-if="days_left(examination.upload_date, examination.expiration_days) >= 0">
                                    Срок действия истечет через {{
                                    days_left(examination.upload_date, examination.expiration_days)
                                }} дн.
                            </span>
                            <span v-else>Срок действия истек</span>
                            <br>
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
                lock_btn: false,
                show_expired: false
            },
            examinations: [],
            errors: []
        }
    },
    computed: {
      filtered_examinations() {
          return this.examinations.filter((e) => !e.expired || this.flags.show_expired)
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

        this.examinations = this.data.examinations.concat(this.data.expired_examinations)
        this.examinations = this.examinations.map((examination) => {
            let notification_date = new Date(examination.notification_date)
            let deadline_date = new Date(examination.deadline_date)

            notification_date.setHours(0, 0, 0)
            deadline_date.setHours(23, 59, 59)

            examination.active = notification_date <= today && deadline_date >= today
            examination.expired = deadline_date < today

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
