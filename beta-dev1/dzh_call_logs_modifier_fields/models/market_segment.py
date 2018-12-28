# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models

class MarketSegment(models.Model):
    _name = "market.segment.dzh"
    
    name = fields.Char(
        string='Name',
        required=True,
    )


class MemberType(models.Model):
    _name = "member.type.dzh"
    
    name = fields.Char(
        string='Name',
        required=True,
    )