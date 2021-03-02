<template>
    <div>
        <vue-confirm-dialog></vue-confirm-dialog>
        <loading v-if="state == 'loading'"/>
        <div v-else>
            <div v-if="mode == 'settings'">
                <dashboard-header :patient="patient"/>

                <div class="container" style="margin-top: 15px;">
                    <dashboard :patient="patient" :templates="templates" v-show="state == 'dashboard'"/>
                    <form-editor v-show="state == 'form-manager'"/>
                    <medicine-editor v-show="state == 'medicine-manager'"/>
                    <algorithm-editor v-show="state == 'algorithm-manager'"/>
                </div>
            </div>
            <div v-if="mode == 'form' || mode == 'done'">
                <div class="container" style="margin-top: 15px;">
                    <form-presenter :data="form" v-if="state == 'form-presenter'"/>
                    <action-done v-if="state == 'done'"></action-done>
                </div>
            </div>
        </div>
    </div>
</template>

<script>

import Loading from "./components/Loading";
import Dashboard from "./components/dashboard/Dashboard";
import FormEditor from "./components/editors/FormEditor";
import MedicineEditor from "./components/editors/MedicineEditor";
import FormPresenter from "./components/presenters/FormPresenter";
import AlgorithmEditor from "./components/editors/AlgorithmEditor";
import DashboardHeader from "./components/dashboard/DashboardHeader";
import ActionDone from "./components/presenters/ActionDone";


export default {
    name: 'app',
    components: {
        ActionDone,
        DashboardHeader, AlgorithmEditor, FormPresenter, FormEditor, Loading, Dashboard, MedicineEditor},
    data() {
        return {
            state: "loading",
            patient: {},
            form: {},
            mode: "",
            object_id: -1,
            templates: {
                forms: [],
                algorithms: [],
                medicines: []
            }
        }
    },
    created() {
        console.log("running created");
        Event.listen('navigate-to-create-form-page', () => this.state = 'form-manager');
        Event.listen('navigate-to-create-medicine-page', () => this.state = 'medicine-manager');
        Event.listen('navigate-to-create-algorithm-page', () => this.state = 'algorithm-manager');
        Event.listen('back-to-dashboard', () => this.state = 'dashboard');
        Event.listen('home', () => this.state = 'dashboard');
        Event.listen('form-done', () => this.state = 'done');
        Event.listen('form-created', (form) => {
            this.state = 'dashboard'
            if (!form.is_template) {
                Event.fire('dashboard-to-main');
                this.patient.forms.push(form)
            } else {
                this.templates.forms.push(form)
            }

        });
        Event.listen('medicine-created', (medicine) => {
            this.state = 'dashboard'
            if (!medicine.is_template) {
                Event.fire('dashboard-to-main');
                this.patient.medicines.push(medicine)
            } else {
                this.templates.medicines.push(medicine)
            }
        });
        Event.listen('algorithm-created', (algorithm) => {
            this.state = 'dashboard'
            if (!algorithm.is_template) {
                Event.fire('dashboard-to-main');
                this.patient.algorithms.push(algorithm)
            } else {
                this.templates.algorithms.push(algorithm)
            }
        });
        Event.listen('edit-form', (form) => {
            this.state = 'form-manager'
            Event.fire('navigate-to-edit-form-page', form);
        });
        Event.listen('edit-medicine', (medicine) => {
            this.state = 'medicine-manager'
            Event.fire('navigate-to-edit-medicine-page', medicine);
        });
        Event.listen('edit-algorithm', (algorithm) => {
            this.state = 'algorithm-manager'
            Event.fire('navigate-to-edit-algorithm-page', algorithm);
        });
    },
    methods: {
        load: function () {
            this.mode = window.PAGE
            this.object_id = window.OBJECT_ID

            if (this.mode == 'done') {
                this.state = 'done'
            }

            if (this.mode == 'settings') {
                this.axios.get(this.url('/api/settings/get_patient')).then(this.process_load_answer);
                this.axios.get(this.url('/api/settings/get_templates')).then(response => this.templates = response.data);
            }
            if (this.mode == 'form') {
                this.axios.get(this.url('/api/form/' + this.object_id)).then(this.process_load_answer);
            }
        },
        process_load_answer: function (response) {
            if (this.mode == 'settings') {
                this.patient = response.data;
                this.state = 'dashboard';
            }
            if (this.mode == 'form') {
                this.form = response.data;
                this.state = 'form-presenter'
            }

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

body {
    background-color: #f8f8fb;
}

</style>

