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

<script>
export default {
    name: 'json',
    props: ['title', 'json']
}
</script>
