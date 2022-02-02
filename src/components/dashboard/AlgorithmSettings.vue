<template>
    <modal height="auto" name="algorithm-settings" @before-open="beforeOpen">
        <div class="container">
            <h5>Настройка параметров алгоритма {{ algorithm.title }}</h5>
            <error-block :errors="errors"></error-block>
            <form-group48 v-for="field in fillable_fields" :key="field.value_code" :title="field.value_name">
                <input type="form-control form-control-sm" v-model="algorithm.setup[field.value_code]"/>
            </form-group48>

            <button class="btn btn-danger btn-sm" @click="close()">Не подключать алгоритм</button>
            <button class="btn btn-success btn-sm" @click="attach()">Подключить</button>
        </div>

    </modal>
</template>

<script>

import FormGroup48 from "../common/FormGroup-4-8";
import ErrorBlock from "../common/ErrorBlock";

export default {
    name: "AlgorithmSettings",
    components: {ErrorBlock, FormGroup48},
    data() {
        return {
            algorithm: {},
            errors: []
        }
    },
    computed: {
        fillable_fields: function () {
            if (!this.algorithm || !this.algorithm.steps) {
                return []
            }

            let fields = [];
            let codes = new Set();

            this.algorithm.steps.map(step => step.conditions.map(condition => {
                    condition.criteria.forEach((block) => {
                        block.forEach(c => {
                            if (c.ask_value == true && !codes.has(c.value_code)) {
                                fields.push(c);
                                codes.add(c.value_code);
                            }
                        })
                    })
                }))

            return fields;
        }
    },
    methods: {
        close: function () {
            this.$modal.hide('algorithm-settings')
        },
        attach: function () {
            if (this.check())
            {
                Event.fire('attach-algorithm', this.algorithm)
                this.close()
            }
        },
        check: function () {
            let prepare_field = (field) => {
                let category = this.get_category(field.category)
                if (category.type == 'integer') this.algorithm.setup[field.value_code] = parseInt(this.algorithm.setup[field.value_code])
                if (category.type == 'float') this.algorithm.setup[field.value_code] = parseFloat(this.algorithm.setup[field.value_code])
            }

            this.fillable_fields.map(prepare_field)

            if (this.fillable_fields.filter(f => this.empty(this.algorithm.setup[f.value_code])).length > 0)
            {
                this.errors.push('Заполните все поля!')
                return false
            }
            return true
        },
        beforeOpen(event) {
            this.algorithm = event.params.algorithm;
            this.algorithm.setup = {}

            this.fillable_fields.forEach(f => {
                this.algorithm.setup[f.value_code] = f.value
            })
            this.errors = []
        }
    }
}
</script>

<style scoped>
 .container {
     padding-top: 15px;
     padding-bottom: 15px;
 }

</style>
