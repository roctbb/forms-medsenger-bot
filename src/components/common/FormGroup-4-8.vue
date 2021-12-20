<template>
    <div class="form-group form-group-sm row" :class="{'required': required}">
        <div class="col-md-4">
            <strong class="big" v-if="big">{{ title }}</strong>
            <strong v-else>{{ title }}</strong>
        </div>
        <div class="col-md-8">
            <slot></slot>
            <span class="text-muted" v-if="description">{{ description }}</span>
            <div v-if="errors">
                <span style="color: red;">{{ errors }}</span>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "FormGroup-4-8",
    props: ['title', 'description', 'required', 'errors', 'big']
}
</script>

<style scoped>
strong {
    font-size: 0.9rem;
}

strong.big {
    font-size: 1rem;
}

.form-group.required strong:after {
    color: red;
    content: ' *';
    font-size: 18px;
}
</style>
