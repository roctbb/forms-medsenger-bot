<template>
    <card>
        <form-group48 title="Текст вопроса">
            <input class="form-control form-control-sm" v-model="field.text"/>
        </form-group48>

        <form-group48 title="Тип">
            <select @change="clear_params()" class="form-control form-control-sm" v-model="mode">
                <option v-for="type in Object.entries(field_types)" :value="type[0]">{{ type[1] }}</option>
            </select>
        </form-group48>

        <form-group48 title="Пояснение к вопросу" v-if="field.type != 'radio'">
            <input class="form-control form-control-sm" v-model="field.description"/>
        </form-group48>

        <form-group48 title="Код категории" v-if="field.type != 'radio'">

            <select class="form-control form-control-sm" v-model="field.category">
                <option value="none">Не сохранять ответ</option>

                <optgroup
                    v-for="(group, name) in group_by(category_list.filter(c => c.type == native_types[field.type]), 'subcategory')"
                    v-bind:label="name">
                    <option v-for="category in group" :value="category.name">{{ category.description }}
                    </option>
                </optgroup>
            </select>
        </form-group48>

        <form-group48 title="Обязательный вопрос?">
            <input type="checkbox" class="form-check" v-model="field.required">
        </form-group48>
        <hr>

        <div v-if="field.type == 'integer'">
            <div class="form-group row">
                <div class="col-md-4">
                    <strong>Ограничения</strong>
                </div>
                <div class="col-md-3">
                    <small>от </small><input type="number" pattern="\d*" class="form-control form-control-sm"
                                             v-model="field.params.min"/>
                </div>
                <div class="col-md-3">
                    <small>до </small><input type="number" pattern="\d*" class="form-control form-control-sm"
                                             v-model="field.params.max"/>
                </div>
            </div>
        </div>

        <div v-if="field.type == 'float'">
            <div class="form-group row">
                <div class="col-md-4">
                    <strong>Ограничения</strong>
                </div>
                <div class="col-md-3">
                    <small>от </small><input type="number" step="0.01" class="form-control form-control-sm"
                                             v-model="field.params.min"/>
                </div>
                <div class="col-md-3">
                    <small>до </small><input type="number" step="0.01" class="form-control form-control-sm"
                                             v-model="field.params.max"/>
                </div>
            </div>
        </div>

        <div v-if="field.type == 'radio'">
            <strong>Варианты ответа</strong>

            <div class="form-group row" v-for="(variant, j) in field.params.variants">
                <div class="col-md-3">
                    <small class="text-mutted">Код категории</small><br>

                    <select class="form-control form-control-sm" v-model="variant.category">
                        <option value="none">Не сохранять ответ</option>

                        <optgroup v-for="(group, name) in group_by(category_list, 'subcategory')" v-bind:label="name">
                            <option v-for="category in group" :value="category.name">{{ category.description }}
                            </option>
                        </optgroup>
                    </select>
                </div>
                <div class="col-md-2" v-if="variant.category != 'none'">
                    <small class="text-mutted">Значение</small><br>
                    <input type="text" class="form-control form-control-sm" v-model="variant.category_value"/>
                </div>
                <div class="col-md-5">
                    <small class="text-mutted">Текст варианта</small><br>
                    <input type="text" class="form-control form-control-sm" v-model="variant.text"/>
                </div>
                <div class="col-md-2"><br>
                    <a class="btn btn-default btn-sm" v-if="field.params.variants.length > 2"
                       @click="remove_variant(j)">Удалить
                        вариант</a>
                </div>
            </div>
        </div>
        <a v-if="field.type == 'radio'" class="btn btn-primary btn-sm" @click="add_variant()">Добавить вариант</a>
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
