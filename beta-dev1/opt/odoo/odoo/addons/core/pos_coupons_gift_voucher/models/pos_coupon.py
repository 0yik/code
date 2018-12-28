# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2015-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from openerp import fields, models, api, _
from openerp.exceptions import Warning
import random
from datetime import date, datetime

class pos_gift_coupon(models.Model):
    _name = 'pos.gift.coupon'


    @api.one
    def existing_coupon(self,code):
    	#print "****************codeeeeeeeeeeeeeeeeeeeeeeeee",code
    	coupon_code_record =self.search([('gift_coupen_code', '=',code)])
    	if len(coupon_code_record) == 1:
    		#print "########################yesssssssssssssssssssssssssssssssss"
    		coupon_record = coupon_code_record[0]
    		return True
    	else:
    		return False
    	
    @api.multi
    def search_coupon(self,code):
    	#print "********search********codeeeeeeeeeeeeeeeeeeeeeeeee",code
    	coupon_code_record =self.search([('gift_coupen_code', '=',code)])
    	#print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&coupon_code_record",coupon_code_record
    	
    	return [coupon_code_record.id,coupon_code_record.amount]
    				


    @api.model
    def default_get(self, fields):
        pos_config_obj = self.env['pos.coupons.setting']
        if pos_config_obj.search_count([('active', '=',True)]) !=1 :
            raise Warning(_('Please configure gift coupons'))        

        
        rec = super(pos_gift_coupon, self).default_get(fields)
        config_obj = self.env['pos.coupons.setting']
        if config_obj.search_count([('active', '=',True)]) == 1:
			 config_record = config_obj.search([('active', '=', True)])[0]
			 if config_record:
			 	rec.update ({'total_available': config_record.default_availability,
								'amount': config_record.default_value ,
								'validity': config_record.default_validity})				
        return rec



    @api.one
    @api.constrains('amount')
    def _check_amount(self):
        confing_obj = self.env['pos.coupons.setting']
        if confing_obj.search_count([('active', '=',True)]) == 1:
            config_record = confing_obj.search([('active', '=', True)])[0]
            if self.amount < config_record.min_coupan_value or self.amount > config_record.max_coupan_value:
			    raise Warning(_( "Amount is wrong"))




    @api.model
    def create(self, vals):
        pos_config_obj = self.env['pos.coupons.setting']
        if pos_config_obj.search_count([('active', '=',True)]) !=1 :
            raise Warning(_('Please configure gift coupons'))        
  
        else:
            code =(random.randrange(1111111111111,9999999999999))
            if pos_config_obj.search_count([('active', '=',True)]) == 1:
                config_record = pos_config_obj.search([('active', '=', True)])[0]
                if config_record.default_availability != -1:
                    if self.search_count([]) == config_record.default_availability:
                        raise Warning(_('You can only create %d coupons  ') %  config_record.default_availability )                         
                config_record = config_record.search([('active', '=', True)])[0]
                if config_record:
					vals.update({'expiry_date':config_record.max_exp_date,
									'gift_coupen_code': str(code),
                                    
								 })
        return super(pos_gift_coupon,self).create(vals)       


		

		
    name  = fields.Char('Name')
    gift_coupen_code = fields.Char('Gift Coupon Code')
    user_id  =  fields.Many2one('res.users' ,'Created By',default  = lambda self: self.env.user)
    issue_date  =  fields.Datetime(default = datetime.now(), )
    expiry_date  = fields.Datetime('Expiry date')
    validity =  fields. Integer('Validity(in days)')
    total_available = fields.Integer('Total Available')
    partner_id  =  fields.Many2one('res.partner')
    order_ids = fields.One2many('pos.order','coupon_id')
    active = fields.Boolean('Active')
    amount  =  fields.Float('Coupon Amount')
    description  =  fields.Text('Note')	

	
	

