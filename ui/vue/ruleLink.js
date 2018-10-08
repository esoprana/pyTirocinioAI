import rule from './rule.js'

export default {
	template: `
	<div>
		<a @click="click()">{{ id }}</a>
		<rule :id="id" ref="rule"></rule>
	</div>
	`,
	name: 'a-rule',
	props: ['id'],
	methods: {
		click(){
			this.$refs.rule.show = true;
		}
	},
	beforeCreate: function () {
	  this.$options.components.rule = rule
	}
}
