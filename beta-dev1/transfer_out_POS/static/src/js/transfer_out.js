odoo.define('transfer_out_POS.transfer_out', function (require) {
"use strict";

    var OptionsPopupWidget = require('pizzahut_modifier_startscreen.pizzahut_modifier_startscreen');
    var Model = require('web.DataModel');

    OptionsPopupWidget.include({
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },

        events: _.extend(OptionsPopupWidget.prototype.events, {
             'click .transfer_out_btn':  'transfer_out_pos',
        }),

        transfer_out_pos: function(){
            console.log("Transfer out category");
            this.pos.category = 'transfer_out';
            var $CreateSalesOrderbutton = $('.CreateSalesOrderbutton');
            if(this.pos.category != 'dive_in' && $CreateSalesOrderbutton){
                $CreateSalesOrderbutton.removeClass('oe_hidden');
            }
            this.prepare_order();
            this.pos.add_new_order();
            this.gui.show_screen('products');
            this.get_current_category();
        },
        prepare_order : function () {
            var current_pos = this.pos;
            var floors = current_pos.floors;
            current_pos.floors_for_temp = floors;
            current_pos.floors = [];
            current_pos.floors_by_id = {};
            current_pos.popup_option = 'Transfer Out'
            for (var i = 0; i < floors.length; i++) {
                floors[i].tables = [];
                current_pos.floors_by_id[floors[i].id] = floors[i];
            }
            current_pos.config.iface_floorplan = 0
            current_pos.floors_for_temp = current_pos.floors_for_temp.sort(function(a,b){ return a.sequence - b.sequence; });

            for (var i = current_pos.floors_for_temp.length - 1; i >= 0; i--) {
                var floor = current_pos.floors_for_temp[i];
                for (var j = floor.tables.length - 1; j >= 0; j--) {
                    var table_name = floor.tables[j]['name']+' ('+floor['name']+')';
                    tables.push([floor.tables[j]['id'],  table_name]);
                }
            }
        },
        get_current_category: function () {
            var self = this.pos;
            
            var def = new $.Deferred();
            var fields = _.find(this.pos.models,function(model){
                return model.model === 'product.product';
            }).fields;
            var model = new Model('pos.order.category');
            self.db.product_by_id = {};
            self.db.product_by_category_id = {};
            model.call("get_current_category", ['Transfer Out',fields,this.pos.pricelist.id]).then(function (result) {
                console.log('>>>>>Transfer Out>>>>>>>>>>',result)
                if (result != 0){
                    if (result == 1){
                        self.gui.screen_instances['products'].product_list_widget.product_list = [];
                        self.gui.screen_instances['products'].product_list_widget.renderElement();
                        self.db.add_products([]);
                    }else{
                        self.db.add_products(result);
                        self.gui.screen_instances['products'].product_list_widget.product_list = result;
                        self.gui.screen_instances['products'].product_list_widget.renderElement();
                    }
                }else{
                    alert("Wrong Product Order Category Defined")
                }
            });
        },
    });

});