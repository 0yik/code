odoo.define('multiple_pos_category', function (require) {
"use strict";
	var Model = require('web.DataModel');
	var models = require('point_of_sale.models');
	var DB = require('point_of_sale.DB');
	models.load_fields('product.product', 'pos_categ_ids');
	
	DB.include({
		add_products: function(products){
	        var stored_categories_temp = this.product_by_category_id;
	        var stored_categories = this.product_by_category_id;
	        if(!products instanceof Array){
	            products = [products];
	        }
	        for(var i = 0, len = products.length; i < len; i++){
	            var product = products[i];
	            var search_string = this._product_search_string(product);
	            var categ_ids = product.pos_categ_ids ? product.pos_categ_ids : this.root_category_id;
	            if (categ_ids.length <= 0){
	            	categ_ids = this.root_category_id;
	            	if(!stored_categories[categ_ids]){
	                    stored_categories[categ_ids] = [];
	                }
	                stored_categories[categ_ids].push(product.id);

	                if(this.category_search_string[categ_ids] === undefined){
	                    this.category_search_string[categ_ids] = '';
	                }
	                this.category_search_string[categ_ids] += search_string;

	                var ancestors = this.get_category_ancestors_ids(categ_ids) || [];

	                for(var j = 0, jlen = ancestors.length; j < jlen; j++){
	                    var ancestor = ancestors[j];
	                    if(! stored_categories[ancestor]){
	                        stored_categories[ancestor] = [];
	                    }
	                    stored_categories[ancestor].push(product.id);

	                    if( this.category_search_string[ancestor] === undefined){
	                        this.category_search_string[ancestor] = '';
	                    }
	                    this.category_search_string[ancestor] += search_string; 
	                }
	            }
	            product.product_tmpl_id = product.product_tmpl_id[0];
            	for(var categ=0,clen=categ_ids.length;categ<clen;categ++){
		            if(!stored_categories[categ_ids[categ]]){
		                stored_categories[categ_ids[categ]] = [];
		            }
		            stored_categories[categ_ids[categ]].push(product.id);
	
		            if(this.category_search_string[categ_ids[categ]] === undefined){
		                this.category_search_string[categ_ids[categ]] = '';
		            }
		            this.category_search_string[categ_ids[categ]] += search_string;
	
		            var ancestors = this.get_category_ancestors_ids(categ_ids[categ]) || [];
	
		            for(var j = 0, jlen = ancestors.length; j < jlen; j++){
		                var ancestor = ancestors[j];
		                if(! stored_categories[ancestor]){
		                    stored_categories[ancestor] = [];
		                }
		                stored_categories[ancestor].push(product.id);
	
		                if( this.category_search_string[ancestor] === undefined){
		                    this.category_search_string[ancestor] = '';
		                }
		                this.category_search_string[ancestor] += search_string; 
		            }
            	}
	            this.product_by_id[product.id] = product;
	            if(product.barcode){
	                this.product_by_barcode[product.barcode] = product;
	            }
	        }
	    }, 
	});
});