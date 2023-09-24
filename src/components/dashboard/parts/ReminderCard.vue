<template>
    <card class="col-lg-3 col-md-4" :class="reminder.canceled_at ? 'text-muted' : ''"
          :image="reminder.canceled_at ? images.old_reminder : images.reminder">
        <strong class="card-title">
            {{ reminder.title ? reminder.title : 'Без названия' }}
        </strong>
        <small>
            <i>Для {{ reminder.type === 'both' ? 'всех' : (reminder.type === 'patient' ? 'пациента' : 'врача') }}</i>
            <br>
            {{ reminder.text }}
        </small><br>
        <br>
        <small><i>{{ tt_description(reminder.timetable) }}</i></small>
        <small><i> {{ duration }}</i></small><br>
        <div v-if="!['manual', 'dates'].includes(reminder.timetable.mode)">
            <small v-if="!reminder.canceled_at && !reminder.is_template"><b>Начало: </b>{{ attach_date }}<br></small>
            <small v-if="!reminder.canceled_at && !reminder.is_template"><b>Завершение: </b>{{
                    detach_date
                }}<br></small>
        </div>
        <small v-if="reminder.canceled_at"><b>Отключено: </b>{{ reminder.canceled_at }}<br></small>

        <div v-if="!reminder.is_template">
            <div v-if="reminder.contract_id === current_contract_id && !reminder.canceled_at">
                <a href="#" @click="edit_reminder()">Редактировать</a>
                <a href="#" @click="delete_reminder()">Отключить</a>
            </div>
            <div v-else>
                <small>Добавлено в другом контракте.</small>
            </div>

            <small v-if="!empty(reminder.template_id)" class="text-muted">ID шаблона: {{ reminder.template_id }}</small>
        </div>
        <div v-else>
            <a href="#" @click="attach_reminder()">Подключить</a>
            <a href="#" v-if="is_admin" @click="edit_reminder()">Редактировать</a><br>
            <a href="#" v-if="is_admin" @click="delete_reminder()">Удалить</a><br>
            <small class="text-muted">ID: {{ reminder.id }}</small>
        </div>
    </card>
</template>

<script>
import Card from "../../common/Card";
import * as moment from "moment/moment";

export default {
    name: "ReminderCard",
    components: {Card},
    props: {
        reminder: {required: true}
    },
    computed: {
        attach_date() {
            if (!this.reminder.attach_date) return ''
            let d = this.reminder.attach_date.split('-')
            return `${d[2]}.${d[1]}.${d[0]}`
        },
        detach_date() {
            if (!this.reminder.detach_date) return ''
            let d = this.reminder.detach_date.split('-')
            return `${d[2]}.${d[1]}.${d[0]}`
        },
        duration: function () {
            if (this.reminder.timetable.mode === 'dates') {
                let dates = new Set(this.reminder.timetable.points.map(d => moment(d.date).format('DD.MM.YYYY')))
                return `(${Array.from(dates).join(', ')})`
            }

            if (!this.reminder.attach_date || !this.reminder.detach_date) return 'Пока не отключить вручную'
            let attach = moment(this.reminder.attach_date, "YYYY-MM-DD")
            let detach = moment(this.reminder.detach_date, "YYYY-MM-DD")
            let duration = moment.duration(detach.diff(attach)).asDays()
            return `В течение ${duration} дн.`
        },
    },
    methods: {
        attach_reminder: function () {
            Event.fire('attach-reminder', this.reminder)
        },
        edit_reminder: function () {
            Event.fire('edit-reminder', this.reminder)
        },
        delete_reminder: function () {
            this.$confirm({
                message: `Вы уверены, что хотите удалить напоминание?`,
                button: {
                    no: 'Нет',
                    yes: 'Да, удалить'
                },
                callback: confirm => {
                    if (confirm) {
                        this.axios.post(this.direct_url('/api/settings/delete_reminder'), this.reminder)
                            .then((response) => Event.fire('reminder-deleted', response.data.deleted_id));
                    }
                }
            })
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
