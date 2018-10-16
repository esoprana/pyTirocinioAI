<template>
  <v-layout row justify-center v-if="raw !== undefined">
    <v-dialog v-model="show" max-width="600px">
      <v-card >
      <v-toolbar dark color="primary">
        <v-btn icon dark @click.native="show = false">
        <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>Topic {{id}}</v-toolbar-title>
        <v-spacer></v-spacer>
      </v-toolbar>
      <v-list subheader>
        <v-subheader>General</v-subheader>
        <v-list-tile>
        <v-list-tile-content>
          <v-list-tile-title>Name</v-list-tile-title>
          <v-list-tile-sub-title>{{ raw.name }}</v-list-tile-sub-title>
        </v-list-tile-content>
        </v-list-tile>
      </v-list>
      <v-divider></v-divider>
      <v-list subheader>
        <v-subheader>Rules</v-subheader>
        <v-list-tile v-for="(item, index) in raw.rules">
        <v-list-tile-content>
          <v-list-tile-title>Rule {{ index }}</v-list-tile-title>
          <v-list-tile-sub-title><a-rule :id="item"/></v-list-tile-sub-title>
        </v-list-tile-content>
        </v-list-tile>
      </v-list>
      </v-card>
    </v-dialog>
  </v-layout>
</template>
<script>
import ruleLink from '@/components/ruleLink.vue'

export default {
  name: 'context',
  props: ['id'],
  data () {
    return {
      'show': false,
      'raw': undefined
    }
  },
  watch: {
    'show': function (val, oldVal) {
      if (val === true && this.raw === undefined) {
        const baseUrl = location.protocol + '//' + location.hostname + (location.port ? ':' + location.port : '')

        this.$root.waiting = true

        fetch(baseUrl + '/api/topic/' + this.id).then(x => x.json()).then(x => {
          this.raw = x
          this.$root.waiting = false
        }).catch(e => alert(e))
      }
    }
  },
  components: {
    'a-rule': ruleLink
  }
}
</script>
