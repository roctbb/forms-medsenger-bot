<template>
    <div>
        <h3>Доступные графики</h3>

        <a class="btn btn-info" v-for="category in plottable_categories" @click="load_graph(category)">{{ category.title }}</a>

    </div>
</template>

<script>
import FormGroup48 from "../common/FormGroup-4-8";
import ErrorBlock from "../common/ErrorBlock";
import ActionDone from "./ActionDone";

export default {
    name: "GraphCategoryChooser",
    components: {ActionDone, FormGroup48, ErrorBlock},
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
                }
            ]
        }
    },
    methods: {
        load_graph: function (params) {
            Event.fire('load-graph', params)
        }
    },
    computed: {
        plottable_categories: function () {
            let plottable = this.data.filter((category) => {
                return !category.is_legacy && category.default_representation == 'values' && category.type != 'string'
            })

            console.log("plottable", plottable)

            let custom = this.groups.filter((group) => {
                return group.categories.some((category_name) => {
                    console.log(category_name, plottable)
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
