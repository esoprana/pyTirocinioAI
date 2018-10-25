<template>
    <v-layout row justify-center>
        <v-dialog v-model="show" max-width="600px">
            <v-card>
                <v-toolbar dark color="primary">
                    <v-toolbar-title>{{ title }}</v-toolbar-title>
                    <v-spacer></v-spacer>
                    <v-btn icon dark @click.native="$router.push(fullPath)">
                        <v-icon>open_in_browser</v-icon>
                    </v-btn>
                    <v-btn icon dark @click.native="show = false">
                        <v-icon>close</v-icon>
                    </v-btn>
                </v-toolbar>
                <template v-if="show">
                    <ContextView :id="id"      v-if="tag == 'Context'"/>
                    <RuleView    :id="id" v-else-if="tag == 'Rule'"/>
                    <TopicView   :id="id" v-else-if="tag == 'Topic'"/>
                </template>
            </v-card>
        </v-dialog>
    </v-layout>
</template>

<script lang=ts>
import Vue from 'vue';
import Component from 'vue-class-component';
import { Prop } from 'vue-property-decorator';

import TopicView from '@/views/Topic.vue';
import ContextView from '@/views/Context.vue';
import RuleView from '@/views/Rule.vue';

@Component({
    name: 'InfoDialog',
})
export default class InfoDialog extends Vue {
    show = false;

    @Prop({ required: true }) id  !: string;
    @Prop({ required: true }) tag !: 'Context'|'Topic'|'Rule';

    get title() {
        return `${this.tag} ${this.id}`;
    }

    get fullPath() {
        switch(this.tag) {
            case 'Context': return {
                'name': 'context',
                'params': { 'id': this.id }
            };
            case 'Topic': return {
                'name': 'topic',
                'params': { 'id': this.id }
            };
            case 'Rule': return {
                'name': 'rule',
                'params': { 'id': this.id }
            };

            default: {
                console.error('Wrong TagType(should be one of "Context", "Topic", "Rule")')
            }
        }
    }

    beforeCreate() {
        this.$options!.components!.ContextView = ContextView;
        this.$options!.components!.RuleView = RuleView;
        this.$options!.components!.TopicView = TopicView;
    }
}
</script>
