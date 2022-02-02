<template>
    <card title="Расписание">
        <form-group48 title="Режим  ">
            <select @change="clear_time_points()" class="form-control form-control-sm"
                    v-model="mode">
                <option value="manual">Заполняется вручную</option>
                <option value="daily">Ежедневно</option>
                <option value="weekly">Еженедельно</option>
                <option value="monthly">Ежемесячно</option>
            </select>
        </form-group48>


        <div v-if="timetable.mode != 'manual'">
            <hr>
            <div class="form-group row" v-for="(timepoint, index) in timetable.points">
                <div class="col-md-3">
                    <div v-if="timetable.mode == 'weekly'">
                        <small class="text-muted">День недели</small>
                        <select class="form-control form-control-sm" v-model="timepoint.day">
                            <option v-for="(day, i) in weekdays"
                                    v-bind:value="i">{{ day }}
                            </option>
                        </select>
                    </div>
                    <div v-if="timetable.mode == 'monthly'">
                        <small class="text-muted">День</small>
                        <input type="number" min="1" max="31" class="form-control form-control-sm"
                               :class="timetable_save_clicked[index] && (!timepoint.day || timepoint.day < 1 || timepoint.day > 31) ? 'is-invalid' : ''"
                               v-model="timepoint.day"/>
                    </div>
                </div>
                <div class="col-md-3">
                    <small class="text-muted">Часы</small>
                    <input type="number" min="0" max="23" class="form-control form-control-sm"
                           :class="timetable_save_clicked[index] && ((!timepoint.hour && timepoint.hour !== 0)|| timepoint.hour < 0 || timepoint.hour > 23) ? 'is-invalid' : ''"
                           v-model="timepoint.hour"/>
                </div>
                <div class="col-md-3">
                    <small class="text-muted">Минуты</small>
                    <input type="number" min="0" max="59"
                           class="form-control form-control-sm"
                           :class="timetable_save_clicked[index] && ((!timepoint.minute && timepoint.minute !== 0) || timepoint.minute < 0 || timepoint.minute > 59) ? 'is-invalid' : ''"
                           v-model="timepoint.minute"/>
                </div>
                <div class="col-md-3"><br>
                    <a class="btn btn-sm btn-default" @click="remove_time_point(index)"
                       v-if="timetable.points.length > 1">Удалить</a>
                </div>
            </div>

            <a class="btn btn-primary btn-sm" @click="add_time_point()">Добавить время</a><slot></slot>

        </div>
        <div v-else>
          <slot></slot>
        </div>
    </card>
</template>

<script>
import FormGroup48 from "../../common/FormGroup-4-8";
import Card from "../../common/Card";

export default {
    name: "TimetableEditor",
    components: {FormGroup48, Card},
    props: {
        data: {
            required: true
        },
        timetable_save_clicked: {
            required: true
        }
    },
    methods: {
        clear_time_points: function () {
            this.backup[this.timetable.mode] = JSON.stringify(this.timetable.points)
            this.timetable.mode = this.mode

            if (this.backup[this.mode]) {
                this.timetable.points = JSON.parse(this.backup[this.mode])
            } else {
                Event.fire('clear-time-points')
                this.timetable.points = [];
                this.add_time_point();
            }

        },
        add_time_point: function () {
            if (this.timetable.mode == 'manual') {
                return;
            }
            if (this.timetable.mode == 'daily') {
                this.timetable.points.push({
                    hour: '',
                    minute: '00'
                })
                Event.fire('add-time-point')
            } else {
                this.timetable.points.push({
                    day: '',
                    hour: '',
                    minute: '00'
                })
                Event.fire('add-time-point')
            }
        },
        remove_time_point: function (index) {
            this.timetable.points.splice(index, 1);
            Event.fire('remove-time-point', index);
        },
    },
    data() {
        return {
            mode: 'daily',
            timetable: {},
            backup: {}
        }
    },
    created() {
        this.timetable = this.data
        this.mode = this.timetable.mode
        console.log("got timetable", this.timetable)
    }
}
</script>

<style scoped>

</style>
