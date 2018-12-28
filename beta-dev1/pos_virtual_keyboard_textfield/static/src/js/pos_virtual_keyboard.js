odoo.define('pos_virtual_keyboard_textfield.pos_virtual_keyboard', function (require) {
"use strict";
	var keyboard = require('point_of_sale.keyboard');
	var screen = require('point_of_sale.screens');
	var core = require('web.core');
	var Model = require('web.DataModel');
	var utils = require('web.utils');
	var formats = require('web.formats');

	var QWeb = core.qweb;
	var _t = core._t;
	
	keyboard.OnscreenKeyboardWidget.include({
		deleteAllCharacters: function(){
			return
		}
		
	});
	screen.ProductCategoriesWidget.include({
		renderElement: function(){
	        var self = this;
	        this._super();
	        if(this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard){
	            this.chrome.widget.keyboard.connect($(this.el.querySelector('.searchbox input')));	        	
	        }					        
			this.el.querySelector('.searchbox input').addEventListener('click',function(event){
				self.set_virtual_keyboard();
			});
			
		},
		set_virtual_keyboard:function(){
	        if(this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard){
	            this.chrome.widget.keyboard.connect($(this.el.querySelector('.searchbox input')));	        	
	        }					        			
		},
	});
	
	screen.ClientListScreenWidget.include({
	    display_client_details: function(visibility,partner,clickpos){
	
	        var self = this;
	        var contents = this.$('.client-details-contents');
	        var parent   = this.$('.client-list').parent();
	        var scroll   = parent.scrollTop();
	        var height   = contents.height();

	        contents.off('click','.button.edit'); 
	        contents.off('click','.button.save'); 
	        contents.off('click','.button.undo'); 
	        contents.on('click','.button.edit',function(){ self.edit_client_details(partner); });
	        contents.on('click','.button.save',function(){ self.save_client_details(partner); });
	        contents.on('click','.button.undo',function(){ self.undo_client_details(partner); });
	        this.editing_client = false;
	        this.uploaded_picture = null;

	        if(visibility === 'show'){
	            contents.empty();
	            contents.append($(QWeb.render('ClientDetails',{widget:this,partner:partner})));
	            var new_height   = contents.height();
	            if(!this.details_visible){
	                if(clickpos < scroll + new_height + 20 ){
	                    parent.scrollTop( clickpos - 20 );
	                }else{
	                    parent.scrollTop(parent.scrollTop() + new_height);
	                }
	            }else{
	                parent.scrollTop(parent.scrollTop() - height + new_height);
	            }

	            this.details_visible = true;
	            this.toggle_save_button();
	        } else if (visibility === 'edit') {
	            this.editing_client = true;
	            contents.empty();
	            contents.append($(QWeb.render('ClientDetailsEdit',{widget:this,partner:partner})));
	            contents.find('.client-detail input').each(function(event){
	            	self.bind_virtual_keyboard(this);
	            	$(this).on('click',function(){
	        			self.bind_virtual_keyboard(this);
	            	});
	            });
	            self.bind_virtual_keyboard(contents.find('.client-name'));
	            contents.find('.client-name').on('click',function(event){
	            	self.bind_virtual_keyboard(contents.find('.client-name'));
	            });

	            this.toggle_save_button();

	            contents.find('.image-uploader').on('change',function(event){
	                self.load_image_file(event.target.files[0],function(res){
	                    if (res) {
	                        contents.find('.client-picture img, .client-picture .fa').remove();
	                        contents.find('.client-picture').append("<img src='"+res+"'>");
	                        contents.find('.detail.picture').remove();
	                        self.uploaded_picture = res;
	                    }
	                });
	            });
	        } else if (visibility === 'hide') {
	            contents.empty();
	            if( height > scroll ){
	                contents.css({height:height+'px'});
	                contents.animate({height:0},400,function(){
	                    contents.css({height:''});
	                });
	            }else{
	                parent.scrollTop( parent.scrollTop() - height);
	            }
	            this.details_visible = false;
	            this.toggle_save_button();
	        }
	    },


	    bind_virtual_keyboard: function(order){
	        if(this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard){
	        	this.chrome.widget.keyboard.connect($(order));
	    	}            	        	
	    },	    

	});	
});
