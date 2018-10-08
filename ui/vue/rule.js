import json from './json.js'
import topicLink from './topicLink.js'

export default {
	template: `
	<v-layout row justify-center v-if="raw !== undefined">
		<v-dialog v-model="show" max-width="600px">
		  <v-card >
			<v-toolbar dark color="primary">
			  <v-btn icon dark @click.native="show = false">
				<v-icon>close</v-icon>
			  </v-btn>
			  <v-toolbar-title>Rule {{id}}</v-toolbar-title>
			  <v-spacer></v-spacer>
			</v-toolbar>
			<v-list subheader>
			  <v-subheader>General</v-subheader>
			  <v-list-tile>
				<v-list-tile-content>
				  <v-list-tile-title>Score</v-list-tile-title>
				  <v-list-tile-sub-title>{{ raw.score }}</v-list-tile-sub-title>
				</v-list-tile-content>
			  </v-list-tile>
			</v-list>
			<v-divider></v-divider>
			<v-list subheader>
			  <v-subheader>Condition</v-subheader>
				<json title="OnMsg"    :json="raw.condition.onMsg"    v-if="raw.condition.onMsg !== null"></json>
				<json title="Py"       :json="raw.condition.py"       ></json>
			</v-list>
			<v-divider></v-divider>
			<v-list subheader v-for="(item, index) in raw.condition.onParams">
			  <v-subheader>Condition.OnParams {{ index }} </v-subheader>
			  <v-list-tile>
				<v-list-tile-content>
				  <v-list-tile-title>Topic used</v-list-tile-title>
				  <v-list-tile-sub-title><a-topic :id="item.__type__"/></v-list-tile-sub-title>
				</v-list-tile-content>
			  </v-list-tile>
				<json title="Other conditions" :json="item" ></json>
			</v-list>

			<v-divider></v-divider>
			<v-list subheader>
			  <v-subheader>Action</v-subheader>
				<v-list-tile>
					<v-list-tile-content>
						<v-list-tile-title>ImmediatlyNext</v-list-tile-title>
						<v-list-tile-sub-title>{{ raw.action.immediatlyNext }}</v-list-tile-sub-title>
					</v-list-tile-content>
				</v-list-tile>
				<v-list-tile>
					<v-list-tile-content>
						<v-list-tile-title>IsQuestion</v-list-tile-title>
						<v-list-tile-sub-title>{{ raw.action.isQuestion }}</v-list-tile-sub-title>
					</v-list-tile-content>
				</v-list-tile>
				<json title="Operations" :json="raw.action.operations"></json>
				<json title="Text"       :json="raw.action.text"      ></json>
			</v-list>
			<v-divider></v-divider>
		  </v-card>
		</v-dialog>
	  </v-layout>
	`,
	name: 'context',
	props: ['id'],
	data(){
		return {
			'show': false,
			'raw': undefined,
		}
	},
	watch: {
		'show': function(val, oldVal) {
			if (val === true && this.raw === undefined) {
				const baseUrl = location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '');

				this.$root.waiting = true;

				fetch(baseUrl + '/api/rule/' + this.id).then(x => x.json()).then(x => {
					this.raw = x;
					this.$root.waiting = false;
				}).catch(e => alert(e))
			}
		},
	},
	components: {
		'json': json,
	},
	beforeCreate: function () {
	  this.$options.components['a-topic'] = topicLink
	}
}
