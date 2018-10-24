<template>
    <v-layout row justify-center v-if="raw !== undefined">
        <v-dialog v-model="show" max-width="600px">
            <v-card >
                <v-toolbar dark color="primary">
                    <v-btn icon dark @click.native="show = false">
                        <v-icon>close</v-icon>
                    </v-btn>
                    <v-toolbar-title>Rule {{id}}</v-toolbar-title>
                    <v-spacer></v-spacer>
                </v-toolbar>

                <v-divider></v-divider>

                <RuleView :id="id"/>

            </v-card>
        </v-dialog>
    </v-layout>
</template>

<script>
//  import json from '@/components/json.vue';
//  import topicLink from '@/components/topicLink.vue';
//  
//  import RuleView from '@/views/Rule.vue'
//  
//  import ApiClient from '@/ApiClient.ts';
//  
//  export default {
//      name: 'RuleDialog',
//      props: ['id'],
//      data () {
//          return {
//              'show': false,
//          }
//      },
//      components: {
//          RuleView
//      },
//  }
</script>
