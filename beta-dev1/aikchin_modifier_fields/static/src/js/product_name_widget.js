odoo.define('aikchin_modifier_fields.product_name_widget', function (require) {
"use strict";

var Model = require('web.DataModel');
var FieldChar = require('web.form_widgets').FieldChar;

var FieldCharExtend = FieldChar.include({
    render_value: function() {
        var tmp = this._super();
        var self = this
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
