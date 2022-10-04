<template>
  <div>
    <h5>Доступные графики</h5>

    <div class="row">
      <card v-for="(category, i) in plottable_categories" :key="'graph_' + i" :image="images.graph"
            class="col-lg-3 col-md-4">
        <h6>{{ category.title }}</h6>

        <a @click="load_graph(category)" href="#" class="btn btn-primary">Открыть</a>
      </card>
    </div>

    <h5>Доступные тепловые карты</h5>

    <div class="row">
      <card v-for="(category, i) in heatmaps" :key="'heatmap_' + i" :image="images.heatmap" class="col-lg-3 col-md-4">
        <h6>{{ category.title }}</h6>
        <a @click="load_heatmap(category)" href="#" class="btn btn-primary">Открыть</a>
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
        },
        {
          "title": "Глюкоза",
          "categories": ['glukose', 'glukose_fasting'],
        },
        {
          "title": "Спортивная форма",
          "categories": ['appetite', 'readiness_for_training', 'performance', 'mood', 'sleep', 'health'],
        }
      ],
      heatmaps: [
        {
          "title": "Симптомы",
          "categories": ['symptom', 'medicine'],
        },
        {
          "title": "Приемы лекарств",
          "categories": ['medicine'],
        }
      ]
    }
  },
  methods: {
    load_graph: function (params) {
      Event.fire('load-graph', params)
    },
    load_heatmap: function (params) {
      Event.fire('load-heatmap', params)
    }
  },
  computed: {
    plottable_categories: function () {
      let plottable = this.data.filter((category) => {
        return !category.is_legacy && ['scatter', 'values'].includes(category.default_representation) && category.type != 'string'
      })

      let custom = this.groups.filter((group) => {
        return group.categories.some((category_name) => {
          return plottable.filter((category) => category.name == category_name).length > 0
        })
      })

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
  mounted() {
    if (window.OBJECT_ID) {
      try {
        let data = this.data.filter(c => c.id == window.OBJECT_ID)
        if (data.length) {
          let name = data[0].name;
          let params = this.plottable_categories.filter(c => c.categories.includes(name))[0];
          Event.fire('load-graph', params);
        }
      } catch (e) {
        console.log(e);
      }
    }
  }
}
</script>

<style scoped>

</style>
