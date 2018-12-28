odoo.define('arkco_modifier_purchase_return_line.edit_button', function (require) {
"use strict";

var core = require('web.core');
var FormView = require('web.FormView');

var _t = core._t;
var QWeb = core.qweb;

FormView.include({
  load_record: function(record) {
    this._super.apply(this, arguments);
    if (this.model=='purchase.order'){
      if (this.get_fields_values().state=='pending'){
            this.$buttons.find('.o_form_button_edit').css({"display":"none"});
          }
          else{
            this.$buttons.find('.o_form_button_edit').css({"display":""});
          }
    }
        
  }
  
});

});