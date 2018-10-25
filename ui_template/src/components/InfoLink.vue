<template>
    <div>
        <a @click="$refs.dialog.show = true">{{ id }}</a>
        <InfoDialog :tag="tag" :id="id" ref="dialog"/>
    </div>
</template>

<script lang="ts">
import Vue from 'vue';
import Component from 'vue-class-component';
import { Prop } from 'vue-property-decorator';

import InfoDialog from '@/components/InfoDialog.vue'

@Component({
    name: 'InfoLink',
})
export default class InfoLink extends Vue {
    @Prop({ required: true }) id  !: string
    @Prop({ required: true }) tag !: string

    beforeCreate() {
        this.$options!.components!.InfoDialog = InfoDialog;
    }
}
</script>
