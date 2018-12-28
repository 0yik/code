odoo.define('pos_note_category_onproduct', function (require) {
	var PopupWidget = require('point_of_sale.popups');
	var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var Model = require('web.Model');
	var core = require('web.core');
	var _t = core._t;
	var _super_orderline = models.Orderline.prototype;
	var NewOrderlineNoteButton = require('pos_note_category_pos_restaurant.notes');
	models.load_fields('product.product', 'note_ids');
		
	models.Orderline = models.Orderline.extend({
	    initialize: function(attr, options) {
	        _super_orderline.initialize.call(this,attr,options);
	        this.displaynote = this.displaynote || "";
	    },
	    set_displaynote: function(displaynote){
	        this.displaynote = displaynote;
	        this.trigger('change',this);
	    },
	    get_displaynote: function(displaynote){
	        return this.displaynote.slice(0, 3);
	    },
	    _show_popup:function (line,attribute,self) {
	        if (line && $('.order-container .order-empty').length == 0) {
	            if(!line.get_attribute() || !line.get_attribute().length){
	                line.set_attribute(attribute);
	            }
	            this.pos.gui.show_popup('textarea',{
	                title: _t('Add Note'),
	                value:  line.get_note(),
	                attribute: line.get_attribute(),
	                confirm: function(note) {
	                    var attribute = [];
	                    var displaynote = []
	                    $('.pos_note_category_button').each(function () {
	                       if($(this).hasClass('active')){
	                    	   if (displaynote.length <= 0){
	                    		   displaynote.push('-' + $(this).text().trim());
	                    	   }
	                    	   else{
	                    		   displaynote.push('\n-' + $(this).text().trim());
	                    	   }
	                           attribute.push({
	                               'name':$(this).text().trim(),
	                               'isToggle':true,
	                           })
	                       }else{
	                           attribute.push({
	                               'name':$(this).text().trim(),
	                               'isToggle':false,
	                           })
	                       }
	                    });
	                    if (note === undefined || note == null || note.length <= 0){
	                    	displaynote = displaynote;
	                    }
	                    else{
	                    	displaynote.push('-' +note);
	                    }
	                    line.set_attribute(attribute);
	                    line.set_note(note);
	                    line.set_displaynote(displaynote);
	                },
	            });
	        }else{
	            var warning = "Please select the menu first!";
	            this.pos.gui.show_popup('error', {
	                title: _t('Warning'),
	                body: _t(warning),
	            });
	        }
	    },
	});
	var NewOrderlineNoteButton= screens.ActionButtonWidget.extend({
	    template: 'NewOrderlineNoteButton1',
	    button_click: function(){
	    	console.log("button clieck ctegory");
	        var self = this;
	        var line = this.pos.get_order().get_selected_orderline();
	        var POS_NOTE_CATEGORY = new Model('pos.note.category');
	        if (line && line.product.pos_categ_id && (!-line.get_attribute() || !line.get_attribute().length)){
	            var category_id = line.product.pos_categ_id[0];
	            var array = JSON.parse("[" + line.product.note_ids + "]");
	            POS_NOTE_CATEGORY.query(['id','name','product_id']).filter([['id','in',array]]).limit(15).all().then(function (result){
	                var attribute = [];
	                var is_note = false;
	                result.forEach(function (item) {
	                	is_note = true;
	                   attribute.push({
	                       'name':item.name,
	                       'isToggle':false
	                   })
	                });
	                if (is_note){
                    	line._show_popup(line,attribute,self);
                    }
	            });
	            POS_NOTE_CATEGORY.query(['name','pos_category_id']).filter([['pos_category_id','=',parseInt(category_id)]]).limit(15).all().then(function (result){
                    var attribute = [];
                    var is_note = false;
                    result.forEach(function (item) {
                    	is_note = true;
                       attribute.push({
                           'name':item.name,
                           'isToggle':false
                       })
                    });
                    if (is_note){
                    	line._show_popup(line,attribute,self);
                    }
                    else{
                    	line._show_popup(line,[],self);
                    }
                	});
            }else if(line && line.product.note_ids)
        		{
        			var array = JSON.parse("[" + line.product.note_ids + "]");
        			POS_NOTE_CATEGORY.query(['id','name','product_id']).filter([['id','in',array]]).limit(15).all().then(function (result){
        				var attribute = [];
        				var is_note = false;
                        result.forEach(function (item) {
                        	is_note = true;
                           attribute.push({
                               'name':item.name,
                               'isToggle':false
                           })
                        });
                        if (is_note){
                        	line._show_popup(line,attribute,self);
                        }
                        else{
                        	line._show_popup(line,[],self);
                        }
        			});
        			
        		}
            else{
            	line._show_popup(line,[],self);
            }
        },
	});

	screens.define_action_button({
	    'name': 'Orderline_Note_Inherit',
	    'widget': NewOrderlineNoteButton,
	});
	/*var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        add_product: function(product, options){
            var res = _super_order.add_product.call(this,product, options);
            var line = this.get_last_orderline();
            var POS_NOTE_CATEGORY = new Model('pos.note.category');
            if (line && line.product.pos_categ_id && (!line.get_attribute() || !line.get_attribute().length)){
                var category_id = line.product.pos_categ_id[0];
                var array = JSON.parse("[" + product.note_ids + "]");
                POS_NOTE_CATEGORY.query(['id','name','product_id']).filter([['id','in',array]]).limit(15).all().then(function (result){
                	var attribute = [];
                	var is_note = false;
                	result.forEach(function (item) {
                    	is_note = true;
                       attribute.push({
                           'name':item.name,
                           'isToggle':false
                       })
                    });
                    if (is_note){
                    	line._show_popup(line,attribute,self);
                    }
                });
                POS_NOTE_CATEGORY.query(['name','pos_category_id']).filter([['pos_category_id','=',parseInt(category_id)]]).limit(15).all().then(function (result){
                    var attribute = [];
                    var is_note = false;
                    result.forEach(function (item) {
                    	is_note = true;
                       attribute.push({
                           'name':item.name,
                           'isToggle':false
                       })
                    });
                    if (is_note){
                    	line._show_popup(line,attribute,self);
                    }
                	});
            }else{
            	if(line && line.product.note_ids)
        		{
        			var array = JSON.parse("[" + product.note_ids + "]");
        			POS_NOTE_CATEGORY.query(['id','name','product_id']).filter([['id','in',array]]).limit(15).all().then(function (result){
        				var attribute = [];
        				var is_note = false;
                        result.forEach(function (item) {
                        	is_note = true;
                           attribute.push({
                               'name':item.name,
                               'isToggle':false
                           })
                        });
                        if (is_note){
                        	line._show_popup(line,attribute,self);
                        }
        			});
        			
        		}
            }
        },
    });*/
});