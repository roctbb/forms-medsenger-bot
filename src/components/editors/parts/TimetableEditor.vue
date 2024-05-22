<template>
    <card title="Расписание">
        <form-group48 title="Режим  ">
            <select @change="clear_time_points()" class="form-control form-control-sm"
                    v-model="mode">
                <option value="manual">Заполняется вручную</option>
                <option value="dates" v-if="timetable.dates_enabled">Определенные даты</option>
                <option value="daily">Ежедневно</option>
                <option value="weekly">Еженедельно</option>
                <option value="monthly">Ежемесячно</option>
                <option value="ndays">Раз в N дней</option>
            </select>
        </form-group48>

        <div v-if="!['manual', 'dates', 'ndays'].includes(timetable.mode)">
            <hr>
            <div class="form-group row" v-for="(timepoint, index) in timetable.points">
                <div class="col-md-4">
                    <div v-if="timetable.mode === 'weekly'">
                        <small class="text-muted">День недели</small>
                        <select class="form-control form-control-sm" v-model="timepoint.day">
                            <option v-for="(day, i) in weekdays"
                                    v-bind:value="i">{{ day }}
                            </option>
                        </select>
                    </div>
                    <div v-if="timetable.mode === 'monthly'">
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
                <div class="col-md-2"><br>
                    <a @click="remove_time_point(index)"
                       v-if="timetable.points.length > 1">Удалить</a>
                </div>
            </div>

            <div class="text-center" style="margin-top: 15px;">
                <a class="btn btn-default btn-sm" @click="add_time_point()">Добавить время</a>
                <slot></slot>
            </div>
        </div>

        <div v-if="timetable.mode === 'ndays'">
            <div class="form-group row">
                <div class="col-md-4">
                </div>
                <div class="col-md-4">
                    <small>Период</small>
                </div>
                <div class="col-md-4">
                     <input type="number" min="1" max="365"
                           class="form-control form-control-sm"
                           v-model="timetable.period"/>
                </div>
            </div>
        </div>

        <div v-if="timetable.mode === 'dates'">
            <hr>
            <i>Напоминания будут отправляться в выбранные даты.</i>
            <div class="row form-group" v-for="(timepoint, index) in timetable.points"
                 :key="'timepoint_' + index">
                <div class="col-md-4">
                    <small class="text-muted">Дата и время</small><br>
                    <date-picker v-model="timepoint.date" lang="ru"
                                 format="DD.MM.YYYY в HH:mm" title-format="DD.MM.YYYY"
                                 type="datetime" value-type="timestamp"></date-picker>
                </div>
                <div class="col-md-2">
                    <br>
                    <a @click="remove_time_point(index)"
                       v-if="timetable.points.length > 1">Удалить</a>
                </div>
            </div>
            <div class="text-center" style="margin-top: 15px;">
                <a class="btn btn-default btn-sm" @click="add_time_point()">Добавить дату и время</a>
                <slot></slot>
            </div>
        </div>

        <div v-if="source === 'medicine'">
            <hr>
            <form-group48 title="Добавить дату отмены приема">
                <input class="form-check" type="checkbox" v-model="timetable.detach_date_enabled"
                       @change="$forceUpdate()"/>
            </form-group48>
            <div v-if="timetable.detach_date_enabled">
                <form-group48 title="Дата отмены">
                    <date-picker v-model="timetable.detach_date" lang="ru"
                                 format="DD.MM.YYYY" value-type="YYYY-MM-DD"></date-picker>
                </form-group48>
            </div>
        </div>

          <div v-if="source === 'reminder' && !['manual', 'dates'].includes(timetable.mode)">
            <hr>
            <i>Напоминания будут отправляться в выбранный период. По завершении периода они автоматически отключатся.</i>
            <form-group48 title="Дата начала" :required="true">
                <date-picker lang="ru" v-model="timetable.attach_date" @change="$forceUpdate()"
                             format="DD.MM.YYYY" value-type="YYYY-MM-DD"></date-picker>
            </form-group48>

            <form-group48 title="Дата завершения">
                <date-picker lang="ru" v-model="timetable.detach_date" @change="$forceUpdate()"
                             format="DD.MM.YYYY" value-type="YYYY-MM-DD"></date-picker>
            </form-group48>
        </div>

    </card>
</template>

<script>
import FormGroup48 from "../../common/FormGroup-4-8";
import Card from "../../common/Card";
import DatePicker from 'vue2-datepicker';
import moment from "moment";

export default {
    name: "TimetableEditor",
    components: {FormGroup48, Card, DatePicker},
    props: {
        data: {
            required: true
        },
        timetable_save_clicked: {
            required: true
        },
        source: {
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
            if (this.timetable.mode === 'manual') {
                return;
            }
            if (this.timetable.mode === 'daily') {
                this.timetable.points.push({
                    hour: '10',
                    minute: '00'
                })
                Event.fire('add-time-point')
            } else if (this.timetable.mode === 'dates') {
                this.timetable.points.push({
                    date: +moment().add(7, 'day')
                })
                Event.fire('add-time-point')
            } else {
                this.timetable.points.push({
                    day: '',
                    hour: '10',
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
            timetable: {
                period: 1
            },
            backup: {}
        }
    },
    created() {
        this.timetable = this.data
        this.mode = this.timetable.mode
    }
}
</script>

<style scoped>

</style>
