<template>
    <div>
        <highcharts :constructor-type="'stockChart'" v-if="loaded" :options="options"></highcharts>

        <div class="container">
            <a class="btn btn-danger" @click="select_graph()">Назад</a>
        </div>

    </div>

</template>

<script>
import {Chart} from 'highcharts-vue'
import exporting from "highcharts/modules/exporting";
import 'highcharts/modules/heatmap.src.js';
import Highcharts from "highcharts";
import stockInit from 'highcharts/modules/stock'
import heatmap from 'highcharts/modules/heatmap';

stockInit(Highcharts)
heatmap(Highcharts);

export default {
    name: "HeatmapPresenter",
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
            let offset = -1 * new Date().getTimezoneOffset() * 60  * 1000
            var now = new Date()
            now.setHours(0)
            now.setMinutes(0)
            now.setSeconds(0)
            now.setDate(now.getDate() + 1)

            this.options = {
                rangeSelector: {
                    allButtonsEnabled: true,
                    buttons: [
                        {
                            type: 'week',
                            count: 1,
                            text: 'Неделя',
                        }, {
                            type: 'week',
                            count: 2,
                            text: '2 недели',
                        }, {
                            type: 'month',
                            count: 1,
                            text: 'Месяц',
                        }, {
                            type: 'all',
                            text: 'Все'
                        }],
                    buttonTheme: {
                        width: 60
                    },
                    selected: 1
                },
                chart: {
                    type: 'heatmap',
                    zoomType: 'x',
                    height: window.innerHeight - 70
                },
                title: {
                    text: 'Симптомы и приемы лекарств'
                },
                series: [],
                xAxis: {
                    type: 'datetime',
                    gridLineWidth: 1,
                    max: +now + offset,
                    ordinal: false,
                    labels: {
                        align: 'left',
                        reserveSpace: true
                    },
                },
                zoom: 'x',
                yAxis: [
                    {
                        height: '48%',
                        gridLineWidth: 1,
                        lineWidth: 2,
                        resize: {
                            enabled: true
                        },
                        labels: {
                            align: 'left',
                            reserveSpace: true
                        },
                        title: {
                            text: 'Симптомы'
                        }
                    },
                    {
                        title: {
                            text: 'Лекарства'
                        },
                        labels: {
                            align: 'left',
                            reserveSpace: true
                        },
                        top: '52%',
                        height: '48%',
                        gridLineWidth: 1,
                        offset: 0,
                        lineWidth: 2
                    }
                ],
                legend: {
                    enabled: true
                },
                tooltip: {
                    formatter: function () {
                        let point = this.point;
                        return point.comment
                    },
                    valueSuffix: ' cm',
                    shared: true
                },
                colorAxis: {
                    stops: [
                        [0, '#50B432'], [0.1, '#fcff00'],
                        [0.9, '#ed341b'], [1, '#c20000']
                    ],
                    min: 0,
                    max: 1,
                    startOnTick: false,
                    endOnTick: false,
                    labels: {
                        format: '{value}'
                    }
                }
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

            let symptoms = {}

            this.data.filter((graph) => graph.category.name == 'symptom').forEach((graph) => {
                graph.values.forEach((symptom) => {
                    let date = new Date(symptom.timestamp * 1000)
                    date.setHours(12)
                    date.setMinutes(0)
                    date.setSeconds(0)
                    date.setMilliseconds(0)

                    let s = {
                        points: [{
                            time: new Date(symptom.timestamp * 1000),
                            description: symptom.value,
                        }],
                        date: +date + offset,
                        grade: symptom.params.grade != null ? symptom.params.grade : 0.7,
                        description: "",
                        count: 1
                    }

                    let gr = symptom.params.symptom_group ? symptom.params.symptom_group : symptom.value

                    if (gr in symptoms) {
                        let old = symptoms[gr].find(ss => ss.date == s.date)
                        if (old) {
                            old.count++
                            old.grade = old.grade > s.grade ? old.grade : s.grade
                            old.points.push(s.points[0])
                        } else {
                            symptoms[gr].push(s)
                        }
                    } else {
                        symptoms[gr] = [s]
                    }
                })
            });

            let y = 0;

            Object.entries(symptoms).forEach(([key, value]) => {
                value.forEach(val => {
                    val.points.sort((a, b) => {
                        return a.time < b.time ? -1 : a.time > b.time ? 1 : 0
                    })
                    val.points.forEach(p => {
                        val.description += " • <strong>" + this.formatTime(p.time) + "</strong> - " + p.description + "<br>"
                    })
                })

                this.options.series.push({
                    colsize: 24 * 36e5,
                    connectNulls: true,
                    nullColor: '#50B432',
                    yAxis: 0,
                    name: key,
                    borderWidth: 1,
                    borderColor: "#555555",
                    data: value.map((val) => {
                        return {
                            dataLabels: {
                                enabled: true,
                                formatter: function () {
                                    return val.count
                                },
                            },
                            x: val.date,
                            y: y,
                            name: key,
                            value: val.grade,
                            comment: val.description,
                        }
                    }).reverse()
                })
                y += 1;
            })
            this.options.yAxis[0].categories = Object.keys(symptoms)

            let medicines = {}

            this.data.filter((graph) => graph.category.name == 'medicine').forEach((graph) => {
                graph.values.forEach((medicine) => {
                    let date = new Date(medicine.timestamp * 1000)
                    date.setHours(12)
                    date.setMinutes(0)
                    date.setSeconds(0)
                    date.setMilliseconds(0)

                    let m = {
                        points: [{
                            time: new Date(medicine.timestamp * 1000)
                        }],
                        date: +date + offset,
                        description: "Прием лекарства <strong>" + medicine.value + "</strong> в ",
                        count: 1
                    }

                    if (medicine.value in medicines) {
                        let old = medicines[medicine.value].find(mm => mm.date == m.date)
                        if (old) {
                            old.count++
                            old.points.push(m.points[0])
                        } else {
                            medicines[medicine.value].push(m)
                        }
                    } else {
                        medicines[medicine.value] = [m]
                    }
                })
            });

            y = 0;

            Object.entries(medicines).forEach(([key, value]) => {
                value.forEach(val => {
                    val.points.sort((a, b) => {
                        return a.time < b.time ? -1 : a.time > b.time ? 1 : 0
                    })
                    val.points.forEach(p => {
                        val.description += "<br> • <strong>" + this.formatTime(p.time) + "</strong>"
                    })
                })

                this.options.series.push({
                    colsize: 24 * 36e5,
                    yAxis: 1,
                    name: key,
                    borderWidth: 1,
                    borderColor: "#555555",
                    data: value.map((val) => {
                        return {
                            dataLabels: {
                                enabled: true,
                                formatter: function () {
                                    return val.count
                                },
                            },
                            x: +val.date,
                            y: y,
                            name: key,
                            color: '#d1f6f6',
                            comment: val.description,
                        }
                    }).reverse()
                })
                y += 1;
            })
            this.options.yAxis[1].categories = Object.keys(medicines)

            this.loaded = true
        },
        select_graph: function () {
            this.loaded = false;
            Event.fire('select-graph')
        },
        formatTime: function (date) {
            return date.toTimeString().substr(0, 5)
        }
    },
    created() {
        Event.listen('load-heatmap', (group) => {
            this.group = {"categories": []}
            this.load_data()
        });
    }
}
</script>

<style scoped>

</style>
