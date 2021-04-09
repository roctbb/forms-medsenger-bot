<template>
    <div style="background-color: white;">
        <div class="container">
            <div class="row">
                <div class="col-12">
                    <p><strong>Пациент:</strong> {{ patient.info.name }} ({{ patient.info.birthday }}) <span class="float-right"><a @click="go_home()" href="#">Вернуться к началу</a></span></p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "DashboardHeader",
    props: ['patient'],
    methods: {
        go_home: function () {
            Event.fire('home');
        }
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
}
</style>
