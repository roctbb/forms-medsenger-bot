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
                rangeSelector: {
                    allButtonsEnabled: true,
                    buttons: [{
                        type: 'day',
                        count: 1,
                        text: 'День',
                        dataGrouping: {
                            forced: true,
                            units: [['day', [1]]]
                        }
                    },{
                        type: 'day',
                        count: 3,
                        text: '3 дня',
                        dataGrouping: {
                            forced: true,
                            units: [['day', [3]]]
                        }
                    }, {
                        type: 'week',
                        count: 1,
                        text: 'Неделя',
                        dataGrouping: {
                            forced: true,
                            units: [['week', [1]]]
                        }
                    }, {
                        type: 'week',
                        count: 2,
                        text: '2 недели',
                        dataGrouping: {
                            forced: true,
                            units: [['week', [2]]]
                        }
                    }, {
                        type: 'month',
                        count: 1,
                        text: 'Месяц',
                        dataGrouping: {
                            forced: true,
                            units: [['month', [1]]]
                        }
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
                    height: window.innerHeight - 70
                },
                title: {
                    text: this.group.title
                },
                series: [],
                xAxis: {
                    type: 'datetime',
                    plotLines: [],
                    max: +new Date() + 60 * 60 * 1000,
                    ordinal: false
                },
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
                        }
                    },
                    series: {
                        marker: {
                            fillColor: '#FFFFFF',
                            lineWidth: 2,
                            lineColor: null,
                        },

                    }
                },
                legend: {
                    enabled: true
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

            this.data.filter((graph) => graph.category.type == 'string').forEach((graph) => {
                this.options.series.push({
                    name: graph.category.description,
                    data: graph.values.map((value) => {
                        return {
                            dataLabels: {
                                enabled: false,
                            },
                            x: (value.timestamp + offset) * 1000,
                            y: 30,
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
                                lineColor: this.get_color(value),
                                radius: this.get_radius(value),
                            }
                        }
                    }).reverse(),
                    dashStyle: 'Dot',
                    marker: {
                        enabled: true,
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
        get_radius: function (point) {
            if (point.additions) {
                return 5;
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
