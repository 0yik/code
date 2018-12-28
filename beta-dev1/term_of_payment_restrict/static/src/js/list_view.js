odoo.define('term_of_payment_restrict.list_view', function (require) {
'use strict';
    var session = require('web.session');
    var ListView = require('web.ListView');

     ListView.include({
        load_list: function(data, grouped) {
            var self = this;
            if(this.model == 'sale.order.line'){
                try{
                    var list_id = [];
                    self.dataset.ids.forEach(function (item) {
                        var data = self.dataset.cache[item].from_read;
                        if (data.using_discount || !data.is_promo){
                            list_id.push(item);
                        }
                    });
                    self.dataset.ids = list_id;
                }catch (error){
                    console.log(error)
                }
            }
            return this._super(data,grouped);
        },
    });
});
