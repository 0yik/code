# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResPartnerUSERS(models.Model):
    _inherit = 'dzh.partner.user'
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
    	args = args or []
    	recs = self.browse()
    	if self._context.has_key('dzh_user'):
    		if self._context.has_key('partner_id') and self._context.get('partner_id'):
    			res_partner_ids = self.env['res.partner'].browse(self._context.get('partner_id'))
    			recs = res_partner_ids.partner_users
    	else:
    		recs = self.search([('name', operator, name)] + args, limit=limit)
    	return recs.name_get()

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    
    @api.onchange('dzh_partner_user_ids')
    def _count_user_id(self):
        values = {
            'number_of_dzh_user': len(self.dzh_partner_user_ids),
        }
        self.update(values)
    
    dzh_partner_user_ids = fields.Many2many('dzh.partner.user','sol_dzh_partner_rel','sol_id','dzh_partner_id', string='User ID')
    number_of_dzh_user = fields.Integer('Number Of User Id')
    #number_of_dzh_user = fields.Integer(compute='_count_user_id', string='Number Of User Id', readonly=True)
    
