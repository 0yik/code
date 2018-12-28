odoo.define('down_payment_pos.pos_create_deposit', function (require) {
"use strict";
    var models = require('point_of_sale.models');
    var Model = require('web.DataModel');
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');
    // var floors = require('pos_restaurant.floors');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var PopupWidget = require('point_of_sale.popups');

    var QWeb = core.qweb;
    var _t  = require('web.core')._t;



    var CreateCustomerDeposit = screens.ScreenWidget.extend({
        template: 'CreateCustomerDeposit',

        init: function(parent, options) {
            this._super(parent, options);
            var self = this;

        },

        show: function () {
            this._super();
            var self = this;
            var partner_id = self.pos.selected_partner_id;
            var partner = self.pos.db.get_partner_by_id(parseInt(partner_id));
            this.$el.find('.create').off().click(function () {
                self.create_deposit();
            });
            this.$el.find('.button.back').click(function () {
                self.gui.show_screen('clientlist');
            });



            self.render_form(partner);

        },
        create_deposit: function () {
            var self = this;
            var partner_id = self.pos.selected_partner_id;
            var partner = self.pos.db.get_partner_by_id(parseInt(partner_id));
            var amount = $('input.amount').val();
            var payment_date = $('input.payment_date').val();
            var payment_memthod = $('select.payment_method').val();
            var deposit_account = $('select.deposit_account').val();
            var reference = $('input.reference').val();
            var event = $('input.event').val();
            var event_date = $('input.event_date').val();
            //validate
            if(!amount || amount<0){
                alert('invalid amount');
                return;
            }
            if(!payment_date){
                alert('invalid payment date');
                return;
            }
            if(!event_date){
                alert('invalid event date');
                return;
            }

            var context = {
                'partner_id': partner_id,
                'amount':amount,
                'communication': reference,
                'payment_date': payment_date,
                'journal_id':payment_memthod,
                'writeoff_account_id':deposit_account,
                'event' : event ? event : '',
                'event_date': event_date,
            };
            new Model('account.payment').call('create_customer_deposit_from_pos',[context],{context:context}).then(function (result) {
                if(result.code == 200){
                    alert('Created Successfully');
                    self.pos.gui.show_screen('products');
                }else{
                    alert('something error');
                }
            });
        },
        render_form: function (partner) {
            var self = this;
            var render_node = this.$el[0].querySelector('.customer-deposit-details');
            render_node.innerHTML = "";
            var customer_html = QWeb.render('FormCreateCustomerDeposit', {
                widget: self,
                partner: partner
            });
            var div = document.createElement('div');
            div.innerHTML = customer_html;
            render_node.appendChild(div);
            this.render_select();

        },
        render_select: function () {
            var self = this;
            var account_journal = new Model('account.journal');
                account_journal.query(['id', 'name'])
                 .filter([['type', 'in', ['bank','cash']]])
                 .limit(100)
                 .all().then(function (data) {
                     var render_node = self.$el[0].querySelector('.render-payment-method');
                    render_node.innerHTML = "";
                    var customer_html = QWeb.render('InputSelectPaymentMethod', {
                        list: data
                    });
                    var div = document.createElement('div');
                    div.innerHTML = customer_html;
                    $(render_node).replaceWith($(div.children[0]));
                }
            );
            var account_account = new Model('account.account');
                account_account.query(['id','code', 'name'])
                 .filter([['deprecated', '=', false]])
                 .limit(100)
                 .all().then(function (data) {
                     var render_node = self.$el[0].querySelector('.render-deposit-account');
                    render_node.innerHTML = "";
                    var customer_html = QWeb.render('InputSelectDepositAccount', {
                        list: data
                    });
                    var div = document.createElement('div');
                    div.innerHTML = customer_html;
                    $(render_node).replaceWith($(div.children[0]));
                }
            );
        },

        partner_icon_url: function(id){
            return '/web/image?model=res.partner&id='+id+'&field=image_small';
        },
        render_element: function () {
            this._super();
        },

    });

    gui.define_screen({
        'name': 'createcustomerdepositscreen',
        'widget': CreateCustomerDeposit,
        'condition': function(){
            return true;
        },
    });

    return CreateCustomerDeposit;
});