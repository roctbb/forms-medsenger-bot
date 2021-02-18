<template>
    <div>
    <card v-for="(field, i) in fields">
        <form-group48 title="Текст вопроса">
            <input class="form-control" v-model="field.text"/>
        </form-group48>

        <form-group48 title="Тип">
            <select @change="clear_params(field)" class="form-control" v-model="field.type">
                <option v-for="type in Object.entries(field_types)" :value="type[0]">{{ type[1] }}</option>
            </select>
        </form-group48>

        <form-group48 title="Код категории" v-if="field.type != 'radio'">
            <input class="form-control" v-model="field.category"/>
        </form-group48>

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
                <div class="col-md-4">
                    <small class="text-mutted">Код категории</small><br>
                    <input type="text" class="form-control" v-model="variant.category"/>
                </div>
                <div class="col-md-6">
                    <small class="text-mutted">Текст варианта</small><br>
                    <input type="text" class="form-control" v-model="variant.text"/>
                </div>
                <a href="#" v-if="field.params.variants.length > 2" @click="remove_variant(field, j)">Удалить
                    вариант</a>
            </div>
            <a class="btn btn-primary btn-sm" @click="add_variant(field)">Добавить вариант</a>

        </div>

        <a class="btn btn-danger btn-sm" @click="remove_field(i)">Удалить вопрос</a>

    </card>

    <p class="text-center"><a href="#" class="btn btn-primary btn-sm" @click="add_field()">Добавить поле</a></p>
    </div>
</template>

<script>
import FormGroup48 from "../../common/FormGroup-4-8";
import Card from "../../common/Card";

export default {
    name: "FieldsEditor",
    components: {FormGroup48, Card},
    props: {
        data: {
            required: true,
        }
    },
    data() {
        return {
            fields: []
        }
    },
    created() {
        this.fields = this.data
        console.log("got fields", this.timetable)
    },
    methods: {
        clear_params: function (field) {
            field.params = {};

            if (field.type == 'radio') {
                field.params.variants = [{text: '', category: ''}, {text: '', category: ''}]
            }
        },

        add_field: function () {
            this.fields.push({
                type: 'integer',
                params: {}
            });
        },
        add_variant: function (field) {
            field.params.variants.push({text: '', category: ''});
            this.$forceUpdate()
        },
        remove_variant: function (field, index) {
            field.params.variants.splice(index, 1);
            this.$forceUpdate()
        },
        remove_field: function (index) {
            this.fields.splice(index, 1);
        },
    }
}
</script>

<style scoped>

</style>
