<template>
    <div>
        <vue-confirm-dialog></vue-confirm-dialog>
        <loading v-if="state == 'loading'"/>
        <div v-else>
            <div v-if="mode == 'settings' || mode == 'medicine-manager'">
                <dashboard-header :patient="patient"/>
                <div class="container" style="margin-top: 15px;">
                    <dashboard :patient="patient" :templates="templates" v-show="state == 'dashboard'"/>
                    <form-editor v-show="state == 'form-manager'"/>
                    <medicine-editor v-show="state == 'medicine-manager'"/>
                    <algorithm-editor v-show="state == 'algorithm-manager'"/>
                    <action-done v-if="state == 'done'"></action-done>
                </div>
            </div>
            <div v-if="mode == 'form' || mode == 'done' || mode == 'graph' || mode == 'confirm-medicine'">
                <div class="container" style="margin-top: 15px;">
                    <confirm-medicine-presenter :data="patient.medicines" v-if="state == 'confirm-medicine'"/>
                    <dose-verifier :data="medicine" v-if="state == 'verify-dose'"/>
                    <form-presenter :data="form" v-if="state == 'form-presenter'"/>
                    <graph-category-chooser :data="available_categories" v-if="state == 'graph-category-chooser'"/>
                    <action-done v-if="state == 'done'"></action-done>
                    <load-error v-if="state == 'load-error'"></load-error>
                </div>

                <graph-presenter v-show="state == 'graph-presenter'" :patient="patient"/>
                <heatmap-presenter v-show="state.startsWith('heatmap-presenter')" :heatmap_type="state.split('-')[2]"/>
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
import GraphCategoryChooser from "./components/presenters/GraphCategoryChooser";
import GraphPresenter from "./components/presenters/GraphPresenter";
import LoadError from "./components/presenters/LoadError";
import ConfirmMedicinePresenter from "./components/presenters/ConfirmMedicinePresenter";
import HeatmapPresenter from "./components/presenters/HeatmapPresenter";
import DoseVerifier from "./components/presenters/DoseVerifier";



export default {
    name: 'app',
    components: {
        DoseVerifier,
        HeatmapPresenter,
        ConfirmMedicinePresenter,
        LoadError,
        GraphPresenter,
        GraphCategoryChooser,
        ActionDone,
        DashboardHeader, AlgorithmEditor, FormPresenter, FormEditor, Loading, Dashboard, MedicineEditor},
    data() {
        return {
            state: "loading",
            patient: {},
            form: {},
            medicine: {},
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
        Event.listen('confirm-medicine-done', () => this.state = 'done');
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
            this.state = 'dashboard'
            if (!data.medicine.is_template) {
                Event.fire('dashboard-to-main');
                this.patient.medicines.push(data.medicine)
            } else {
                this.templates.medicines.push(data.medicine)
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
        Event.listen('edit-algorithm', (algorithm) => {
            this.state = 'algorithm-manager'
            Event.fire('navigate-to-edit-algorithm-page', algorithm);
        });
        Event.listen('load-graph', (form) => {
            this.state = 'graph-presenter'
        });
        Event.listen('load-heatmap', (heatmap_type) => {
            this.state = 'heatmap-presenter-' + heatmap_type
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
            if (this.mode == 'confirm-medicine') {
                this.axios.get(this.url('/api/settings/get_patient')).then(this.process_load_answer);
            }
            if (this.mode == 'medicine-manager') {
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

            if (this.mode == 'confirm-medicine') {
                this.patient = response.data;
                this.state = 'confirm-medicine'
            }

            if (this.mode == 'medicine-manager') {
                this.patient = response.data;
                Event.fire('navigate-to-create-medicine-page')
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

