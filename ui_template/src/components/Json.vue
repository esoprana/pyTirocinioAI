<template>
    <v-list-group no-action>
        <v-list-tile slot="activator">
            <v-list-tile-content>
                <v-list-tile-title>{{ title }}</v-list-tile-title>
            </v-list-tile-content>
        </v-list-tile>
        <pre style="width: 100%"><code style="width: 100%">{{ json }}</code></pre>
    </v-list-group>
</template>

<script lang="ts">
import Vue from 'vue';
import Component from 'vue-class-component';
import { Prop } from 'vue-property-decorator';

@Component({
    name: 'Json',
})
export default class Json extends Vue {
    @Prop({ required: true })
    public title !: string;

    @Prop({ required: true })
    public json  !: object;
}
</script>
