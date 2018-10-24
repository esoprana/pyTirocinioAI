<template>
    <div>
        <v-layout row justify-center>
            <v-progress-linear :indeterminate="true" class="mt-0 pt-0"></v-progress-linear>
        </v-layout>
        <v-layout row justify-center class="pb-3">
            <span>Please wait until the request is completed</span>
        </v-layout>
    </div>
</template>

<script lang="ts">
import Vue from 'vue';
import Component from 'vue-class-component';
import { Prop } from 'vue-property-decorator';

@Component({
    name: 'Loading',
})
export default class Message extends Vue {}
</script>
