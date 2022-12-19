<template>
    <div>
        <field :form="form" v-for="(field, i) in fields" :data="field" :pkey="i" :key="field.uid" :num="get_field_num(field.uid)"
               :save_clicked="fields_save_clicked[i]"></field>

        <div class="row justify-content-md-center" style="column-gap: 5px; margin-bottom: 10px">
            <a class="btn btn-primary btn-sm" @click="add_field()">Добавить вопрос</a>
            <a class="btn btn-primary btn-sm" @click="add_header()">Добавить подзаголовок</a>
        </div>
    </div>
</template>

<script>
import FormGroup48 from "../../common/FormGroup-4-8";
import Card from "../../common/Card";
import Field from "./Field";

export default {
    name: "FieldsEditor",
    components: {Field, FormGroup48, Card},
    props: {
        fields: {
            required: true,
        },
        form: {
            required: true
        },
        fields_save_clicked: {
            required: true
        }
    },
    data() {
        return {}
    },
    created() {
        Event.listen('remove-field', (i) => this.remove_field(i));
        Event.listen('move-field-up', (i) => {
            this.fields = this.swap(this.fields, i, i-1)
            this.$forceUpdate()
        })
        Event.listen('move-field-down', (i) => {
            this.fields = this.swap(this.fields, i, i+1)
            this.$forceUpdate()
        })
        Event.listen('duplicate-field', (i) => {
            let copy = {...this.fields[i]}
            copy.uid = this.uuidv4()
            this.fields.splice(i, 0, copy);
            this.$forceUpdate()
        })
    },
    methods: {
        get_field_num: function (uid) {
            return this.fields.filter(f => f.type != 'header').findIndex(f => f.uid == uid) + 1
        },
        add_field: function () {
            this.fields.push({
                type: 'integer',
                params: {},
                uid: this.uuidv4()
            });
            this.fields_save_clicked.push(false)
        },
        add_header: function () {
            this.fields.push({
                type: 'header',
                params: {},
                uid: this.uuidv4()
            });
            this.fields_save_clicked.push(false)
        },
        remove_field: function (index) {
            this.$confirm({
                message: `Вы уверены?`,
                button: {
                    no: 'Нет',
                    yes: 'Удалить ' + (this.fields[index].type != 'header' ? 'вопрос' : 'подзаголовок')
                },
                callback: confirm => {
                    if (confirm) {
                        this.fields.splice(index, 1);
                        this.fields_save_clicked.splice(index, 1);
                    }
                }
            })

        },
    }
}
</script>

<style scoped>

</style>
