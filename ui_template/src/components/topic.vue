<template>
    <v-layout row justify-center v-if="raw !== undefined">
        <v-dialog v-model="show" max-width="600px">
            <v-card >
                <v-toolbar dark color="primary">
                    <v-btn icon dark @click.native="show = false">
                        <v-icon>close</v-icon>
                    </v-btn>
                    <v-toolbar-title>Topic {{id}}</v-toolbar-title>
                    <v-spacer></v-spacer>
                </v-toolbar>
            </v-card>
        </v-dialog>
    </v-layout>
</template>

<script>

import ruleLink from '@/components/ruleLink.vue';

import ApiClient from '@/ApiClient.ts';

export default {
    name: 'context',
    props: ['id'],
    data () {
        return {
            'show': false,
            'raw': undefined
        }
    },
    watch: {
        'show': function (val, oldVal) {
            if (val === true && this.raw === undefined) {
                this.$root.waiting = true

                ApiClient.Instance
                    .getTopic(this.id)
                    .then(x => {
                        this.raw = x
                        this.$root.waiting = false
                    }).catch(e => alert(e));
            }
        }
    },
    components: {
        'a-rule': ruleLink
    }
}
</script>
