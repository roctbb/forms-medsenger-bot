<template>
    <div v-if="reminder">
        <h3>Напоминание</h3>
        <p>{{ reminder.text }}</p>
        <div v-if="main_page">
            <button class="btn btn-success btn-block" @click="set_state('done')">Подтвердить выполнение</button>
            <button class="btn btn-danger btn-block" @click="set_state('reject')">Отказаться от выполнения</button>
            <button class="btn btn-default btn-block" @click="remind_later()">Напомнить позже</button>
            <button class="btn btn-default btn-block" @click="set_state('stop')">Больше не напоминать</button>
        </div>
        <div v-if="!main_page">
            <button class="btn btn-default btn-block" @click="set_reminder(1, 'hour')">Через 1 час</button>
            <button class="btn btn-default btn-block" @click="set_reminder(2, 'hour')">Через 2 часа</button>
            <button class="btn btn-default btn-block" @click="set_reminder(1, 'day')">Завтра</button>
            <button class="btn btn-danger" @click="remind_later()" style="margin-top: 15px;">Назад</button>
        </div>
    </div>
</template>

<script>
import ActionDone from "./ActionDone";
import FormGroup48 from "../common/FormGroup-4-8";
import ErrorBlock from "../common/ErrorBlock";

export default {
    name: "ReminderConfirmer",
    components: {ActionDone, ErrorBlock, FormGroup48},
    props: {
        data: {
            required: false
        }
    },
    data() {
        return {
            reminder: undefined,
            main_page: true,
            errors: []
        }
    },
    methods: {
        set_state: function (state) {
            let data = {
                state: state
            }
            this.axios.post(this.direct_url('/api/reminder/' + this.reminder.id + '/set_state'), data).then(r => Event.fire('confirm-reminder-done')).catch(r => this.errors.push('Ошибка сохранения'));
        },
        set_reminder: function (count, type) {
            let data = {
                state: 'later',
                count: count,
                type: type
            }
            this.axios.post(this.direct_url('/api/reminder/' + this.reminder.id + '/set_state'), data).then(r => Event.fire('confirm-reminder-done')).catch(r => this.errors.push('Ошибка сохранения'));
        },
        remind_later: function () {
            this.main_page = !this.main_page
        }
    },
    created() {
        this.reminder = this.data
    }
}
</script>

<style scoped>
.btn {
    margin-bottom: 5px;
}
</style>
