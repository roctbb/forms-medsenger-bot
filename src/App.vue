<template>
    <div style="padding-bottom: 15px;">
        <vue-confirm-dialog/>
        <loading v-if="state == 'loading'"/>
        <div v-else>
            <dashboard-header :patient="patient" v-if="mode == 'settings' && dashboard_parts.length == 0"/>

            <div class="container slim-container" style="margin-top: 15px;"
                 v-if="state == 'form-presenter' || mode == 'outsource-form'">
                <form-presenter :patient="patient" :data="form" v-if="state == 'form-presenter'"/>
                <result-presenter :result="result" v-if="state == 'form-result'"/>
            </div>

            <div class="container" style="margin-top: 15px;" v-else>
                <dashboard :patient="patient" :templates="templates" v-show="state == 'dashboard'" v-if="mode == 'settings'"
                           :parts="dashboard_parts"/>
                <form-editor :patient="patient" v-show="state == 'form-manager'"/>
                <form-presenter v-show="state == 'form-preview-presenter'"/>

                <medicine-editor :patient="patient" v-show="state == 'medicine-manager'"/>
                <medicines-list :data="patient" v-if="state == 'medicines-list'"/>
                <dose-verifier :data="medicine" v-if="state == 'verify-dose'"/>

                <reminder-editor v-show="state == 'reminder-manager'"/>
                <reminder-confirmer :data="reminder" v-if="state == 'confirm-reminder'"/>

                <examinations-list :data="patient" v-if="state == 'examinations-list'"/>
                <examination-editor v-show="state == 'examination-manager'"/>
                <examination-presenter v-show="state == 'examination-loader'"/>
                <examination-group-presenter :data="examination_group" v-show="state == 'examination-group'"/>

                <algorithm-editor v-show="state == 'algorithm-manager'"/>
                <action-done v-if="state == 'done'"/>

                <load-error v-if="state == 'load-error'"/>
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
import LoadError from "./components/presenters/LoadError";
import DoseVerifier from "./components/presenters/DoseVerifier";
import ReminderEditor from "./components/editors/ReminderEditor";
import ReminderConfirmer from "./components/presenters/ReminderConfirmer";
import MedicinesList from "./components/managers/MedicineList";
import ResultPresenter from "./components/presenters/ResultPresenter";
import ExaminationEditor from "./components/editors/ExaminationEditor";
import ExaminationsList from "./components/managers/ExaminationsList";
import ExaminationPresenter from "./components/presenters/ExaminationPresenter";
import ExaminationGroupPresenter from "./components/presenters/ExaminationGroupPresenter.vue";


export default {
    name: 'app',
    components: {
        ExaminationGroupPresenter,
        ExaminationPresenter,
        ExaminationsList, ExaminationEditor,
        FormPresenter, FormEditor, ResultPresenter,
        ReminderConfirmer, ReminderEditor,
        MedicinesList, MedicineEditor, DoseVerifier,
        LoadError, ActionDone, Loading,
        DashboardHeader, Dashboard,
        AlgorithmEditor
    },
    data() {
        return {
            state: "loading",
            patient: {},
            form: {},
            medicine: {},
            reminder: {},
            examination: {},
            examination_group: {},
            mode: "",
            result: {},
            object_id: -1,
            templates: {
                forms: [],
                algorithms: [],
                medicines: [],
                examinations: []
            }
        }
    },
    created() {
        console.log("running created");
        Event.listen('navigate-to-create-form-page', () => this.state = 'form-manager');
        Event.listen('navigate-to-create-medicine-page', () => this.state = 'medicine-manager');
        Event.listen('navigate-to-create-reminder-page', () => this.state = 'reminder-manager');
        Event.listen('navigate-to-create-examination-page', () => this.state = 'examination-manager');
        Event.listen('navigate-to-load-examination-page', () => this.state = 'examination-loader');
        Event.listen('navigate-to-load-examination-group-page', () => this.state = 'examination-group');
        Event.listen('navigate-to-create-algorithm-page', () => this.state = 'algorithm-manager');
        Event.listen('back-to-dashboard', () => this.state = this.mode == 'settings' ? 'dashboard' : 'medicine-chooser');
        Event.listen('back-to-medicine-list', () => this.state = 'medicines-list');
        Event.listen('back-to-examinations-list', () => this.state = 'examinations-list');
        Event.listen('home', () => this.state = this.mode == 'settings' ? 'dashboard' : 'medicine-chooser');
        Event.listen('form-done', () => this.state = 'done');
        Event.listen('confirm-medicine-done', () => this.state = 'done');
        Event.listen('confirm-reminder-done', () => this.state = 'done');
        Event.listen('action-done', () => this.state = 'done');
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
        Event.listen('examination-created', (examination) => {
            this.state = 'dashboard'
            if (!examination.is_template) {
                Event.fire('dashboard-to-main');
                this.patient.examinations.push(examination)
            } else {
                this.templates.examinations.push(examination)
            }
        });
        Event.listen('edit-form', (form) => {
            this.state = 'form-manager'
            Event.fire('navigate-to-edit-form-page', form);
        });
        Event.listen('preview-form', (form) => {
            this.state = 'form-preview-presenter'
            Event.fire('load-form-preview', form);
        });
        Event.listen('fill-form', (form) => {
            this.state = 'form-presenter'
            Event.fire('load-doctor-form', form);
        });
        Event.listen('edit-medicine', (medicine) => {
            this.state = 'medicine-manager'
            Event.fire('navigate-to-edit-medicine-page', medicine);
        });
        Event.listen('edit-reminder', (reminder) => {
            this.state = 'reminder-manager'
            Event.fire('navigate-to-edit-reminder-page', reminder);
        });
        Event.listen('edit-examination', (examination) => {
            this.state = 'examination-manager'
            Event.fire('navigate-to-edit-examination-page', examination);
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
        Event.listen('verify-dose', (medicine) => {
            this.medicine = medicine
            this.state = 'verify-dose'
        })
        Event.listen('outsource-form-done', (result) => {
            this.result = result
            this.state = 'form-result'
        });
        Event.listen('examination-loaded', (examination) => this.state = 'examinations-list')
    },
    methods: {
        load: function () {
            this.mode = window.PAGE
            this.object_id = window.OBJECT_ID

            if (this.mode == 'done') {
                this.state = 'done'
            }

            if (this.mode == 'settings') {
                this.axios.get(this.direct_url('/api/settings/get_templates')).then(response => {
                    this.templates = response.data
                    this.axios.get(this.direct_url('/api/settings/get_patient')).then(this.process_load_answer);
                });
            }
            if (this.mode == 'form') {
                this.axios.get(this.direct_url('/api/settings/get_patient_data')).then(response => {
                    this.patient = response.data
                    this.axios.get(this.direct_url('/api/form/' + this.object_id)).then(this.process_load_answer).catch(this.process_load_error);
                });
            }
            if (this.mode == 'outsource-form') {
                this.axios.get('/api/outsource_form/' + this.object_id).then(this.process_load_answer).catch(this.process_load_error);
            }
            if (this.mode == 'confirm-reminder') {
                this.axios.get(this.direct_url('/api/reminder/' + this.object_id)).then(this.process_load_answer);
            }
            if (this.mode == 'create-reminder') {
                this.axios.get(this.direct_url('/api/settings/get_patient')).then((response) => {
                    this.patient = response.data
                    this.state = 'reminder-manager'
                    this.axios.get(this.direct_url('/api/reminder/' + this.object_id)).then(this.process_load_answer);
                });
            }
            if (this.mode == 'attach-examination') {
                this.axios.get(this.direct_url('/api/settings/get_patient')).then((response) => {
                    this.patient = response.data
                    this.state = 'examination-manager'
                    this.axios.get(this.direct_url('/api/examination/' + this.object_id)).then(this.process_load_answer);
                });
            }
            if (this.mode == 'verify-dose') {
                this.axios.get(this.direct_url('/api/medicine/' + this.object_id)).then(this.process_load_answer);
            }
            if (this.mode == 'medicine-chooser') {
                this.axios.get(this.direct_url('/api/settings/get_templates')).then(response => {
                    this.templates = response.data
                    this.axios.get(this.direct_url('/api/settings/get_patient')).then(this.process_load_answer);
                });
            }
            if (this.mode == 'examination') {
                this.axios.get(this.direct_url('/api/examination/' + this.object_id)).then(this.process_load_answer);
            }
            if (this.mode == 'examination-group') {
                this.axios.get(this.direct_url('/api/examination-group/' + this.object_id)).then(this.process_load_answer);
            }
            if (this.mode == 'medicines-list') {
                this.axios.get(this.direct_url('/api/settings/get_patient_data')).then(this.process_load_answer);
            }
            if (this.mode == 'examinations-list') {
                this.axios.get(this.direct_url('/api/settings/get_patient')).then(this.process_load_answer);
            }
        },
        process_load_answer: function (response) {
            if (this.mode == 'settings') {
                this.patient = response.data;
                this.state = 'dashboard';
            }

            if (this.mode == 'form' || this.mode == 'outsource-form') {
                this.form = response.data;
                this.state = 'form-presenter'
            }

            if (this.mode == 'confirm-reminder') {
                this.reminder = response.data;
                this.state = 'confirm-reminder'
            }

            if (this.mode == 'create-reminder') {
                Event.fire('create-reminder-from-template', response.data)
            }

            if (this.mode == 'attach-examination') {
                Event.fire('create-examination-from-template', response.data)
            }

            if (this.mode == 'medicines-list') {
                this.patient = response.data;
                this.state = 'medicines-list'
            }

            if (this.mode == 'examinations-list') {
                this.patient = response.data;
                this.state = 'examinations-list'
            }

            if (this.mode == 'examination') {
                Event.fire('navigate-to-load-examination-page')
                this.state = 'examination-loader'
            }

            if (this.mode == 'examination-group') {
                this.examination_group = response.data
                this.state = 'examination-group'
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
.row {
    margin: 5px -5px;
}

input[type=checkbox] {
    /* Double-sized Checkboxes */
    -ms-transform: scale(1.2); /* IE */
    -moz-transform: scale(1.2); /* FF */
    -webkit-transform: scale(1.2); /* Safari and Chrome */
    -o-transform: scale(1.2); /* Opera */
    transform: scale(1.2);
    margin: 10px;
}

</style>

