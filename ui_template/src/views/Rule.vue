<template>
    <div v-if="raw !== null">
        <v-list subheader>
            <v-subheader>General</v-subheader>
            <v-list-tile>
                <v-list-tile-content>
                    <v-list-tile-title>Score</v-list-tile-title>
                    <v-list-tile-sub-title>{{ raw.score }}</v-list-tile-sub-title>
                </v-list-tile-content>
            </v-list-tile>
        </v-list>

        <v-divider></v-divider>

        <v-list subheader>
            <v-subheader>Condition</v-subheader>
            <Json title="OnMsg" :json="raw.condition.onMsg" v-if="raw.condition.onMsg !== null"></Json>
            <Json title="Py"    :json="raw.condition.py"                                       ></Json>
        </v-list>
        <v-divider></v-divider>
        <v-list subheader v-for="(item, index) in raw.condition.onParams">
            <v-subheader>Condition.OnParams {{ index }} </v-subheader>
            <v-list-tile>
                <v-list-tile-content>
                    <v-list-tile-title>Topic used</v-list-tile-title>
                    <v-list-tile-sub-title><InfoLink tag="Topic" :id="item.__type__"/></v-list-tile-sub-title>
                </v-list-tile-content>
            </v-list-tile>
            <Json title="Other conditions" :json="item"></Json>
        </v-list>

        <v-divider></v-divider>

        <v-list subheader>
            <v-subheader>Action</v-subheader>
            <v-list-tile>
                <v-list-tile-content>
                    <v-list-tile-title>ImmediatlyNext</v-list-tile-title>
                    <v-list-tile-sub-title>{{ raw.action.immediatlyNext }}</v-list-tile-sub-title>
                </v-list-tile-content>
            </v-list-tile>
            <v-list-tile>
                <v-list-tile-content>
                    <v-list-tile-title>IsQuestion</v-list-tile-title>
                    <v-list-tile-sub-title>{{ raw.action.isQuestion }}</v-list-tile-sub-title>
                </v-list-tile-content>
            </v-list-tile>
            <Json title="Operations" :json="raw.action.operations"></Json>
            <Json title="Text"       :json="raw.action.text"      ></Json>
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

import Json from '@/components/Json.vue';
import InfoLink from '@/components/InfoLink.vue';
import Loading from '@/components/Loading.vue';

import ApiClient from '@/ApiClient.ts';

import { IRule } from '@/ApiInterfaces.ts';

@Component({
    name: 'RuleView',
    components: {
        Json,
        Loading,
    },
})
export default class RuleView extends Vue {
    @Prop({ required: true })
    public id!: string;

    private raw: IRule|null = null;

    private created(): void {
        ApiClient.Instance
            .getRule(this.id)
            .then((x: IRule) => {
                this.raw = x;
            }).catch((e: any) => alert(e));
    }

    private beforeCreate(): void {
        this.$options!.components!.InfoLink = InfoLink;
    }
}
</script>
