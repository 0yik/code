/**
 * Created by vieterp on 8/18/17.
 */

odoo.define('absolutepiano_reusable_poscustomer.poscustomer', function (require) {
"use strict";

    var core = require('web.core');
    var POSSCREEN = require('point_of_sale.screens');
    var POSMODEL = require('point_of_sale.models');
    var Model = require('web.DataModel');
    var session = require('web.session');

    var QWeb = core.qweb;
    var _t = core._t;
    POSSCREEN.ClientListScreenWidget.include({

        show: function(){
            this._super.apply(this, arguments);

            var self = this;
            this.$('.new-customer').off('click');
            this.$('.new-customer').click(function(){
                session.rpc('/web/pos/client_info',{}).done(function(res) {
                    self.display_client_details('edit',{
                        'country_id': res.country,
                        'd_country_id': res.country,
                        'country_code': res.country_code,
                    });
                });
            });
        },

        click_delivery_address : function () {
            var deli_add = $('.delivery-address');
            var check = $('.client-use-delivery-addr').is(":checked");
            if (check){
                deli_add.css('display','block');
            }else {
                deli_add.css('display','none');
            }
        },
        display_client_details: function(visibility,partner,clickpos){
            var res = this._super.apply(this, arguments);
            var self = this;
            var contents = this.$('.client-details-contents');
            contents.on('click','.client-use-delivery-addr',function(){ self.click_delivery_address(); });

            if (visibility === 'edit') {
                if(partner.use_delivery_addr){
                    var use_deli = $('.client-use-delivery-addr');
                    use_deli.trigger( "click" );
                }
            }
            return res
        },
        save_client_details: function(partner) {
            var self = this;
            var fields = {};
            this.$('.client-details-contents .detail').each(function(idx,el){
                fields[el.name] = el.value || false;
            });
            var error_string = '';
            var check_error = false;
            if (!fields.name) {
                error_string += ' Customer';
                check_error = true;
            }

            if (!fields.email) {

                if (check_error){
                    error_string += ', Email'
                }else{
                    error_string += ' Email';
                    check_error = true;
                }
            }
            if (!fields.country_code || !fields.company_mobile) {

                if (check_error){
                    error_string += ', Mobile'
                }else{
                    error_string += ' Mobile';
                    check_error = true;
                }
            }
            if (check_error){
                this.gui.show_popup('error',{
                    'title': _t('Missing Required Fields'),
                    'body': _t(error_string),
                });
                return;
            }
            if (this.uploaded_picture) {
                fields.image = this.uploaded_picture;
            }

            fields.id           = partner.id || false;
            fields.country_id   = fields.country_id || false;
            fields.d_country_id   = fields.d_country_id || false;
            fields.use_delivery_addr = $('.client-use-delivery-addr').is(":checked");

            new Model('res.partner').call('create_from_ui',[fields]).then(function(partner_id){
                self.saved_client_details(partner_id);
            },function(err,event){
                event.preventDefault();
                self.gui.show_popup('error',{
                    'title': _t('Error: Could not Save Changes'),
                    'body': _t('Your Internet connection is probably down.'),
                });
            });
        },
    });
    POSSCREEN.PaymentScreenWidget.include({
        validate_order: function(force_validation) {
            if (!this.pos.get_client()) {
                this.gui.show_popup('error',{
                    'title': _t('Could not Validate'),
                    'body': _t('Missing Customer.'),
                });
                return;
            }
            this._super.apply(this, arguments);
        },
    });
})