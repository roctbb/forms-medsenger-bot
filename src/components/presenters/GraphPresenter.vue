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
                rangeSelector: {
                    selected: 1
                },
                chart: {
                    type: 'line',
                    zoomType: 'x',
                },
                title: {
                    text: this.group.title
                },
                series: [],
                xAxis: {
                    type: 'datetime',
                    plotLines: [],
                    max: + new Date() + 60 * 60 * 1000,
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
                        }
                    }
                },
                legend: {
                    enabled: true
                },
                tooltip: {
                    pointFormatter: function () {
                        let point = this;
                        let label = point.series.name + ': <b>' + point.y + '</b><br/>'
                        if (point.comment) {
                            label += point.comment;
                        }
                        return label
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

            this.data.filter((graph) => graph.category.type == 'string').forEach((graph) => {
                this.options.series.push({
                    name: graph.category.description,
                    data: graph.values.map((value) => {
                        let comment = 'Препарат: '
                        if (graph.category.name == 'symptom') comment = 'Симптом: '
                        if (graph.category.name == 'action') comment = 'Действие: '

                        return {
                            x: value.timestamp * 1000,
                            y: 30,
                            comment: comment + value.value,
                            marker: {
                                lineColor: '#000',
                                radius: 1,
                            }
                        }
                    }).reverse(),
                    dashStyle: 'Dot',
                    marker: {
                        enabled: true,
                        symbol: 'circle'
                    }
                })

            });

            this.data.filter((graph) => graph.category.type != 'string').forEach((graph) => {
                this.options.series.push({
                    name: graph.category.description,
                    data: graph.values.map((value) => {
                        return {
                            x: value.timestamp * 1000,
                            y: value.value,
                            comment: this.get_comment(value),
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

            console.log(this.options)

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
        get_comment: function (point) {
            if (point.additions) {
                let comment = ''

                point.additions.forEach((value) => {
                    comment += '<strong style="color: red;">' + value['addition']['comment'] + '</strong><br/>'
                })

                return comment
            }
            return undefined;
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
