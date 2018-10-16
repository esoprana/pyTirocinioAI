<template>
  <v-layout row justify-center v-if="raw !== undefined">
    <v-dialog v-model="show" max-width="600px">
      <v-card >
      <v-toolbar dark color="primary">
        <v-btn icon dark @click.native="show = false">
        <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>Context {{id}}</v-toolbar-title>
        <v-spacer></v-spacer>
      </v-toolbar>
      <v-list subheader>
        <v-subheader>General</v-subheader>
        <v-list-tile>
          <v-list-tile-content>
            <v-list-tile-title>OfUser</v-list-tile-title>
            <v-list-tile-sub-title>{{ raw.ofUser }}</v-list-tile-sub-title>
          </v-list-tile-content>
        </v-list-tile>
        <v-list-tile>
        <v-list-tile-content>
          <v-list-tile-title>Timestamp</v-list-tile-title>
          <v-list-tile-sub-title>{{ raw.timestamp }}</v-list-tile-sub-title>
        </v-list-tile-content>
        </v-list-tile>
      </v-list>
      <v-divider></v-divider>
      <v-list subheader>
        <v-subheader>Message</v-subheader>
        <v-list-tile>
        <v-list-tile-content>
          <v-list-tile-title>Type</v-list-tile-title>
          <v-list-tile-sub-title>{{ raw.message.cls }}</v-list-tile-sub-title>
        </v-list-tile-content>
        </v-list-tile>
        <v-list-tile>
        <v-list-tile-content>
          <v-list-tile-title>Text</v-list-tile-title>
          <v-list-tile-sub-title>{{ raw.message.text }}</v-list-tile-sub-title>
        </v-list-tile-content>
        </v-list-tile>
        <v-list-tile v-if="raw.message.cls == 'BotMessage'">
        <v-list-tile-content>
          <v-list-tile-title>ofRule</v-list-tile-title>
          <v-list-tile-sub-title @click="showRule()"><a>{{ raw.message.fromRule }}</a></v-list-tile-sub-title>
          <rule :id="raw.message.fromRule" ref="ofRule"></rule>
        </v-list-tile-content>
        </v-list-tile>
      <div v-if="raw.message.cls == 'UserMessage'">
        <json title="Intent"       :json="raw.message.intent"     ></json>
        <json title="Sentiment"    :json="raw.message.sentiment"  ></json>
        <json title="Photo"        :json="raw.message.photo"      ></json>
        <json title="Google Topic" :json="raw.message.googleTopic"></json>
      </div>
      </v-list>
      <v-divider></v-divider>
      <v-list v-for="(item, index) in raw.params">
        <v-list subheader>
          <v-subheader>Params {{ index }}</v-subheader>
          <v-list-tile>
          <v-list-tile-content>
            <v-list-tile-title>OfTopic</v-list-tile-title>
            <v-list-tile-sub-title><a-topic :id="item.ofTopic"/></v-list-tile-sub-title>
          </v-list-tile-content>
          </v-list-tile>
          <v-list-tile>
          <v-list-tile-content>
            <v-list-tile-title>StartTime</v-list-tile-title>
            <v-list-tile-sub-title>{{ item.startTime }}</v-list-tile-sub-title>
          </v-list-tile-content>
          </v-list-tile>
          <v-list-tile>
          <v-list-tile-content>
            <v-list-tile-title>Priority</v-list-tile-title>
            <v-list-tile-sub-title>{{ item.priority }}</v-list-tile-sub-title>
          </v-list-tile-content>
          </v-list-tile>

          <json title="Values" :json="item.values"></json>
        </v-list>
      </v-list>
      </v-card>
    </v-dialog>
  </v-layout>
</template>
<script>
import json from '@/components/json.vue'
import rule from '@/components/rule.vue'
import topicLink from '@/components/topicLink.vue'

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

        fetch(baseUrl + '/api/context/' + this.id).then(x => x.json()).then(x => {
          this.raw = x
          this.$root.waiting = false
        }).catch(e => alert(e))
      }
    }
  },
  methods: {
    showRule () {
      this.$refs.ofRule.show = true
    }
  },
  components: {
    json,
    rule,
    'a-topic': topicLink
  }
}
</script>
