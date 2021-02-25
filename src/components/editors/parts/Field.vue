<template>
    <card>
        <form-group48 title="Текст вопроса">
            <input class="form-control" v-model="field.text"/>
        </form-group48>

        <form-group48 title="Тип">
            <select @change="clear_params()" class="form-control" v-model="mode">
                <option v-for="type in Object.entries(field_types)" :value="type[0]">{{ type[1] }}</option>
            </select>
        </form-group48>

        <form-group48 title="Пояснение к вопросу" v-if="field.type != 'radio'">
            <input class="form-control" v-model="field.description"/>
        </form-group48>

        <form-group48 title="Код категории" v-if="field.type != 'radio'">
            <select class="form-control" v-model="field.category">
                <option v-for="category in category_list.filter(c => c.type == native_types[field.type])" :value="category.name">{{ category.description }}</option>
            </select>
        </form-group48>

        <form-group48 title="Обязательный вопрос?">
            <input type="checkbox" class="form-check" v-model="field.required">
        </form-group48>
        <hr>

        <div v-if="field.type == 'integer'">
            <hr>
            <div class="form-group row">
                <div class="col-md-4">
                    <strong>Ограничения</strong>
                </div>
                <div class="col-md-3">
                    От <input type="number" pattern="\d*" class="form-control" v-model="field.params.min"/>
                </div>
                <div class="col-md-3">
                    до <input type="number" pattern="\d*" class="form-control" v-model="field.params.max"/>
                </div>
            </div>
        </div>

        <div v-if="field.type == 'float'">
            <hr>
            <div class="form-group row">
                <div class="col-md-4">
                    <strong>Ограничения</strong>
                </div>
                <div class="col-md-3">
                    От <input type="number" step="0.01" class="form-control" v-model="field.params.min"/>
                </div>
                <div class="col-md-3">
                    до <input type="number" step="0.01" class="form-control" v-model="field.params.max"/>
                </div>
            </div>
        </div>

        <div v-if="field.type == 'radio'">
            <hr>

            <strong>Варианты ответа</strong>

            <div class="form-group row" v-for="(variant, j) in field.params.variants">
                <div class="col-md-3">
                    <small class="text-mutted">Код категории</small><br>

                    <select class="form-control" v-model="variant.category">
                        <option v-for="category in category_list" :value="category.name">{{ category.description }}</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <small class="text-mutted">Значение</small><br>
                    <input type="text" class="form-control" v-model="variant.category_value"/>
                </div>
                <div class="col-md-5">
                    <small class="text-mutted">Текст варианта</small><br>
                    <input type="text" class="form-control" v-model="variant.text"/>
                </div>
                <div class="col-md-2">
                    <a v-if="field.params.variants.length > 2" @click="remove_variant(j)">Удалить
                        вариант</a>
                </div>
            </div>
            <a class="btn btn-primary btn-sm" @click="add_variant()">Добавить вариант</a>

        </div>

        <a class="btn btn-danger btn-sm" @click="remove()">Удалить вопрос</a>

    </card>
</template>

<script>

import Card from "../../common/Card";
import FormGroup48 from "../../common/FormGroup-4-8";

export default {
    name: "Field",
    components: {FormGroup48, Card},
    props: ['data', 'pkey'],
    data() {
        return {
            mode: 'integer',
            field: {},
            backup: {}
        }
    },
    methods: {
        clear_params: function () {
            console.log(this.backup)

            console.log('set backup for', this.field.type)
            this.backup[this.field.type] = JSON.stringify(this.field.params)
            console.log('old mode is', this.field.type)
            console.log(this.backup)

            this.field.type = this.mode
            console.log('new mode is', this.mode)

            if (this.backup[this.mode]) {
                console.log('got backup', this.backup[this.mode])
                this.field.params = JSON.parse(this.backup[this.mode])
            } else {
                this.field.params = {};
                if (this.field.type == 'radio') {
                    this.field.params.variants = [{text: '', category: ''}, {text: '', category: ''}]
                }
            }

        },
        add_variant: function () {
            this.field.params.variants.push({text: '', category: ''});
            this.$forceUpdate()
        },
        remove_variant: function (j) {
            this.field.params.variants.splice(j, 1);
            this.$forceUpdate()
        },
        remove: function () {
            Event.fire('remove-field', this.pkey)
        }

    },
    created() {
        this.mode = this.data.type;
        this.field = this.data;

    }
}
</script>

<style scoped>

</style>
