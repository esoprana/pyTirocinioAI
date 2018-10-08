export default {
	template: `
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
				  <v-list-tile-sub-title>{{ raw.message.fromRule }}</v-list-tile-sub-title>
				</v-list-tile-content>
			  </v-list-tile>

				<v-list-group no-action  v-if="raw.message.cls == 'UserMessage'">
				  <v-list-tile slot="activator">
					<v-list-tile-content>
					  <v-list-tile-title>Intent</v-list-tile-title>
					</v-list-tile-content>
				  </v-list-tile>
					<pre style="width: 100%"><code style="width: 100%">{{ raw.message.intent }}</code></pre>
				</v-list-group>
				<v-list-group no-action  v-if="raw.message.cls == 'UserMessage'">
				  <v-list-tile slot="activator">
					<v-list-tile-content>
					  <v-list-tile-title>Sentiment</v-list-tile-title>
					</v-list-tile-content>
				  </v-list-tile>
					<pre style="width: 100%"><code style="width: 100%">{{ raw.message.sentiment }}</code></pre>
				</v-list-group>
				<v-list-group no-action  v-if="raw.message.cls == 'UserMessage'">
				  <v-list-tile slot="activator">
					<v-list-tile-content>
					  <v-list-tile-title>Photo</v-list-tile-title>
					</v-list-tile-content>
				  </v-list-tile>
					<pre style="width: 100%"><code style="width: 100%">{{ raw.message.photo }}</code></pre>
				</v-list-group>
				<v-list-group no-action  v-if="raw.message.cls == 'UserMessage'">
				  <v-list-tile slot="activator">
					<v-list-tile-content>
					  <v-list-tile-title>Google Topic</v-list-tile-title>
					</v-list-tile-content>
				  </v-list-tile>
					<pre style="width: 100%"><code style="width: 100%">{{ raw.message.googleTopic }}</code></pre>
				</v-list-group>
			</v-list>
			<v-divider></v-divider>
			<v-list v-for="(item, index) in raw.params">
				<v-list subheader>
				  <v-subheader>Params {{index }}</v-subheader>
				  <v-list-tile>
					<v-list-tile-content>
					  <v-list-tile-title>OfTopic</v-list-tile-title>
					  <v-list-tile-sub-title>{{ item.ofTopic }}</v-list-tile-sub-title>
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

					<v-list-group no-action>
					  <v-list-tile slot="activator">
						<v-list-tile-content>
						  <v-list-tile-title>Values</v-list-tile-title>
						</v-list-tile-content>
					  </v-list-tile>
						<pre style="width: 100%"><code style="width: 100%">{{ item.values }}</code></pre>
					</v-list-group>
				</v-list>
				<v-divider inset></v-divider>
			</v-list>
		  </v-card>
		</v-dialog>
	  </v-layout>


	  <v-layout row justify-center>
		<v-dialog v-model="waiting" persistent max-width="290">
		  <v-card>
			<v-card-title class="headline">Please wait</v-card-title>
			<v-card-text>Wait until the request is complete</v-card-text>
			<v-progress-linear :indeterminate="true"></v-progress-linear>
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
			'waiting': false,
		}
	},
	watch: {
		'show': function(val, oldVal) {
			if (val === true && this.raw === undefined) {
				const baseUrl = location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '');

				this.$root.waiting = true;

				fetch(baseUrl + '/api/context/' + this.id).then(x => x.json()).then(x => {
					this.raw = x;
					this.$root.waiting = false;
				}).catch(e => alert(e))
			}
		},
	},
}
