<template>
    <card>
        <form-group48 title="Текст вопроса">
            <input class="form-control form-control-sm"
                   :class="save_clicked && empty(field.text) ? 'is-invalid' : ''"
                   v-model="field.text"/>
        </form-group48>

        <form-group48 title="Тип">
            <select @change="clear_params()"
                    :class="save_clicked && empty(mode) ? 'is-invalid' : ''"
                    class="form-control form-control-sm" v-model="mode">
                <option v-for="type in Object.entries(field_types)" :value="type[0]">{{ type[1] }}</option>
            </select>
        </form-group48>

        <form-group48 title="Пояснение к вопросу">
            <input class="form-control form-control-sm" v-model="field.description"/>
        </form-group48>

        <form-group48 title="Код категории" v-if="field.type != 'radio'">

            <select class="form-control form-control-sm"
                    :class="save_clicked && empty(field.category) ? 'is-invalid' : ''"
                    v-model="field.category">
                <option value="none">Не сохранять ответ</option>

                <optgroup
                    v-for="(group, name) in group_by(category_list.filter(c => native_types[field.type].includes(c.type)), 'subcategory')"
                    v-bind:label="name">
                    <option v-for="category in group" :value="category.name">{{ category.description }}
                    </option>
                </optgroup>
            </select>
        </form-group48>

        <form-group48 title="Обязательный вопрос?" v-if="!field.show_if">
            <input type="checkbox" class="form-check" v-model="field.required">
        </form-group48>

        <form-group48 title="Показывать если...">
            <select class="form-control form-control-sm" v-model="field.show_if">
                <option value="">Всегда</option>

                <option v-for="other in form.fields.filter(f => f.type == 'checkbox')" :value="other.uid">{{
                        other.text
                    }}
                </option>
            </select>
        </form-group48>
        <hr>

        <div v-if="field.type == 'integer' && is_admin">
            <div class="form-group row">
                <div class="col-md-4">
                    <strong>Ограничения</strong>
                </div>
                <div class="col-md-3">
                    <small>от </small><input type="number" pattern="\d*"
                                             :class="save_clicked && (empty(field.params.min) || field.params.max < field.params.min) ? 'is-invalid' : ''"
                                             class="form-control form-control-sm"
                                             v-model="field.params.min"/>
                </div>
                <div class="col-md-3">
                    <small>до </small><input type="number" pattern="\d*"
                                             :class="save_clicked && (empty(field.params.max) || field.params.max < field.params.min) ? 'is-invalid' : ''"
                                             class="form-control form-control-sm"
                                             v-model="field.params.max"/>
                </div>
            </div>
        </div>

        <div v-if="field.type == 'text' || field.type == 'textarea'">
            <form-group48 title="Префикс">
                <input type="text" class="form-control form-control-sm"
                       :class="save_clicked && empty(field.prefix) ? 'is-invalid' : ''"
                       v-model="field.prefix"/>
            </form-group48>
        </div>

        <div v-if="field.type == 'checkbox'">
            <form-group48 title="Значение при включении">
                <input type="text" class="form-control form-control-sm" v-model="field.category_value"/>
            </form-group48>
            <form-group48 title="Вес" description="Добавляется, если галочка стоит" v-if="form.has_integral_evaluation">
                <input type="number" class="form-control form-control-sm" step="0.1" v-model="field.weight"/>
            </form-group48>
        </div>

        <div v-if="field.type == 'float'">
            <div class="form-group row">
                <div class="col-md-4">
                    <strong>Ограничения</strong>
                </div>
                <div class="col-md-3">
                    <small>от </small><input type="number" step="0.01" class="form-control form-control-sm"
                                             :class="save_clicked && (empty(field.params.min) || field.params.max < field.params.min) ? 'is-invalid' : ''"
                                             v-model="field.params.min"/>
                </div>
                <div class="col-md-3">
                    <small>до </small><input type="number" step="0.01" class="form-control form-control-sm"
                                             :class="save_clicked && (empty(field.params.max) || field.params.max < field.params.min) ? 'is-invalid' : ''"
                                             v-model="field.params.max"/>
                </div>
            </div>
        </div>

        <div v-if="field.type == 'file'">
            <form-group48 title="Отправить файл врачу">
                <input type="checkbox" class="form-check" v-model="field.params.send_to_doctor">
            </form-group48>

            <form-group48 title="Пояснение в медкарте">
                <input type="text" class="form-control form-control-sm" v-model="field.category_value"/>
            </form-group48>
        </div>

        <div v-if="field.type != 'radio' && is_admin">
            <form-group48 title="Дополнительные параметры">
                <input type="text" class="form-control form-control-sm"
                       :class="save_clicked && !isJsonString(field.params.custom_params) ? 'is-invalid' : ''"
                       v-model="field.params.custom_params"/>
            </form-group48>
        </div>

        <div v-if="field.type == 'radio'">
            <strong>Варианты ответа</strong>

            <div class="form-group row" v-for="(variant, j) in field.params.variants">
                <div class="col-md-3">
                    <small class="text-mutted">Код категории</small><br>

                    <select class="form-control form-control-sm"
                            :class="save_clicked && !variant.category ? 'is-invalid' : ''"
                            v-model="variant.category">
                        <option value="none">Не сохранять ответ</option>

                        <optgroup v-for="(group, name) in group_by(category_list, 'subcategory')" v-bind:label="name">
                            <option v-for="category in group" :value="category.name">{{ category.description }}
                            </option>
                        </optgroup>
                    </select>
                </div>
                <div class="col-md-2" v-if="variant.category != 'none'">
                    <small class="text-mutted">Значение</small><br>
                    <input type="text" class="form-control form-control-sm"
                           :class="save_clicked && empty(variant.category_value) ? 'is-invalid' : ''"
                           v-model="variant.category_value"/>
                </div>
                <div class="col-md-5">
                    <small class="text-mutted">Текст варианта</small><br>
                    <input type="text"
                           :class="save_clicked && empty(variant.text) ? 'is-invalid' : ''"
                           class="form-control form-control-sm" v-model="variant.text"/>
                </div>
                <div class="col-md-2" v-if="form.has_integral_evaluation">
                    <small class="text-mutted">Вес</small><br>
                    <input type="number" step="0.1"
                           :class="save_clicked && empty(variant.weight) ? 'is-invalid' : ''"
                           class="form-control form-control-sm" v-model="variant.weight"/>
                </div>
                <div class="col-md-1"><br>
                    <a class="btn btn-default btn-sm" v-if="field.params.variants.length > 2"
                       @click="remove_variant(j)">Удалить
                        вариант</a>
                </div>

                <div class="col-md-12" v-if="is_admin">
                    <small class="text-mutted">Дополнительные параметры</small><br>
                    <input type="text" class="form-control form-control-sm"
                           :class="save_clicked && !isJsonString(variant.custom_params) ? 'is-invalid' : ''"
                           v-model="variant.custom_params"/>
                </div>
            </div>
        </div>

        <div v-if="field.type == 'scale'">
            <form-group48 title="Цвета (через запятую)">
                <input type="text" class="form-control form-control-sm" v-model="field.params.colors"/>
            </form-group48>

            <form-group48 title="Начинать с">
                <input type="number" class="form-control form-control-sm" v-model="field.params.start_from">
            </form-group48>

            <form-group48 title="Предпросмотр шкалы" description="Шкала будет выглядеть так">
                <visual-analog-scale :colors="parsed_colors" :start_from="parseInt(field.params.start_from)">
                    <div class="row">
                        <div class="col-1 d-flex justify-content-center" v-for="(color, i) in parsed_colors" >
                            <input class="form-check-input monitoring-input" style="margin-left: 5px" type="radio"
                                   :id="'radio_' + field.uid + '_' + i" :name="'radio_' + field.uid">
                        </div>
                    </div>
                </visual-analog-scale>
            </form-group48>
        </div>

        <a v-if="field.type == 'radio'" class="btn btn-primary btn-sm" @click="add_variant()">Добавить вариант</a>
        <a class="btn btn-danger btn-sm" @click="remove()">Удалить вопрос</a>

    </card>
</template>

<script>

import Card from "../../common/Card";
import FormGroup48 from "../../common/FormGroup-4-8";
import VisualAnalogScale from "../../presenters/parts/VisualAnalogScale";

export default {
    name: "Field",
    components: {VisualAnalogScale, FormGroup48, Card},
    props: ['data', 'pkey', 'form', 'save_clicked'],
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
                if (this.field.type == 'scale') {
                    this.field.params.start_from = '0'
                    this.field.params.colors = ["#63bf3a","#72c433","#b0dc40","#eed748","#e9b942","#e3a03c","#e18738","#d96932","#d4482e","#d3312c"]
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
        },
    },
    computed : {
        parsed_colors: function () {
            return this.field.params.colors.toString().split(',')
        },
    },
    created() {
        this.mode = this.data.type;
        this.field = this.data;
    }
}
</script>

<style scoped>

</style>
