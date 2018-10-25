<template>
    <v-app dark>

        <v-navigation-drawer v-model="showUsers" app temporary right>
            <v-list>
                <v-list-tile>
                    <v-list-tile-content>
                        <v-list-tile-title>Users</v-list-tile-title>
                    </v-list-tile-content>
                </v-list-tile>

                <v-btn flat icon color="green" @click="newUser = true">
                    <v-icon>add</v-icon>
                </v-btn>
                <v-btn flat icon color="green" @click="updateUsers">
                    <v-icon>cached</v-icon>
                </v-btn>

                <v-divider></v-divider>

                <v-list three-line>
                    <v-radio-group :mandatory="true" v-model="select.id">
                        <template v-for="item in users">
                            <v-list-tile @click="select = item">
                                <v-list-tile-action>
                                    <v-radio :value="item.id" :key="item.id"></v-radio>
                                </v-list-tile-action>
                                <v-list-tile-content>
                                    <v-list-tile-title>{{ item.username }}</v-list-tile-title>
                                    <v-list-tile-sub-title>{{ item.id }}</v-list-tile-sub-title>
                                </v-list-tile-content>
                            </v-list-tile>
                        </template>
                    </v-radio-group>
                </v-list>

            </v-list>
        </v-navigation-drawer>

        <v-toolbar app fixed extended extension-height="4">
            <v-spacer></v-spacer>
            <div v-if="select.id !== undefined && $route.name !== 'userMessages'">
                <span>Messages</span>
                <v-btn flat icon @click.stop="$router.push({name: 'userMessages', params: { id: select.id }})" color="white">
                    <v-icon>mail_outline</v-icon>
                </v-btn>
            </div>
            <span>{{ select.username }}</span>
            <v-btn flat icon @click.stop="showUsers = !showUsers" color="white">
                <v-icon>person</v-icon>
            </v-btn>
            <v-progress-linear
                slot="extension"
                :indeterminate="true"
                style="height: 4px; width: 100vw"
                class="ma-0"
                v-if="waiting"
            >Progress?</v-progress-linear>
        </v-toolbar>

        <v-content>
            <v-layout row justify-center>
                <v-dialog v-model="newUser" max-width="600">
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
                            <v-spacer></v-spacer>
                            <v-btn flat icon color="green" @click="createUser">
                                <v-icon>add</v-icon>
                            </v-btn>
                        </v-card-actions>
                    </v-card>
                </v-dialog>
            </v-layout>

            <router-view :key="$route.fullPath"/>
        </v-content>
    </v-app>
</template>

<script lang="js">
import ApiClient from '@/ApiClient.ts'
import message from '@/components/message.vue'

export default {
    el: "#app",
    data(){
        return {
            users: [],
            select: {
                id: undefined,
                username: undefined
            },
            waiting: false,
            newUser: false,
            newUsername: "",
            showUsers: false,
        }
    },
    created: function () {
        ApiClient.init(process.env.VUE_APP_ROOT_API);
        ApiClient.Instance.getUsers().then(r => {
            this.users = r;

            if (this.$route.name === 'userMessages') {
                this.select = this.users.find((el) => el.id === this.$route.params.id);
            }
        });
    },
    watch: {
        select(newVal){
            this.$router.push({ path: `/userMessages/${newVal.id}` });
        }
    },
    methods: {
        updateUsers(){
            return ApiClient.Instance
                .getUsers()
                .then(users => this.users = users)
                .catch(w => alert('Errore:' + w));
        },
        createUser(e){
            e.preventDefault()

            this.$root.waiting = true;
            ApiClient.Instance
                .createUser(this.newUsername)
                .then( user => this.updateUsers().then(y => Promise.resolve(user)) )
                .then( user => {
                    this.select.id = user.id;
                    this.select.username = user.username;
                    this.$router.push({ name: 'userMessages', params: { id: user.id } });
                })
                .then( w => {this.$root.waiting = false; this.newUser=false;} )
                .catch(e => alert(e));
        }
    },
    components: {
        'message': message
    }
}
</script>
<style>
.v-toolbar__extension{
    padding-left: 0;
    padding-right: 0;
}
</style>
