<template>
  <v-app toolbar>
    <v-toolbar fixed class="pb-2">
      <v-btn flat icon color="green" @click="newUser = true">
        <v-icon>add</v-icon>
      </v-btn>
      <v-toolbar-title style="margin-right: 1rem">User</v-toolbar-title>
      <v-select
        v-model="select"
        :hint="`${select.id || 'Pick a user'}`"
        :items="users"
        item-text="username"
        item-value="id"
        label="Select"
        persistent-hint
        return-object
        single-line
      ></v-select>
      <v-btn flat icon color="green" @click="updateUsers">
        <v-icon>cached</v-icon>
      </v-btn>
    </v-toolbar>
    <main class="pt-4">
      <v-container id="lc">
        <div ref="messageList" style="margin-top: 3rem">
          <v-layout row v-for="message in messages" style="margin-top: 3rem" v-bind:class="{bot: message.bot}">
            <message v-bind:message="message"></message>
          </v-layout>
        </div>
      </v-container>

        <v-layout row justify-center>
        <v-dialog v-model="waiting" persistent max-width="290">
          <v-card>
          <v-card-title class="headline">Please wait</v-card-title>
          <v-card-text>Wait until the request is complete</v-card-text>
          <v-progress-linear :indeterminate="true" class="ma-0"></v-progress-linear>
          </v-card>
        </v-dialog>
        </v-layout>

        <v-layout row justify-center>
        <v-dialog v-model="newUser" persistent max-width="600">
          <v-card>
          <v-card-title class="headline">Create new user</v-card-title>
          <v-form @submit.prevent="createUser">
            <v-text-field
              v-model="newUsername"
              box
              label="Username"
              clearable
            ></v-text-field>
          </v-form>
          <v-card-actions>
            <v-btn flat icon color="red" @click="newUser = false">
              <v-icon>cancel</v-icon>
            </v-btn>
            <v-spacer>
            </v-spacer>
            <v-btn flat icon color="green" @click="createUser">
              <v-icon>add</v-icon>
            </v-btn>
          </v-card-actions>
          </v-card>
        </v-dialog>
        </v-layout>


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
    </main>
  </v-app>
</template>

<script type="application/typescript">

import ApiClient from '@/ApiClient.ts'
import message from '@/components/message.vue'

export default {
    el: "#app",
    data(){
        return {
            apiClient: undefined,
            users: [],
            messages: [],
            select: {},
            msg: "",
            waiting: false,
            newUser: false,
            newUsername: ""
        }
    },
    created: function () {
        ApiClient.init(process.env.VUE_APP_ROOT_API);
        ApiClient.Instance.getUsers().then(r => this.users = r);
    },
    watch: {
        select(val) {
            this.updateMessages(this.select.id);
        }
    },
    methods: {
        updateMessages(userId, after) {
            return ApiClient.Instance.getMessages(userId, after).then(r => {
                if (after !== undefined) {
                    this.messages = this.messages.concat(r);
                } else {
                    this.messages = r;
                }
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

            this.waiting = true;
            ApiClient.Instance
                .sendMessage(this.select.id, this.msg)
                .then( x => this.updateMessages(this.select.id, this.messages[this.messages.length-1].timestamp) )
                .then( w => {this.waiting = false; this.msg = '';} )
                .catch( e => alert(e) );
        },
        createUser(e){
            e.preventDefault()

            this.waiting = true
            ApiClient.Instance
                .createUser(this.newUsername)
                .then( user => this.updateUsers().then(y => Promise.resolve(user)) )
                .then( user => {
                  this.select.id = user.id;
                  this.select.username= user.username;
                  this.updateMessages(user.id);
                })
                .then( w => {this.waiting = false; this.newUser=false;} )
                .catch(e => alert(e));
        }
    },
    components: {
        'message': message
    }
}
</script>
