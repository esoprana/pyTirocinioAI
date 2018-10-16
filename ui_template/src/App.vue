<template>
  <v-app toolbar>
    <v-toolbar fixed class="pb-2">
      <v-btn flat icon color="green" @click="newUser = true">
        <v-icon>add</v-icon>
      </v-btn>
      <v-toolbar-title style="margin-right: 1rem">User</v-toolbar-title>
      <v-select
        v-model="select"
        :hint="`${select.id}`"
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

<script>
import message from '@/components/message.vue'

const baseUrl = location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '');

export default {
  el: "#app",
  data(){
    return {
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
    this.updateUsers();
  },
  watch: {
    select(val) {
      this.updateMessages(val.id)
    }
  },
  methods: {
    updateMessages(userId, after) {
      var url = baseUrl + '/api/message/user/' + userId
      if (after != undefined) {
        url+='?after='+encodeURIComponent(after)
      }

      return fetch(url).then(x => x.json()).then(x => {
        if (after != undefined) {
          this.messages = app.messages.concat(x.reverse())
        } else {
          this.messages = x.reverse()
        }
      }).catch(w => alert('Errore:' + w))
    },
    updateUsers(){
      return fetch(baseUrl + '/api/user').then(x => x.json()).then(x => {
        this.users = x
      }).catch(w => alert('Errore:' + w))
    },
    sendMessage(e){
      e.preventDefault()

      this.waiting = true
      return fetch(baseUrl + '/api/message/' + this.select.id +'/000000000000000000000001', {
        method: 'PUT',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          'text': this.msg
        })
      }).then(
        x => x.json()
      ).then(
        x => updateMessages(this.select.id, this.messages[this.messages.length-1].timestamp)
      ).then(
        w => {this.waiting = false; this.msg = '';}
      ).catch(e => alert(e))
    },
    createUser(e){
      e.preventDefault()

      this.waiting = true
      fetch(baseUrl + '/api/user', {
        method: 'PUT',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          'username': this.newUsername
        })
      }).then(
        user => user.json()
      ).then(
        user => this.updateUsers().then(y => Promise.resolve(user))
      ).then(
        user => updateMessages(user.id)
      ).then(
        w => {this.waiting = false; this.newUser=false}
      ).catch(e => alert(e))
    }
  },
  components: {
    'message': message
  }
}
</script>
