<template>
    <div>
        <h3>График "{{ group.title }}"</h3>

        <highcharts :constructor-type="'stockChart'" v-if="loaded" :options="options"></highcharts>

        <a class="btn btn-danger" @click="select_graph()">Назад</a>

    </div>
</template>

<script>
import {Chart} from 'highcharts-vue'
import exporting from "highcharts/modules/exporting";
import Highcharts from "highcharts";
import stockInit from 'highcharts/modules/stock'

stockInit(Highcharts)

export default {
    name: "GraphPresenter",
    components: {highcharts: Chart},
    props: {},
    data() {
        return {
            group: {},
            data: [],
            options: {},
            loaded: false
        }
    },
    methods: {
        load_data: function () {
            this.axios.post(this.url('/api/graph/group'), this.group).then(this.process_load_answer);
        },
        process_load_answer: function (response) {
            this.data = response.data

            this.options = {
                chart: {
                    type: 'line',
                    zoomType: 'x',
                },
                title: {
                    text: this.group.title
                },
                series: [],
                xAxis: {type: 'datetime'},
                zoom: 'x',
                yAxis: {
                    title: {
                        text: 'Значение'
                    }
                },
                plotOptions: {
                    line: {
                        dataLabels: {
                            enabled: true
                        },
                    }
                },
            }

            Highcharts.setOptions({
                lang: {
                    loading: 'Загрузка...',
                    months: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
                    weekdays: ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'],
                    shortMonths: ['Янв', 'Фев', 'Март', 'Апр', 'Май', 'Июнь', 'Июль', 'Авг', 'Сент', 'Окт', 'Нояб', 'Дек'],
                    exportButtonTitle: "Экспорт",
                    printButtonTitle: "Печать",
                    rangeSelectorFrom: "С",
                    rangeSelectorTo: "По",
                    rangeSelectorZoom: "Период",
                    downloadPNG: 'Скачать PNG',
                    downloadJPEG: 'Скачать JPEG',
                    downloadPDF: 'Скачать PDF',
                    downloadSVG: 'Скачать SVG',
                    printChart: 'Напечатать график',
                    resetZoom: 'Весь график'
                }
            });

            this.data.forEach((graph) => {
                this.options.series.push({
                    name: graph.category.description,
                    data: graph.values.map((value) => [value.timestamp * 1000, value.value]).reverse()
                })
            })

            console.log(this.options)

            this.loaded = true
        },
        select_graph: function () {
            this.loaded = false;
            Event.fire('select-graph')
        }
    },
    computed: {},
    created() {
        Event.listen('load-graph', (group) => {
            this.group = group
            this.load_data()
        });
    }
}
</script>

<style scoped>

</style>
