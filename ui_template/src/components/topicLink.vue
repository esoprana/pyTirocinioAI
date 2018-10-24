<template>
    <div>
        <a @click="click()">{{ id }}</a>
        <InfoDialog tag="Topic" :id="id" ref="topic"/>
    </div>
</template>

<script>
import InfoDialog from '@/components/context.vue'

export default {
    name: 'a-topic',
    props: ['id'],
    methods: {
        click () {
            this.$refs.topic.show = true
        }
    },
    beforeCreate() {
        this.$options.components.InfoDialog = InfoDialog;
    }
}
</script>
