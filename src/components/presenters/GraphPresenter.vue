<template>
    <div>
        <div style="margin-left: 10px;">
            <a class="btn btn-danger" @click="select_graph()">Назад</a>
        </div>

        <highcharts :constructor-type="'stockChart'" v-if="loaded" :options="options"></highcharts>

        <div class="container">
            <input type="checkbox" v-model="options.legend.enabled" id="show_legend"/>
            <label for="show_legend">Показать легенду</label>
        </div>

        <div class="container center" v-if="this.statistics.length && this.show_table()">
            <h5>Значения за отображенный период</h5>
            <table class="table table-hover">
                <thead>
                <tr>
                    <th scope="col" class="bg-info text-light">Параметр</th>
                    <th scope="col" class="bg-info text-light">В среднем</th>
                    <th scope="col" class="bg-info text-light">Минимум</th>
                    <th scope="col" class="bg-info text-light">Максимум</th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="stat in this.statistics">
                    <th scope="row">{{ stat.name }}</th>
                    <td>{{ stat.avg }}</td>
                    <td>{{ stat.min }}</td>
                    <td>{{ stat.max }}</td>
                </tr>
                </tbody>
            </table>
        </div>
        <br>
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
    props: ['patient'],
    data() {
        return {
            group: {},
            data: [],
            options: {},
            statistics: [],
            loaded: false,
        }
    },
    methods: {
        show_table: function () {
            return window.innerWidth >= window.innerHeight
        },
        load_data: function () {
            this.axios.post(this.url('/api/graph/group'), this.group).then(this.process_load_answer);
        },
        process_load_answer: function (response) {
            this.data = response.data
            let today = new Date()
            today.setHours(23,59,59)
            let now = +today + this.offset

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
                            let isInside = (point) => {
                                const min = event.target.axes[0].min
                                const max = event.target.axes[0].max
                                return point.x >= min && point.x <= max
                            }

                            let stats = []

                            this.series.filter(series => series.userOptions.yAxis == 0).forEach(series => {
                                let data = series.data.filter(point => isInside(point)).map(point => point.y);

                                // calculate statistics for visible points
                                const max = Math.max.apply(null, data)
                                const min = Math.min.apply(null, data)
                                const average = (data.reduce((a, b) => a + b, 0) / data.length).toFixed(1)

                                const legendItem = series.legendItem;

                                // construct the legend string
                                const text = series.name + '<br><strong style="color: dimgrey">min: ' + min +
                                    ' max: ' + max +
                                    '<br>avg: ' + average + '</strong>';

                                // set the constructed text for the legend
                                legendItem.attr({
                                    text: data.length > 0 ? text : (series.name + '<br><strong style="color: dimgrey">Нет данных</strong>')
                                });
                                if (data.length > 0) {
                                    stats.push({
                                        name: series.name,
                                        avg: average,
                                        min: min,
                                        max: max
                                    })
                                }
                            });

                            Event.fire('refresh-stats', stats)

                            this.series.filter(series => series.userOptions.yAxis == 1).forEach(series => {
                                let data = series.data.filter(point => isInside(point));

                                const legendItem = series.legendItem;
                                // construct the legend string
                                const text = series.name + '<br><strong style="color: dimgrey">' +
                                    (data.length > 0 ? ('Количество: ' + data.length) : 'Нет данных') + '</strong>';

                                // set the constructed text for the legend
                                legendItem.attr({
                                    text: text
                                });
                            });
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
                    max: now + 1000 * 3600 * 10,
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
                        },

                    }
                },
                legend: {
                    enabled: true,
                    maxHeight: 100,
                    labelFormatter: function () {
                        return this.name + '<br>.<br>.'
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
                    }
                })
            })

            let y = -5;

            let medicines = {}
            this.data.filter((graph) => graph.category.name == 'medicine').forEach((graph) => {
                graph.values.forEach((medicine) => {
                    if (medicine.value in medicines)
                        medicines[medicine.value].push(medicine.timestamp)
                    else
                        medicines[medicine.value] = [medicine.timestamp]
                })
            });

            Object.entries(medicines).forEach(([medicine, values]) => {
                this.options.series.push({
                    yAxis: 1,
                    name: medicine,
                    data: values.map((timestamp) => {
                        return {
                            dataLabels: {
                                enabled: false,
                            },
                            x: (timestamp + this.offset) * 1000,
                            y: y,
                            comment: this.get_comment({
                                value: medicine,
                                timestamp: timestamp
                            },  'Прием лекарства'),
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
            });

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

            let comment =  "<strong>" + this.formatTime(new Date((point.timestamp + this.offset) * 1000))+ " </strong>"
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
            console.log(this.options.yAxis[0].plotBands)
        }
    },
    computed: {
        offset() {
            return -1 * new Date().getTimezoneOffset() * 60
        }
    },
    created() {
        this.options = {
            legend: {
                enabled: true
            }
        }

        Event.listen('load-graph', (group) => {
            this.group = group
            this.load_data()
        });

        Event.listen('refresh-stats', (stats) => {
            this.statistics = stats
        })

        Event.listen('window-resized', () => {
            if (this.options) {
                this.options.chart.height = window.innerHeight
                this.options.chart.width = window.innerWidth
            }
        })
    }
}
</script>

<style scoped>
.table {
    font-size: small;
}
</style>
