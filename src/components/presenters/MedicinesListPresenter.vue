<template>
    <div v-if="medicines">
        <h3>Назначенные лекарства</h3>
        <div class="row">
            <card v-for="(medicine, i) in medicines" :key="medicine.id" :image="images.medicine" class="col-lg-6 col-md-7">
                <h6>{{ medicine.title }}</h6>
                <small><strong>Дозировка: </strong> {{ medicine.dose ? medicine.dose : '-' }}</small><br>
                <small><strong>Правила приема: </strong> {{ medicine.rules ? medicine.rules : '-' }}</small><br>
                <small><i>{{ tt_description(medicine.timetable) }}</i></small><br>
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
    methods: {},
    created() {
        this.medicines = this.data
    }
}
</script>

<style scoped>

</style>
