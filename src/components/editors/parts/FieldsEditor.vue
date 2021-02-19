<template>
    <div>
        <field v-for="(field, i) in fields" :data="field" :pkey="i" :key="field.uid"></field>

        <p class="text-center"><a class="btn btn-primary btn-sm" @click="add_field()">Добавить поле</a></p>
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
        Event.listen('remove-field', (i) => this.remove_field(i));
    },
    methods: {
        add_field: function () {
            this.fields.push({
                type: 'integer',
                params: {},
                uid: this.uuidv4()
            });
        },
        remove_field: function (index) {
            console.log("remove field", index)
            this.fields.splice(index, 1);
        },
    }
}
</script>

<style scoped>

</style>
