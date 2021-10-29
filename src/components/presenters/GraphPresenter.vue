<template>
    <div>
        <!-- выбор периода -->
        <div class="container" v-if="!mobile">
            <div class="row">
                <a class="btn btn-danger btn-sm" @click="select_graph()">Назад</a>
                <button class="btn btn-primary btn-sm" @click="scroll_dates(true)">◂</button>

                <date-picker format="с YYYY-MM-DD" v-model="dates.range[0]" @change="dates.period = -1"></date-picker>
                <date-picker format="по YYYY-MM-DD" v-model="dates.range[1]" @change="dates.period = -1"></date-picker>

                <button class="btn btn-primary btn-sm" @click="scroll_dates(false)">▸</button>

                <select class="form-control form-control-sm col-2" v-model="dates.period" @change="select_period()">
                    <option :value="30">Месяц</option>
                    <option :value="14">Две недели</option>
                    <option :value="7">Неделя</option>
                    <option :value="3" v-if="type == 'line'">Три дня</option>
                    <option :value="1" v-if="type == 'line'">День</option>
                    <option :value="-1">Не выбран</option>
                </select>

                <a class="btn btn-success btn-sm" @click="load_data()">Загрузить</a>
            </div>
        </div>
        <div class="container" v-else>
            <div class="row" style="margin-left: 0">
                <a class="btn btn-danger btn-sm" @click="select_graph()">Назад</a>
            </div>
            <div class="row">
                <date-picker format="с YYYY-MM-DD" v-model="dates.range[0]" class="col" @change="dates.period = -1"></date-picker>
            </div>
            <div class="row">
                <date-picker format="по YYYY-MM-DD" v-model="dates.range[1]" class="col"
                             @change="dates.period = -1"></date-picker>
            </div>

            <div class="row" style="margin-left: 0; grid-column-gap: 3px;">
                <button class="btn btn-primary btn-sm" @click="scroll_dates(true)">◂</button>
                <button class="btn btn-primary btn-sm" @click="scroll_dates(false)">▸</button>

                <select class="form-control form-control-sm col" style="margin-right: 15px;"
                        v-model="dates.period" @change="select_period()">
                    <option :value="30">Месяц</option>
                    <option :value="14">Две недели</option>
                    <option :value="7">Неделя</option>
                    <option :value="3" v-if="type == 'line'">Три дня</option>
                    <option :value="1" v-if="type == 'line'">День</option>
                    <option :value="-1">Не выбран</option>
                </select>
            </div>

            <a class="btn btn-success btn-sm" @click="load_data()">Загрузить</a>
        </div>

        <!-- Ошибки -->
        <hr>
        <error-block :errors="errors" v-if="errors.length"></error-block>

        <!-- График -->
        <div v-if="loaded">
            <div style="margin-left: 10px;" class="container"
                 v-if="type == 'heatmap' && group.categories.includes('symptom') && heatmap_data.medicine_series.length && !no_data">
                <input type="checkbox" id="show_medicines" @change="show_medicines()" v-model="heatmap_data.show_medicines"/>
                <label for="show_medicines">Показать лекарства</label>
            </div>

            <div class="container" v-if="type == 'line' && !no_data">
                <input type="checkbox" v-model="options.legend.enabled" id="show_legend"/>
                <label for="show_legend">Показать легенду</label>
            </div>

            <div class="text-center text-muted" v-if="no_data">
                Нет данных за выбранный период
            </div>

            <highcharts :constructor-type="'stockChart'" :options="options" v-else></highcharts>

            <!-- Табличка -->
            <div class="container center" v-if="type == 'line' && this.statistics.length  && !no_data">
                <h5 class="text-center">Значения параметров за выбранный период</h5>

                <table class="table table-hover table-striped" v-if="!mobile">
                    <thead>
                    <tr>
                        <th scope="col" class="bg-info text-light">Параметр</th>
                        <th scope="col" class="bg-info text-light">Среднее</th>
                        <th scope="col" class="bg-info text-light">Мин</th>
                        <th scope="col" class="bg-info text-light">Макс</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr v-for="stat in this.statistics">
                        <th scope="row" style="text-align: left;">{{ stat.name }}</th>
                        <td>{{ stat.avg.toFixed(2) * 1 }}</td>
                        <td>{{ stat.min.toFixed(2) * 1 }}</td>
                        <td>{{ stat.max.toFixed(2) * 1 }}</td>
                    </tr>
                    </tbody>
                </table>

                <div v-else-if="type == 'line'" v-for="stat in this.statistics">
                    <hr>
                    <h6 class="text-center">{{ stat.name }}</h6>
                    <table class="table table-hover table-striped">
                        <thead>
                        <tr>
                            <th scope="col" class="bg-info text-light">Среднее</th>
                            <th scope="col" class="bg-info text-light">Мин</th>
                            <th scope="col" class="bg-info text-light">Макс</th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr>
                            <td>{{ stat.avg.toFixed(2) * 1 }}</td>
                            <td>{{ stat.min.toFixed(2) * 1 }}</td>
                            <td>{{ stat.max.toFixed(2) * 1 }}</td>
                        </tr>
                        </tbody>
                    </table>
                </div>

            </div>
        </div>
        <loading v-else-if="!errors.length"></loading>
        <br>

    </div>
</template>

<script>
import {Chart} from 'highcharts-vue'
import Highcharts from "highcharts";
import stockInit from 'highcharts/modules/stock'
import DatePicker from 'vue2-datepicker';
import 'vue2-datepicker/index.css';
import 'vue2-datepicker/locale/ru';
import * as moment from "moment/moment";
import ErrorBlock from "../common/ErrorBlock";
import Loading from "../Loading";
import boost from "highcharts/modules/boost";
import heatmap from "highcharts/modules/heatmap";
import 'highcharts/modules/heatmap.src.js';

stockInit(Highcharts)
heatmap(Highcharts);
boost(Highcharts)

export default {
    name: "GraphPresenter",
    components: {Loading, ErrorBlock, highcharts: Chart, DatePicker},
    props: ['patient'],
    data() {
        return {
            dates: [],
            errors: [],
            group: {},
            data: [],
            heatmap_data: {},
            options: {},
            statistics: [],
            type: undefined,
            loaded: false,
            no_data: true
        }
    },
    computed: {
        offset() {
            return -1 * new Date().getTimezoneOffset() * 60
        }
    },
    methods: {
        select_graph: function () {
            this.loaded = false;
            window.OBJECT_ID = undefined;
            Event.fire('select-graph')
        },
        load_data: function () {
            this.loaded = false
            this.no_data = true
            this.errors = []

            if (this.type == 'line' && !this.group.categories.includes('symptom')) {
                this.group.categories = this.group.categories.concat(['symptom', 'medicine'])
            }

            let data = {
                group: this.group,
                dates: {
                    start: this.dates.range[0].getTime() / 1000,
                    end: this.dates.range[1].getTime() / 1000 + 24 * 60 * 60 - 1,
                }
            }

            if (data.dates.start > data.dates.end) {
                this.errors = ['Выбран некорректный период']
                return
            }
            this.axios.post(this.url('/api/graph/group'), data).then(this.process_load_answer);
        },

        process_load_answer: function (response) {
            this.data = response.data
            let start = this.dates.range[0].getTime()
            let end = this.dates.range[1].getTime() + 24 * 60 * 60 * 1000 - 1

            this.options = {
                chart: this.get_chart(),
                series: [],
                title: {
                    text: this.group.title
                },
                xAxis: {
                    type: 'datetime',
                    gridLineWidth: 1,
                    minorGridLineWidth: 2,
                    minorTickLength: 0,
                    minorTickInterval: 24 * 3600 * 1000,
                    min: start,
                    max: end,
                    ordinal: false,
                    dateTimeLabelFormats: {
                        day: '%d.%m'
                    }
                },
                zoom: 'x',
                yAxis: [
                    this.get_y_axis(0),
                    this.get_y_axis(1)
                ],
                tooltip: {
                    formatter: function () {
                        let point = this.point ? this.point : this.points[0];
                        return point.comment
                    },
                    pointFormatter: function () {
                        let point = this;
                        return point.series.userOptions.data.filter(p => p.x == point.x).map(p => {
                            return p.comment
                        }).join('<br>')
                    },
                    shared: true,
                    headerFormat: null
                },
                legend: {},
                plotOptions: {},
                rangeSelector: {
                    enabled: false,
                },
                scrollbar: {
                    step: 1
                },
            }

            if (this.type == 'line') {
                this.options.colors = ['#058DC7', '#50B432', '#aa27ce', '#fcff00',
                    '#24CBE5', '#64E572', '#c355ff', '#fce200', '#6AF9C4']
                this.options.tooltip.formatter = undefined

                this.options.plotOptions = {
                    line: {
                        dataLabels: {
                            enabled: true
                        }
                    },
                    series: {
                        marker: {
                            lineWidth: 1,
                            lineColor: null,
                        }
                    }
                }
                this.options.legend = {
                    enabled: true,
                    itemDistance: 70,
                    labelFormatter: function () {
                        return this.name
                    }
                }
            } else {
                this.options.tooltip.pointFormatter = undefined
                this.options.colorAxis = {
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

            this.options.series = this.get_series()

            if (this.type == 'heatmap') {
                let count = this.heatmap_data.categories.symptoms.length + this.heatmap_data.categories.medicines.length
                this.options.chart.height = count * 20 + 250

                this.options.yAxis[0].categories = this.heatmap_data.categories.symptoms
                this.options.yAxis[1].categories = this.heatmap_data.categories.medicines

                if (this.group.categories.includes('symptom')) {
                    this.options.yAxis[0].height = 20 * this.heatmap_data.categories.symptoms.length

                    this.options.yAxis[1].top = 20 * this.heatmap_data.categories.symptoms.length + 100
                    this.options.yAxis[1].height = 20 * this.heatmap_data.categories.medicines.length

                    if (this.heatmap_data.categories.symptoms.length) {
                        this.heatmap_data.show_medicines = false
                        this.show_medicines()
                    }
                } else {
                    this.options.yAxis.splice(0, 1)
                }
            }

            if (this.group.categories.includes('glukose'))
                this.set_bands()

            this.is_empty()
            this.loaded = true
        },
        get_series: function () {
            let series = []
            series = series.concat(this.get_symptom_series())
            series = series.concat(this.get_medicine_series())

            if (this.type == 'line') {
                let graph_series = this.get_graph_series()
                series = graph_series.concat(series)

                if (graph_series.length && graph_series.map(s => s.data.length).reduce((a, b) => a + b) > 500) {
                    this.errors = ['За данный период в медицинской карте присутствует слишком большое количество записей (> 500). ' +
                    'Чтобы увидеть комментарии к точкам и симптомы, загрузите период с меньшим количеством записей.']
                    graph_series.forEach(s => {
                        s.data = s.data.map(d => [d.x, d.y])
                    })
                    this.options.plotOptions.line.dataLabels.enabled = false
                }

                if (this.mobile && series.length > 2)
                    this.options.chart.height += 50 * (this.options.series.length - 2)
            }

            return series
        },
        get_graph_series: function () {
            return this.data.filter((graph) => graph.category.type != 'string').map((graph) => {
                let series_data = {
                    name: graph.category.description,
                    code: graph.category.name,
                    values: graph.values,
                    marker: 'circle'
                }

                return this.prepare_series(series_data)
            })
        },
        get_medicine_series: function () {
            let medicines = {}
            let series

            if (this.type == 'line') {
                let y = -5
                this.data.filter((graph) => graph.category.name == 'medicine').forEach((graph) => {
                    graph.values.forEach((medicine) => {
                        let dict = {
                            timestamp: medicine.timestamp,
                            dose: !medicine.params || medicine.params.dose == null ? '' : ` (${medicine.params.dose})`
                        }
                        if (medicine.value in medicines)
                            medicines[medicine.value].push(dict)
                        else
                            medicines[medicine.value] = [dict]
                    })
                });

                series = Object.entries(medicines).map(([medicine, values]) => {
                    let series_data = {
                        name: medicine,
                        code: 'medicine',
                        values: values,
                        marker: 'square',
                        y: y
                    }

                    y -= 4

                    return this.prepare_series(series_data)
                })
            } else {
                let medicines = {}
                let y = 0;

                this.data.filter((graph) => graph.category.name == 'medicine').forEach((graph) => {
                    graph.values.forEach((medicine) => {
                        let x = new Date((medicine.timestamp) * 1000)
                        x.setHours(12, 0, 0)

                        let medicine_data = {
                            points: [{
                                time: new Date(medicine.timestamp * 1000),
                                dose: !medicine.params || medicine.params.dose == null ? '' : ` (${medicine.params.dose})`
                            }],
                            x: +x + this.offset * 1000,
                            description: `Прием лекарства <strong>${medicine.value}</strong> в `,
                        }

                        if (medicine.value in medicines) {
                            let old = medicines[medicine.value].find(m => m.x == medicine_data.x)
                            if (old) {
                                old.points.push(medicine_data.points[0])
                            } else {
                                medicines[medicine.value].push(medicine_data)
                            }
                        } else {
                            medicines[medicine.value] = [medicine_data]
                        }
                    })
                });

                series = Object.entries(medicines).map(([medicine, medicine_data]) => {
                    medicine_data.forEach(data => {
                        data.points.sort((a, b) => {
                            return a.time < b.time ? -1 : a.time > b.time ? 1 : 0
                        })
                        data.points.forEach(p => {
                            data.description += `<br>• <strong>${this.format_time(p.time)}</strong> ${p.dose}`
                        })
                    })

                    let series_data = {
                        name: medicine,
                        code: 'medicine',
                        values: medicine_data,
                        y: y
                    }

                    y += 1
                    return this.prepare_series(series_data)
                });

                this.heatmap_data.medicine_series = series
                this.heatmap_data.categories.medicines = Object.keys(medicines)
            }

            return series
        },
        get_symptom_series: function () {
            let series

            if (this.type == 'line') {
                series = this.data.filter((graph) => graph.category.name == 'symptom').map((graph) => {
                    let series_data = {
                        name: 'Симптом',
                        code: 'symptom',
                        values: graph.values,
                        marker: 'triangle',
                        y: -3
                    }

                    return this.prepare_series(series_data)
                })
            } else {
                let symptoms = {}
                let y = 0;

                this.data.filter((graph) => graph.category.name == 'symptom').forEach((graph) => {
                    graph.values.forEach((symptom) => {
                        let x = new Date((symptom.timestamp) * 1000)
                        x.setHours(12, 0, 0)

                        let symptom_data = {
                            points: [{
                                time: new Date(symptom.timestamp * 1000),
                                description: symptom.value,
                            }],
                            color: symptom.params.color != null ? symptom.params.color : 0.7,
                            description: '',
                            x: +x + this.offset * 1000,
                        }

                        let symptom_group = symptom.params.symptom_group ? symptom.params.symptom_group : symptom.value

                        if (symptom_group in symptoms) {
                            let old = symptoms[symptom_group].find(s => s.x == symptom_data.x)
                            if (old) {
                                old.color = old.color > symptom_data.color ? old.color : symptom_data.color
                                old.points.push(symptom_data.points[0])
                            } else {
                                symptoms[symptom_group].push(symptom_data)
                            }
                        } else {
                            symptoms[symptom_group] = [symptom_data]
                        }
                    })
                });

                series = Object.entries(symptoms).map(([symptom, symptom_data]) => {
                    symptom_data.forEach(data => {
                        data.points.sort((a, b) => {
                            return a.time < b.time ? -1 : a.time > b.time ? 1 : 0
                        })
                        data.points.forEach(p => {
                            data.description += `• <strong>${this.format_time(p.time)}</strong> - ${p.description}<br>`
                        })
                    })

                    let series_data = {
                        name: symptom,
                        code: 'symptom',
                        values: symptom_data,
                        y: y
                    }

                    y += 1
                    return this.prepare_series(series_data)
                });

                this.heatmap_data.categories.symptoms = Object.keys(symptoms)
            }

            return series
        },
        prepare_series: function (data) {
            let series = {
                name: data.name,
                category_code: data.code,
                data: this.prepare_values(data),
                showInNavigator: false,
                states: {
                    inactive: {
                        opacity: 1,
                    }
                },
            }

            if (this.type == 'line') {
                series.marker = {
                    enabled: true,
                    radius: 4,
                    symbol: data.marker
                }

                series.dataGrouping = {
                    enabled: false
                }

                if (['symptom', 'medicine'].includes(data.code)) {
                    series.yAxis = 1
                    series.lineWidth = 0
                    if (data.code == 'symptom') {
                        series.color = '#ad0eca'
                        series.marker.radius = 5
                    }
                } else {
                    series.yAxis = 0
                    series.showInNavigator = true
                    series.dashStyle = 'ShortDot'
                    series.lineWidth = 3
                }
            } else {
                series.yAxis = +(this.group.categories.length == 2 && data.code == 'medicine')
                series.colsize = 24 * 36e5
                series.connectNulls = true

                series.nullColor = '#50B432'
                series.borderWidth = 1
                series.borderColor = '#555555'
            }

            return series
        },
        prepare_values: function (data) {
            let res
            if (this.type == 'line') {
                if (data.code == 'medicine') {
                    res = data.values.map((value) => {
                        return {
                            dataLabels: {
                                enabled: false,
                            },
                            x: (value.timestamp + this.offset) * 1000,
                            y: data.y,
                            comment: this.get_comment({
                                value: data.name + value.dose,
                                timestamp: value.timestamp
                            }, `Прием лекарства`),
                        }
                    })
                } else if (data.code == 'symptom') {
                    res = data.values.map((value) => {
                        let x = new Date((value.timestamp) * 1000)
                        x.setHours(12, 0, 0)
                        return {
                            dataLabels: {
                                enabled: false,
                            },
                            x: +x + this.offset * 1000,
                            y: data.y,
                            comment: this.get_comment(value, data.name),
                        }
                    })
                } else {
                    res = data.values.map((value) => {
                        return {
                            x: (value.timestamp + this.offset) * 1000,
                            y: value.value,
                            comment: this.get_comment(value, data.name),
                            marker: {
                                symbol: this.get_symbol(value),
                                lineColor: this.get_color(value),
                                radius: this.get_radius(value),
                            }
                        }
                    })
                }
            } else {
                if (data.code == 'symptom') {
                    res = data.values.map(value => {
                        return {
                            dataLabels: {
                                enabled: true,
                                formatter: function () {
                                    return value.points.length
                                },
                            },
                            x: value.x,
                            y: data.y,
                            name: data.name,
                            value: value.color,
                            comment: value.description,
                        }
                    })
                } else {
                    res = data.values.map(value => {
                        return {
                            dataLabels: {
                                enabled: true,
                                formatter: function () {
                                    return value.points.length
                                },
                            },
                            x: value.x,
                            y: data.y,
                            name: data.name,
                            color: '#d1f6f6',
                            comment: value.description,
                        }
                    })
                }
            }
            return res.reverse()
        },
        get_y_axis: function (index) {
            let axis = {
                gridLineWidth: 1,
                lineWidth: 2,
                resize: {
                    enabled: true
                }
            }

            if (this.type == 'line') {
                axis.title = {
                    text: index ? 'События' : 'Значения'
                }

                axis.labels = {
                    align: 'right',
                    x: -3
                }
                axis.height = index ? '15%' : '80%'
                if (index) axis.top = '85%'
            } else {
                axis.title = {
                    text: index ? 'Лекарства' : 'Симптомы'
                }

                axis.labels = {
                    align: 'left',
                    y: 5,
                    reserveSpace: true
                }

                axis.height = index ? '100%' : '70%'
                axis.top = '0%'
                axis.offset = 0
            }

            return axis
        },
        get_chart: function () {
            let chart = {
                type: this.type,
                boostThreshold: 500,
                turboThreshold: 0,
                animation: false,
                zoomType: 'x',
                backgroundColor: "#f8f8fb",
                height: window.innerHeight,
                width: window.innerWidth
            }

            if (this.type == 'line') {
                chart.events = {
                    render: function (event) {
                        let stats = []

                        let binary_search = function (arr, value, l, r) {
                            let mid = Math.floor((r - l) / 2) + l

                            if (arr[mid] == value)
                                return mid;
                            if (r - l == 0)
                                return r + (arr[r] < value ? 1 : 0);
                            if (arr[mid] < value) {
                                l = (mid + 1) > r ? r : (mid + 1)
                                return binary_search(arr, value, l, r);
                            }
                            r = (mid - 1) < l ? l : (mid - 1)
                            return binary_search(arr, value, l, r);
                        }

                        let find_visible_data = function (data) {
                            const start = event.target.axes[0].min
                            const end = event.target.axes[0].max

                            let timestamps = data.map(point => point.x)

                            let start_index = binary_search(timestamps, start, 0, data.length - 1)
                            let end_index = binary_search(timestamps, end, 0, data.length - 1)

                            return data.slice(start_index, end_index).map(point => point.y)
                        }

                        this.series.filter(series => series.userOptions.yAxis == 0).forEach(series => {
                            let data = find_visible_data(series.data)

                            if (data.length) {
                                // calculate statistics for visible points
                                const max = data.reduce((a, b) => Math.max(a, b))
                                const min = data.reduce((a, b) => Math.min(a, b))
                                const average = (data.reduce((a, b) => a + b, 0) / data.length).toFixed(2) * 1

                                if (data.length > 0) {
                                    stats.push({
                                        name: series.name,
                                        code: series.options.category_code,
                                        data: data,
                                        avg: average,
                                        min: min,
                                        max: max
                                    })
                                }
                            }
                        });

                        let systolic_pressure = stats.find(st => st.code == 'systolic_pressure')
                        let diastolic_pressure = stats.find(st => st.code == 'diastolic_pressure')

                        if (systolic_pressure != null && diastolic_pressure != null) {
                            let pp_data = []
                            let map_data = []
                            systolic_pressure.data.forEach((s, index) => {
                                let d = diastolic_pressure.data[index]
                                map_data.push((s - d) / 3 + d)
                                pp_data.push(s - d)
                            })

                            stats.push({
                                name: 'Среднее давление (MAP)',
                                code: 'map',
                                avg: map_data.reduce((a, b) => a + b, 0) / map_data.length,
                                min: map_data.reduce((a, b) => Math.min(a, b)),
                                max: map_data.reduce((a, b) => Math.max(a, b))
                            })

                            stats.push({
                                name: 'Пульсовое давление',
                                code: 'pulse_pressure',
                                avg: pp_data.reduce((a, b) => a + b, 0) / pp_data.length,
                                min: pp_data.reduce((a, b) => Math.min(a, b)),
                                max: pp_data.reduce((a, b) => Math.max(a, b))
                            })
                        }

                        Event.fire('refresh-stats', stats)
                    }
                }
            }

            return chart
        },

        set_bands: function () {
            this.options.yAxis[0].plotBands = [{
                from: 0,
                to: 3,
                color: "rgba(255,117,117,0.25)"
            }, {
                from: 18,
                to: 100,
                color: "rgba(255,117,117,0.25)"
            }, {
                from: 3,
                to: 4,
                color: "rgba(255,209,117,0.25)"
            }, {
                from: 12,
                to: 18,
                color: "rgba(255,209,117,0.25)"
            }, {
                from: 4,
                to: 12,
                color: "rgba(186,255,117,0.25)"
            }]

            let min = null, max = null

            this.axios.get(this.url('/params')).then(response => {
                response.data.forEach(param => {
                    if (param.name && param.value != null) {
                        if (param.code == 'min_glukose' && (min == null || min > param.value))
                            min = param.value
                        if (param.code == 'max_glukose' && (max == null || max < param.value))
                            max = param.value
                    }
                })

                if (min != null) {
                    this.options.yAxis[0].plotBands[2].to = min
                    this.options.yAxis[0].plotBands[4].from = min
                }
                if (max != null) {
                    this.options.yAxis[0].plotBands[3].from = max
                    this.options.yAxis[0].plotBands[4].to = max
                }
            });
        },

        // Вспомогательные
        get_color: function (point) {
            if (point.additions) {
                return '#FF0000';
            }
            return undefined;
        },
        get_symbol: function (point) {
            if (point.additions) {
                return 'url(' + this.images.warning + ')'
            }
            return undefined;
        },
        get_radius: function (point) {
            if (point.additions) {
                return 6;
            }
            return undefined;
        },
        get_comment: function (point, category) {

            let comment = `<strong>${this.format_time(new Date((point.timestamp) * 1000))}</strong> - ${category}: ${point.value}`
            if (point.additions) {
                point.additions.forEach((value) => {
                    comment += `<br><strong style="color: red;">${value['addition']['comment']}</strong>`
                })
            }
            return comment
        },
        format_time: function (date) {
            return date.toTimeString().substr(0, 5)
        },
        is_empty: function () {
            this.options.series.forEach(s => {
                if (s.data.length) this.no_data = false
            })
            if (this.type == 'heatmap' && this.group.categories.includes('symptom') &&
                !this.heatmap_data.categories.symptoms.length) this.no_data = true
        },
        show_medicines: function () {
            if (this.heatmap_data.show_medicines) {
                this.options.series = this.options.series.concat(this.heatmap_data.medicine_series)

                this.options.yAxis[1].title.text = 'Лекарства'

                this.options.chart.height += 20 * this.heatmap_data.categories.medicines.length
            } else {
                let index = this.heatmap_data.categories.symptoms.length
                this.options.series.splice(index, this.heatmap_data.categories.medicines.length)

                this.options.yAxis[1].title.text = ''
                this.options.chart.height -= 20 * this.heatmap_data.categories.medicines.length
            }
        },

        scroll_dates: function (back) {
            let start = moment(this.dates.range[0])
            let end = moment(this.dates.range[1])
            let duration = start.diff(end, 'day')

            if (this.dates.range[1] > this.dates.range[0]) {
                this.dates.range[0] = new Date(start.add((back ? 1 : -1) * duration, 'days').format('YYYY-MM-DD'))
                this.dates.range[1] = new Date(end.add((back ? 1 : -1) * duration, 'days').format('YYYY-MM-DD'))
            }
        },
        select_period: function () {
            let end = moment(this.dates.range[1])
            this.dates.range[0] = new Date(end.add(-this.dates.period, 'days').format('YYYY-MM-DD'))
        }
    },
    created() {
        this.dates = {
            range: [],
            period: '2 week'
        }
        Event.listen('load-graph', (group) => {
            this.type = 'line'
            this.dates.range = [new Date(moment().add(-14, 'days').format('YYYY-MM-DD')), new Date(moment().format('YYYY-MM-DD'))]
            this.dates.period = 14
            this.group = group
            this.load_data()
        });

        Event.listen('load-heatmap', (group) => {
            this.type = 'heatmap'
            this.dates.range = [new Date(moment().add(-14, 'days').format('YYYY-MM-DD')), new Date(moment().format('YYYY-MM-DD'))]
            this.dates.period = 14
            this.group = group

            this.heatmap_data = {
                medicine_series: [],
                categories: {
                    symptoms: [],
                    medicines: []
                },
                show_medicines: true
            }

            this.load_data()
        });

        Event.listen('refresh-stats', (stats) => {
            this.statistics = stats
        })

        Event.listen('window-resized', () => {
            if (this.options.chart != null) {
                this.options.chart.height = window.innerHeight
                this.options.chart.width = window.innerWidth

                if (this.options.chart.height > this.options.chart.width && this.options.series.length > 2) {
                    this.options.chart.height += 50 * (this.options.series.length - 2)
                }
            }
        })
    }
}
</script>

<style scoped>
.table {
    table-layout: fixed;
    width: 100%;
    text-align: center;
    font-size: 0.8rem;
}

.container {
    padding: 5px 10px 5px 0;
}

.row {
    grid-column-gap: 10px;
    margin-bottom: 5px;
}
</style>
