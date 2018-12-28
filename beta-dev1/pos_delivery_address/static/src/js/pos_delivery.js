
odoo.define('pos_delivery_address.pos_db', function (require) {
    "use strict";
    var DB = require('point_of_sale.DB');
    
    DB.include({
        init: function(options){
            this.add_delivery_address_by_id = {};
            this._super(options);
        },

        get_delivery_address_by_id: function(id){
            return this.add_delivery_address_by_id[id];
        },

        add_delivery_addresses: function(line){
            for(var i=0 ; i < line.length; i++){
                this.add_delivery_address_by_id[line[i].id] = line[i];
            }
        },
    });
});

odoo.define('pos_delivery_address.pos_custom', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var SuperPosModel = models.PosModel.prototype;
    var SuperOrder = models.Order.prototype;

    models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes) {
            SuperPosModel.initialize.call(this, session, attributes);
            var self = this;

            self.models.push({
                model:  'delivery.address',
                fields: ['street','city','state_id','country_id','zip'],
                loaded: function(self,addresses){
                    self.db.add_delivery_addresses(addresses);
                    self.deliveriy_addresses = addresses;
                    self.db.add_delivery_addresses = addresses;
                },
            });
            var partner_model = _.find(this.models, function(model){ return model.model === 'res.partner'; });
            if(!partner_model){
                self.models.push({
                    model:  'res.partner',
                    fields: ['delivery_address_ids','name','street','city','state_id','country_id','vat','phone','zip','mobile','email','barcode','write_date','property_account_position_id'],
                    domain: [['customer','=',true]], 
                    loaded: function(self,partners){
                        self.partners = partners;
                        self.db.add_partners(partners);
                    },
                });
            }else{partner_model.fields.push('delivery_address_ids')}
            
        }
    });
    models.Order = models.Order.extend({
        init_from_JSON: function(json) {
            return SuperOrder.init_from_JSON.call(this, json);
            this.set_delivery_address(json.delivery_address_id)  
        },
        set_delivery_address: function(delivery_address_id){
            this.assert_editable();
            this.set('delivery_address_id',delivery_address_id);
        },
        get_delivery_address: function(){
            return this.get('delivery_address_id');
        },
        get_delivery_address_details: function(){
            if(this.get('delivery_address_id')){
                var delivery = this.pos.db.get_delivery_address_by_id(this.get('delivery_address_id'));
                return (delivery.street || '') +', '+ 
                                      (delivery.zip || '')    +' '+
                                      (delivery.city || '')   +', '+ 
                                      (delivery.country_id[1] || '')
            }
            return ''
        },
        export_as_JSON: function() {
            var result = SuperOrder.export_as_JSON.call(this);
            var delivery_address_id = this.get_delivery_address();
            if (!isNaN(delivery_address_id)){
                result.delivery_address_id = parseInt(delivery_address_id)
            }else{result.delivery_address_id=false}
            return result
        }
    });
});

odoo.define('pos_delivery_address.screens', function (require) {
    var screens = require('point_of_sale.screens');

    var SuperClientListScreenWidget = screens.ClientListScreenWidget.prototype

    screens.ClientListScreenWidget = screens.ClientListScreenWidget.include({
        
    display_client_details: function(visibility,partner,clickpos){
        var self = this;
        if(visibility === 'show'){
            var order = this.pos.get_order();
            partner.delivery_address = []
            if(partner.delivery_address_ids){
                for (var i = partner.delivery_address_ids.length - 1; i >= 0; i--) {
                    var delivery = this.pos.db.get_delivery_address_by_id(partner.delivery_address_ids[i])
                    partner.delivery_address.push([partner.delivery_address_ids[i], 
                        (delivery.street || '') +', '+ 
                                          (delivery.zip || '')    +' '+
                                          (delivery.city || '')   +', '+ 
                                          (delivery.country_id[1] || '')])
                };
                partner.selected_delivery_address_id = order.get_delivery_address();
            }
        }
        this._super(visibility,partner,clickpos);
        self.$('#delivery-address').change(function(){
            self.delivery_address = $( this ).val();
        });
    },
    save_changes: function(){
        this._super();
        var order = this.pos.get_order();
        if( this.has_client_changed() ){
            order.set_delivery_address(this.delivery_address);
        }
        this.delivery_address = false
    },
    });


});


