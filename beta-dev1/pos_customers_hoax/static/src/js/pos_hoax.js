odoo.define('pos_customers_hoax.pos_hoax', function (require) {
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var _t  = require('web.core')._t;
    var QWeb = core.qweb;
    var Model = require('web.Model');

    models.load_fields('res.partner', ['is_hoax']);

    screens.ClientListScreenWidget.include({
        toggle_save_button:function () {
            this._super();
            if(!this.$el.find('.button.next.highlight').hasClass('oe_hidden')){
                if(this.$el.find('.button.next.highlight:contains("Set Customer")').length>0){
                    $('span.hoax').css('right','150px');
                }else{
                    $('span.hoax').css('right','200px');
                }
            }else{
                $('span.hoax').css('right','0px');
            }
        },
		renderElement: function() {
            var self = this;
            this._super();
            this.$('.input-hoax').change(function(){
                var order = self.pos.get_order();
                var partners = self.pos.partners;
                var active = $(this).is(':checked');
                partners.forEach(function (item) {
                    if(!item.is_hoax){
                        if(active){
                            $('tr.client-line[data-id="'+item.id+'"]').addClass('oe_hidden');
                        }else{
                            $('tr.client-line[data-id="'+item.id+'"]').removeClass('oe_hidden');
                        }
                    }
                });
            });
        },
        render_list:function (partners) {
            var self = this;
            this._super(partners);
            partners.forEach(function (item) {
                if(item.is_hoax){
                    $('tr.client-line[data-id="'+item.id+'"]').find('.hoax-active').hide();
                    $('tr.client-line[data-id="'+item.id+'"]').addClass('hightlight-hoax');
                }
                $('tr.client-line[data-id="'+item.id+'"]').find('.hoax-active').click(function () {
                    var element_node = $(this);
                    self.gui.show_popup('number', {
                        'title':  _t('Enter PIN Number'),
                        'cheap': true,
                        'value': '',
                        'confirm': function(value) {
                            var pin = $('.popup-input').text();
                            if(!pin.trim()){
                                alert('Please Enter PIN First!')
                                return false
                            }
                            else{
                                var model = new Model('res.users');
                                model.call("compare_pin_number", [pin]).then(function (result) {
                                    if (result){
                                        item.is_hoax = true;
                                        new Model('res.partner').call('update_hoax',[item.id]).then(function (result) {
                                            if(result.code == 200){
                                                element_node.parent().parent().addClass('hightlight-hoax');
                                                element_node.hide();
                                            }
                                        });
                                    }
                                    else{
                                        alert("You have entered a wrong PIN")
                                    }
                                });
                            }
                        },
                    });
                });
            });
        }
	});
});