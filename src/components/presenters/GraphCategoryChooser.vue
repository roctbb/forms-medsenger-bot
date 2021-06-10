<template>
    <div>
        <h5>Доступные графики</h5>

        <div class="row">
            <card v-for="(category, i) in plottable_categories" :key="i" :image="images.graph"
                  class="col-lg-3 col-md-4">
                <h6>{{ category.title }}</h6>

                <a @click="load_graph(category)" href="#" class="btn btn-primary">Открыть</a>
            </card>
            <card :image="images.graph" class="col-lg-3 col-md-4" v-for="(gr,i) in ['symptoms','medicines']" :key="'heatmap-'+i">
                <h6> {{gr == 'symptoms' ? 'Симптомы' :'Лекарства'}} </h6>
                <a @click="load_heatmap(gr)" href="#" class="btn btn-primary">Открыть</a>
            </card>
        </div>

        <div style="margin-top: 15px;" class="alert alert-info" role="alert">
            <p>В этой разделе можно посмотреть внесенные данные в виде графиков. Числовые данные отображаются в виде кривых, а
                текстовые (симптомы и лекарства) на линии в нижней части графика. Чтобы посмотреть подробную информацию, наведите
                мышку на нужную точку графика.</p>
        </div>

    </div>
</template>

<script>
import Card from "../common/Card";

export default {
    name: "GraphCategoryChooser",
    components: {Card},
    props: {
        data: {
            required: true,
        }
    },
    data() {
        return {
            groups: [
                {
                    "title": "Давление и пульс",
                    "categories": ['systolic_pressure', 'diastolic_pressure', 'pulse'],
                },
                {
                    "title": "Обхват голеней",
                    "categories": ['leg_circumference_right', 'leg_circumference_left'],
                }
            ]
        }
    },
    methods: {
        load_graph: function (params) {
            Event.fire('load-graph', params)
        },
        load_heatmap: function (data_type) {
            Event.fire('load-heatmap', data_type)
        }
    },
    computed: {
        plottable_categories: function () {
            let plottable = this.data.filter((category) => {
                return !category.is_legacy && ['scatter', 'values'].includes(category.default_representation) && category.type != 'string'
            })

            console.log("plottable", plottable)

            let custom = this.groups.filter((group) => {
                return group.categories.some((category_name) => {
                    return plottable.filter((category) => category.name == category_name).length > 0
                })
            })

            console.log("custom", custom)

            let not_custom = plottable.filter((category) => {
                return !this.groups.some((group) => {
                    return group.categories.includes(category.name)
                })
            })

            not_custom.forEach((category) => {
                custom.push({
                    "title": category.description,
                    "categories": [category.name]
                })
            })

            return custom
        }
    },
    created() {

    }
}
</script>

<style scoped>

</style>
