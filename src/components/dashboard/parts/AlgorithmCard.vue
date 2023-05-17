<template>
    <card class="col-lg-3 col-md-4" :image="images.algorithm">
        <strong class="card-title">{{ algorithm.title }}</strong>
        <small>{{ algorithm.description }}</small><br>
        <small v-html="alg_description(algorithm)"></small>
        <div v-if="!algorithm.is_template">
            <div v-if="algorithm.contract_id == current_contract_id">
                <a href="#" @click="edit_algorithm()">Редактировать</a>
                <a href="#" @click="delete_algorithm()">Удалить</a>
            </div>
            <div v-else>
                <small>Добавлен в другом контракте.</small>
            </div>
            <br>
            <small v-if="!empty(algorithm.template_id)" class="text-muted">
                ID шаблона: {{ algorithm.template_id }}
            </small>
        </div>
        <div v-else>
            <a href="#" v-if="need_filling(algorithm)" @click="setup_algorithm()">
                Настроить и подключить
            </a>
            <a href="#" v-else @click="attach_algorithm()">Подключить</a>
            <a href="#" v-if="is_admin" @click="edit_algorithm()">Редактировать</a>
            <a href="#" v-if="is_admin" @click="delete_algorithm()">Удалить</a>

            <br>
            <small class="text-muted">ID: {{ algorithm.id }}</small>
        </div>
    </card>
</template>

<script>
import Card from "../../common/Card";

export default {
    name: "AlgorithmCard",
    components: {Card},
    props: {
        algorithm: {required: true}
    },
    methods: {
        edit_algorithm: function () {
            Event.fire('edit-algorithm', this.algorithm)
        },
        delete_algorithm: function () {
            this.$confirm({
                message: `Вы уверены, что хотите удалить алгоритм ` + this.algorithm.title + `?`,
                button: {
                    no: 'Нет',
                    yes: 'Да, удалить'
                },
                callback: confirm => {
                    if (confirm) {
                        this.axios.post(this.direct_url('/api/settings/delete_algorithm'), this.algorithm)
                            .then((response) => Event.fire('algorithm-deleted', response.data.deleted_id));
                    }
                }
            })
        },
        attach_algorithm: function () {
            Event.fire('attach-algorithm-from-card', this.algorithm)
        },
        setup_algorithm: function () {
            Event.fire('setup-algorithm-from-card', this.algorithm)
        },
    }
}
</script>

<style scoped>
p {
    margin-top: 5px;
    margin-bottom: 5px;
}

h5 {
    margin-bottom: 10px;
    margin-top: 10px;
    font-size: 1.15rem;
}

small {
    font-size: 90%;
}

.card a {
    font-size: 90% !important;
}
</style>
