<template>
    <div>
        <a @click="click()">{{ id }}</a>
        <rule :id="id" ref="rule"></rule>
    </div>
</template>

<script>
import rule from '@/components/rule.vue'

export default {
    name: 'a-rule',
    props: ['id'],
    methods: {
        click () {
            this.$refs.rule.show = true
        }
    },
    beforeCreate: function () {
        this.$options.components.rule = rule
    }
}
</script>
