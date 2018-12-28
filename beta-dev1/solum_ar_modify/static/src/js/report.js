odoo.define('solum_ar_modify.report', function(require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var Sidebar = require('web.Sidebar');
    var _t = core._t;
    var qweb = core.qweb;
   
    Sidebar.include({
        add_toolbar: function(toolbar) {
            var self = this;
            var user_id = self.__parentedParent.ViewManager.dataset.context.uid;
            _.each(['print','action','relate'], function(type) {
                var items = toolbar[type];
                if (items) {
                    var actions = _.map(items, function (item) {
                        return {
                            label: item.name,
                            action: item,
                        };
                    });
                    console.log('actions',actions);
                    ajax.jsonRpc("/get_compnay_name", 'call', {
                        user_id: user_id,
                    }).done(function(data){
                        $.each(actions, function(key,value) {
                            if(data.toLowerCase().indexOf('sol')>=0){
                                if (value){
                                    if (value.label.toLowerCase().indexOf('design') >=0){
                                        actions.splice(key,1)
                                        self.add_items(type === 'print' ? 'print' : 'other', actions);
                                    }
                                }
                            }
                            if(data.toLowerCase().indexOf('design')>=0){
                                if (value){
                                    if (value.label.toLowerCase().indexOf('sol') >=0){
                                        actions.splice(key,1)
                                        self.add_items(type === 'print' ? 'print' : 'other', actions);
                                    }
                                }
                            }
                        });
                    });
                }
            });
        },
    });
    
});
