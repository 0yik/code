odoo.define('pos_note_category_pos_restaurant.notes', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var Model = require('web.Model');
var gui = require('point_of_sale.gui');
    var multiprint = require('pos_restaurant.multiprint');
var notes = require('pos_restaurant.notes');

var QWeb = core.qweb;
var _t   = core._t;

    // var models = require('point_of_sale.models');
var _super_order = models.Order.prototype;


var _super_orderline = models.Orderline.prototype;

models.Orderline = models.Orderline.extend({
    initialize: function(attr, options) {
        _super_orderline.initialize.call(this,attr,options);
        this.note = this.note || "";
        this.attribute = this.attribute || [];
    },
    set_note: function(note){
        this.note = note;
        this.trigger('change',this);
    },
    get_note: function(note){
        return this.note;
    },

    set_attribute: function (attribute) {
        this.attribute = attribute;
    },
    get_attribute_string:function () {
        var result = '';
        this.attribute.forEach(function (item) {
            if(item.isToggle){
                result += (item.name+', ');
            }
        });
        if(this.note){
            return result;
        }
        else{
            return result.substring(0, result.length - 2);
        }
    },
    get_attribute: function(){
        return this.attribute;
    },

    can_be_merged_with: function(orderline) {
        if (orderline.get_note() !== this.get_note()) {
            return false;
        } else {
            return _super_orderline.can_be_merged_with.apply(this,arguments);
        }
    },
    clone: function(){
        var orderline = _super_orderline.clone.call(this);
        orderline.note = this.note;
        return orderline;
    },
    export_as_JSON: function(){
        var json = _super_orderline.export_as_JSON.call(this);
        json.note = this.note;
        json.attribute = this.get_attribute()
        return json;
    },
    init_from_JSON: function(json){
        _super_orderline.init_from_JSON.apply(this,arguments);
        this.note = json.note;
        this.attribute = json.attribute
    },
});


var NewOrderlineNoteButton = screens.ActionButtonWidget.extend({
    template: 'NewOrderlineNoteButton',
    button_click: function(){
        var self = this;
        var line = this.pos.get_order().get_selected_orderline();
        var POS_NOTE_CATEGORY = new Model('pos.note.category');
        if (line && line.product.pos_categ_id && (!line.get_attribute() || !line.get_attribute().length)){
            var category_id = line.product.pos_categ_id[0];
            POS_NOTE_CATEGORY.query(['name','pos_category_id']).filter([['pos_category_id','=',parseInt(category_id)]]).limit(15).all().then(function (result){
                var attribute = [];
                result.forEach(function (item) {
                   attribute.push({
                       'name':item.name,
                       'isToggle':false
                   })
                });
                self._show_popup(line,attribute,self);
            });
        }else{
            self._show_popup(line,[],self);
        }
    },
    _show_popup:function (line,attribute,self) {
        if (line && $('.order-container .order-empty').length == 0) {
            if(!line.get_attribute() || !line.get_attribute().length){
                line.set_attribute(attribute);
            }
            self.gui.show_popup('textarea',{
                title: _t('Add Note'),
                value:  line.get_note(),
                attribute: line.get_attribute(),
                confirm: function(note) {
                    var attribute = [];
                    $('.pos_note_category_button').each(function () {
                       if($(this).hasClass('active')){
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
                    line.set_attribute(attribute);
                    line.set_note(note);
                },
            });
        }else{
            var warning = "Please select the menu first!";
            self.gui.show_popup('error', {
                title: _t('Warning'),
                body: _t(warning),
            });
        }
    }
});

screens.define_action_button({
    'name': 'Orderline_Note_Inherit',
    'widget': NewOrderlineNoteButton,
});
});
