<template>
    <div :style="style">
        <br v-if="narrowScreen">

        <div class="container">
            <a class="btn btn-danger" @click="select_graph()">Назад</a>
        </div>

        <div class="container">
            <input type="checkbox" v-model="options.legend.enabled" id="show_legend"/>
            <label for="show_legend">Показать легенду</label>
        </div>

        <highcharts :constructor-type="'stockChart'" v-if="loaded" :options="options"></highcharts>
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
            var now = new Date()
            now.setDate(now.getDate() + 1)

            this.options = {
                colors: ['#058DC7', '#50B432', '#aa27ce', '#fcff00',
                    '#24CBE5', '#64E572', '#c355ff', '#fce200', '#6AF9C4'],
                rangeSelector: {
                    allButtonsEnabled: true,
                    buttons: [
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
                    selected: 2
                },

                chart: {
                    type: 'line',
                    zoomType: 'x',
                    backgroundColor: "#f8f8fb",
                    height: this.height,
                    width: this.width
                },
                title: {
                    text: this.group.title
                },
                series: [],
                xAxis: {
                    type: 'datetime',
                    gridLineWidth: 1,
                    plotLines: [],
                    max: +now,
                    ordinal: false,
                    dateTimeLabelFormats: {
                        day: '%d.%m'
                    }
                },
                zoom: 'x',
                yAxis: [
                    {
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
                    maxHeight: 100
                },
                tooltip: {
                    pointFormatter: function () {
                        let point = this;
                        return point.series.userOptions.data.filter(p => p.x == point.x).map(p => {
                            return p.comment
                        }).join('<br>')
                    },
                    valueSuffix: ' cm',
                    shared: true
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

            let offset = -1 * new Date().getTimezoneOffset() * 60
            let y = 1;

            let medicines = {}
            this.data.filter((graph) => graph.category.name == 'medicine').forEach((graph) => {
                graph.values.forEach((medicine) => {
                    if (medicine.value in medicines)
                        medicines[medicine.value].push(medicine.timestamp)
                    else
                        medicines[medicine.value] = [medicine.timestamp]
                })
            });

            Object.entries(medicines).forEach(([key, value]) => {
                this.options.series.push({
                    yAxis: 1,
                    name: key,
                    data: value.map((val) => {
                        return {
                            dataLabels: {
                                enabled: false,
                            },
                            x: (val + offset) * 1000,
                            y: y,
                            comment: 'Прием лекарства: ' + key,
                        }
                    }).reverse(),
                    lineWidth: 0,
                    marker: {
                        enabled: true,
                        radius: 4,
                        symbol: 'square'
                    }
                })
                y += 4;
            })

            this.data.filter((graph) => graph.category.name == 'symptom').forEach((graph) => {
                this.options.series.push({
                    yAxis: 1,
                    name: graph.category.description,
                    data: graph.values.map((value) => {
                        return {
                            dataLabels: {
                                enabled: false,
                            },
                            x: (value.timestamp + offset) * 1000,
                            y: y,
                            comment: this.get_comment(value, graph.category.description),
                        }
                    }).reverse(),
                    lineWidth: 0,
                    marker: {
                        enabled: true,
                        lineColor: '#ad0eca',
                        radius: 3,
                        symbol: 'triangle'
                    }
                })
                y += 1;
            });

            this.data.filter((graph) => graph.category.type != 'string').forEach((graph) => {
                this.options.series.push({
                    name: graph.category.description,
                    data: graph.values.map((value) => {
                        return {
                            x: (value.timestamp + offset) * 1000,
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
                    }
                })
            })

            this.loaded = true
        },
        select_graph: function () {
            this.loaded = false;
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

            let comment = category + ': ' + point.value
            if (point.additions) {
                point.additions.forEach((value) => {
                    comment += '<br/><strong style="color: red;">' + value['addition']['comment'] + '</strong>'
                })
            }
            return comment
        },
    },
    computed: {
        style() {
            return this.narrowScreen ? {
                height: this.width + "px",
                width: this.width + "px",
                'transform-origin': '50% 50%',
                transform: 'rotate(-90deg)'
            } : {}
        },
        width() {
            return (this.narrowScreen ? (window.innerHeight - 50) : window.innerWidth)
        },
        height() {
            return this.narrowScreen ? (window.innerWidth + Math.round(window.innerWidth/10)) : window.innerHeight
        },
        narrowScreen() {
            return window.innerWidth < window.innerHeight
        }
    },
    created() {
        this.options = {
            legend: {
                enabled: true,
                maxHeight: 100
            }
        }

        Event.listen('load-graph', (group) => {
            this.group = group
            this.load_data()
        });
    }
}
</script>

<style scoped>

</style>
