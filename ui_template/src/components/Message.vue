<template>
    <v-card :color="message.bot?'purple':'green'" class="white--text" v-bind:class="{user: !message.bot}" >
        <v-layout row>
            <v-flex xs10>
                <v-card-title primary-title>
                    <div>
                        <div class="headline">{{ message.text }}</div>
                    </div>
                </v-card-title>
            </v-flex>
            <v-flex xs2 style="text-align: right">
                <v-card-text>{{ message.bot?'Bot':'User' }}</v-card-text>
            </v-flex>
        </v-layout>
        <v-divider light></v-divider>
        <v-card-actions class="pa-3">
            <v-btn flat outline color="white" @click='$refs.ctx.show = true' small>{{ message.id }}</v-btn>
            <v-spacer class="pl-2 pr-2"></v-spacer>
            <v-tooltip bottom>
                <span slot="activator">{{ formattedTimestamp }}</span>
                <span>{{ message.timestamp }}</span>
            </v-tooltip>
            <span></span>
            <InfoDialog :id='message.id' tag="Context" ref="ctx"/>
        </v-card-actions>
    </v-card>
</template>

<style scoped>
.user{
    margin-left: auto;
    margin-right: 0
}
</style>

<script lang="ts">
import Vue from 'vue';
import Component from 'vue-class-component';
import { Prop } from 'vue-property-decorator';

import InfoDialog from '@/components/InfoDialog.vue';

import { IMessage } from '@/ApiInterfaces.ts';

@Component({
    name: 'Message',
    components: {
        InfoDialog
    }
})
export default class Message extends Vue {
    $refs!: {
        ctx: InfoDialog
    }

    @Prop({ required: true }) message !: IMessage;

    get formattedTimestamp(){
        const t = this.message.timestamp;
        return (new Date(t)).toLocaleString();
    }
}
</script>
