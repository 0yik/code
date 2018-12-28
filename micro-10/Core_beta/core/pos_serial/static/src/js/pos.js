odoo.define('pos_serial.pos_serial', function (require) {
"use strict";
    
    var Model   = require('web.Model');
    var core    = require('web.core');
    var gui     = require('point_of_sale.gui');
    var pos_model = require('point_of_sale.models');
    var PopupWidget = require('point_of_sale.popups');
    var screens = require('point_of_sale.screens');
    var QWeb = core.qweb;

    var _t = core._t;
    
    screens.OrderWidget.include({
    	render_orderline: function(orderline){
    		var el_node = this._super(orderline);
    		var self = this;
            var oe_del = el_node.querySelector('.oe_del');
            if(oe_del){
            	oe_del.addEventListener('click', (function() {
            		if(!confirm(_t("Are you sure you want to unassign lot/serial number(s) ?"))){
        	    		return
        	    	}
            		var pack_lot_lines = orderline.pack_lot_lines;
            		var len = pack_lot_lines.length;
            		var cids = [];
            		for(var i=0; i<len; i++){
            			var lot_line = pack_lot_lines.models[i];
            			cids.push(lot_line.cid);
            		}
            		for(var j in cids){
            			var lot_model = pack_lot_lines.get({cid: cids[j]});
            			lot_model.remove();
            		}
            		self.renderElement();
            	}.bind(this)));
            }
            return el_node
    	},
    });
    
    screens.PaymentScreenWidget.include({
        renderElement: function(){
            this._super();
            var self =  this;
            this.$('#is_ereciept').click(function(){
                var order = self.pos.get('selectedOrder');
                order.set_print_serial($('#is_ereciept').is(':checked'));
            });
        },
    });
    
    var _super_orderline = pos_model.Orderline.prototype;
    pos_model.Orderline = pos_model.Orderline.extend({
    	export_as_JSON: function() {
            var lines = _super_orderline.export_as_JSON.call(this);
            var self = this;
            var serials = "Serial No(s).: ";
            var back_ser = "";
            var serials_lot = [];
            if(this.pack_lot_lines && this.pack_lot_lines.models){
            	_.each(this.pack_lot_lines.models,function(lot) {
            		if(lot && lot.get('lot_name')){
        				if($.inArray(lot.get('lot_name'), serials_lot) == -1){
        					var count = 0;
        					serials_lot.push(lot.get('lot_name'));
        					_.each(self.pack_lot_lines.models,function(lot1) {
                        		if(lot1 && lot1.get('lot_name')){
                        			if(lot1.get('lot_name') == lot.get('lot_name')){
                        				count ++;
                        			}
                        		}
                            });
        					serials += lot.get('lot_name')+"("+count+")"+", ";
        				}
            		}
                });
            } else { serials = "";}
            this.lots = serials;
            var new_val = {
                serial_nums: back_ser,
            }
            $.extend(lines, new_val);
            return lines;
        },
        is_print_serial: function() {
        	var order = this.pos.get('selectedOrder');
        	return order.get_print_serial();
        },
        export_for_printing: function() {
            var lines = _super_orderline.export_for_printing.call(this);
            var serials = "Serial No(s).: ";
            var serials_lot = [];
            var self = this;
            if(this.pack_lot_lines && this.pack_lot_lines.models){
            	_.each(this.pack_lot_lines.models,function(lot) {
            		if(lot && lot.get('lot_name')){
        				if($.inArray(lot.get('lot_name'), serials_lot) == -1){
        					var count = 0;
        					serials_lot.push(lot.get('lot_name'));
        					_.each(self.pack_lot_lines.models,function(lot1) {
                        		if(lot1 && lot1.get('lot_name')){
                        			if(lot1.get('lot_name') == lot.get('lot_name')){
                        				count ++;
                        			}
                        		}
                            });
        					serials += lot.get('lot_name')+"("+count+")"+", ";
        				}
            		}
                });
            } else { serials = "";}
            var order = self.pos.get('selectedOrder');
            var new_val = {
            	serials: serials ? serials : false,
            	is_print: order.get_print_serial()
            }
            $.extend(lines, new_val);
            return lines;
        },
    });
    
    var _super_order = pos_model.Order.prototype;
    pos_model.Order = pos_model.Order.extend({
    	initialize: function(attributes,options){
    		_super_order.initialize.apply(this, arguments);
    		this.serial_list = [];
    		this.print_serial = true;
    	},
    	set_print_serial: function(val) {
    		this.print_serial = val
    	},
    	get_print_serial: function() {
    		return this.print_serial;
    	},
    	display_lot_popup: function() {
    		var self = this;
            var order_line = this.get_selected_orderline();
            if(order_line){
            	var pack_lot_lines =  order_line.compute_lot_lines();
            	var product_id = order_line.get_product().id;
            	if(this.pos.config.enable_pos_serial){
                	if(product_id){
        	            new Model('stock.production.lot').get_func('search_read')([['product_id', '=', product_id]],
        	            ['name', 'ref', 'product_id', 'create_date','remaining_qty','life_date'])
        	            .then(function(serials){
        	            	self.pos.gui.show_popup('packlotline', {
                                'title': _t('Lot/Serial Number(s) Required'),
                                'pack_lot_lines': pack_lot_lines,
                                'order': self,
                                'serials': serials
                            });
        	            });
        	        }
                } else {
                	self.pos.gui.show_popup('packlotline', {
                        'title': _t('Lot/Serial Number(s) Required'),
                        'pack_lot_lines': pack_lot_lines,
                        'order': self,
                        'serials': []
                    });
                }
            }
        },
    });

	var PackLotLinePopupWidget = PopupWidget.extend({
	    template: 'PackLotLinePopupWidget',
	    events: _.extend({}, PopupWidget.prototype.events, {
	        'click .remove-lot': 'remove_lot',
	        'click .select-lot': 'select_lot',
	        'keydown .popup-input': 'add_lot',
	        'blur .packlot-line-input': 'lose_input_focus',
	        'keyup .popup-search': 'seach_lot',
	    }),

	    show: function(options){
	        this._super(options);
	        this.focus();
	        var self = this;
	        var order = this.pos.get_order();
	        var serials = self.options.serials;
	        _.each(order.get_orderlines(),function(item) {
		        for(var i=0; i < item.pack_lot_lines.length; i++){
		        	var lot_line = item.pack_lot_lines.models[i];
	                if(serials.length != 0){
		                for(var j=0 ; j < serials.length ; j++){
		                	if(serials[j].name == lot_line.get('lot_name')){
		                		serials[j]['remaining_qty'] = serials[j]['remaining_qty'] - 1;
		                	}
		                }
	                }
		        }
            });
	        this.renderElement();
	    },

	    click_confirm: function(){
	        var pack_lot_lines = this.options.pack_lot_lines;
	        this.$('.packlot-line-input').each(function(index, el){
	            var cid = $(el).attr('cid'),
	                lot_name = $(el).val();
	            var pack_line = pack_lot_lines.get({cid: cid});
	            pack_line.set_lot_name(lot_name);
	        });
	        pack_lot_lines.remove_empty_model();
	        pack_lot_lines.set_quantity_by_lot();
	        this.options.order.save_to_db();
	        this.gui.close_popup();
	    },
	    click_cancel: function(){
	    	if(!this.pos.config.enable_pos_serial){
	    		this.gui.close_popup();
	    		return
	    	}
	    	var pack_lot_lines = this.options.pack_lot_lines;
	    	if(pack_lot_lines.length > 0){
	    		if(!confirm(_t("Are you sure you want to unassign lot/serial number(s) ?"))){
		    		return
		    	}
	    	}
	    	var self = this;
	        this.$('.packlot-line-input').each(function(index, el){
	            var cid = $(el).attr('cid'),
	                lot_name = $(el).val();
	            var lot_model = pack_lot_lines.get({cid: cid});
		        lot_model.remove();
		        var serials = self.options.serials;
	            for(var i=0 ; i < serials.length ; i++){
	            	if(serials[i].name == lot_name){
	            		serials[i]['remaining_qty'] = serials[i]['remaining_qty'] + 1;
	            		break
	            	}
	            }
	        });
	        var order = this.pos.get_order();
	        var order_line = order.get_selected_orderline();
	        self.renderElement()
	        this.gui.close_popup();
	    },
	    select_lot: function(ev) {
	    	var $i = $(ev.target);
            var data = $i.attr('data');
            var add_qty = $(ev.currentTarget).find("input").val();
            var order = this.pos.get_order();
            var order_line = order.get_selected_orderline();
            if(data && add_qty){
            	for(var i=0; i< add_qty;i++){
                	this.focus();
        	    	this.$("input[autofocus]").val(data);
        	    	this.add_lot(false,true);
                }
            }
	    },
	    add_lot: function(ev,val) {
	        if ((ev && ev.keyCode === $.ui.keyCode.ENTER)|| val){
	            var pack_lot_lines = this.options.pack_lot_lines,
	                $input = ev ? $(ev.target) : this.$("input[autofocus]"),
	                cid = $input.attr('cid'),
	                lot_name = $input.val();
                var serials = this.options.serials;
                if(serials.length != 0){
                	var flag = true
	                for(var i=0 ; i < serials.length ; i++){
	                	if(serials[i].name == lot_name){
	                		if((serials[i]['remaining_qty'] - 1) < 0){
	                			flag = true;
	                		} else {
	                			if(serials[i].life_date){
	                				if(moment(new moment().add(this.pos.config.product_exp_days, 'd').format('YYYY-MM-DD HH:mm:mm')).format('DD/MM/YYYY') < moment(serials[i].life_date).format('DD/MM/YYYY')){
		                				serials[i]['remaining_qty'] = serials[i]['remaining_qty'] - 1;
			                			flag = false;
		                			}
	                			}else{
	                				serials[i]['remaining_qty'] = serials[i]['remaining_qty'] - 1;
		                			flag = false;
	                			}
	                		}
	                		break
	                	}
	                }
	                if(flag){
	                	$input.css('border','5px solid red');
	                	$input.val('');
	                	return
	                }
                }
	            var lot_model = pack_lot_lines.get({cid: cid});
	            lot_model.set_lot_name(lot_name);  // First set current model then add new one
	            if(!pack_lot_lines.get_empty_model()){
	                var new_lot_model = lot_model.add();
	                this.focus_model = new_lot_model;
	            }
	            pack_lot_lines.set_quantity_by_lot();
	            this.renderElement();
	            this.focus();
	        }
	    },
	    remove_lot: function(ev){
	        var pack_lot_lines = this.options.pack_lot_lines,
	            $input = $(ev.target).prev(),
	            cid = $input.attr('cid'),
	        	lot_name = $input.val();
	        if(lot_name){
	        	var lot_model = pack_lot_lines.get({cid: cid});
		        lot_model.remove();
		        pack_lot_lines.set_quantity_by_lot();
		        var serials = this.options.serials;
	            for(var i=0 ; i < serials.length ; i++){
	            	if(serials[i].name == lot_name){
	            		serials[i]['remaining_qty'] = serials[i]['remaining_qty'] + 1;
	            		break
	            	}
	            }
		        this.renderElement();
	        }
	    },
	    seach_lot: function(ev){
	    	var self = this;
	    	var valThis = $(ev.target).val().toLowerCase();
	    	var sr_list = [];
	        $('.select-lot').each(function(){
	        	var text = $(this).attr('data');
		        (text.indexOf(valThis) == 0) ? sr_list.push(text) : "";
		    });
	        var serials = this.options.serials;
	        var sr = [];
	        var all_sr = [];
            for(var i=0 ; i < serials.length ; i++){
            	if($.inArray(serials[i].name, sr_list) !== -1 && serials[i].remaining_qty > 0){
            		sr.push(serials[i]);
            	}
            	if(serials[i].remaining_qty > 0){
            		all_sr.push(serials[i])
            	}
            }
            if(sr.length != 0 && valThis != ""){
            	this.render_list(sr);
            } else {
            	this.render_list(all_sr);
            }
	    },
	    render_list: function(orders){
	    	if(!orders){
	    		return
	    	}
        	var self = this;
            var contents = $('.serial-list-contents');
            contents.html('');
            var temp = [];
            for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
                var serial    = orders[i];
            	var clientline_html = QWeb.render('listLine',{widget: this, serial:serial});
                var clientline = document.createElement('tbody');
                clientline.innerHTML = clientline_html;
                clientline = clientline.childNodes[1];
                contents.append(clientline);
            }
            $("#lot_list").simplePagination({
				previousButtonClass: "btn btn-danger",
				nextButtonClass: "btn btn-danger",
				previousButtonText: '<i class="fa fa-angle-left fa-lg"></i>',
				nextButtonText: '<i class="fa fa-angle-right fa-lg"></i>',
				perPage:10
			});
        },
	    lose_input_focus: function(ev){
	        var $input = $(ev.target),
	            cid = $input.attr('cid');
	        var lot_model = this.options.pack_lot_lines.get({cid: cid});
	        lot_model.set_lot_name($input.val());
	    },
	    
	    renderElement: function(){
	    	this._super();
	    	var serials = this.options.serials;
	    	var serials_lst = []
	    	if(serials){
	    		for(var i=0 ; i < serials.length ; i++){
	            	if(serials[i].remaining_qty > 0){
	            		serials_lst.push(serials[i])
	            	}
	            }
		    	this.render_list(serials_lst);
	    	}
	    },
	    
	    focus: function(){
	        this.$("input[autofocus]").focus();
	        this.focus_model = false;   // after focus clear focus_model on widget
	    }
	});
	gui.define_popup({name:'packlotline', widget:PackLotLinePopupWidget});
	
});
