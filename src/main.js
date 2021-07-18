import Vue from 'vue'
import App from './App.vue'
import axios from "axios";
import VueConfirmDialog from 'vue-confirm-dialog'
import vmodal from 'vue-js-modal'


window.Event = new class {
    constructor() {
        this.vue = new Vue();
    }

    fire(event, data = null) {
        if (!data && data !== 0) {
            console.log('sending event', event);
        } else {
            console.log('sending event', event, 'with data', data);
        }

        this.vue.$emit(event, data);
    }

    listen(event, callback) {
        this.vue.$on(event, callback);
    }
};

Vue.mixin({
    methods: {
        br: function (doc) {
            if (!doc) return doc;
            return doc.replace(/([^>])\n/g, '$1<br/>')
        },
        blur: function ()
        {
            if (window.activeElement)
            {
                window.activeElement.blur()
            }
        },
        getWindow: function () {
            return window;
        },
        url: function (action) {
            let api_host = window.API_HOST;
            let agent_token = window.AGENT_TOKEN;
            let contract_id = window.CONTRACT_ID;
            let agent_id = window.AGENT_ID;

            return api_host + '/api/client/agents/' + agent_id + '/?action=' + action + '&contract_id=' + contract_id + '&agent_token=' + agent_token
        },
        empty: function (e) {
            return !e && e !== 0
        },
        isJsonString: function(str) {
            if (!str)
                return true;
            try {
                JSON.parse(str);
            } catch (e) {
                return false;
            }
            return true;
        },
        verify_timetable: function (timetable) {
            if (timetable.mode == 'manual') return true;
            let prepare_point = (point) => {
                point.hour = parseInt(point.hour);
                point.minute = parseInt(point.minute);
                if (point.day) point.day = parseInt(point.day);
                return point
            }
            timetable.points = timetable.points.map(prepare_point);

            let general_validate = (point) => {
                if (this.empty(point.hour) || this.empty(point.minute)) return true;
                if (point.hour < 0 || point.hour > 23) return true;
                if (point.minute < 0 || point.minute > 59) return true;
                return false;
            }
            let validate_point = general_validate;

            if (timetable.mode == 'weekly') {
                validate_point = (point) => {
                    if (general_validate(point)) return true;
                    if (this.empty(point.day) || point.day < 0 || point.day > 6) return true;
                    return false;
                }
            }
            if (timetable.mode == 'monthly') {
                validate_point = (point) => {
                    if (general_validate(point)) return true;
                    if (this.empty(point.day) || point.day < 1 || point.day > 31) return true;
                    return false;
                }
            }

            return !(timetable.points.filter(validate_point).length > 0);

        },
        empty_timetable: function () {
            return {
                mode: 'daily',
                points: [{
                    hour: '',
                    minute: ''
                }]
            }
        },
        uuidv4: () => {
            return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
                (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
            );
        },
        get_category: function (category_name) {
            if (category_name == 'time' || category_name == "exact_time") {
                return {
                    description: 'время',
                    type: "date"
                }
            }

            if (category_name == "exact_date" ) {
                return {
                    description: 'дата',
                    type: "date",
                }
            }

            if (category_name == "contract_start_date" ) {
                return {
                    description: 'дата начала контракта',
                    type: "date",
                }
            }

            if (category_name == "contract_end_date" ) {
                return {
                    description: 'дата завершения контракта',
                    type: "date",
                }
            }

            if (category_name == "algorithm_attach_date" ) {
                return {
                    description: 'дата отсчета алгоритма',
                    type: "date",
                }
            }

            if (category_name == "algorithm_detach_date" ) {
                return {
                    description: 'дата завершения алгоритма',
                    type: "date",
                }
            }

            let category = this.category_list.find(x => x.name == category_name)

            if (!category)
            {
                return {
                    description: ''
                }
            }
            return category
        },
        copy: function (to, from) {
            Object.keys(from).forEach(k => {
                to[k] = from[k]
            })
        },
        tt_description: function (timetable) {
            if (timetable.mode == 'manual')
            {
                return 'Заполняется вручную или присылается алгоритмом.'
            }
            if (timetable.mode == 'daily') {
                return timetable.points.length + ' раз(а) в день.'
            } else if (timetable.mode == 'weekly') {
                return timetable.points.length + ' раз(а) в неделю.'
            } else {
                return timetable.points.length + ' раз(а) в месяц.'
            }
        },
        alg_description: function (algorithm) {
            let criteria = `<b>Анализирует:</b> ` + algorithm.categories.split('|').map((c) => this.get_category(c).description.toLowerCase()).filter((v, i, a) => a.indexOf(v) === i).join(', ') + `<br>`;

            /*
            let actions = new Set();

            algorithm.actions.forEach((a) => {
                if (a.type == 'patient_message') {
                    actions.add('сообщение пациенту');
                }
                if (a.type == 'doctor_message') {
                    actions.add('сообщение врачу');
                }
                if (a.type == 'record') {
                    actions.add('запись в карту');
                }
                if (a.type == 'medicine') {
                    actions.add('прием препарата' + a.params.medicine_name);
                }
                if (a.type == 'form') {
                    actions.add('отправка дополнительного опросника');
                }
                if (a.type == 'attach_medicine') {
                    actions.add('назначение лекарства');
                }
                if (a.type == 'detach_medicine') {
                    actions.add('отмена лекарства');
                }
                if (a.type == 'attach_form') {
                    actions.add('подключение опросника');
                }
                if (a.type == 'detach_form') {
                    actions.add('отключение опросника');
                }
                if (a.type == 'attach_algorithm') {
                    actions.add('подключение алгоритма');
                }
                if (a.type == 'detach_algorithm') {
                    actions.add('отключение алгоритма');
                }
            })*/


            /*actions = `<b>Действия:</b> ` + Array.from(actions).join(', ')*/

            return criteria /* + actions */
        },
        need_filling: function (algorithm) {
            console.log(algorithm.steps)
            return algorithm.steps.some(s => s.conditions.some(k => k.criteria.some(c => c.some(b => b.ask_value == true))));
        },
        group_by: function (categories, field) {
            return categories.reduce((groups, item) => {
                const group = (groups[item[field]] || []);
                group.push(item);
                groups[item[field]] = group;
                return groups;
            }, {});
        }
    },
    data() {
        return {
            field_types: {
                integer: "Целое число",
                float: "Число с точкой",
                text: "Текст",
                textarea: "Многострочный текст",
                checkbox: "Галочка",
                radio: "Выбор варианта",
                scale: "Шкала",
                date: "Дата",
                time: "Время",
            },
            current_contract_id: window.CONTRACT_ID,
            weekdays: ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'],
            axios: require('axios'),
            category_list: window.CATEGORY_LIST,
            native_types: {
                integer: ['integer'],
                float: ['float'],
                textarea: ['string'],
                text: ['string'],
                checkbox: ['string'],
                date: ['date'],
                time: ['string']
            },
            images: {
                form: window.LOCAL_HOST + '/static/images/icons8-fill-in-form-48.png',
                warning: window.LOCAL_HOST + '/static/images/icons8-error-18.png',
                medicine: window.LOCAL_HOST + '/static/images/icons8-pill-96.png',
                algorithm: window.LOCAL_HOST + '/static/images/icons8-artificial-intelligence-96.png',
                ok: window.LOCAL_HOST + '/static/images/icons8-ok-128.png',
                error: window.LOCAL_HOST + '/static/images/icons8-delete-128.png',
                graph: window.LOCAL_HOST + '/static/images/icons8-play-graph-report-48.png',
            },
            is_admin: window.IS_ADMIN,
            clinic_id: window.CLINIC_ID
        }
    }
})

window.onresize = function () {
    Event.fire('window-resized')
}

Vue.use(vmodal, {componentName: 'Modal'})
Vue.use(VueConfirmDialog)
Vue.component('vue-confirm-dialog', VueConfirmDialog.default)

new Vue({
    el: '#app',
    render: h => h(App),
})
