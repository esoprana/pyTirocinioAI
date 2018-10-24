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
            <v-btn flat outline color="white" @click='showRaw()' small>{{ message.id }}</v-btn>&nbsp;&nbsp;<v-spacer></v-spacer>&nbsp;&nbsp;{{ message.timestamp }}
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

import InfoDialog from '@/components/InfoDialog.vue'

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

    @Prop({ required: true }) message !: string;

    showRaw () {
        this.$refs.ctx.show = true;
    }
}
</script>
