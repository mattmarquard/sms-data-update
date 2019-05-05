var Shelter = Backbone.Model.extend({
    defaults: {
	_id: 1,
	name: 'generic shelter',
	population: 0,
	address: 'generic shelter address',
    }

    //validate: function(attributes) {
    //    if ( attributes._id < 1 ) {
    //        return 'ID must be greater than zero'
    //    }
    //    if ( !attributes.name) {
    //        return 'every shelter must have a name';
    //    }
    //},
    //work: function() {
    //    return this.get('name') + 'is working.';
    //}
});

var Hospital = Backbone.Model.extend({
    defaults: {
	_id: 1,
	name: 'generic hospital',
	population: 0,
	address: 'generic hospital address',
    }

    //validate: function(attributes) {
    //    if ( attributes._id < 1 ) {
    //        return 'ID must be greater than zero'
    //    }
    //    if ( !attributes.name) {
    //        return 'every shelter must have a name';
    //    }
    //},
    //work: function() {
    //    return this.get('name') + 'is working.';
    //}
});

var ShelterView = Backbone.View.extend({
   tagName: 'li',

   initialize: function(){
     this.render();
   },

   render: function(){
     this.$el.html( this.model.get('name') + ' (' + this.model.get('population') + ') - ' + this.model.get('address') );
  }
});

var HospitalView = Backbone.View.extend({
   tagName: 'li',

   initialize: function(){
     this.render();
   },

   render: function(){
     this.$el.html( this.model.get('name') + ' (' + this.model.get('population') + ') - ' + this.model.get('address') );
  }
});
