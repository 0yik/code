# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, tools, _


class Pos_Promotion(models.Model):
    _inherit = 'pos.promotion'

    period_type = fields.Selection([('all time discount','All Time Discount'),
									('birthday discount','Birthday Discount'),
									('certain time discount','Certain Time Discount')
									], string='Period Type')
    item_type = fields.Selection([('all item no exception','All Item No Exception'),
									('all item with exception','All Item With Exception'),
									('must include specific item','Must Include Specific Item'),
									('specific item only','Specific Item Only')
									], string='Item Type', help='1. All item No Exception : Promo will apply to all item without exception, you don`t have to enter any item.\n 2.All item with Exception : Promo will apply to all item except item listed here, please select exceptional item from the list. \n 3.Must Include Specific Item : Promo will apply if included specific item listed here, please select functional from list. \n 4.Specific Item Only : Promo will apply only to specific item listed here, please select functional item from the list')
