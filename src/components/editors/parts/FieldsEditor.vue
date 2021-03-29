<template>
    <div>
        <field v-for="(field, i) in fields" :data="field" :pkey="i" :key="field.uid" :save_clicked="fields_save_clicked[i]"></field>

        <p class="text-center"><a class="btn btn-primary btn-sm" @click="add_field()">Добавить вопрос</a></p>
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
            required: true
        },
        fields_save_clicked: {
            required: true
        }
    },
    data() {
        return {
        }
    },
    created() {
        Event.listen('remove-field', (i) => this.remove_field(i));
    },
    methods: {
        add_field: function () {
            this.fields.push({
                type: 'integer',
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
                    yes: 'Удалить вопрос'
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
