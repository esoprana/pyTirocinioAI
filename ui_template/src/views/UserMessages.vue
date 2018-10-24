<template>
    <div>
        <v-container>
            <div ref="messageList" style="margin-top: 3rem">
                <v-layout row v-for="message in messages" style="margin-top: 3rem" v-bind:class="{bot: message.bot}">
                    <message v-bind:message="message"></message>
                </v-layout>
            </div>
        </v-container>
        <v-form @submit.prevent="sendMessage">
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

<script lang="js">
import ApiClient from '@/ApiClient.ts'
import message from '@/components/message.vue'

export default {
    data(){
        return {
            messages: [],
            msg: "",
        }
    },
    watch: {
        '$route.params.id': function(id) {
            this.updateMessages(this.$route.params.id, undefined);
        }
    },
    created(){
        this.updateMessages(this.$route.params.id, undefined);
    },
    methods: {
        updateMessages(userId, after) {
            this.$root.waiting = true;

            return ApiClient.Instance.getMessages(userId, after).then(r => {
                this.messages = after === undefined ? r : this.messages.concat(r);
                this.$root.waiting = false;
            }).catch(w => alert(w));
        },
        updateUsers(){
            return ApiClient.Instance
                .getUsers()
                .then(users => this.users)
                .catch(w => alert('Errore:' + w));
        },
        sendMessage(e){
            e.preventDefault();

            this.$root.waiting = true;

            ApiClient.Instance
                .sendMessage(this.$route.params.id, this.msg)
                .then( x => this.updateMessages(this.$route.params.id, this.messages[this.messages.length - 1].timestamp) )
                .then( w => {this.$root.waiting = false; this.msg = '';} )
                .catch( e => alert(e) );
        },
    },
    components: {
        'message': message
    }
}
</script>

