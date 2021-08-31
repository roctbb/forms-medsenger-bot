<template>
    <div>
        <div class="container row">
            <div class="col-1">
                <a class="btn btn-outline-info btn-sm" @click="select_graph()">Назад</a>
            </div>
            <div class="col-4">
                <span>c </span>
                <date-picker v-model="dates.start" value-type="YYYY-MM-DD"></date-picker>
            </div>
            <div class="col-4">
                <span>по </span>
                <date-picker v-model="dates.end" value-type="YYYY-MM-DD"></date-picker>
            </div>
            <div class="col-1">
                <a class="btn btn-success btn-sm" @click="load_data()">Загрузить</a>
            </div>
        </div>

        <hr>
        <error-block :errors="errors" v-if="errors.length"></error-block>

        <div v-if="loaded">
            <highcharts :constructor-type="'stockChart'" :options="options"></highcharts>

            <div class="container">
                <input type="checkbox" v-model="options.legend.enabled" id="show_legend"/>
                <label for="show_legend">Показать легенду</label>
            </div>

            <div class="container center" v-if="this.statistics.length">
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

                <div v-else v-for="stat in this.statistics">
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
import exporting from "highcharts/modules/exporting";
import Highcharts from "highcharts";
import stockInit from 'highcharts/modules/stock'
import DatePicker from 'vue2-datepicker';
import 'vue2-datepicker/index.css';
import 'vue2-datepicker/locale/ru';
import * as moment from "moment/moment";
import ErrorBlock from "../common/ErrorBlock";
import Loading from "../Loading";

stockInit(Highcharts)

export default {
    name: "GraphPresenter",
    components: {Loading, ErrorBlock, highcharts: Chart, DatePicker},
    props: ['patient'],
    data() {
        return {
            group: {},
            data: [],
            errors: [],
            options: {},
            statistics: [],
            loaded: false,
            dates: {}
        }
    },
    methods: {
        load_data: function () {
            this.loaded = false
            this.errors = []
            let data = {
                group: this.group,
                dates: {
                    start: Date.parse(this.dates.start) / 1000,
                    end: Date.parse(this.dates.end) / 1000 + 24 * 60 * 60 - 1,
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
            console.log('data', this.data)
            let start = Date.parse(this.dates.start)
            let end = Date.parse(this.dates.end) + 24 * 60 * 60 * 1000 - 1

            this.options = {
                colors: ['#058DC7', '#50B432', '#aa27ce', '#fcff00',
                    '#24CBE5', '#64E572', '#c355ff', '#fce200', '#6AF9C4'],
                rangeSelector: {
                    allButtonsEnabled: true,
                    buttons: [
                        {
                            type: 'hour',
                            count: 1,
                            text: 'Час',
                        },
                        {
                            type: 'day',
                            count: 1,
                            text: 'День',
                        }, {
                            type: 'day',
                            count: 3,
                            text: '3 дня',
                        }, {
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
                    selected: 4,
                    inputDateFormat: "%b %e, %Y %H:%M"
                },

                chart: {
                    type: 'line',
                    zoomType: 'x',
                    backgroundColor: "#f8f8fb",
                    height: window.innerHeight,
                    width: window.innerWidth,
                    events: {
                        render: function (event) {
                            let stats = []

                            let binary_search = function (arr, value, l, r) {
                                let mid = Math.floor((r - l) / 2) + l

                                if (arr[mid] == value)
                                    return  mid;
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

                                if  (data.length) {
                                    // calculate statistics for visible points
                                    const max = data.reduce((a,b) => Math.max(a,b))
                                    const min = data.reduce((a,b) => Math.min(a,b))
                                    const average = (data.reduce((a, b) => a + b, 0) / data.length).toFixed(2) * 1

                                    if (data.length > 0) {
                                        stats.push({
                                            name: series.name,
                                            code: series.options.graph_code,
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
                                    min: map_data.reduce((a,b) => Math.min(a,b)),
                                    max: map_data.reduce((a,b) => Math.max(a,b))
                                })

                                stats.push({
                                    name: 'Пульсовое давление',
                                    code: 'pulse_pressure',
                                    avg: pp_data.reduce((a, b) => a + b, 0) / pp_data.length,
                                    min: pp_data.reduce((a,b) => Math.min(a,b)),
                                    max: pp_data.reduce((a,b) => Math.max(a,b))
                                })
                            }

                            Event.fire('refresh-stats', stats)
                        }
                    }
                },
                title: {
                    text: this.group.title
                },
                series: [],
                scrollbar: {
                    step: 1
                },
                xAxis: {
                    type: 'datetime',
                    gridLineWidth: 1,
                    minorGridLineWidth: 2,
                    minorTickLength: 0,
                    minorTickInterval: 24 * 3600 * 1000,
                    plotLines: [],
                    min: start,
                    max: end,
                    ordinal: false,
                    dateTimeLabelFormats: {
                        day: '%d.%m'
                    }
                },
                zoom: 'x',
                yAxis: [
                    {
                        plotBands: [],
                        labels: {
                            align: 'right',
                            x: -3
                        },
                        height: "80%",
                        gridLineWidth: 1,
                        lineWidth: 2,
                        resize: {
                            enabled: true
                        },
                        title: {
                            text: 'Значения'
                        }
                    },
                    {
                        labels: {
                            align: 'right',
                            x: -3
                        },
                        title: {
                            text: 'События'
                        },
                        top: "85%",
                        height: "15%",
                        gridLineWidth: 1,
                        offset: 0,
                        lineWidth: 2
                    }
                ],
                plotOptions: {
                    line: {
                        dataLabels: {
                            enabled: true
                        }
                    },
                    series: {
                        marker: {
                            lineWidth: 2,
                            lineColor: null,
                        }
                    }
                },
                legend: {
                    enabled: true,
                    itemDistance: 70,
                    labelFormatter: function () {
                        return this.name
                    }
                },
                tooltip: {
                    pointFormatter: function () {
                        let point = this;
                        return point.series.userOptions.data.filter(p => p.x == point.x).map(p => {
                            return p.comment
                        }).join('<br>')
                    },
                    shared: true,
                    headerFormat: null
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
            this.data.filter((graph) => graph.category.type != 'string').forEach((graph) => {
                this.options.series.push({
                    name: graph.category.description,
                    graph_code: graph.category.name,
                    yAxis: 0,
                    showInNavigator: true,
                    data: graph.values.map((value) => {

                        return {
                            x: (value.timestamp + this.offset) * 1000,
                            y: value.value,
                            comment: this.get_comment(value, graph.category.description),
                            marker: {
                                symbol: this.get_symbol(value),
                                lineColor: this.get_color(value),
                                radius: this.get_radius(value),
                            }
                        }
                    }).reverse(),
                    dashStyle: 'ShortDot',
                    lineWidth: 3,
                    marker: {
                        enabled: true,
                        radius: 4,
                        symbol: 'circle'
                    },
                    states: {
                        inactive: {
                            opacity: 1,
                        }
                    },
                    dataGrouping: {
                        enabled: false
                    }
                })
            })


            let y = -5;

            let medicines = {}
            this.data.filter((graph) => graph.category.name == 'medicine').forEach((graph) => {
                graph.values.forEach((medicine) => {

                    if (medicine.value in medicines) {
                        medicines[medicine.value].push({
                            timestamp: medicine.timestamp,
                            dose: medicine.params.dose == null ? '' : ` (${medicine.params.dose})`
                        })
                    }
                    else
                        medicines[medicine.value] = [{
                            timestamp: medicine.timestamp,
                            dose: medicine.params.dose == null ? '' :  ` (${medicine.params.dose})`
                        }]
                })
            });

            Object.entries(medicines).forEach(([medicine, values]) => {
                this.options.series.push({
                    yAxis: 1,
                    name: medicine,
                    data: values.map((value) => {
                        return {
                            dataLabels: {
                                enabled: false,
                            },
                            x: (value.timestamp + this.offset) * 1000,
                            y: y,
                            comment: this.get_comment({
                                value: medicine + value.dose,
                                timestamp: value.timestamp
                            }, `Прием лекарства`),
                        }
                    }).reverse(),
                    lineWidth: 0,
                    marker: {
                        enabled: true,
                        radius: 4,
                        symbol: 'square'
                    },
                    states: {
                        inactive: {
                            opacity: 1,
                        }
                    }
                })
                y -= 4;
            })

            y = -3
            this.data.filter((graph) => graph.category.name == 'symptom').forEach((graph) => {
                if (graph.values.length > 0) {
                    this.options.series.push({
                        yAxis: 1,
                        color: '#ad0eca',
                        name: graph.category.description,
                        data: graph.values.map((value) => {
                            let x = new Date((value.timestamp + this.offset) * 1000)
                            x.setHours(12, 0, 0)
                            return {
                                dataLabels: {
                                    enabled: false,
                                },
                                x: +x + this.offset * 1000,
                                y: y,
                                comment: this.get_comment(value, graph.category.description),
                            }
                        }).reverse(),
                        lineWidth: 0,
                        marker: {
                            enabled: true,
                            radius: 5,
                            symbol: 'triangle'
                        },
                        states: {
                            inactive: {
                                opacity: 1,
                            }
                        }
                    })
                }
            });

            let group_series = this.options.series.filter(s => s.yAxis == 0)
            if (group_series.map(s => s.data.length).reduce((a,b) => a + b) > 1000) {
                this.errors = ['За данный период в медицинской карте присутствует слишком большое количество записей (> 1000). ' +
                'Чтобы увидеть комментарии к точкам и симптомы, загрузите период с меньшим количеством записей.']
                group_series.forEach(s => {
                    s.data = s.data.map(d => [d.x, d.y])
                })
            }

            if (this.options.chart.height > this.options.chart.width && this.options.series.length > 2) {
                this.options.chart.height += 50 * (this.options.series.length - 2)
            }

            if (this.group.categories.includes('glukose')) {
                this.set_bands()
            }

            this.loaded = true
        },
        select_graph: function () {
            this.loaded = false;
            window.OBJECT_ID = undefined;
            Event.fire('select-graph')
        },
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

            let comment = "<strong>" + this.formatTime(new Date((point.timestamp + this.offset) * 1000)) + " </strong>"
                + category + ': ' + point.value
            if (point.additions) {
                point.additions.forEach((value) => {
                    comment += '<br/><strong style="color: red;">' + value['addition']['comment'] + '</strong>'
                })
            }
            return comment
        },
        formatTime: function (date) {
            return date.toTimeString().substr(0, 5)
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

            this.patient.algorithms.forEach(algorithm => {
                if (algorithm.categories.includes('glukose')) {
                    algorithm.steps.forEach(step => {
                        step.conditions.forEach(condition => {
                            condition.criteria.forEach(cr => {
                                cr.forEach(c => {
                                    if (c.value_code == 'min_glukose' && (min == null || min > c.value))
                                        min = c.value
                                    if (c.value_code == 'max_glukose' && (max == null || max < c.value))
                                        max = c.value
                                })
                            })
                        })
                    })
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
        }
    },
    computed: {
        offset() {
            //return -1 * new Date().getTimezoneOffset() * 60
            return 1
        },
        mobile() {
            return window.innerWidth < window.innerHeight
        }
    },
    created() {
        this.options = {
            legend: {
                enabled: true
            }
        }

        Event.listen('load-graph', (group) => {
            this.dates = {
                start: moment().add(-14, 'days').format('YYYY-MM-DD'),
                end: moment().format('YYYY-MM-DD')
            }
            this.group = group
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
</style>
