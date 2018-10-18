<template>
  <div>
    <a @click="click()">{{ id }}</a>
    <topic :id="id" ref="topic"></topic>
  </div>
</template>

<script>
import topic from '@/components/topic.vue'

export default {
    name: 'a-topic',
    props: ['id'],
    methods: {
        click () {
            this.$refs.topic.show = true
        }
    },
    beforeCreate: function () {
        this.$options.components.topic = topic
    }
}
</script>
