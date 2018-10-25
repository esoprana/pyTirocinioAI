<template>
    <Loading v-if="!messages.length"/>
    <div v-else>
        <v-container>
            <div ref="messageList" style="margin-top: 3rem">
                <v-layout row v-for="message in messages" style="margin-top: 3rem" v-bind:class="{bot: message.bot}">
                    <Message :message="message"/>
                </v-layout>
            </div>
        </v-container>
        <Loading v-if="waiting"/>
        <v-form @submit.prevent="sendMessage" v-else>
            <v-container>
                <v-layout row wrap>
                    <v-flex xs12>
                        <v-text-field
                            v-model="msg"
                            append-outer-icon="send"
                            box
                            label="Message"
                            clearable
                            @click:append-outer="sendMessage"
                        ></v-text-field>
                    </v-flex>
                </v-layout>
            </v-container>
        </v-form>
    </div>
</template>

<script lang="ts">


import Vue from 'vue';
import Component from 'vue-class-component';
import { Prop, Watch } from 'vue-property-decorator';

import Loading from '@/components/Loading.vue';

import InfoLink from '@/components/InfoLink.vue';
import Message from '@/components/Message.vue';

import ApiClient from '@/ApiClient.ts';

import { IMessage, IResponse } from '@/ApiInterfaces.ts';

@Component({
    name: 'TopicView',
    components: {
        Message,
        Loading,
    },
})
export default class TopicView extends Vue {

    @Prop({ required: true })
    public id !: string;

    private messages: IMessage[] = [];
    private msg: string = '';
    private waiting: boolean = false;

    private updateMessages(userId: string, after: string|undefined): Promise<void> {
        this.waiting = true;

        return ApiClient.Instance.getMessages(userId, after).then((r: IMessage[]) => {
            this.messages = after === undefined ? r : this.messages.concat(r);
            this.waiting = false;
        }).catch((w: any) => alert(w));
    }

    private sendMessage(ev: any): void {
        ev.preventDefault();

        this.waiting = true;

        ApiClient.Instance
            .sendMessage(this.id, this.msg)
            .then( (x: IResponse) => this.updateMessages(this.id, this.messages[this.messages.length - 1].timestamp) )
            .then( (w: void) => {
                this.waiting = false;
                this.msg = '';
            })
            .catch( (e: any) => alert(e) );
    }

    @Watch('id')
    private updateId(newId: string): void {
        this.updateMessages(this.id, undefined);
    }

    private created(): void {
        this.updateMessages(this.id, undefined);
    }
}
</script>

