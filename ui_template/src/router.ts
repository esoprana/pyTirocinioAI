import Vue from 'vue';
import Router from 'vue-router';

import Topic from '@/views/Topic.vue'
import Rule from '@/views/Rule.vue'
import Context from '@/views/Context.vue';

import UserMessages from '@/views/UserMessages.vue';

Vue.use(Router);

export default new Router({
    mode: 'history',
    base: process.env.BASE_URL + 'index.html/',
    routes: [
        {
            path: '/',
            name: 'home'
        },
        {
            path: '/context/:id',
            name: 'context',
            component: Context,
            props: true,
        },
        {
            path: '/rule/:id',
            name: 'rule',
            component: Rule,
            props: true,
        },
        {
            path: '/topic/:id',
            name: 'topic',
            component: Topic,
            props: true,
        },
        {
            path: '/userMessages/:id',
            name: 'userMessages',
            component: UserMessages,
            props: true,
        },
    ],
});
