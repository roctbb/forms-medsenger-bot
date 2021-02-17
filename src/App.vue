<template>
    <div>
        <loading v-if="state == 'loading'" />
        <dashboard :patient="patient" v-else-if="state == 'dashboard'" />
        <form-editor v-else-if="state == 'create-form'" />
    </div>
</template>

<script>

import Loading from "./components/Loading";
import Dashboard from "./components/dashboard/Dashboard";
import FormEditor from "./components/form-editor/FormEditor";

const axios = require('axios');

export default {
    name: 'app',
    components: {FormEditor, Loading, Dashboard},
    data() {
        return {
            state: "loading",
            patient: {},
        }
    },
    created() {
        console.log("running created");
        Event.listen('navigate-to-create-form-page', () => this.state = 'create-form');
        Event.listen('back-to-dashboard', () => this.state = 'dashboard');
        Event.listen('form-created', (form) => {
            console.log(form);
            this.patient.forms.push(form)
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

ul {
    list-style-type: none;
    padding: 0;
}

li {
    display: inline-block;
    margin: 0 10px;
}

a {
    color: #42b983;
}
</style>

