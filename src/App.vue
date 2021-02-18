<template>
    <div>
        <loading v-if="state == 'loading'"/>
        <div v-else>
            <dashboard :patient="patient" v-show="state == 'dashboard'"/>
            <form-editor v-show="state == 'form-manager'"/>
            <medicine-editor v-show="state == 'medicine-manager'" />
        </div>
    </div>
</template>

<script>

import Loading from "./components/Loading";
import Dashboard from "./components/dashboard/Dashboard";
import FormEditor from "./components/editors/FormEditor";
import MedicineEditor from "./components/editors/MedicineEditor";

const axios = require('axios');

export default {
    name: 'app',
    components: {FormEditor, Loading, Dashboard, MedicineEditor},
    data() {
        return {
            state: "loading",
            patient: {},
        }
    },
    created() {
        console.log("running created");
        Event.listen('navigate-to-create-form-page', () => this.state = 'form-manager');
        Event.listen('navigate-to-create-medicine-page', () => this.state = 'medicine-manager');
        Event.listen('back-to-dashboard', () => this.state = 'dashboard');
        Event.listen('form-created', (form) => {
            this.state = 'dashboard'
            this.patient.forms.push(form)
        });
        Event.listen('medicine-created', (medicine) => {
            this.state = 'dashboard'
            this.patient.medicines.push(medicine)
        });
        Event.listen('edit-form', (form) => {
            this.state = 'form-manager'
            Event.fire('navigate-to-edit-form-page', form);
        });
        Event.listen('edit-medicine', (medicine) => {
            this.state = 'medicine-manager'
            Event.fire('navigate-to-edit-medicine-page', medicine);
        });
    },
    methods: {
        load: function () {
            axios.get(this.url('/api/get_patient')).then(this.process_load_answer);
        },
        process_load_answer: function (response) {
            this.patient = response.data;
            this.state = 'dashboard'
        }
    },
    mounted: function () {
        this.load();
    }
}
</script>

<style>
#app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
    margin-top: 60px;
}

h1, h2 {
    font-weight: normal;
}

a {
    color: #42b983;
}
</style>

