<template>
    <div v-if="raw !== null">
        <v-list subheader>
            <v-subheader>General</v-subheader>
            <v-list-tile>
                <v-list-tile-content>
                    <v-list-tile-title>Name</v-list-tile-title>
                    <v-list-tile-sub-title>{{ raw.name }}</v-list-tile-sub-title>
                </v-list-tile-content>
            </v-list-tile>
        </v-list>
        <v-divider></v-divider>
        <v-list subheader>
            <v-subheader>Rules</v-subheader>
            <v-list-tile v-for="(item, index) in raw.rules">
                <v-list-tile-content>
                    <v-list-tile-title>Rule {{ index }}</v-list-tile-title>
                    <v-list-tile-sub-title><InfoLink tag="Rule" :id="item"/></v-list-tile-sub-title>
                </v-list-tile-content>
            </v-list-tile>
        </v-list>
    </div>
    <div v-else>
        <Loading/>
    </div>
</template>

<script lang="ts">
import Vue from 'vue';
import Component from 'vue-class-component';
import { Prop } from 'vue-property-decorator';

import Loading from '@/components/Loading.vue';
import InfoLink from '@/components/InfoLink.vue';

import ApiClient from '@/ApiClient.ts';

import { ITopic } from '@/ApiInterfaces.ts';

@Component({
    name: 'TopicView',
    components: {
        Loading,
    },
})
export default class TopicView extends Vue {

    @Prop({ required: true })
    public id !: string;

    private raw: ITopic|null = null;

    private created(): void {
        ApiClient.Instance
            .getTopic(this.id)
            .then((x: ITopic) => {
                this.raw = x;
            }).catch((e: any) => alert(e));
    }

    private beforeCreate(): void {
        this.$options!.components!.InfoLink = InfoLink;
    }
}
</script>
