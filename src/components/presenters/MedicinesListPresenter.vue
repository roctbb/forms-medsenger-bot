<template>
    <div v-if="medicines">
        <h3>Назначенные лекарства</h3>
        <div class="row">
            <card v-for="(medicine, i) in medicines" :key="medicine.id" :image="images.medicine"
                  class="col-lg-6 col-md-7">
                <h6>{{ medicine.title }}</h6>
                <small><strong>Дозировка: </strong> {{ medicine.dose ? medicine.dose : '-' }}</small><br>
                <small><strong>Правила приема: </strong> {{ medicine.rules ? medicine.rules : '-' }}</small><br>
                <small><i>{{ tt_description(medicine.timetable) }}</i></small>
                <div v-if="medicine.timetable.mode !='manual'">
                    <small v-if="medicine.notifications_disabled"><strong>Уведомления выключены</strong><br></small>
                    <a href="#" v-if="!medicine.notifications_disabled" @click="disable_notifications(medicine)">Отключить
                        уведомления</a>
                    <a href="#" v-if="medicine.notifications_disabled" @click="enable_notifications(medicine)">Включить
                        уведомления</a>
                </div>
            </card>
        </div>
    </div>
</template>

<script>
import Card from "../common/Card";

export default {
    name: "MedicinesListPresenter",
    components: {Card},
    props: {
        data: {
            required: false
        }
    },
    data() {
        return {
            medicines: {}
        }
    },
    methods: {
        disable_notifications: function (medicine) {
            this.$confirm({
                message: `Вы уверены, что хотите отключить напоминания для препарата ${medicine.title}?`,
                button: {
                    no: 'Нет',
                    yes: 'Да'
                },
                callback: confirm => {
                    if (confirm) {
                        this.axios.post(this.url('/api/medicine/' + medicine.id + '/disable_notifications')).then(answer => medicine.notifications_disabled = answer.data.notifications_disabled);
                    }
                }
            })
        },
        enable_notifications: function (medicine) {
            this.axios.post(this.url('/api/medicine/' + medicine.id + '/enable_notifications')).then(answer => medicine.notifications_disabled = answer.data.notifications_disabled);
        }
    },
    created() {
        this.medicines = this.data.filter(medicine => medicine.contract_id == this.current_contract_id)
        this.medicines.sort((a, b) => {
            return a.title < b.title ? -1 : a.title > b.title ? 1 : 0
        })

    }
}
</script>

<style scoped>

</style>
