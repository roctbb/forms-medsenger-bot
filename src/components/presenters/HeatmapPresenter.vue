<template>
    <div>
        <div style="margin-left: 10px;">
            <a class="btn btn-outline-info btn-sm" @click="select_graph()">Назад</a>
        </div>

        <div v-if="loaded">
            <div style="margin-left: 10px;"
                 v-if="heatmap_type == 'symptoms' && heatmap_data.medicine_series.length">
                <input type="checkbox" id="show_medicines" @change="showMedicines()" v-model="show_medicines"/>
                <label for="show_medicines">Показать лекарства</label>
            </div>


            <highcharts :constructor-type="'stockChart'" :options="options"
                        v-if="heatmap_data.medicine_series.length || heatmap_data.has_symptoms"></highcharts>

            <div class="text-center text-muted"
                 v-if="heatmap_type == 'symptoms' && !heatmap_data.has_symptoms ||
                       heatmap_type == 'medicines' && !heatmap_data.medicine_series.length">
                Нет данных
            </div>
        </div>

        <br>
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
    props: ['heatmap_type'],
    data() {
        return {
            group: {},
            data: [],
            options: {},
            show_medicines: true,
            loaded: false,
            heatmap_data: {},
            axis_height: "70%"
        }
    },
    methods: {
        load_data: function () {
            let data = {
                group: this.group
            }
            this.axios.post(this.url('/api/graph/group'), data).then(this.process_load_answer);
        },
        process_load_answer: function (response) {
            this.data = response.data

            let offset = -1 * new Date().getTimezoneOffset() * 60 * 1000
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
                scrollbar: {
                    step: 1
                },
                chart: {
                    type: 'heatmap',
                    zoomType: 'x',
                    backgroundColor: "#f8f8fb",
                    height: 0,
                    width: window.innerWidth
                },
                title: {
                    text: this.heatmap_type == 'symptoms' ? 'Симптомы' : 'Приемы лекарств'
                },
                series: [],
                xAxis: {
                    type: 'datetime',
                    gridLineWidth: 1,
                    minorGridLineWidth: 2,
                    minorTickLength: 0,
                    minorTickInterval: 24 * 3600 * 1000,
                    max: +now + offset,
                    ordinal: false,
                    dateTimeLabelFormats: {
                        day: '%d.%m'
                    }
                },
                zoom: 'x',
                yAxis: [
                    {
                        height: '70%',
                        gridLineWidth: 1,
                        lineWidth: 2,
                        resize: {
                            enabled: true
                        },
                        labels: {
                            align: 'left',
                            y: 5,
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
                            y: 5,
                            reserveSpace: true
                        },
                        top: '0%',
                        height: '100%',
                        gridLineWidth: 1,
                        offset: 0,
                        lineWidth: 2
                    }
                ],
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
                        [0, '#50B432'], [0.1, '#fcff00'], [1, '#ed341b']
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

            let y = 0;
            let symptoms = {}
            if (this.heatmap_type == 'symptoms') {
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
                            color: symptom.params.color != null ? symptom.params.color : 0.7,
                            description: "",
                            count: 1
                        }

                        let gr = symptom.params.symptom_group ? symptom.params.symptom_group : symptom.value

                        if (gr in symptoms) {
                            let old = symptoms[gr].find(ss => ss.date == s.date)
                            if (old) {
                                old.count++
                                old.color = old.color > s.color ? old.color : s.color
                                old.points.push(s.points[0])
                            } else {
                                symptoms[gr].push(s)
                            }
                        } else {
                            symptoms[gr] = [s]
                        }
                    })
                });

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
                        showInNavigator: false,
                        nullColor: '#50B432',
                        yAxis: 0,
                        name: key,
                        borderWidth: 1,
                        borderColor: "#555555",
                        states: {
                            inactive: {
                                opacity: 1,
                            }
                        },
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
                                value: val.color,
                                comment: val.description,
                            }
                        }).reverse()
                    })
                    y += 1;
                })
                this.options.yAxis[0].categories = Object.keys(symptoms)
            }

            let medicines = {}
            this.heatmap_data = {
                medicine_series: []
            }

            this.data.filter((graph) => graph.category.name == 'medicine').forEach((graph) => {
                graph.values.forEach((medicine) => {
                    let date = new Date(medicine.timestamp * 1000)
                    date.setHours(12)
                    date.setMinutes(0)
                    date.setSeconds(0)
                    date.setMilliseconds(0)

                    let m = {
                        points: [{
                            time: new Date(medicine.timestamp * 1000),
                            dose: medicine.params.dose
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
                        val.description += `<br> • <strong> ${this.formatTime(p.time)} ${p.dose == null ? '' : `(${p.dose})`} </strong>`
                    })
                })

                this.heatmap_data.medicine_series.push({
                    colsize: 24 * 36e5,
                    yAxis: this.heatmap_type == 'symptoms' ? 1 : 0,
                    name: key,
                    borderWidth: 1,
                    borderColor: "#555555",
                    states: {
                        inactive: {
                            opacity: 1,
                        }
                    },
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
            Array.prototype.push.apply(this.options.series, this.heatmap_data.medicine_series);
            this.options.yAxis[1].categories = Object.keys(medicines)

            if (this.heatmap_type == 'medicines') {
                this.options.yAxis.splice(0, 1)
            }

            let count = Object.keys(medicines).length + Object.keys(symptoms).length
            this.options.chart.height = count * 20 + 250
            if (this.heatmap_type == 'symptoms') {
                this.options.yAxis[0].height = 20 * Object.keys(symptoms).length
                this.options.yAxis[1].top = 20 * Object.keys(symptoms).length + 100
                this.options.yAxis[1].height = 20 * Object.keys(medicines).length
                this.axis_height = this.options.yAxis[0].height
            }


            if (this.heatmap_type == 'symptoms' && Object.entries(symptoms).length > 0) {
                this.heatmap_data.has_symptoms = true
                this.show_medicines = false
            }

            if (this.heatmap_type == 'symptoms' && !this.show_medicines) {
                this.showMedicines()
            }

            this.loaded = true
        },
        select_graph: function () {
            this.loaded = false;
            Event.fire('select-graph')
        },
        formatTime: function (date) {
            return date.toTimeString().substr(0, 5)
        },
        showMedicines: function () {
            if (this.show_medicines) {
                this.heatmap_data.medicine_series.forEach(s => {
                    this.options.series.push(s)
                })
                this.options.yAxis[0].height = this.axis_height
                this.options.yAxis[1].title.text = 'Лекарства'
            } else {
                let index = this.options.series.length - this.heatmap_data.medicine_series.length
                this.options.series.splice(index, this.heatmap_data.medicine_series.length)
                this.options.yAxis[0].height = "100%"
                this.options.yAxis[1].title.text = ''
            }
        }
    },
    created() {
        this.heatmap_data = {
            medicine_series: [],
            has_symptoms: false
        }

        Event.listen('load-heatmap', (group) => {
            this.group = {"categories": []}
            this.load_data()
        });

        Event.listen('window-resized', () => {
            if (this.options.chart != null)
                this.options.chart.width = window.innerWidth
        })
    }
}
</script>

<style scoped>

</style>
