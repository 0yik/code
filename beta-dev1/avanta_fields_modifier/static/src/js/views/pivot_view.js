odoo.define('avanta_fields_modifier.PivotView', function (require) {
"use strict";

    var PivotView = require('web.PivotView');
    var core = require('web.core');
    var crash_manager = require('web.crash_manager');
    var data_manager = require('web.data_manager');
    var formats = require('web.formats');
    var framework = require('web.framework');
    var Model = require('web.DataModel');
    var session = require('web.session');
    var Sidebar = require('web.Sidebar');
    var utils = require('web.utils');
    var View = require('web.View');

    var _lt = core._lt;
    var _t = core._t;
    var QWeb = core.qweb;

    PivotView.include({
        prepare_fields: function (fields) {
            var self = this,
                groupable_types = ['many2one', 'char', 'boolean',
                                   'selection', 'date', 'datetime'];
            var crm_field_names = ['create_date','stage_id','user_id','products','partner_id','industry_type'];
//            var crm_field_names = ['create_date','stage_id','country_id','user_id','products','partner_id','industry_type'];
            this.fields = fields;
            _.each(fields, function (field, name) {
                var other_fields = [];
                other_fields.push(name);
                if ((name !== 'id') && (field.store === true)) {
                    if (field.type === 'integer' || field.type === 'float' || field.type === 'monetary') {
                        self.measures[name] = field;
                    }
                    if (_.contains(groupable_types, field.type)){

                        if ((crm_field_names.indexOf(name) > -1) && (self._model['name'] == 'crm.opportunity.report')) {
                            self.groupable_fields[name] = field;
                            var str = field['string'];
                            if (str == 'Creation Date') {
                                var res = str.replace('Creation Date','Period');
                            }
                            if (str == 'Country') {
                                var res = str.replace('Country','Location');
                            }
                            if (str == 'User') {
                                var res = str.replace('User','Sales Person');
                            }
                            if (str == 'Products') {
                                var res = str.replace('Products','Product');
                            }
                            if (str == 'Stage') {
                                var res = str.replace('Stage','Stages');
                            }
                            if (str == 'Partner') {
                                var res = str.replace('partner','partners');
                            }
                            if (str == 'Industry Type') {
                                var res = str.replace('Industry Type','Industry Types');
                            }
                            field['string'] = res;
                        }else if ((other_fields.indexOf(name) > -1) && (self._model['name'] != 'crm.opportunity.report')) {
                          self.groupable_fields[name] = field;
                        }
                    }
                }
            });
            this.measures.__count__ = {string: _t("Count"), type: "integer"};
        },
    });
});