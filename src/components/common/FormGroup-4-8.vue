<template>
    <div class="form-group form-group-sm row" :class="{'required': required}">
        <div class="col-md-4" :class="{'col-10': check}">
            <strong :class="{'big': big}">{{ title }}</strong>
            <div v-if="description">
                <span class="text-muted">{{ description }}</span>
            </div>

        </div>
        <div class="col-md-8" :class="{'col-2': check}">
            <slot></slot>
            <div v-if="errors">
                <span style="color: red;">{{ errors }}</span>
            </div>
        </div>

    </div>
</template>

<script>
export default {
    name: "FormGroup-4-8",
    props: ['title', 'description', 'required', 'errors', 'big', 'check']
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
