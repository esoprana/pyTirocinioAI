<template>
    <div>
        <a @click="click()">{{ id }}</a>
        <InfoDialog tag="Rule" :id="id" ref="rule"/>
    </div>
</template>

<script>
import InfoDialog from '@/components/InfoDialog.vue'

export default {
    name: 'a-rule',
    props: ['id'],
    methods: {
        click () {
            this.$refs.rule.show = true
        }
    },
    beforeCreate() {
        this.$options.components.InfoDialog = InfoDialog;
    }
}
</script>
