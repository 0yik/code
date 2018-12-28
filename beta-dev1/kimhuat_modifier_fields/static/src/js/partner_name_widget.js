odoo.define('kimhuat_modifier_fields.form_name_widget', function (require) {
"use strict";

var Model = require('web.DataModel');
var FieldChar = require('web.form_widgets').FieldChar;

var FieldCharExtend = FieldChar.include({
    render_value: function() {
        var tmp = this._super();
        var self = this
        if(self.name === "name" && self.view.dataset.model=='res.partner') {
            var model = new Model('res.partner');
            var customer = self.build_context().__eval_context.__contexts[1].customer
            var supplier = self.build_context().__eval_context.__contexts[1].supplier
            var dom = []
            if(customer && supplier){
                dom = []
            }else{
                if(customer){dom.push(['customer', '=', true])}
                if(supplier){dom.push(['supplier', '=', true])}
            }
            model.call("search_read", [dom, ['name']], {"context": self.build_context()}).then(function (result) {
                self.$el.easyAutocomplete({data: result,
                getValue: "name",
                list: {
                    match: {
                        enabled: true,
                        method: function(element, phrase) {
                            return (element.startsWith(phrase));
                            }
                        }
                }
                });
            });
        }
		if(self.name === "name" && self.view.dataset.model=='product.product') {
            var model = new Model('product.product');
            model.call("search_read", [[], ["name"]], {"context": self.build_context()}).then(function (result) {
                self.$el.easyAutocomplete({data: result,
                getValue: "name",
                list: {
                    match: {
                        enabled: true,
                        method: function(element, phrase) {
                            return (element.startsWith(phrase));
                            }
                        }
                }
                });
            });
        }
		if(self.name === "name" && self.view.dataset.model=='product.template') {
            var model = new Model('product.template');
            model.call("search_read", [[], ["name"]], {"context": self.build_context()}).then(function (result) {
                self.$el.easyAutocomplete({data: result,
                getValue: "name",
                list: {
                    match: {
                        enabled: true,
                        method: function(element, phrase) {
                            return (element.startsWith(phrase));
                            }
                        }
                }
                });
            });
        }
        return tmp
    },
});
});

odoo.define('sale.view_order_form', function (require) {
"use strict";

var core = require('web.core');
var FormView = require('web.FormView');

var _t = core._t;
var QWeb = core.qweb;

FormView.include({
    load_record: function (record) {
        this._super.apply(this, arguments);
        if (this.model == 'sale.order'){
            if (this.get_fields_values().state != 'draft'){
	        	setTimeout(function() {
                    $(".btn-group ul li a:contains('Quotation')").css({"display":"none"});
                }, 500);
	        }
	        else {
                setTimeout(function() {
                    $(".btn-group ul li a:contains('Sale Order')").css({"display":"none"});
                }, 500);
            }
		}

    },
    });
});
