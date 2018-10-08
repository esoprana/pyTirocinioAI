import context from './context.js'

export default {
	template: `
		<v-card :color="message.bot?'purple':'green'" class="white--text" v-bind:class="{user: !message.bot}" >
		  <v-layout row>
			<v-flex xs10>
			  <v-card-title primary-title>
				<div>
				  <div class="headline">{{ message.text }}</div>
				</div>
			  </v-card-title>
			</v-flex>
			<v-flex xs2 style="text-align: right">
				<v-card-text >
					{{ message.bot?'Bot':'User' }}
				</v-card-text>
			</v-flex>
		  </v-layout>
          <v-card-actions>
            <v-spacer></v-spacer>
			<v-btn flat outline color="white" @click='showRaw()'>Show detailed info</v-btn>
          </v-card-actions>
		  <v-divider light></v-divider>
		  <v-card-actions class="pa-3">
			<span @click='showRaw()'>{{ message.id }}</span>&nbsp;&nbsp;<v-spacer></v-spacer>&nbsp;&nbsp;{{ message.timestamp }}
			<context :id='message.id' ref="ctx"></context>
		  </v-card-actions>
		</v-card>
	`,
	name: 'message',
	props: ['message'],
	data(){
		return {
			'raw': {
			}
		}
	},
	methods: {
		showRaw(){
			this.$refs.ctx.show = true
		}
	},
	components: {
		'context': context
	}
}
