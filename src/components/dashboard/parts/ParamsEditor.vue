<template>
    <div style="margin-right: -5px;" v-if="params.backup && params.backup.length">
        <input class="btn btn-block btn-outline-info" type="button" data-toggle="collapse"
               aria-expanded="false"
               value="Настройка параметров уведомлений" data-target="#collapse" aria-controls="collapse">
        <div class="collapse" id="collapse" style="font-size: 14px">
            <div class="card card-body">
                <div v-if="flags.loaded">
                    <div v-for="(param, i) in params.backup">
                        <form-group-4-8 :title="param.name">
                            <input class="form-control form-control-sm"
                                   :class="errors.length && isNaN(to_float(params.edited[i])) ? 'is-invalid' : ''"
                                   v-model="params.edited[i]">
                        </form-group-4-8>
                    </div>
                    <div>
                        <button class="btn btn-success btn-sm" @click="save_params()" :disabled="flags.lock_btn">
                            Сохранить
                        </button>
                    </div>
                    <div class="alert alert-success" v-if="errors.length && errors[0] == 'Сохранено'"
                         style="margin-top: 15px">Данные успешно сохранены.
                    </div>
                    <error-block v-else :errors="errors"></error-block>
                </div>
                <loading v-else/>
            </div>
        </div>
    </div>
</template>

<script>
import FormGroup48 from "../../common/FormGroup-4-8";
import ErrorBlock from "../../common/ErrorBlock";
import Loading from "../../Loading";

export default {
    name: "ParamsEditor",
    components: {Loading, ErrorBlock, FormGroup48},
    data() {
        return {
            errors: [],
            params: {
                backup: []
            },
            flags: {
                loaded: false,
                lock_btn: false
            }
        }
    },
    methods: {
        update_params: function () {
            this.flags.loaded = false
            this.params = {
                backup: [],
                edited: []
            }
            this.axios.get(this.url('/params')).then(response => {
                response.data.forEach(param => {
                    if (param.name && param.value != null) {
                        this.params.backup.push(param)
                        this.params.edited.push(param.value)
                    }
                })
                this.flags.loaded = true
            });
        },
        save_params: function () {
            this.errors = []
            this.flags.lock_btn = true

            // check values
            this.params.edited.map((param, i) => {
                let val = this.to_float(param)
                if (!isNaN(val)) {
                    return val
                } else {
                    this.errors.push(`Пожалуйста, проверьте поле "${this.params.backup[i].name}"`)
                    return param
                }
            })

            // change values
            if (!this.errors.length) {
                Event.fire('change-params', this.params)
            }
        }
    },
    created() {
        if (this.page == 'dashboard') this.update_params()

        Event.listen('dashboard-to-main', () => {
            if (window.PAGE == 'settings') {
                this.update_params()
            }
        });
        Event.listen('home', () => {
            this.update_params()
        });
        Event.listen('back-to-dashboard', () => this.update_params())

        Event.listen('params-saved', () => {
            this.errors = ['Сохранено']
            this.params.backup.forEach((param, i) => {
                param.value = this.params.edited[i]
            })
            this.flags.lock_btn = false
        })

        Event.listen('params-not-saved', () => {
            this.errors = ['Ошибка сохранения']
            this.flags.lock_btn = false
        })

    }
}
</script>

<style scoped>

</style>
