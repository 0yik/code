/**
 * Created by vieterp on 8/29/17.
 */
odoo.define('barcode_extention.formview', function (require) {
"use strict";
    var core = require('web.core');
    var Model = require('web.Model');
    var Widget = require('web.Widget');
    var Dialog = require('web.Dialog');
    var Session = require('web.session');
    var FormView = require('web.FormView');
    var _t = core._t;
    FormView.include({
        on_processed_onchange : function (result) {
            console.log('onchange');
            this._super.apply(this, arguments);
            var self = this;
            if (this.model === 'stock.pack.operation'){
                if ('check_close' in result.value && result.value.check_close === true){
                    this.save().done(function() {
                        self.do_action({type: "ir.actions.act_window_close"});
                        self.reload();
                    });
                }
                else{
                    if ('next_view_id' in result.value){
                        this.open_pack_operation(result.value.next_view_id[0])
                    }
                }
            }
            if (this.model === 'stock.picking'){
                if('picking_scaned_barcode' in result.value){
                    this.save().done(function() {
                        self.reload().done(function() {
                            var po_model = new Model('stock.pack.operation');
                            var pi_model = new Model('stock.picking');
                            pi_model.call("create_pack_operation_line", [[self.datarecord.id],result.value.picking_scaned_barcode]).done(function(res1) {
                                po_model.call("split_lot", [[res1]]).done(function(res2) {
                                    self.do_action(res2, {
                                        on_close: function() {
                                            self.reload();
                                        }
                                    });
                                });
                            });
                        });
                    });
                }
            }
        },
        open_pack_operation : function (open_id) {
            var self = this;
            var po_model = new Model('stock.pack.operation');
            this.save().done(function() {
                self.reload().done(function() {
                    po_model.call("split_lot", [[open_id]]).done(function(result) {
                        self.do_action(result, {
                            on_close: function() {
                                self.reload();
                            }
                        });
                    });
                });
            });
        }
    });

});