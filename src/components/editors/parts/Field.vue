<template>
    <card>
        <h5 v-if="field.type != 'header'">Вопрос {{ num }}</h5>
        <form-group48 :title="field.type != 'header' ? 'Текст вопроса' : 'Подзаголовок'">
            <input class="form-control form-control-sm"
                   :class="save_clicked && empty(field.text) ? 'is-invalid' : ''"
                   v-model="field.text"/>
        </form-group48>

        <form-group48 title="Тип" v-if="field.type == 'header'">
            <select class="form-control form-control-sm" v-model="field.subtype">
                <option value="block">Блок вопросов</option>
                <option value="subheader">Подзаголовок в блоке</option>
            </select>
        </form-group48>

        <form-group48 title="Описание раздела" v-if="field.type == 'header'">
            <textarea class="form-control form-control-sm" v-model="field.description"></textarea>
        </form-group48>

        <div v-if="field.type != 'header'">
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

            <form-group48 title="Код категории" v-if="!['radio', 'medicine_list'].includes(field.type)">
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

            <form-group48 title="Цвет" v-if="field.show_if">
                <div class="row">
                    <div class="col">
                        <ColorPicker v-model="field.params.color"/>
                    </div>
                    <div class="col">
                        <input type="text" class="form-control form-control-sm" v-model="field.params.color">
                    </div>
                </div>
            </form-group48>

            <form-group48 title="Не включать в оценку?" v-if="form.has_integral_evaluation">
                <input type="checkbox" class="form-check" v-model="field.exclude_weight">
            </form-group48>

        </div>
        <form-group48 title="Показывать если...">
            <select class="form-control form-control-sm" v-model="field.show_if">
                <option value="">Всегда</option>

                <option v-for="other in form.fields.filter(f => f.type == 'checkbox')" :value="other.uid">{{
                        other.text
                    }}
                </option>

                <optgroup v-for="field in form.fields.filter(f => f.type == 'radio')" :label="field.text">
                    <option v-for="(variant, i) in field.params.variants" :value="{uid: field.uid, ans: i}">
                        {{ variant.text }}
                    </option>
                </optgroup>

                <optgroup v-for="field in form.fields.filter(f => f.type == 'map' && f.params.zone_groups_enabled)" :label="field.text">
                    <option v-for="(group, i) in field.params.zone_groups" :value="{uid: field.uid, group_index: i}">
                        {{ group.description }} {{i}}
                    </option>
                </optgroup>
            </select>
        </form-group48>

        <div v-if="field.type != 'header'">
            <hr>
            <form-group48 title="Код для скрипта"
                          v-if="form.has_integral_evaluation && form.integral_evaluation.script_enabled && !field.exclude_weight">
                <input type="text" class="form-control form-control-sm" v-model="field.script_group"/>
            </form-group48>
            <div v-if="['integer', 'range'].includes(field.type) && (is_admin || field.type === 'range')">
                <div class="form-group row">
                    <div class="col-md-4">
                        <strong>Ограничения</strong>
                    </div>
                    <div class="col-md-2">
                        <small>от </small><input type="number" step="0.1"
                                                 :class="save_clicked && (empty(field.params.min) || field.params.max < field.params.min) ? 'is-invalid' : ''"
                                                 class="form-control form-control-sm"
                                                 v-model="field.params.min"/>
                    </div>
                    <div class="col-md-2">
                        <small>до </small><input type="number" step="0.1"
                                                 :class="save_clicked && (empty(field.params.max) || field.params.max < field.params.min) ? 'is-invalid' : ''"
                                                 class="form-control form-control-sm"
                                                 v-model="field.params.max"/>
                    </div>

                    <div class="col-md-2" v-if="field.type === 'range'">
                        <small>шаг </small><input type="number" step="0.1"
                                                  :class="save_clicked && (empty(field.params.step) || field.params.step < field.params.min) ? 'is-invalid' : ''"
                                                  class="form-control form-control-sm"
                                                  v-model="field.params.step"/>
                    </div>
                    <div class="col-md-2" v-if="field.type === 'range'">
                        <small>начать с </small><input type="number" step="0.1"
                                                       :class="save_clicked && (empty(field.params.default) || field.params.default < field.params.min) ? 'is-invalid' : ''"
                                                       class="form-control form-control-sm"
                                                       v-model="field.params.default"/>
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
                <form-group48 title="Вес" description="Добавляется, если галочка стоит"
                              v-if="form.has_integral_evaluation && !field.exclude_weight">
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
                        <small class="text-muted">Код категории</small><br>

                        <select class="form-control form-control-sm"
                                :class="save_clicked && !variant.category ? 'is-invalid' : ''"
                                v-model="variant.category">
                            <option value="none">Не сохранять ответ</option>

                            <optgroup v-for="(group, name) in group_by(category_list, 'subcategory')"
                                      v-bind:label="name">
                                <option v-for="category in group" :value="category.name">{{ category.description }}
                                </option>
                            </optgroup>
                        </select>
                    </div>
                    <div class="col-md-2" v-if="variant.category != 'none'">
                        <small class="text-muted">Значение</small><br>
                        <input type="text" class="form-control form-control-sm"
                               :class="save_clicked && empty(variant.category_value) ? 'is-invalid' : ''"
                               v-model="variant.category_value"/>
                    </div>
                    <div class="col-md-5">
                        <small class="text-muted">Текст варианта</small><br>
                        <input type="text"
                               :class="save_clicked && empty(variant.text) ? 'is-invalid' : ''"
                               class="form-control form-control-sm" v-model="variant.text"/>
                    </div>
                    <div class="col-md-2" v-if="form.has_integral_evaluation && !field.exclude_weight">
                        <small class="text-muted">Вес</small><br>
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
                        <small class="text-muted">Дополнительные параметры</small><br>
                        <input type="text" class="form-control form-control-sm"
                               :class="save_clicked && !isJsonString(variant.custom_params) ? 'is-invalid' : ''"
                               v-model="variant.custom_params"/>
                    </div>
                </div>
            </div>

            <!-- Шкала -->
            <div v-if="field.type == 'scale'">
                <div v-if="category && category.type == 'string'">
                    <form-group48 title="Пояснение в медкарте">
                        <input type="text" class="form-control form-control-sm"
                               :class="save_clicked && empty(field.category_value) ? 'is-invalid' : ''"
                               v-model="field.category_value"/>
                    </form-group48>
                </div>

                <form-group48 title="Цвета (через запятую)">
                    <input type="text" class="form-control form-control-sm" v-model="field.params.tmp_colors"
                           @input="update_vas_params()"/>
                </form-group48>

                <form-group48 title="Подписи">
                    <div class="row">
                        <div class="col">
                            <small>справа </small>
                            <input type="text" class="form-control form-control-sm" v-model="field.params.left_label"
                                   @input="update_vas_params()"/>
                        </div>
                        <div class="col">
                            <small>слева </small>
                            <input type="text" class="form-control form-control-sm" v-model="field.params.right_label"
                                   @input="update_vas_params()"/>
                        </div>
                    </div>
                </form-group48>

                <form-group48 title="Начинать с">
                    <input type="number" class="form-control form-control-sm" v-model="field.params.start_from"
                           @input="update_vas_params()">
                </form-group48>

                <form-group48 title="Числа по убыванию">
                    <input type="checkbox" class="form-check" v-model="field.params.reversed"
                           @change="update_vas_params()">
                </form-group48>

                <form-group48 title="Не показывать знак –">
                    <input type="checkbox" class="form-check" v-model="field.params.abs"
                           @change="update_vas_params()">
                </form-group48>

                <form-group48 title="Предпросмотр" description="Шкала будет выглядеть так">
                    <visual-analog-scale :params="field.params">
                        <div class="row">
                            <div class="col d-flex justify-content-center" v-for="(color, i) in field.params.colors">
                                <input class="form-check-input monitoring-input" style="margin-left: 5px" type="radio"
                                       :id="'radio_' + field.uid + '_' + i" :name="'radio_' + field.uid">
                            </div>
                        </div>
                    </visual-analog-scale>
                </form-group48>
            </div>

            <!-- Карта -->
            <div v-if="field.type == 'map'">
                <div v-if="category && category.type == 'string'">
                    <form-group48 title="Пояснение в медкарте">
                        <input type="text" class="form-control form-control-sm"
                               :class="save_clicked && empty(field.category_value) ? 'is-invalid' : ''"
                               v-model="field.category_value"/>
                    </form-group48>
                </div>

                <form-group48 title="Тип">
                    <select :class="save_clicked && empty(field.params.type) ? 'is-invalid' : ''"
                            class="form-control form-control-sm" v-model="field.params.map">
                        <option v-for="map in Object.entries(maps)" :value="map[0]">{{ map[1] }}</option>
                    </select>
                </form-group48>

                <form-group48 title="Предпросмотр" description="Карта будет выглядеть так">
                    <interactive-map :map="field.params.map" :uid="field.uid" :is_map_preview="true"/>
                </form-group48>

                <form-group48 title="Добавить группы зон?">
                    <input type="checkbox" class="form-check" @change="$forceUpdate()"
                           v-model="field.params.zone_groups_enabled">
                </form-group48>

                <div v-if="field.params.zone_groups_enabled">
                    <strong>Группы зон</strong>
                    <div class="form-group row" v-for="(group, j) in field.params.zone_groups">
                        <div class="col-md-5">
                            <small class="text-muted">Описание группы</small><br>
                            <input type="text"
                                   :class="save_clicked && empty(group.description) ? 'is-invalid' : ''"
                                   class="form-control form-control-sm" v-model="group.description"/>
                        </div>
                        <div class="row" style="margin: 0">
                            <div>
                                <small class="text-muted">Цвет</small><br>
                                <ColorPicker @input="change_zone_group_color(j)"
                                    v-model="group.color"/>
                            </div>
                            <div class="col"><br>
                                <input type="text" class="form-control form-control-sm"
                                       @change="change_zone_group_color(j)"
                                       v-model="group.color">
                            </div>

                        </div>
                        <div><br>
                            <a class="btn btn-primary btn-sm" @click="change_zone_group(j)">
                                {{ field.params.current_group_index == j ? 'Текущая группа' : 'Выбрать зоны' }}
                            </a>
                        </div>
                        <div><br>
                            <a class="btn btn-default btn-sm" @click="remove_zone_group(j)">Удалить группу</a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Список лекарств -->
            <div v-if="field.type == 'medicine_list'">
            </div>
        </div>

        <a v-if="field.type == 'map' && field.params.zone_groups_enabled" class="btn btn-default btn-sm" @click="add_zone_group()">Добавить группу</a>
        <a v-if="field.type == 'radio'" class="btn btn-default btn-sm" @click="add_variant()">Добавить вариант</a>
        <a class="btn btn-danger btn-sm" @click="remove()">Удалить {{
                field.type != 'header' ? 'вопрос' : 'заголовок'
            }}</a>
        <button class="btn btn-primary btn-sm" style="font-size: 12px" @click="duplicate()">Дублировать</button>
        <button class="btn btn-sm" style="font-size: 12px" v-if="pkey + 1 < form.fields.length" @click="move('down')">
            &#9660;
        </button>
        <button class="btn btn-sm" style="font-size: 12px" v-if="pkey > 0" @click="move('up')">&#9650;</button>
    </card>
</template>

<script>

import Card from "../../common/Card";
import FormGroup48 from "../../common/FormGroup-4-8";
import VisualAnalogScale from "../../presenters/parts/VisualAnalogScale";
import InteractiveMap from "../../presenters/parts/InteractiveMap";
import ColorPicker from 'primevue/colorpicker';
import 'primevue/resources/themes/saga-blue/theme.css'
import 'primevue/resources/primevue.min.css'


export default {
    name: "Field",
    components: {InteractiveMap, VisualAnalogScale, FormGroup48, Card, ColorPicker},
    props: ['data', 'pkey', 'form', 'save_clicked', 'num'],
    data() {
        return {
            mode: 'integer',
            field: {},
            backup: {},
            colors: ['#058dc7', '#50b432', '#c355ff', '#ffc800',
                '#3673e8', '#f16400', "#853cff", '#24cbe5']
        }
    },
    computed: {
        category() {
            return this.category_list.filter(c => c.name == this.field.category)[0]
        }
    },
    methods: {
        clear_params: function () {
            this.backup[this.field.type] = JSON.stringify(this.field.params)
            this.field.type = this.mode

            if (this.backup[this.mode]) {
                this.field.params = JSON.parse(this.backup[this.mode])
            } else {
                this.field.params = {};
                if (this.field.type == 'radio') {
                    this.field.params.variants = [{text: '', category: ''}, {text: '', category: ''}]
                }
                if (this.field.type == 'scale') {
                    this.field.params.start_from = 0
                    this.field.params.colors = ["#63bf3a", "#72c433", "#b0dc40", "#eed748", "#e9b942", "#e3a03c", "#e18738", "#d96932", "#d4482e", "#d3312c"]
                    this.field.params.tmp_colors = this.field.params.colors.toString()
                }
                if (this.field.type == 'map') {
                    this.field.params.zone_groups_enabled = false
                    this.field.params.zone_groups = []
                    this.field.params.current_group_index = 0
                }
            }
            this.$forceUpdate()
        },
        add_variant: function () {
            let variant = {text: '', category: ''}
            if (this.form.has_integral_evaluation && !this.field.exclude_weight)
                variant.weight = 0
            this.field.params.variants.push(variant);
            this.$forceUpdate()
        },
        remove_variant: function (j) {
            this.field.params.variants.splice(j, 1);
            this.$forceUpdate()
        },
        change_zone_group_color: function () {
            this.$forceUpdate()
            Event.fire('map-zone-groups-changed', {uid: this.field.uid, groups: this.field.params.zone_groups})
        },
        add_zone_group: function () {
            if (!this.field.params.zone_groups) {
                this.field.params.zone_groups = []
            }

            this.field.params.current_group_index = this.field.params.zone_groups.length

            let color = this.colors[this.field.params.zone_groups.length % 8].replace('#', '')
            let group = {zones: [], description: '', color: color}

            this.field.params.zone_groups.push(group);

            Event.fire('map-zone-groups-changed', {uid: this.field.uid, groups: this.field.params.zone_groups})
            this.$forceUpdate()
        },
        remove_zone_group: function (j) {
            this.field.params.zone_groups.splice(j, 1);
            Event.fire('map-zone-groups-changed', {uid: this.field.uid, groups: this.field.params.zone_groups})
            this.$forceUpdate()
        },
        change_zone_group: function (j) {
            this.field.params.current_group_index = j
            this.$forceUpdate()
        },
        remove: function () {
            Event.fire('remove-field', this.pkey)
        },
        move: function (direction) {
            Event.fire('move-field-' + direction, this.pkey)
        },
        duplicate: function () {
            Event.fire('duplicate-field', this.pkey)
        },
        update_vas_params: function () {
            this.field.params.colors = this.field.params.tmp_colors.toString().split(',')
            this.field.params.start_from = parseInt(this.field.params.start_from.toString())
            this.$forceUpdate()
        }
    },
    created() {
        this.mode = this.data.type;
        this.field = this.data;

        if (this.field.type == 'scale')
            this.field.params.tmp_colors = this.field.params.colors.toString()
        if (this.field.type == 'map') {
            if (this.field.params.zone_groups_enabled) {
                Event.fire('map-zone-groups-changed', {uid: this.field.uid, groups: this.field.params.zone_groups})
                let zones = []
                this.field.params.zone_groups.forEach((gr) => {
                    zones = zones.concat(gr.zones)
                })

                setTimeout(() => {
                    Event.fire('map-zone-groups-changed', {uid: this.field.uid, groups: this.field.params.zone_groups})
                    Event.fire('set-map-zones', {uid: this.field.uid, parts: zones})
                }, 100)
            }
        }

        Event.listen('mouse-down', (data) => {
            if (data.uid !== this.field.uid || this.field.type != 'map') return

            if (this.field.params.zone_groups_enabled) {
                if (data.group_index > -1)
                    this.field.params.zone_groups[data.group_index].zones =
                        this.field.params.zone_groups[data.group_index].zones.filter((z) => z != data.zone)
                this.field.params.zone_groups[this.field.params.current_group_index].zones.push(data.zone)
                Event.fire('map-zone-groups-changed', {uid: this.field.uid, groups: this.field.params.zone_groups})
                this.$forceUpdate()
            }
        })
    }
}
</script>

<style scoped>

</style>
