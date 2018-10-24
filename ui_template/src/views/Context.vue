<template>
    <div v-if="Object.keys(raw).length">
        <v-list subheader>
            <v-subheader>General</v-subheader>
            <v-list-tile>
                <v-list-tile-content>
                    <v-list-tile-title>OfUser</v-list-tile-title>
                    <v-list-tile-sub-title>{{ raw.ofUser }}</v-list-tile-sub-title>
                </v-list-tile-content>
            </v-list-tile>
            <v-list-tile>
                <v-list-tile-content>
                    <v-list-tile-title>Timestamp</v-list-tile-title>
                    <v-list-tile-sub-title>{{ raw.timestamp }}</v-list-tile-sub-title>
                </v-list-tile-content>
            </v-list-tile>
        </v-list>
        <v-divider></v-divider>
        <v-list subheader>
            <v-subheader>Message</v-subheader>
            <v-list-tile>
                <v-list-tile-content>
                    <v-list-tile-title>Type</v-list-tile-title>
                    <v-list-tile-sub-title>{{ raw.message.cls }}</v-list-tile-sub-title>
                </v-list-tile-content>
            </v-list-tile>
            <v-list-tile>
                <v-list-tile-content>
                    <v-list-tile-title>Text</v-list-tile-title>
                    <v-list-tile-sub-title>{{ raw.message.text }}</v-list-tile-sub-title>
                </v-list-tile-content>
            </v-list-tile>
            <v-list-tile v-if="raw.message.cls == 'BotMessage'">
            <v-list-tile-content>
                <v-list-tile-title>ofRule</v-list-tile-title>
                <v-list-tile-sub-title @click="showRule()"><a>{{ raw.message.fromRule }}</a></v-list-tile-sub-title>
                <InfoDialog :id="raw.message.fromRule" tag="Rule" ref="ofRule"/>
            </v-list-tile-content>
            </v-list-tile>
            <div v-if="raw.message.cls == 'UserMessage'">
                <json title="Intent"       :json="raw.message.intent"     ></json>
                <json title="Sentiment"    :json="raw.message.sentiment"  ></json>
                <json title="Photo"        :json="raw.message.photo"      ></json>
                <json title="Google Topic" :json="raw.message.googleTopic"></json>
            </div>
        </v-list>
        <v-divider></v-divider>
        <v-list v-for="(item, index) in raw.params">
            <v-list subheader>
                <v-subheader>Params {{ index }}</v-subheader>
                <v-list-tile>
                    <v-list-tile-content>
                        <v-list-tile-title>OfTopic</v-list-tile-title>
                        <v-list-tile-sub-title><a-topic :id="item.ofTopic"/></v-list-tile-sub-title>
                    </v-list-tile-content>
                </v-list-tile>
                <v-list-tile>
                    <v-list-tile-content>
                        <v-list-tile-title>StartTime</v-list-tile-title>
                        <v-list-tile-sub-title>{{ item.startTime }}</v-list-tile-sub-title>
                    </v-list-tile-content>
                </v-list-tile>
                <v-list-tile>
                    <v-list-tile-content>
                        <v-list-tile-title>Priority</v-list-tile-title>
                        <v-list-tile-sub-title>{{ item.priority }}</v-list-tile-sub-title>
                    </v-list-tile-content>
                </v-list-tile>

                <json title="Values" :json="item.values"></json>
            </v-list>
        </v-list>
    </div>
    <div v-else>
        <Loading/>
    </div >
</template>

<script lang="ts">
import Vue from 'vue';
import Component from 'vue-class-component';
import { Prop } from 'vue-property-decorator';

import json from '@/components/json.vue';
import topicLink from '@/components/topicLink.vue';

import InfoDialog from '@/components/InfoDialog.vue';

import Loading from '@/components/Loading.vue';

import ApiClient from '@/ApiClient.ts';

@Component({
    name: 'ContextView',
    components: {
        json,
        Loading,
        'a-topic': topicLink
    }
})
export default class ContextView extends Vue {
    raw: object = {}

    $refs!: {
        ofRule: InfoDialog
    }

    @Prop({ required: true }) id !: string;

    showRule () {
        this.$refs.ofRule.show = true
    }

    created() {
        //this.$root!.waiting = true;

        ApiClient.Instance
            .getContext(this.id)
            .then(x => {
                this.raw = x;
                //this.$root['waiting'] = false;
            }).catch(e => alert(e));
    }

    beforeCreate() {
        this.$options!.components!.InfoDialog = InfoDialog;
    }
}
</script>
