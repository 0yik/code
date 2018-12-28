odoo.define("pos_price_list.pos_price_list",function (require) {

    var core = require('web.core');
    var Model = require('web.DataModel');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var data = require('web.data');
    var chorme = require("point_of_sale.chrome");
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var load_product;

    var QWeb = core.qweb;
    var _t = core._t;
    var product_model = new Model('product.product');

    models.load_fields("res.partner",['property_product_pricelist'])

    var products_pricelist;
    product_model.call("get_products_by_pricelist",[]).then(function(callback){
        products_pricelist = callback;
        $('.pricelist_selection').change();
    },function(err,event) {event.preventDefault();});

    models.PosModel.prototype.models.push({
        model:  'product.pricelist',
        fields: ['name', 'id','currency_id'],
        domain:  null,
        loaded: function(self, pricelists){
            self.pricelists = pricelists;
//            product_model.call("get_products_by_pricelist",[]).then(function(callback){
//                self.products_pricelist = callback;
//                $('.pricelist_selection').change();
//            },function(err,event) {event.preventDefault();});
        },
    },{
        model: 'res.currency',
        fields: ['name','symbol','position','rounding'],
        loaded: function(self, currencies){
            self.all_currency = currencies;
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function() {
            this.set({
                'pricelist_id' : null
            })
            _super_order.initialize.apply(this,arguments);
            this.price_list_container_minimize_maximize = _t("minimize");
        },
        set_client: function(client){
            var self = this;
            if(client && client.property_product_pricelist && client.property_product_pricelist[0]){
                _.each(self.pos.pricelists,function(pricelist){
                    if (pricelist.id == client.property_product_pricelist[0]){
                        _.each(self.pos.all_currency,function(currency){
                            if(currency.id == pricelist.currency_id[0]){
                                $(".pricelist_selection").val(pricelist.id + '-' + pricelist.name  + '-'+ pricelist.currency_id[0] );
                            }
                        });
                    }
                });
            }
            $('.pricelist_selection').change();
            _super_order.set_client.apply(this,arguments);
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);
            var self = this;
            self.attributes.pricelist_id = json.pricelist_id;
        },
        export_as_JSON : function(json) {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            var self =this;
            json.pricelist_id = this.attributes.pricelist_id ? this.attributes.pricelist_id : null;
            json.creation_date =  self.validation_date || self.creation_date;
            return json;
        },
    });

    var PricelistWidget = PosBaseWidget.extend({
        template: 'PricelistWidget',
        renderElement: function() {
            var self = this;
            this._super();
            var curr_order = self.pos.get_order();
            if(curr_order && curr_order.attributes.pricelist_id){
                for(pricelist in self.pos.pricelists){
                    if(self.pos.pricelists[pricelist].id == curr_order.attributes.pricelist_id){
                        curr_order.selected_pricelist = curr_order.pos.pricelists[pricelist].id;
                        var product_list =  self.pos.db.get_product_by_category(0);
                        self.$(".pricelist_selection").val(curr_order.pos.pricelists[pricelist].id + '-' + curr_order.pos.pricelists[pricelist].name + '-'+curr_order.pos.pricelists[pricelist].currency_id[0] );
                        self.pos.current_pricelist = curr_order.pos.pricelists[pricelist].id;
                        var default_currency = true;
                        if(curr_order.selected_pricelist){
                            _.each(product_list, function(product) {
                                if(products_pricelist && products_pricelist[curr_order.selected_pricelist][product.id]){
                                    product.price = products_pricelist[curr_order.selected_pricelist][product.id];
                                }else  if(products_pricelist && products_pricelist[curr_order.selected_pricelist][product.id] == 0){
                                    product.price = products_pricelist[curr_order.selected_pricelist][product.id];
                                }
                            });
                        }
                        var default_currency = true;
                        _.each(curr_order.pos.all_currency,function(currency){
                            if(currency.id == curr_order.pos.pricelists[pricelist].currency_id[0]){
                                curr_order.pos.currency['id'] = currency.id;
                                curr_order.pos.currency['symbol'] = currency.symbol;
                                curr_order.pos.currency['position'] = currency.position;
                                default_currency = false;
                            }
                        });
                        if(default_currency){
                            self.pos.currency['id'] = self.pos.currency_temp_id;
                            self.pos.currency['symbol'] = self.pos.currency_temp_symbol;
                            self.pos.currency['position'] = self.pos.currency_temp_position;
                        }
                    }
                }
            }
            self.$('.pricelist_selection').on( "change", function(attrs){
                var value = $(this).val();
                var curr_order = self.pos.get_order();
                curr_order.selected_pricelist = parseInt(value);
                self.pos.current_pricelist = parseInt(value);
                self.pos.current_pricelist_id = value;
                var default_currency = true;
                _.each(self.pos.all_currency,function(currency){
                    if(currency.id == parseInt(attrs.currentTarget.value.split("-")[2])){
                        self.pos.currency['id'] = currency.id;
                        self.pos.currency['symbol']= currency.symbol;
                        self.pos.currency['position']= currency.position;
                        default_currency = false;
                    }
                });
                if(default_currency){
                    self.pos.currency['id'] = self.pos.currency_temp_id;
                    self.pos.currency['symbol']= self.pos.currency_temp_symbol;
                    self.pos.currency['position']= self.pos.currency_temp_position;
                }
                var product_list =  self.pos.db.get_product_by_category(0);
                if(curr_order.selected_pricelist){
                    _.each($(".pricelist_selection option"), function(att){
                        if(att.value == self.pos.current_pricelist_id){
                            att.selected = true;
                        }
                    });
                    _.each(product_list, function(product) {
                        if(products_pricelist && products_pricelist[curr_order.selected_pricelist][product.id]){
                            product.price = products_pricelist[curr_order.selected_pricelist][product.id];
                        }else if(products_pricelist && products_pricelist[curr_order.selected_pricelist][product.id] == 0){
                            product.price = products_pricelist[curr_order.selected_pricelist][product.id];
                        }
                    });
                    load_product.set_product_list(product_list);
                    _.each(curr_order.orderlines.models, function(line){
                        if(products_pricelist && products_pricelist[curr_order.selected_pricelist][line.product.id]){
                            if(line.description_ids){
                                var price = products_pricelist[curr_order.selected_pricelist][line.product.id]; 
                               _.each(line.description_ids,function(desc){
                                   price = price +  products_pricelist[curr_order.selected_pricelist][desc.split('_')[1]];
                               });
                               line.set_unit_price(price);
                            }else{
                                line.set_unit_price(products_pricelist[curr_order.selected_pricelist][line.product.id]);
                            }
                        }else if(products_pricelist && products_pricelist[curr_order.selected_pricelist][line.product.id] == 0){
                            if(line.description_ids){
                                var price = products_pricelist[curr_order.selected_pricelist][line.product.id]; 
                               _.each(line.description_ids,function(desc){
                                   price = price +  products_pricelist[curr_order.selected_pricelist][desc.split('_')[1]];
                               });
                               line.set_unit_price(price);
                            }else{
                                line.set_unit_price(products_pricelist[curr_order.selected_pricelist][line.product.id]);
                            }
                        }
                    });
                }
                self.pos.get('selectedOrder').set('pricelist_id', self.pos.current_pricelist);
                self.pos.get('selectedOrder').attributes.pricelist_id = self.pos.current_pricelist;
            });
        }
    });

    screens.ProductListWidget.include({
        render_product: function(product){
            var image_url = this.get_product_image_url(product);
            var product_html = QWeb.render('Product',{ 
                  widget:  this, 
                  product: product, 
                  image_url: this.get_product_image_url(product),
            });
            var product_node = document.createElement('div');
            product_node.innerHTML = product_html;
            product_node = product_node.childNodes[1];
            this.product_cache.cache_node(product.id,product_node);
            return product_node;
        },
    });

    screens.ProductScreenWidget.include({
        start: function(){
            var self = this;
            this._super();
            this.PricelistWidget = new PricelistWidget(this,{});
            this.PricelistWidget.appendTo(this.$('.placeholder-OptionsListWidget .option_list_box_container'));
            load_product = this.product_list_widget;
        },
    });

    chorme.OrderSelectorWidget.include({
        renderElement: function(){
            var self = this;
            this._super();
            var order = self.pos.get_order();
            var curr_order = self.pos.get_order();
            if(order && order.attributes.pricelist_id){
                for(pricelist in self.pos.pricelists){
                    if(self.pos.pricelists[pricelist].id == order.attributes.pricelist_id){
                        curr_order.selected_pricelist = order.pos.pricelists[pricelist].id;
                        var product_list =  self.pos.db.get_product_by_category(0);
                        $(".pricelist_selection").val(order.pos.pricelists[pricelist].id + '-' + order.pos.pricelists[pricelist].name + '-'+order.pos.pricelists[pricelist].currency_id[0] );
                        self.pos.current_pricelist = order.pos.pricelists[pricelist].id;
                        var default_currency = true;
                        if(curr_order.selected_pricelist){
                            _.each(product_list, function(product) {
                                if(products_pricelist && products_pricelist[curr_order.selected_pricelist][product.id]){
                                    product.price = products_pricelist[curr_order.selected_pricelist][product.id];
                                }else if(products_pricelist && products_pricelist[curr_order.selected_pricelist][product.id] == 0){
                                    product.price = products_pricelist[curr_order.selected_pricelist][product.id];
                                }
                            });
                        }
                        var default_currency = true;
                        _.each(order.pos.all_currency,function(currency){
                            if(currency.id == order.pos.pricelists[pricelist].currency_id[0]){
                                order.pos.currency['id'] = currency.id;
                                order.pos.currency['symbol'] = currency.symbol;
                                order.pos.currency['position'] = currency.position;
                                default_currency = false;
                            }
                        });
                        if(default_currency){
                            self.pos.currency['id'] = self.pos.currency_temp_id;
                            self.pos.currency['symbol'] = self.pos.currency_temp_symbol;
                            self.pos.currency['position'] = self.pos.currency_temp_position;
                        }
                        if(load_product){
                            load_product.set_product_list(product_list);
                        }
                    }
                }
            }else{
                if(order){
                    var self = this;
                    _.each(this.pos.pricelists,function(pricelist){
                        if(pricelist.id == self.pos.pricelist.id){
                            $(".pricelist_selection").val(pricelist.id + '-' + pricelist.name  + '-'+ pricelist.currency_id[0] );
                            self.pos.current_pricelist = pricelist.id;
                            order.set('pricelist_id', parseInt(pricelist.id));
                            order.attributes.pricelist_id = parseInt(pricelist.id);
                        }
                    });
                    $(".pricelist_selection").change(); 
                }
                
            }
        },
    });

    chorme.Chrome.include({
        init: function() {
            var self = this;
            this._super(arguments[0],{});
            this.pos.ready.done(function(){
                self.pos.currency_temp_id = self.pos.currency['id'];
                self.pos.currency_temp_symbol = self.pos.currency['symbol'];
                self.pos.currency_temp_position = self.pos.currency['position'];
            }).fail(function(err){   // error when loading models data from the backend
                self.loading_error(err);
            });
        },
    });

});