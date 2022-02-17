<template>
    <div style="padding-bottom: 15px;">
        <vue-confirm-dialog></vue-confirm-dialog>
        <loading v-if="state == 'loading'"/>
        <div v-else>
            <dashboard-header :patient="patient" v-if="mode == 'settings'"/>

            <div class="container slim-container" v-if="state == 'form-presenter'">
                <form-presenter :data="form" v-if="state == 'form-presenter'"/>
            </div>
            <div class="container" style="margin-top: 15px;" v-else>
                <dashboard :patient="patient" :templates="templates" v-show="state == 'dashboard'"/>
                <medicine-manager :patient="patient" :templates="templates" v-show="state == 'medicine-chooser'"/>
                <form-editor v-show="state == 'form-manager'"/>
                <medicine-editor v-show="state == 'medicine-manager'"/>
                <reminder-editor v-show="state == 'reminder-manager'"/>
                <algorithm-editor v-show="state == 'algorithm-manager'"/>
                <action-done v-if="state == 'done'"></action-done>

                <reminder-confirmer :data="reminder" v-if="state == 'confirm-reminder'"></reminder-confirmer>
                <medicines-list :data="patient.medicines" v-if="state == 'medicines-list'"/>
                <dose-verifier :data="medicine" v-if="state == 'verify-dose'"/>
                <graph-category-chooser :data="available_categories" v-if="state == 'graph-category-chooser'"/>
                <load-error v-if="state == 'load-error'"></load-error>
            </div>

            <graph-presenter v-show="state == 'graph-presenter'" :patient="patient"/>
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
import GraphCategoryChooser from "./components/presenters/GraphCategoryChooser";
import GraphPresenter from "./components/presenters/GraphPresenter";
import LoadError from "./components/presenters/LoadError";
import DoseVerifier from "./components/presenters/DoseVerifier";
import ReminderEditor from "./components/editors/ReminderEditor";
import ReminderConfirmer from "./components/presenters/ReminderConfirmer";
import MedicinesList from "./components/managers/MedicineList";
import MedicineManager from "./components/managers/MedicineManager";


export default {
    name: 'app',
    components: {
        MedicineManager,
        ReminderConfirmer,
        ReminderEditor,
        MedicinesList,
        DoseVerifier,
        LoadError,
        GraphPresenter,
        GraphCategoryChooser,
        ActionDone,
        DashboardHeader, AlgorithmEditor, FormPresenter, FormEditor, Loading, Dashboard, MedicineEditor
    },
    data() {
        return {
            state: "loading",
            patient: {},
            form: {},
            medicine: {},
            reminder: {},
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
        Event.listen('navigate-to-create-reminder-page', () => this.state = 'reminder-manager');
        Event.listen('navigate-to-create-algorithm-page', () => this.state = 'algorithm-manager');
        Event.listen('back-to-dashboard', () => this.state = this.mode == 'settings' ? 'dashboard' : 'medicine-chooser');
        Event.listen('back-to-medicine-list', () => this.state = 'medicines-list');
        Event.listen('home', () => this.state = this.mode == 'settings' ? 'dashboard' : 'medicine-chooser');
        Event.listen('form-done', () => this.state = 'done');
        Event.listen('confirm-medicine-done', () => this.state = 'done');
        Event.listen('confirm-reminder-done', () => this.state = 'done');
        Event.listen('form-created', (form) => {
            this.state = 'dashboard'
            if (!form.is_template) {
                Event.fire('dashboard-to-main');
                this.patient.forms.push(form)
            } else {
                this.templates.forms.push(form)
            }

        });
        Event.listen('medicine-created', (data) => {
            this.state = this.mode == 'settings' ? 'dashboard' : 'medicine-chooser'
            if (!data.medicine.is_template) {
                Event.fire('dashboard-to-main');
                this.patient.medicines.push(data.medicine)
            } else {
                this.templates.medicines.push(data.medicine)
            }
            if (data.close_window) this.state = 'done'
        });
        Event.listen('reminder-created', (data) => {
            this.state = 'dashboard'
            if (!data.reminder.is_template) {
                Event.fire('dashboard-to-main');
                this.patient.reminders.push(data.reminder)
            } else {
                this.templates.reminders.push(data.reminder)
            }
            if (data.close_window) this.state = 'done'
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
        Event.listen('edit-reminder', (reminder) => {
            this.state = 'reminder-manager'
            Event.fire('navigate-to-edit-reminder-page', reminder);
        });
        Event.listen('edit-algorithm', (algorithm) => {
            this.state = 'algorithm-manager'
            Event.fire('navigate-to-edit-algorithm-page', algorithm);
        });
        Event.listen('edit-timetable', (data) => {
            this.state = 'form-manager'
            Event.fire('navigate-to-edit-form-page', data);
            Event.fire('edit-form-tt-only');
        });
        Event.listen('load-graph', (params) => {
            this.state = 'graph-presenter'
        });
        Event.listen('load-heatmap', (params) => {
            this.state = 'graph-presenter'
        });
        Event.listen('select-graph', () => {
            this.state = 'graph-category-chooser'
        });
        Event.listen('verify-dose', (medicine) => {
            this.medicine = medicine
            this.state = 'verify-dose'
        })
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
                this.axios.get(this.url('/api/form/' + this.object_id)).then(this.process_load_answer).catch(this.process_load_error);
            }
            if (this.mode == 'confirm-reminder') {
                this.axios.get(this.url('/api/reminder/' + this.object_id)).then(this.process_load_answer);
            }
            if (this.mode == 'verify-dose') {
                this.axios.get(this.url('/api/medicine/' + this.object_id)).then(this.process_load_answer);
            }
            if (this.mode == 'medicine-chooser') {
                this.axios.get(this.url('/api/settings/get_patient')).then(this.process_load_answer);
                this.axios.get(this.url('/api/settings/get_templates')).then(response => this.templates = response.data);
            }
            if (this.mode == 'medicines-list') {
                this.axios.get(this.url('/api/settings/get_patient')).then(this.process_load_answer);
            }
            if (this.mode == 'graph') {
                this.axios.get(this.url('/api/settings/get_patient')).then(response => {
                    this.patient = response.data
                    this.axios.get(this.url('/api/graph/categories')).then(this.process_load_answer);
                });
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

            if (this.mode == 'confirm-reminder') {
                this.reminder = response.data;
                this.state = 'confirm-reminder'
            }

            if (this.mode == 'medicines-list') {
                this.patient = response.data;
                this.state = 'medicines-list'
            }

            if (this.mode == 'verify-dose') {
                this.medicine = response.data
                this.state = 'verify-dose'
            }

            if (this.mode == 'medicine-chooser') {
                this.patient = response.data;
                this.state = 'medicine-chooser'
            }

            if (this.mode == 'graph') {
                this.available_categories = response.data;
                this.state = 'graph-category-chooser'
            }

        },
        process_load_error: function (response) {
            this.state = 'load-error'
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

.container {
    max-width: 95%;
}

h1, h2 {
    font-weight: normal;
}

a {
    color: #006c88;
    font-weight: bold;
}

body {
    background-color: #fcfcfc;
}

@media screen and (max-width: 900px) {
    .slim-container {
        max-width: 100% !important;
        padding-left: 10px;
        padding-right: 10px;
    }
}

.col, .col-1, .col-10, .col-11, .col-12, .col-2, .col-3, .col-4, .col-5, .col-6, .col-7, .col-8, .col-9, .col-auto, .col-lg, .col-lg-1, .col-lg-10, .col-lg-11, .col-lg-12, .col-lg-2, .col-lg-3, .col-lg-4, .col-lg-5, .col-lg-6, .col-lg-7, .col-lg-8, .col-lg-9, .col-lg-auto, .col-md, .col-md-1, .col-md-10, .col-md-11, .col-md-12, .col-md-2, .col-md-3, .col-md-4, .col-md-5, .col-md-6, .col-md-7, .col-md-8, .col-md-9, .col-md-auto, .col-sm, .col-sm-1, .col-sm-10, .col-sm-11, .col-sm-12, .col-sm-2, .col-sm-3, .col-sm-4, .col-sm-5, .col-sm-6, .col-sm-7, .col-sm-8, .col-sm-9, .col-sm-auto, .col-xl, .col-xl-1, .col-xl-10, .col-xl-11, .col-xl-12, .col-xl-2, .col-xl-3, .col-xl-4, .col-xl-5, .col-xl-6, .col-xl-7, .col-xl-8, .col-xl-9, .col-xl-auto {
    padding-right: 5px;
    padding-left: 5px;
}
.row {
    margin: 5px -5px;
}

.card {

    border-color: rgba(0,108,136, 0.3);
}

.btn-primary, .btn-primary:active, .btn-primary:hover, .btn-primary:focus {
    border-color: #006c88;
    background-color: #006c88;
}

.btn-success, .btn-success:active, .btn-success:hover, .btn-success:focus  {
    border-color: #24a8b4;
    background-color: #24a8b4;
}

.btn-danger, .btn-danger:active, .btn-danger:hover, .btn-danger:focus {
    border-color: #ff5763;
    background-color: #ff5763;
}

</style>

