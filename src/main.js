import Vue from 'vue'
import App from './App.vue'
import axios from "axios";

window.Event = new class {
    constructor() {
        this.vue = new Vue();
    }

    fire(event, data = null) {
        if (!data && data !== 0)
        {
            console.log('sending event', event);
        }
        else {
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
        url: function (action) {
            let api_host = window.API_HOST;
            let agent_token = window.AGENT_TOKEN;
            let contract_id = window.CONTRACT_ID;
            let agent_id = window.AGENT_ID;

            return api_host + '/api/client/agents/' + agent_id + '/?action=' + action + '&contract_id=' + contract_id + '&agent_token=' + agent_token
        },
        ne: function (e) {
            return !e && e !== 0
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
                if (this.ne(point.hour) || this.ne(point.minute)) return true;
                if (point.hour < 0 || point.hour > 23) return true;
                if (point.minute < 0 || point.minute > 59) return true;
                return false;
            }
            let validate_point = general_validate;

            if (timetable.mode == 'weekly') {
                validate_point = (point) => {
                    if (general_validate(point)) return true;
                    if (this.ne(point.day) || point.day < 0 || point.day > 6) return true;
                    return false;
                }
            }
            if (timetable.mode == 'monthly') {
                validate_point = (point) => {
                    if (general_validate(point)) return true;
                    if (this.ne(point.day) || point.day < 1 || point.day > 31) return true;
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
          return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
            (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
          );
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
            },
            weekdays: ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'],
            axios: require('axios')
        }
    }
})

new Vue({
    el: '#app',
    render: h => h(App),
})
