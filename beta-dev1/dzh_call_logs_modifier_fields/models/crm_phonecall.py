# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class CrmPhonecall(models.Model):
    _inherit = "crm.phonecall"

    crm_market_segment_id = fields.Many2one(
        comodel_name='market.segment',
        string='Market Segment'
    )
    crm_member_type_id = fields.Many2one(
         comodel_name='member.type',
         string='Member Type'
    )
    product_ids = fields.Many2many(
         'product.product', 
         'rel_product_product', 
         'phone_call_id', 'product_id', 
         'Products')
    country_id = fields.Many2one(
         comodel_name='res.country',
         string='Country')
    source_id = fields.Many2one('utm.source', "Source", ondelete='cascade')

    @api.onchange('partner_id')
    def on_change_partner_id(self):
        if self.partner_id:
            print ">>>>>>>>>",self.partner_id
            self.crm_market_segment_id = self.partner_id.market_segment_id.id
            self.crm_member_type_id = self.partner_id.member_type_id.id