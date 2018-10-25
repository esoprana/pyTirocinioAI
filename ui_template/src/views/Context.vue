<template>
    <div v-if="raw !== null">
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
                <v-list-tile-sub-title>
                    <InfoLink :id="raw.message.fromRule" tag="Rule"/>
                </v-list-tile-sub-title>
            </v-list-tile-content>
            </v-list-tile>
            <div v-if="raw.message.cls == 'UserMessage'">
                <Json title="Intent"       :json="raw.message.intent"     ></Json>
                <Json title="Sentiment"    :json="raw.message.sentiment"  ></Json>
                <Json title="Photo"        :json="raw.message.photo"      ></Json>
                <Json title="Google Topic" :json="raw.message.googleTopic"></Json>
            </div>
        </v-list>
        <v-divider></v-divider>
        <v-list v-for="(item, index) in raw.params">
            <v-list subheader>
                <v-subheader>Params {{ index }}</v-subheader>
                <v-list-tile>
                    <v-list-tile-content>
                        <v-list-tile-title>OfTopic</v-list-tile-title>
                        <v-list-tile-sub-title><InfoLink tag="Topic" :id="item.ofTopic"/></v-list-tile-sub-title>
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

                <Json title="Values" :json="item.values"></Json>
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

import Json from '@/components/Json.vue';
import topicLink from '@/components/topicLink.vue';

import InfoDialog from '@/components/InfoDialog.vue';
import InfoLink from '@/components/InfoLink.vue';

import Loading from '@/components/Loading.vue';

import ApiClient from '@/ApiClient.ts';

import { IContext } from '@/ApiInterfaces.ts';

@Component({
    name: 'ContextView',
    components: {
        Json,
        Loading,
    },
})
export default class ContextView extends Vue {
    @Prop({ required: true })
    public id !: string;

    private raw: IContext|null = null;

    private created(): void {
        ApiClient.Instance
            .getContext(this.id)
            .then((x: IContext) => {
                this.raw = x;
            }).catch((e: any) => alert(e));
    }

    private beforeCreate(): void {
        this.$options!.components!.InfoDialog = InfoDialog;
        this.$options!.components!.InfoLink   = InfoLink;
    }
}
</script>
