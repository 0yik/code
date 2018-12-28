# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_time_id = fields.Many2one('delivery.time.dynamic','Delivery Time')



class DeliveryTimeDynamic(models.Model):
    _name = 'delivery.time.dynamic'
    _rec_name='name'

    name = fields.Char('Name', required=True)
    

class CoatingEnquiry(models.Model):
    _inherit = 'coating.enquiry'
    
    name = fields.Char('Name', required=True)
