import topic from './topic.js'

export default {
	template: `
	<div>
		<a @click="click()">{{ id }}</a>
		<topic :id="id" ref="topic"></topic>
	</div>
	`,
	name: 'a-topic',
	props: ['id'],
	methods: {
		click(){
			this.$refs.topic.show = true;
		}
	},
	beforeCreate: function () {
	  this.$options.components.topic = topic
	}
}
