import Vue from 'vue'
import App from './App.vue'

window.Event = new class {
    constructor() {
        this.vue = new Vue();
    }
    fire (event, data = null) {
        console.log('sending event', event);
        this.vue.$emit(event, data);
    }
    listen(event, callback)
    {
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
           weekdays: ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
       }
    }
})

new Vue({
    el: '#app',
    render: h => h(App),
})
